from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Rectangle:
    left: int
    top: int
    right: int
    bottom: int

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom


@dataclass(frozen=True)
class Ellipse:
    center_x: int
    center_y: int
    radius_x: int
    radius_y: int

    def contains(self, x: int, y: int) -> bool:
        normalized_x = (x - self.center_x) / self.radius_x
        normalized_y = (y - self.center_y) / self.radius_y
        return normalized_x * normalized_x + normalized_y * normalized_y <= 1


MaskShape = Union[Rectangle, Ellipse]


@dataclass(frozen=True)
class MaskDefinition:
    width: int
    height: int
    editable_shapes: tuple[MaskShape, ...]

    def to_png(self) -> bytes:
        """Create an RGBA mask: transparent pixels are editable by OpenAI."""
        rows = bytearray()
        opaque = bytes((255, 255, 255, 255))
        editable = bytes((255, 255, 255, 0))

        for y in range(self.height):
            rows.append(0)  # PNG filter: None
            for x in range(self.width):
                is_editable = any(shape.contains(x, y) for shape in self.editable_shapes)
                rows.extend(editable if is_editable else opaque)

        def chunk(kind: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(rows), level=9))
            + chunk(b"IEND", b"")
        )
