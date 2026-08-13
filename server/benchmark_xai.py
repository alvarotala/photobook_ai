from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from time import perf_counter

from .config import Settings
from .identity_reference import IdentityReferenceError, convert_source_to_png
from .openai_gateway import ImageGenerationError
from .scenes import SCENES
from .storage import ImageStorage
from .xai_gateway import XAIImageGateway


THIRD_IMAGE_INSTRUCTION = (
    ", and the third image is an enlarged face reference of that same participant. "
    "The third image is authoritative for identity."
)


def prompt_for_two_images(prompt: str) -> str:
    return (
        prompt.replace(THIRD_IMAGE_INSTRUCTION, ".")
        .replace("second and third images", "second image")
        .replace(" inside the transparent masked area", "")
    )


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
    template_bytes = template_path.read_bytes()
    prepared_at = perf_counter()

    storage = ImageStorage(settings.images_dir)
    image_id = storage.create_id()
    gateway = XAIImageGateway(api_key=xai_api_key, model=xai_model)

    print("Proveedor: xAI")
    print(f"Modelo: {xai_model}")
    print(f"Escena: {scene_name}")
    print(f"Foto: {photo_path.resolve()}")
    print("Archivos enviados: plantilla + sujeto (sin máscara)")
    print("Enviando a xAI...")

    api_started_at = perf_counter()
    image_bytes = await gateway.generate_from_images(
        images=[
            (template_bytes, "image/png"),
            (source_png, "image/png"),
        ],
        prompt=prompt_for_two_images(scene.prompt),
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
