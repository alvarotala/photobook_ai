from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import struct
import zlib

from fastapi.testclient import TestClient

from server.app import create_app
from server.config import Settings
from server.masking import MaskDefinition, Rectangle


GENERATED_PNG = b"\x89PNG\r\n\x1a\nmock-generated-image"
SOURCE_PNG = MaskDefinition(
    width=64,
    height=64,
    editable_shapes=(Rectangle(left=16, top=16, right=48, bottom=48),),
).to_png()


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def generate(self, **kwargs: object) -> bytes:
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
            self.assertEqual(saved_path.read_bytes(), GENERATED_PNG)
            source_path = self.settings.images_dir / f"{payload['id']}-S.png"
            face_path = self.settings.images_dir / f"{payload['id']}-F.png"
            mask_path = self.settings.images_dir / f"{payload['id']}-M.png"
            template_path = self.settings.images_dir / f"{payload['id']}-T.png"
            request_path = self.settings.images_dir / f"{payload['id']}-REQUEST.json"
            self.assertTrue(source_path.is_file())
            self.assertTrue(source_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertTrue(face_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertTrue(mask_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(template_path.read_bytes(), b"template")
            self.assertEqual(
                payload["source_image_url"],
                f"https://photos.example.test/images/{payload['id']}-S.png",
            )
            self.assertEqual(
                payload["face_reference_url"],
                f"https://photos.example.test/images/{payload['id']}-F.png",
            )
            manifest = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["quality"], "high")
            self.assertEqual(
                [part["role"] for part in manifest["multipart"]],
                ["template", "participant-source", "participant-face-reference", "edit-mask"],
            )
            self.assertEqual(len(self.gateway.calls), 1)
            call = self.gateway.calls[0]
            self.assertEqual(call["template_bytes"], template_path.read_bytes())
            self.assertEqual(call["participant_bytes"], source_path.read_bytes())
            self.assertEqual(call["identity_closeup_bytes"], face_path.read_bytes())
            self.assertEqual(call["mask_bytes"], mask_path.read_bytes())
            self.assertEqual(call["mask_filename"], mask_path.name)
            self.assertIn("authoritative for identity", str(call["prompt"]))
            mask = call["mask_bytes"]
            self.assertIsInstance(mask, bytes)
            self.assertTrue(mask.startswith(b"\x89PNG\r\n\x1a\n"))

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
            {"status": "ok", "openai_configured": True, "model": "gpt-image-2"},
        )
        self.assertNotIn("test-key", str(payload))


if __name__ == "__main__":
    unittest.main()
