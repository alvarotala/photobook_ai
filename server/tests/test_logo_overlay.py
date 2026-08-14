from __future__ import annotations

from io import BytesIO
import unittest

from PIL import Image

from server.logo_overlay import LOGO_PLATES, add_partner_logos


class PartnerLogoOverlayTests(unittest.TestCase):
    def test_adds_ordered_logo_plates_without_changing_dimensions(self) -> None:
        source = Image.new("RGB", (1200, 800), (120, 20, 20))
        source_bytes = BytesIO()
        source.save(source_bytes, format="PNG")

        output_bytes = add_partner_logos(source_bytes.getvalue())

        with Image.open(BytesIO(output_bytes)) as result:
            self.assertEqual(result.size, source.size)
            self.assertEqual(result.format, "PNG")
            self.assertGreater(result.getpixel((60, 710))[0], 220)
            self.assertGreater(result.getpixel((312, 710))[0], 220)
            self.assertGreater(result.getpixel((624, 710))[0], 220)

        self.assertEqual(
            [filename for _, _, filename in LOGO_PLATES],
            ["itaipu.png", "yasyreta.png", "gdp.png"],
        )


if __name__ == "__main__":
    unittest.main()
