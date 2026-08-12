from __future__ import annotations

import secrets
import json
from pathlib import Path


class ImageStorage:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def create_id(self) -> str:
        """Create an unguessable ID that is not currently used by this directory."""
        while True:
            image_id = secrets.token_urlsafe(24)
            if not any(self.directory.glob(f"{image_id}*")):
                return image_id

    def save_png(self, contents: bytes, image_id: str, *, suffix: str = "") -> str:
        """Save PNG bytes atomically using an internally generated image ID."""
        if suffix not in {"", "-T", "-S", "-F", "-M"}:
            raise ValueError("Sufijo de imagen inválido")
        filename = f"{image_id}{suffix}.png"
        self._save_atomic(contents, filename)
        return filename

    def save_request_manifest(self, payload: dict[str, object], image_id: str) -> str:
        filename = f"{image_id}-REQUEST.json"
        contents = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._save_atomic(contents, filename)
        return filename

    def _save_atomic(self, contents: bytes, filename: str) -> None:
        destination = self.directory / filename
        temporary = self.directory / f".{filename}.tmp"
        temporary.write_bytes(contents)
        temporary.replace(destination)
