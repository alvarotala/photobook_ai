from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from typing import Protocol

import httpx


OPENAI_IMAGE_ENDPOINT = "https://api.openai.com/v1/images/edits"
OPENAI_IMAGE_SIZE = "1536x1024"
OPENAI_IMAGE_QUALITY = "high"
OPENAI_IMAGE_OUTPUT_FORMAT = "png"


class ImageGenerationError(RuntimeError):
    """Raised when OpenAI cannot produce a usable image."""


class ImageGateway(Protocol):
    async def generate_from_images(
        self,
        *,
        images: list[tuple[str, bytes, str]],
        prompt: str,
        mask: tuple[str, bytes, str] | None = None,
        size: str = OPENAI_IMAGE_SIZE,
        quality: str = OPENAI_IMAGE_QUALITY,
        output_format: str = OPENAI_IMAGE_OUTPUT_FORMAT,
        output_compression: int | None = None,
    ) -> bytes: ...


@dataclass
class OpenAIImageGateway:
    api_key: str
    model: str = "gpt-image-2"
    timeout_seconds: float = 180.0

    async def generate(
        self,
        *,
        template_bytes: bytes,
        template_filename: str,
        participant_bytes: bytes,
        participant_filename: str,
        participant_content_type: str,
        identity_closeup_bytes: bytes,
        identity_closeup_filename: str,
        prompt: str,
        mask_bytes: bytes,
        mask_filename: str,
    ) -> bytes:
        return await self.generate_from_images(
            images=[
                (template_filename, template_bytes, "image/png"),
                (participant_filename, participant_bytes, participant_content_type),
                (identity_closeup_filename, identity_closeup_bytes, "image/png"),
            ],
            prompt=prompt,
            mask=(mask_filename, mask_bytes, "image/png"),
        )

    async def generate_from_images(
        self,
        *,
        images: list[tuple[str, bytes, str]],
        prompt: str,
        mask: tuple[str, bytes, str] | None = None,
        size: str = OPENAI_IMAGE_SIZE,
        quality: str = OPENAI_IMAGE_QUALITY,
        output_format: str = OPENAI_IMAGE_OUTPUT_FORMAT,
        output_compression: int | None = None,
    ) -> bytes:
        if not self.api_key:
            raise ImageGenerationError("OPENAI_API_KEY no está configurada en el servidor")

        files = [("image[]", image) for image in images]
        if mask is not None:
            files.append(("mask", mask))
        data = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "output_format": output_format,
        }
        if output_compression is not None:
            data["output_compression"] = str(output_compression)

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    OPENAI_IMAGE_ENDPOINT,
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
