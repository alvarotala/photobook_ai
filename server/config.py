from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_environment() -> None:
    """Load local secrets without overriding values supplied by the host."""
    load_dotenv(PROJECT_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    public_base_url: str | None
    images_dir: Path
    templates_dir: Path
    max_upload_bytes: int = 20 * 1024 * 1024

    @classmethod
    def from_environment(cls) -> "Settings":
        load_environment()
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2").strip(),
            public_base_url=os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/") or None,
            images_dir=Path(os.getenv("IMAGES_DIR", PROJECT_ROOT / "generated_images")).resolve(),
            templates_dir=(PROJECT_ROOT / "templates").resolve(),
        )
