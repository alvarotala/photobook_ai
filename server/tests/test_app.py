from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import struct
import zlib

from fastapi.testclient import TestClient

from server.app import create_app
from server.config import Settings
from server.masking import MaskDefinition, Rectangle


SOURCE_PNG = MaskDefinition(
    width=64,
    height=64,
    editable_shapes=(Rectangle(left=16, top=16, right=48, bottom=48),),
).to_png()
GENERATED_PNG = SOURCE_PNG


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def generate_from_images(self, **kwargs: object) -> bytes:
        self.calls.append(kwargs)
        return GENERATED_PNG


class PhotobookServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        templates_dir = root / "templates"
        images_dir = root / "images"
        templates_dir.mkdir()
        for filename in ("car.png", "podium.png", "hero.png"):
            (templates_dir / filename).write_bytes(b"template")

        self.gateway = FakeGateway()
        self.settings = Settings(
            api_key="test-key",
            model="gpt-image-2",
            public_base_url="https://photos.example.test",
            images_dir=images_dir,
            templates_dir=templates_dir,
        )
        self.app = create_app(settings=self.settings, gateway=self.gateway)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_generate_saves_random_image_and_exposes_it(self) -> None:
        with TestClient(self.app) as client:
            response = client.post(
                "/api/generate",
                data={"scene": "hero"},
                files={"photo": ("participant.png", SOURCE_PNG, "image/png")},
            )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertRegex(payload["id"], r"^[A-Za-z0-9_-]{32}$")
            self.assertEqual(
                payload["image_url"],
                f"https://photos.example.test/images/{payload['id']}.png",
            )
            saved_path = self.settings.images_dir / f"{payload['id']}.png"
            self.assertTrue(saved_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual([path.name for path in self.settings.images_dir.iterdir()], [saved_path.name])
            self.assertEqual(len(self.gateway.calls), 1)
            call = self.gateway.calls[0]
            images = call["images"]
            self.assertIsInstance(images, list)
            self.assertEqual(len(images), 2)
            self.assertEqual(images[0][1], b"template")
            self.assertTrue(images[1][1].startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertNotIn("third image", str(call["prompt"]))
            self.assertNotIn("masked area", str(call["prompt"]))
            self.assertEqual(call["size"], "1536x1024")
            self.assertEqual(call["quality"], "medium")
            self.assertEqual(call["output_format"], "jpeg")
            self.assertEqual(call["output_compression"], 90)

    def test_each_mask_matches_its_template_and_contains_editable_pixels(self) -> None:
        from server.scenes import SCENES

        expected_dimensions = {
            "car": (1672, 941),
            "podium": (1536, 1024),
            "hero": (1672, 941),
        }
        for name, scene in SCENES.items():
            png = scene.mask.to_png()
            width, height = struct.unpack(">II", png[16:24])
            self.assertEqual((width, height), expected_dimensions[name])

            idat_length = struct.unpack(">I", png[33:37])[0]
            self.assertEqual(png[37:41], b"IDAT")
            raw = zlib.decompress(png[41 : 41 + idat_length])
            row_size = 1 + width * 4
            alpha_values = bytearray()
            for y in range(height):
                row = raw[y * row_size + 1 : (y + 1) * row_size]
                alpha_values.extend(row[3::4])
            self.assertIn(0, alpha_values)
            self.assertIn(255, alpha_values)

    def test_rejects_unknown_scene_without_calling_gateway(self) -> None:
        with TestClient(self.app) as client:
            response = client.post(
                "/api/generate",
                data={"scene": "unknown"},
                files={"photo": ("participant.jpg", b"fake-jpeg", "image/jpeg")},
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.gateway.calls, [])

    def test_rejects_unsupported_file_type(self) -> None:
        with TestClient(self.app) as client:
            response = client.post(
                "/api/generate",
                data={"scene": "car"},
                files={"photo": ("participant.txt", b"not-an-image", "text/plain")},
            )

        self.assertEqual(response.status_code, 415)
        self.assertEqual(self.gateway.calls, [])

    def test_health_reports_configuration_without_exposing_key(self) -> None:
        with TestClient(self.app) as client:
            payload = client.get("/health").json()

        self.assertEqual(
            payload,
            {
                "status": "ok",
                "openai_configured": True,
                "model": "gpt-image-2",
                "image_profile": "balanced",
            },
        )
        self.assertNotIn("test-key", str(payload))


if __name__ == "__main__":
    unittest.main()
