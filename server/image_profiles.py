from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageProfile:
    size: str
    quality: str
    output_format: str
    output_compression: int | None


IMAGE_PROFILES: dict[str, ImageProfile] = {
    "fast": ImageProfile(
        size="1152x640",
        quality="low",
        output_format="jpeg",
        output_compression=85,
    ),
    "balanced": ImageProfile(
        size="1536x1024",
        quality="medium",
        output_format="jpeg",
        output_compression=90,
    ),
    "quality": ImageProfile(
        size="1536x1024",
        quality="high",
        output_format="png",
        output_compression=None,
    ),
}


def get_image_profile(name: str) -> ImageProfile:
    try:
        return IMAGE_PROFILES[name]
    except KeyError as exc:
        choices = ", ".join(IMAGE_PROFILES)
        raise ValueError(f"OPENAI_IMAGE_PROFILE debe ser uno de: {choices}") from exc


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
