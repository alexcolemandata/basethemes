from __future__ import annotations
from typing import Literal
from dataclasses import dataclass

from basethemes.color import Color
from enum import Enum


class TerminalColor(str, Enum):
    COLOR_0 = "color0"
    COLOR_1 = "color1"
    COLOR_2 = "color2"
    COLOR_3 = "color3"
    COLOR_4 = "color4"
    COLOR_5 = "color5"
    COLOR_6 = "color6"
    COLOR_7 = "color7"
    COLOR_8 = "color8"
    COLOR_9 = "color9"
    COLOR_10 = "color10"
    COLOR_11 = "color11"
    COLOR_12 = "color12"
    COLOR_13 = "color13"
    COLOR_14 = "color14"
    COLOR_15 = "color15"


@dataclass(frozen=True)
class TerminalColors:
    color0: Color
    color1: Color
    color2: Color
    color3: Color
    color4: Color
    color5: Color
    color6: Color
    color7: Color
    color8: Color
    color9: Color
    color10: Color
    color11: Color
    color12: Color
    color13: Color
    color14: Color
    color15: Color

    def __getitem__(self, key: str | int) -> Color:
        if isinstance(key, int):
            key = f"color{key}"

        return self.__getattribute__(key)
