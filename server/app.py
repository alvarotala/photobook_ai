from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .image_profiles import get_image_profile, prompt_for_two_images
from .identity_reference import IdentityReferenceError, convert_source_to_png
from .logo_overlay import add_partner_logos
from .openai_gateway import (
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
    image_profile = get_image_profile(settings.image_profile)
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
            "image_profile": settings.image_profile,
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
        except IdentityReferenceError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        image_id = storage.create_id()
        template_bytes = scene_definition.template_path(settings.templates_dir).read_bytes()
        template_filename = f"{image_id}-T.png"
        source_filename = f"{image_id}-S.png"

        # Archivos de depuración deshabilitados para producción. Descomentar
        # temporalmente estas líneas para guardar exactamente lo enviado a OpenAI.
        # storage.save_png(template_bytes, image_id, suffix="-T")
        # storage.save_png(source_png, image_id, suffix="-S")

        logger.info(
            "Sending scene=%s to OpenAI using profile=%s",
            scene,
            settings.image_profile,
        )
        image_bytes = await app.state.gateway.generate_from_images(
            images=[
                (template_filename, template_bytes, "image/png"),
                (source_filename, source_png, "image/png"),
            ],
            prompt=prompt_for_two_images(scene_definition.prompt),
            size=image_profile.size,
            quality=image_profile.quality,
            output_format=image_profile.output_format,
            output_compression=image_profile.output_compression,
        )
        logger.info(
            "Generated scene=%s using participant=%s (%d bytes)",
            scene,
            participant_filename,
            len(participant_bytes),
        )
        result_png = add_partner_logos(convert_source_to_png(image_bytes))
        filename = storage.save_png(result_png, image_id)
        base_url = settings.public_base_url or str(request.base_url).rstrip("/")
        return {
            "id": image_id,
            "image_url": f"{base_url}/images/{filename}",
        }

    return app


app = create_app()
