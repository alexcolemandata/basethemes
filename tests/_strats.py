"""Hypothesis strategies for generating test cases"""
from hypothesis.strategies import text, SearchStrategy, lists

from string import hexdigits

from basethemes import color as _color
from basethemes import base as _base


def hex_string(
    size: int | None = None, max_size: int | None = None, min_size: int = 0
) -> SearchStrategy[str]:
    if size is None and max_size is None:
        raise ValueError("Needs to include either `size` or `max_size` parameter")

    if size is not None:
        if (max_size is not None) or (min_size != 0):
            raise ValueError("Cannot provide both `size` _and_ `max_size`/`min_size`")

        min_size = size
        max_size = size

    return text(alphabet=hexdigits, min_size=min_size, max_size=max_size)


def _palette_from_colors(colors: list[str]) -> _base.BasePalette:
    class TestPalette(_base.BasePalette):
        _palette_length = len(colors)

    color_dict = {
        f"base{_base.int_to_base_key(n)}": color for n, color in enumerate(colors)
    }

    return TestPalette(**color_dict)


valid_color_string = hex_string(size=6)
color = valid_color_string.map(_color.Color)
palette = lists(valid_color_string, min_size=1, max_size=24).map(_palette_from_colors)
