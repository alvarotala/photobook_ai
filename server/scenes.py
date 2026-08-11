from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SceneDefinition:
    template_filename: str
    prompt: str

    def template_path(self, templates_dir: Path) -> Path:
        return templates_dir / self.template_filename


SCENES: dict[str, SceneDefinition] = {
    "car": SceneDefinition(
        template_filename="car.png",
        prompt=(
            "The first image is the target rally-car scene and must define the final composition. "
            "The second image is the participant identity reference. Replace the co-driver/passenger "
            "in the foreground with the participant. Preserve the participant's recognizable identity, "
            "face, skin tone, age, and key facial features. Adapt clothing to the existing racing suit "
            "and helmet. Keep the driver, car interior, framing, realistic lighting, shadows, scale, "
            "perspective, and cinematic photographic style of the first image. Produce one photorealistic "
            "landscape image and do not add text, logos, borders, or extra people."
        ),
    ),
    "podium": SceneDefinition(
        template_filename="podium.png",
        prompt=(
            "The first image is the target podium scene and must define the final composition. The second "
            "image is the participant identity reference. Replace only the central winner standing on the "
            "highest podium with the participant. Preserve their recognizable identity, face, skin tone, "
            "age, and key facial features. Create a coherent full racing-suit body and victory pose. Keep "
            "all other fictional teammates, the podium, background, framing, realistic lighting, shadows, "
            "scale, and perspective from the first image. Produce one photorealistic landscape image and "
            "do not add text, logos, borders, or extra people."
        ),
    ),
    "hero": SceneDefinition(
        template_filename="hero.png",
        prompt=(
            "The first image is the target cinematic rally scene and must define the final composition. "
            "The second image is the participant identity reference. Replace the foreground rally driver "
            "with the participant. Preserve the participant's recognizable identity, face, skin tone, age, "
            "and key facial features. Adapt their body and clothing to the black racing suit and confident "
            "hero pose. Keep the rally car, Paraguay flag, rural background, framing, golden-hour lighting, "
            "shadows, scale, perspective, and depth of field from the first image. Produce one photorealistic "
            "landscape image and do not add text, logos, or borders."
        ),
    ),
}
