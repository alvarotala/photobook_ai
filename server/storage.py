from __future__ import annotations

import secrets
from pathlib import Path


class ImageStorage:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def save_png(self, contents: bytes) -> str:
        """Save bytes atomically and return an unguessable public filename."""
        filename = f"{secrets.token_urlsafe(24)}.png"
        destination = self.directory / filename
        temporary = self.directory / f".{filename}.tmp"
        temporary.write_bytes(contents)
        temporary.replace(destination)
        return filename
