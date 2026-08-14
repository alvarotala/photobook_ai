from __future__ import annotations

from io import BytesIO
import unittest

from PIL import Image

from server.logo_overlay import LOGO_FILENAMES, add_partner_logos


class PartnerLogoOverlayTests(unittest.TestCase):
    def test_adds_ordered_logo_plates_without_changing_dimensions(self) -> None:
        source = Image.new("RGB", (1200, 800), (120, 20, 20))
        source_bytes = BytesIO()
        source.save(source_bytes, format="PNG")

        output_bytes = add_partner_logos(source_bytes.getvalue())

        with Image.open(BytesIO(output_bytes)) as result:
            self.assertEqual(result.size, source.size)
            self.assertEqual(result.format, "PNG")
            self.assertGreater(result.getpixel((190, 710))[0], 220)
            self.assertGreater(result.getpixel((1010, 710))[0], 220)
            self.assertEqual(result.getpixel((50, 710)), (120, 20, 20))

        self.assertEqual(LOGO_FILENAMES, ("itaipu.png", "yasyreta.png", "gdp.png"))


if __name__ == "__main__":
    unittest.main()
