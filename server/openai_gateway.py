from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx


class ImageGenerationError(RuntimeError):
    """Raised when OpenAI cannot produce a usable image."""


class ImageGateway(Protocol):
    async def generate(
        self,
        *,
        template_path: Path,
        participant_bytes: bytes,
        participant_filename: str,
        participant_content_type: str,
        prompt: str,
    ) -> bytes: ...


@dataclass
class OpenAIImageGateway:
    api_key: str
    model: str = "gpt-image-2"
    timeout_seconds: float = 180.0

    async def generate(
        self,
        *,
        template_path: Path,
        participant_bytes: bytes,
        participant_filename: str,
        participant_content_type: str,
        prompt: str,
    ) -> bytes:
        if not self.api_key:
            raise ImageGenerationError("OPENAI_API_KEY no está configurada en el servidor")

        template_bytes = template_path.read_bytes()
        files = [
            ("image[]", (template_path.name, template_bytes, "image/png")),
            (
                "image[]",
                (participant_filename, participant_bytes, participant_content_type),
            ),
        ]
        data = {
            "model": self.model,
            "prompt": prompt,
            "size": "1536x1024",
            "quality": "medium",
            "output_format": "png",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/edits",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data=data,
                    files=files,
                )
        except httpx.TimeoutException as exc:
            raise ImageGenerationError("OpenAI tardó demasiado en responder") from exc
        except httpx.HTTPError as exc:
            raise ImageGenerationError("No se pudo conectar con OpenAI") from exc

        if response.is_error:
            request_id = response.headers.get("x-request-id")
            try:
                detail = response.json().get("error", {}).get("message")
            except ValueError:
                detail = None
            suffix = f" (request_id: {request_id})" if request_id else ""
            raise ImageGenerationError(
                f"OpenAI rechazó la generación: {detail or response.status_code}{suffix}"
            )

        try:
            encoded = response.json()["data"][0]["b64_json"]
            return base64.b64decode(encoded, validate=True)
        except (KeyError, IndexError, TypeError, ValueError, binascii.Error) as exc:
            raise ImageGenerationError("OpenAI devolvió una imagen inválida") from exc
