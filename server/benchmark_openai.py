from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from time import perf_counter

from .config import Settings
from .image_profiles import IMAGE_PROFILES, get_image_profile, prompt_for_two_images
from .identity_reference import (
    IdentityReferenceError,
    convert_source_to_png,
)
from .openai_gateway import ImageGenerationError, OpenAIImageGateway
from .scenes import SCENES
from .storage import ImageStorage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Envía una plantilla y una foto a OpenAI para medir su velocidad."
    )
    parser.add_argument("photo", type=Path, help="Path de la foto del participante")
    parser.add_argument("scene", choices=SCENES, help="Nombre de la escena")
    parser.add_argument(
        "--profile",
        choices=IMAGE_PROFILES,
        default="fast",
        help="Perfil de velocidad/calidad (default: fast)",
    )
    return parser.parse_args()


async def run(photo_path: Path, scene_name: str, profile_name: str) -> Path:
    started_at = perf_counter()
    settings = Settings.from_environment()
    profile = get_image_profile(profile_name)

    if not settings.api_key:
        raise ImageGenerationError("OPENAI_API_KEY no está configurada en .env")
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
    gateway = OpenAIImageGateway(api_key=settings.api_key, model=settings.model)

    print("Proveedor: OpenAI")
    print(f"Modelo: {settings.model}")
    print(f"Perfil: {profile_name}")
    print(
        f"Salida: {profile.size}, calidad {profile.quality}, "
        f"formato {profile.output_format}"
    )
    print(f"Escena: {scene_name}")
    print(f"Foto: {photo_path.resolve()}")
    print("Archivos enviados: plantilla + sujeto (sin máscara)")
    print("Enviando a OpenAI...")

    api_started_at = perf_counter()
    image_bytes = await gateway.generate_from_images(
        images=[
            (f"{image_id}-T.png", template_bytes, "image/png"),
            (f"{image_id}-S.png", source_png, "image/png"),
        ],
        prompt=prompt_for_two_images(scene.prompt),
        size=profile.size,
        quality=profile.quality,
        output_format=profile.output_format,
        output_compression=profile.output_compression,
    )
    api_finished_at = perf_counter()

    result_png = convert_source_to_png(image_bytes)
    filename = storage.save_png(result_png, image_id)
    finished_at = perf_counter()
    output_path = (settings.images_dir / filename).resolve()

    print(f"Preparación: {prepared_at - started_at:.2f} s")
    print(f"OpenAI: {api_finished_at - api_started_at:.2f} s")
    print(f"Total: {finished_at - started_at:.2f} s")
    print(f"Resultado: {output_path}")
    return output_path


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.photo, args.scene, args.profile))
    except (IdentityReferenceError, ImageGenerationError, OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
