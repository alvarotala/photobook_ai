from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .masking import Ellipse, MaskDefinition, Rectangle


@dataclass(frozen=True)
class SceneDefinition:
    template_filename: str
    prompt: str
    mask: MaskDefinition

    def template_path(self, templates_dir: Path) -> Path:
        return templates_dir / self.template_filename


SCENES: dict[str, SceneDefinition] = {
    "car": SceneDefinition(
        template_filename="car.png",
        mask=MaskDefinition(
            width=1672,
            height=941,
            editable_shapes=(
                Ellipse(center_x=520, center_y=315, radius_x=285, radius_y=285),
                Rectangle(left=0, top=365, right=900, bottom=940),
            ),
        ),
        prompt=(
            "IMPORTANT: The woman in the first image is only a placeholder and MUST NOT appear in the "
            "result. The first image defines the target rally-car scene. The second image shows the actual "
            "participant, and the third image is an enlarged face reference of that same participant. The "
            "third image is authoritative for identity. Replace the foreground co-driver/passenger inside "
            "the transparent masked area. Copy the participant's face exactly from the second and third "
            "images: face shape, eyes, "
            "eyebrows, nose, mouth, skin tone, age, hairstyle, and other key facial features. "
            "Adapt clothing to the existing racing suit and helmet. Keep the driver, car interior, "
            "framing, realistic lighting, shadows, scale, "
            "perspective, and cinematic photographic style of the first image. Produce one photorealistic "
            "landscape image and do not add text, logos, borders, or extra people."
        ),
    ),
    "podium": SceneDefinition(
        template_filename="podium.png",
        mask=MaskDefinition(
            width=1536,
            height=1024,
            editable_shapes=(
                Ellipse(center_x=800, center_y=205, radius_x=125, radius_y=135),
                Ellipse(center_x=630, center_y=105, radius_x=100, radius_y=115),
                Rectangle(left=585, top=105, right=710, bottom=390),
                Rectangle(left=650, top=270, right=930, bottom=900),
            ),
        ),
        prompt=(
            "IMPORTANT: The central winner in the first image is only a placeholder and MUST NOT appear in "
            "the result. The first image defines the target epic podium scene with one winner only. The "
            "second image shows the actual "
            "participant, and the third image is an enlarged face reference of that same participant. The "
            "third image is authoritative for identity. Replace only the central winner inside the "
            "transparent masked area. Copy the participant's face exactly from the second and third images: "
            "face shape, eyes, eyebrows, "
            "nose, mouth, skin tone, age, hairstyle, and other key facial features. Create a coherent full "
            "racing-suit body in the same triumphant pose, raising the single championship trophy overhead. "
            "Keep the gold medal, podium, Paraguay flag, historic ruins, golden confetti, dramatic sunset, "
            "framing, realistic lighting, shadows, scale, and perspective from the first image. The result "
            "must contain exactly one person and exactly one trophy. Produce one photorealistic landscape "
            "image and do not add text, logos, borders, spectators, teammates, or extra people."
        ),
    ),
    "hero": SceneDefinition(
        template_filename="hero.png",
        mask=MaskDefinition(
            width=1672,
            height=941,
            editable_shapes=(
                Ellipse(center_x=540, center_y=260, radius_x=255, radius_y=245),
                Rectangle(left=110, top=340, right=925, bottom=940),
            ),
        ),
        prompt=(
            "IMPORTANT: The foreground driver in the first image is only a placeholder and MUST NOT appear "
            "in the result. The first image defines the target cinematic rally scene. The second image shows "
            "the actual participant, and the third image is an enlarged face reference of that same "
            "participant. The third image is authoritative for identity. Replace the foreground driver "
            "inside the transparent masked area. Copy the participant's face exactly from the second and "
            "third images: face shape, eyes, "
            "eyebrows, nose, mouth, skin tone, age, hairstyle, and other key facial features. "
            "Adapt their body and clothing to the black racing suit and confident hero pose. Keep the rally "
            "car, Paraguay flag, rural background, framing, golden-hour lighting, "
            "shadows, scale, perspective, and depth of field from the first image. Produce one photorealistic "
            "landscape image and do not add text, logos, or borders."
        ),
    ),
}
