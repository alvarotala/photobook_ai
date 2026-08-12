from __future__ import annotations

from io import BytesIO


class IdentityReferenceError(RuntimeError):
    pass


def _decode_image(image_bytes: bytes):
    try:
        from PIL import Image, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise IdentityReferenceError(
            "Falta Pillow. Ejecutá: .venv/bin/python -m pip install -r server/requirements.txt"
        ) from exc

    try:
        with Image.open(BytesIO(image_bytes)) as source:
            return ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise IdentityReferenceError("La captura no contiene una imagen válida") from exc


def convert_source_to_png(image_bytes: bytes) -> bytes:
    """Normalize the exact uploaded capture to a viewable PNG for debugging."""
    image = _decode_image(image_bytes)
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def create_centered_identity_closeup(image_bytes: bytes) -> bytes:
    """Create an in-memory square portrait reference centered on the camera guide."""
    from PIL import Image

    image = _decode_image(image_bytes)
    width, height = image.size
    if width < 64 or height < 64:
        raise IdentityReferenceError("La captura es demasiado pequeña")

    # The camera UI centers the participant inside an oval guide. Cropping to 72%
    # of the shortest side removes most background while keeping head and shoulders.
    side = max(64, round(min(width, height) * 0.72))
    left = max(0, (width - side) // 2)
    top = max(0, (height - side) // 2)
    portrait = image.crop((left, top, left + side, top + side))
    portrait = portrait.resize((1024, 1024), Image.Resampling.LANCZOS)

    output = BytesIO()
    portrait.save(output, format="PNG", optimize=True)
    return output.getvalue()
