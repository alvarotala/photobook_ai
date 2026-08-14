from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGOS_DIR = PROJECT_ROOT / "images" / "logos"
LOGO_FILENAMES = ("itaipu.png", "yasyreta.png", "gdp.png")


def _load_trimmed_logo(filename: str) -> Image.Image:
    with Image.open(LOGOS_DIR / filename) as source:
        logo = source.convert("RGBA")

    alpha_bounds = logo.getchannel("A").getbbox()
    return logo.crop(alpha_bounds) if alpha_bounds else logo


def add_partner_logos(image_bytes: bytes) -> bytes:
    """Place the home-style partner bar on the final shared image."""
    with Image.open(BytesIO(image_bytes)) as source:
        result = source.convert("RGBA")

    width, height = result.size
    bar_width = round(width * 0.52)
    bar_height = max(12, round(height * 0.07))
    bottom_margin = max(3, round(height * 0.025))
    left = (width - bar_width) // 2
    top = height - bottom_margin - bar_height
    right = left + bar_width
    bottom = top + bar_height
    radius = max(3, round(bar_height * 0.23))

    shadow = Image.new("RGBA", result.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_offset = max(1, round(height * 0.006))
    shadow_draw.rounded_rectangle(
        (left, top + shadow_offset, right, bottom + shadow_offset),
        radius=radius,
        fill=(0, 0, 0, 150),
    )
    blur_radius = max(1, round(height * 0.008))
    result = Image.alpha_composite(result, shadow.filter(ImageFilter.GaussianBlur(blur_radius)))

    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((left, top, right, bottom), radius=radius, fill=(255, 255, 255, 248))

    # The Gobierno wordmark needs more horizontal room, matching the proportions
    # used by the partner row on the home screen.
    first_divider = left + round(bar_width * 0.245)
    second_divider = left + round(bar_width * 0.49)
    divider_top = top + round(bar_height * 0.26)
    divider_bottom = bottom - round(bar_height * 0.26)
    divider_width = max(1, round(width * 0.0012))
    divider_color = (218, 219, 221, 255)
    draw.rectangle(
        (first_divider, divider_top, first_divider + divider_width, divider_bottom),
        fill=divider_color,
    )
    draw.rectangle(
        (second_divider, divider_top, second_divider + divider_width, divider_bottom),
        fill=divider_color,
    )
    result = Image.alpha_composite(result, overlay)

    horizontal_padding = max(3, round(bar_height * 0.18))
    vertical_padding = max(2, round(bar_height * 0.14))
    sections = (
        (left, first_divider, LOGO_FILENAMES[0]),
        (first_divider + divider_width, second_divider, LOGO_FILENAMES[1]),
        (second_divider + divider_width, right, LOGO_FILENAMES[2]),
    )

    for section_left, section_right, filename in sections:
        logo = _load_trimmed_logo(filename)
        available_width = max(1, section_right - section_left - horizontal_padding * 2)
        available_height = max(1, bar_height - vertical_padding * 2)
        logo.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
        logo_left = section_left + (section_right - section_left - logo.width) // 2
        logo_top = top + (bar_height - logo.height) // 2
        result.alpha_composite(logo, (logo_left, logo_top))

    output = BytesIO()
    result.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue()
