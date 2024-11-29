"""Hypothesis strategies for generating test cases"""
from hypothesis.strategies import text, characters, SearchStrategy

from string import hexdigits


from basethemes.color import Color


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


valid_color_string = hex_string(size=6)
color = valid_color_string.map(Color)
