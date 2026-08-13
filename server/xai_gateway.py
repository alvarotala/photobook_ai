from __future__ import annotations

import base64
from dataclasses import dataclass

import httpx

from .openai_gateway import ImageGenerationError


XAI_IMAGE_ENDPOINT = "https://api.x.ai/v1/images/edits"


def _data_uri(contents: bytes, content_type: str) -> str:
    encoded = base64.b64encode(contents).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


@dataclass
class XAIImageGateway:
    api_key: str
    model: str = "grok-imagine-image"
    timeout_seconds: float = 180.0

    async def generate_from_images(
        self,
        *,
        images: list[tuple[bytes, str]],
        prompt: str,
    ) -> bytes:
        if not self.api_key:
            raise ImageGenerationError("XAI_API_KEY no está configurada en .env")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [
                {"type": "image_url", "url": _data_uri(contents, content_type)}
                for contents, content_type in images
            ],
            "aspect_ratio": "16:9",
            "response_format": "url",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    XAI_IMAGE_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if response.is_error:
                    request_id = response.headers.get("x-request-id")
                    try:
                        detail = response.json().get("error", {}).get("message")
                    except ValueError:
                        detail = None
                    suffix = f" (request_id: {request_id})" if request_id else ""
                    raise ImageGenerationError(
                        f"xAI rechazó la generación: {detail or response.status_code}{suffix}"
                    )

                try:
                    image_url = response.json()["data"][0]["url"]
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    raise ImageGenerationError("xAI devolvió una respuesta inválida") from exc

                image_response = await client.get(image_url)
                image_response.raise_for_status()
                return image_response.content
        except httpx.TimeoutException as exc:
            raise ImageGenerationError("xAI tardó demasiado en responder") from exc
        except httpx.HTTPError as exc:
            raise ImageGenerationError("No se pudo conectar con xAI") from exc
