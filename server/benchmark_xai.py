from __future__ import annotations

import argparse
import asyncio
from io import BytesIO
import os
from pathlib import Path
from time import perf_counter

from .config import Settings
from .identity_reference import (
    IdentityReferenceError,
    convert_source_to_png,
    create_centered_identity_closeup,
)
from .openai_gateway import ImageGenerationError
from .scenes import SCENES
from .storage import ImageStorage
from .xai_gateway import XAIImageGateway


XAI_SCENE_PROMPTS = {
    "car": (
        "Create a new photorealistic composite. IMAGE 1 is the actual participant and "
        "the primary subject. IMAGE 2 is the target rally-car scene with a transparent "
        "empty area in the foreground passenger/co-driver position. IMAGE 3 is "
        "a close-up of the participant in IMAGE 1 and is authoritative for facial "
        "identity. Place the participant from IMAGES 1 and 3 into the foreground "
        "passenger position, filling the transparent area of IMAGE 2 completely. "
        "The final person must be recognizably the participant: preserve face shape, "
        "eyes, eyebrows, nose, mouth, skin tone, age, and hairstyle. Adapt clothing to "
        "the racing suit and helmet. Recreate the driver, car interior, framing, "
        "lighting, shadows, scale, perspective, and cinematic style from IMAGE 2. "
        "Do not return IMAGE 2 unchanged. No text, logos, borders, or extra people."
    ),
    "podium": (
        "Create a new photorealistic composite. IMAGE 1 is the actual participant and "
        "the primary subject. IMAGE 2 is the target podium scene with a transparent "
        "empty area in the central winner position. IMAGE 3 is a close-up of the "
        "participant in IMAGE 1 and is "
        "authoritative for facial identity. Place the participant from IMAGES 1 and 3 "
        "as the central winner, filling the transparent area of IMAGE 2 completely. The "
        "final person must be recognizably the participant: preserve face shape, eyes, "
        "eyebrows, nose, mouth, skin tone, age, and hairstyle. Create a coherent full "
        "racing-suit body and victory pose. Recreate the teammates, podium, background, "
        "framing, lighting, shadows, scale, and perspective from IMAGE 2. Do not return "
        "IMAGE 2 unchanged. No text, logos, borders, or extra people."
    ),
    "hero": (
        "Create a new photorealistic composite. IMAGE 1 is the actual participant and "
        "the primary subject. IMAGE 2 is the target cinematic rally scene with a "
        "transparent empty area in the foreground driver position. IMAGE 3 is a "
        "close-up of the participant in "
        "IMAGE 1 and is authoritative for facial identity. Place the participant from "
        "IMAGES 1 and 3 as the foreground driver, filling the transparent area of "
        "IMAGE 2 completely. The final person must be recognizably the participant: preserve "
        "face shape, eyes, eyebrows, nose, mouth, skin tone, age, and hairstyle. Adapt "
        "the body and clothing to the black racing suit and confident hero pose. "
        "Recreate the rally car, Paraguay flag, rural background, framing, golden-hour "
        "lighting, shadows, scale, perspective, and depth of field from IMAGE 2. Do not "
        "return IMAGE 2 unchanged. No text, logos, or borders."
    ),
}


def create_template_cutout(template_bytes: bytes, mask_bytes: bytes) -> bytes:
    try:
        from PIL import Image

        with Image.open(BytesIO(template_bytes)) as template_source:
            template = template_source.convert("RGBA")
        with Image.open(BytesIO(mask_bytes)) as mask_source:
            mask_alpha = mask_source.convert("RGBA").getchannel("A")
    except OSError as exc:
        raise ValueError("No se pudo preparar la plantilla para xAI") from exc

    if template.size != mask_alpha.size:
        raise ValueError("La plantilla y su máscara tienen dimensiones diferentes")

    template.putalpha(mask_alpha)
    output = BytesIO()
    template.save(output, format="PNG", optimize=True)
    return output.getvalue()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Envía una plantilla y una foto a xAI para medir su velocidad."
    )
    parser.add_argument("photo", type=Path, help="Path de la foto del participante")
    parser.add_argument("scene", choices=SCENES, help="Nombre de la escena")
    return parser.parse_args()


async def run(photo_path: Path, scene_name: str) -> Path:
    started_at = perf_counter()
    settings = Settings.from_environment()

    xai_api_key = os.getenv("XAI_API_KEY", "").strip()
    xai_model = os.getenv("XAI_IMAGE_MODEL", "grok-imagine-image").strip()
    if not xai_api_key:
        raise ImageGenerationError("XAI_API_KEY no está configurada en .env")
    if not photo_path.is_file():
        raise ValueError(f"No existe la foto: {photo_path}")

    participant_bytes = photo_path.read_bytes()
    if not participant_bytes:
        raise ValueError("La foto está vacía")
    if len(participant_bytes) > settings.max_upload_bytes:
        raise ValueError("La foto supera el límite de 20 MB")

    scene = SCENES[scene_name]
    template_path = scene.template_path(settings.templates_dir)
    if not template_path.is_file():
        raise ValueError(f"No existe la plantilla de la escena: {template_path}")

    source_png = convert_source_to_png(participant_bytes)
    identity_closeup_png = create_centered_identity_closeup(participant_bytes)
    template_bytes = create_template_cutout(
        template_path.read_bytes(),
        scene.mask.to_png(),
    )
    prepared_at = perf_counter()

    storage = ImageStorage(settings.images_dir)
    image_id = storage.create_id()
    template_filename = storage.save_png(template_bytes, image_id, suffix="-T")
    source_filename = storage.save_png(source_png, image_id, suffix="-S")
    identity_filename = storage.save_png(identity_closeup_png, image_id, suffix="-F")
    gateway = XAIImageGateway(api_key=xai_api_key, model=xai_model)

    print("Proveedor: xAI")
    print(f"Modelo: {xai_model}")
    print(f"Escena: {scene_name}")
    print(f"Foto: {photo_path.resolve()}")
    print("Orden enviado: sujeto + plantilla recortada + rostro ampliado")
    print(
        "Debug: "
        + ", ".join(
            str((settings.images_dir / filename).resolve())
            for filename in (template_filename, source_filename, identity_filename)
        )
    )
    print("Enviando a xAI...")

    api_started_at = perf_counter()
    image_bytes = await gateway.generate_from_images(
        images=[
            (source_png, "image/png"),
            (template_bytes, "image/png"),
            (identity_closeup_png, "image/png"),
        ],
        prompt=XAI_SCENE_PROMPTS[scene_name],
    )
    api_finished_at = perf_counter()

    result_png = convert_source_to_png(image_bytes)
    filename = storage.save_png(result_png, image_id)
    finished_at = perf_counter()
    output_path = (settings.images_dir / filename).resolve()

    print(f"Preparación: {prepared_at - started_at:.2f} s")
    print(f"xAI (generación + descarga): {api_finished_at - api_started_at:.2f} s")
    print(f"Total: {finished_at - started_at:.2f} s")
    print(f"Resultado: {output_path}")
    return output_path


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.photo, args.scene))
    except (IdentityReferenceError, ImageGenerationError, OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
