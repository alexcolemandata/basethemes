from __future__ import annotations
from string import hexdigits


class Color:
    hex: str

    def __init__(self, hex: str | Color) -> None:
        if isinstance(hex, Color):
            self.hex = hex.hex
            return None

        hex = hex.lstrip("#").upper()

        if len(hex) != 6:
            raise ValueError(f"invalid length for {hex=}")

        invalid_chars = [char for char in hex if char not in hexdigits]
        if invalid_chars:
            raise ValueError(f"hex contained some invalid chars: {invalid_chars}")

        self.hex = hex
        return None

    def __repr__(self) -> str:
        return f"{type(self).__name__}('#{self.hex})'"

    def __str__(self) -> str:
        return f"#{self.hex}"

    @property
    def red(self) -> str:
        return self.hex[0:2]

    @property
    def green(self) -> str:
        return self.hex[2:4]

    @property
    def blue(self) -> str:
        return self.hex[4:6]
