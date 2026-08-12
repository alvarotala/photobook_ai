from __future__ import annotations

from contextlib import asynccontextmanager
import hashlib
import logging
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .identity_reference import (
    IdentityReferenceError,
    convert_source_to_png,
    create_centered_identity_closeup,
)
from .openai_gateway import (
    OPENAI_IMAGE_ENDPOINT,
    OPENAI_IMAGE_OUTPUT_FORMAT,
    OPENAI_IMAGE_QUALITY,
    OPENAI_IMAGE_SIZE,
    ImageGateway,
    ImageGenerationError,
    OpenAIImageGateway,
)
from .scenes import SCENES
from .storage import ImageStorage


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
logger = logging.getLogger("photobook.server")


def create_app(
    *,
    settings: Settings | None = None,
    gateway: ImageGateway | None = None,
) -> FastAPI:
    settings = settings or Settings.from_environment()
    storage = ImageStorage(settings.images_dir)
    gateway = gateway or OpenAIImageGateway(api_key=settings.api_key, model=settings.model)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        missing_templates = [
            scene.template_filename
            for scene in SCENES.values()
            if not scene.template_path(settings.templates_dir).is_file()
        ]
        if missing_templates:
            raise RuntimeError(f"Faltan plantillas: {', '.join(missing_templates)}")
        yield

    app = FastAPI(title="Photobook AI Server", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.gateway = gateway
    app.state.storage = storage

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.mount("/images", StaticFiles(directory=settings.images_dir), name="images")

    @app.exception_handler(ImageGenerationError)
    async def generation_error_handler(_: Request, exc: ImageGenerationError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "openai_configured": bool(settings.api_key),
            "model": settings.model,
        }

    @app.post("/api/generate")
    async def generate(
        request: Request,
        scene: Annotated[str, Form()],
        photo: Annotated[UploadFile, File()],
    ) -> dict[str, str]:
        scene_definition = SCENES.get(scene)
        if scene_definition is None:
            raise HTTPException(status_code=422, detail="Escena desconocida")
        if photo.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="La foto debe ser JPEG, PNG o WebP")

        participant_filename = Path(photo.filename or "participant.jpg").name
        participant_bytes = await photo.read(settings.max_upload_bytes + 1)
        await photo.close()
        if not participant_bytes:
            raise HTTPException(status_code=422, detail="La foto está vacía")
        if len(participant_bytes) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="La foto supera el límite de 20 MB")

        try:
            source_png = convert_source_to_png(participant_bytes)
            identity_closeup_png = create_centered_identity_closeup(participant_bytes)
        except IdentityReferenceError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        image_id = storage.create_id()
        template_bytes = scene_definition.template_path(settings.templates_dir).read_bytes()
        mask_bytes = scene_definition.mask.to_png()
        template_filename = storage.save_png(template_bytes, image_id, suffix="-T")
        source_filename = storage.save_png(source_png, image_id, suffix="-S")
        identity_filename = storage.save_png(identity_closeup_png, image_id, suffix="-F")
        mask_filename = storage.save_png(mask_bytes, image_id, suffix="-M")
        request_manifest = {
            "endpoint": OPENAI_IMAGE_ENDPOINT,
            "model": settings.model,
            "size": OPENAI_IMAGE_SIZE,
            "quality": OPENAI_IMAGE_QUALITY,
            "output_format": OPENAI_IMAGE_OUTPUT_FORMAT,
            "scene": scene,
            "prompt": scene_definition.prompt,
            "multipart": [
                {
                    "field": "image[]",
                    "role": "template",
                    "filename": template_filename,
                    "sha256": hashlib.sha256(template_bytes).hexdigest(),
                },
                {
                    "field": "image[]",
                    "role": "participant-source",
                    "filename": source_filename,
                    "sha256": hashlib.sha256(source_png).hexdigest(),
                },
                {
                    "field": "image[]",
                    "role": "participant-face-reference",
                    "filename": identity_filename,
                    "sha256": hashlib.sha256(identity_closeup_png).hexdigest(),
                },
                {
                    "field": "mask",
                    "role": "edit-mask",
                    "filename": mask_filename,
                    "sha256": hashlib.sha256(mask_bytes).hexdigest(),
                },
            ],
        }
        request_filename = storage.save_request_manifest(request_manifest, image_id)
        logger.info(
            "Sending scene=%s payload=%s to OpenAI",
            scene,
            request_filename,
        )
        image_bytes = await app.state.gateway.generate(
            template_bytes=template_bytes,
            template_filename=template_filename,
            participant_bytes=source_png,
            participant_filename=source_filename,
            participant_content_type="image/png",
            identity_closeup_bytes=identity_closeup_png,
            identity_closeup_filename=identity_filename,
            prompt=scene_definition.prompt,
            mask_bytes=mask_bytes,
            mask_filename=mask_filename,
        )
        logger.info(
            "Generated scene=%s using participant=%s (%d bytes)",
            scene,
            participant_filename,
            len(participant_bytes),
        )
        filename = storage.save_png(image_bytes, image_id)
        base_url = settings.public_base_url or str(request.base_url).rstrip("/")
        return {
            "id": image_id,
            "image_url": f"{base_url}/images/{filename}",
            "source_image_url": f"{base_url}/images/{source_filename}",
            "face_reference_url": f"{base_url}/images/{identity_filename}",
            "mask_url": f"{base_url}/images/{mask_filename}",
            "template_url": f"{base_url}/images/{template_filename}",
            "request_manifest_url": f"{base_url}/images/{request_filename}",
        }

    return app


app = create_app()
