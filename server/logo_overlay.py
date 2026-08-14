from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGOS_DIR = PROJECT_ROOT / "images" / "logos"

# Left, right and logo filename. The proportions leave extra room for the
# Gobierno del Paraguay wordmark while keeping the three plates balanced.
LOGO_PLATES = (
    (0.025, 0.215, "itaipu.png"),
    (0.235, 0.475, "yasyreta.png"),
    (0.495, 0.975, "gdp.png"),
)


def _load_trimmed_logo(filename: str) -> Image.Image:
    with Image.open(LOGOS_DIR / filename) as source:
        logo = source.convert("RGBA")

    alpha_bounds = logo.getchannel("A").getbbox()
    return logo.crop(alpha_bounds) if alpha_bounds else logo


def add_partner_logos(image_bytes: bytes) -> bytes:
    """Place the three official partner logos on the final shared image."""
    with Image.open(BytesIO(image_bytes)) as source:
        result = source.convert("RGBA")

    width, height = result.size
    plate_height = max(12, round(height * 0.105))
    bottom_margin = max(3, round(height * 0.025))
    top = height - bottom_margin - plate_height
    radius = max(3, round(plate_height * 0.23))
    horizontal_padding = max(3, round(plate_height * 0.15))
    vertical_padding = max(2, round(plate_height * 0.14))

    shadow = Image.new("RGBA", result.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    plates: list[tuple[int, int, int, int, str]] = []
    for left_ratio, right_ratio, filename in LOGO_PLATES:
        left = round(width * left_ratio)
        right = round(width * right_ratio)
        box = (left, top, right, top + plate_height)
        plates.append((*box, filename))
        shadow_draw.rounded_rectangle(
            (left, top + max(1, round(height * 0.006)), right, top + plate_height),
            radius=radius,
            fill=(0, 0, 0, 150),
        )
        overlay_draw.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 248))

    blur_radius = max(1, round(height * 0.008))
    result = Image.alpha_composite(result, shadow.filter(ImageFilter.GaussianBlur(blur_radius)))
    result = Image.alpha_composite(result, overlay)

    for left, plate_top, right, plate_bottom, filename in plates:
        logo = _load_trimmed_logo(filename)
        available_width = max(1, right - left - horizontal_padding * 2)
        available_height = max(1, plate_bottom - plate_top - vertical_padding * 2)
        logo.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
        logo_left = left + (right - left - logo.width) // 2
        logo_top = plate_top + (plate_bottom - plate_top - logo.height) // 2
        result.alpha_composite(logo, (logo_left, logo_top))

    output = BytesIO()
    result.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue()
