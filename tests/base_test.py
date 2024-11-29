import pytest
from hypothesis import given, strategies as st

from basethemes.base import BasePalette, int_to_base_key
from basethemes.color import Color

from . import _strats


@given(colors=st.lists(_strats.valid_color_string, min_size=1, max_size=24))
def test_palette_valid_init(colors: list[str]):
    class TestPalette(BasePalette):
        _palette_length = len(colors)

    color_dict = {f"base{int_to_base_key(n)}": color for n, color in enumerate(colors)}

    palette = TestPalette(**color_dict)
    assert len(palette) == len(colors)


@given(colors=st.lists(_strats.valid_color_string, min_size=1, max_size=24))
def test_palette_init_error_missing_key(colors: list[str]):
    class TestPalette(BasePalette):
        _palette_length = len(colors)

    color_dict = {f"base{int_to_base_key(n)}": color for n, color in enumerate(colors)}

    key_to_miss = list(color_dict.keys())[len(colors) // 2]
    color_dict.pop(key_to_miss)

    with pytest.raises(
        ValueError, match=f"Missing the following base_keys:.*{key_to_miss}"
    ):
        TestPalette(**color_dict)


@given(palette=_strats.palette)
def test_palette_index_by_int(palette: BasePalette):
    for n in range(len(palette)):
        assert isinstance(palette[n], Color)


@given(palette=_strats.palette)
def test_palette_index_by_hex(palette: BasePalette):
    for n in range(len(palette)):
        key = int_to_base_key(n)
        assert isinstance(palette[key], Color)
        assert isinstance(palette[key.lower()], Color)
        assert isinstance(palette[key.upper()], Color)


@given(palette=_strats.palette)
def test_palette_index_by_base_name(palette: BasePalette):
    for n in range(len(palette)):
        key = "base" + int_to_base_key(n)
        assert isinstance(palette[key], Color)
        assert isinstance(palette[key.lower()], Color)
        assert isinstance(palette[key.upper()], Color)


@given(palette=_strats.palette)
def test_palette_index_int_out_of_range(palette: BasePalette):
    with pytest.raises(IndexError, match="Base index out of range"):
        palette[-1]

    with pytest.raises(IndexError, match="Base index out of range"):
        palette[len(palette)]


@given(palette=_strats.palette)
def test_palette_index_bad_str(palette: BasePalette):
    with pytest.raises(KeyError, match="Invalid key: "):
        palette["bad_key"]

    with pytest.raises(KeyError, match="Invalid key: "):
        palette["base" + int_to_base_key(len(palette))]  # will be out of range
