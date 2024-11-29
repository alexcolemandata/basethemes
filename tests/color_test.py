import pytest
from hypothesis import given, strategies as st

from basethemes.color import Color
from string import hexdigits

from . import _strats


@given(hex=_strats.valid_color_string)
def test_valid_hex(hex: str):
    assert Color(hex).hex == hex.upper()
    assert Color(hex.lower()).hex == hex.upper()
    assert Color(hex.upper()).hex == hex.upper()
    assert Color(f"#{hex}").hex == hex.upper()


@given(color=_strats.color)
def test_init_from_color(color: Color):
    new = Color(color)

    assert new.hex == color.hex


@given(
    hex=st.text(
        alphabet=hexdigits,
        min_size=0,
        max_size=12,
    ).filter(lambda s: len(s) != 6)
)
def test_invalid_length(hex: str):
    with pytest.raises(ValueError, match="invalid length"):
        Color(hex)


@given(
    valid_hex=_strats.valid_color_string,
    bad_char=st.characters(
        codec="ascii", categories=("L", "N", "P", "S"), exclude_characters=hexdigits
    ),
)
def test_invalid_chars(valid_hex: str, bad_char: str):
    # replace last char with invalid - should raise an error
    invalid_hex = valid_hex[:-1] + bad_char

    with pytest.raises(ValueError, match="invalid chars"):
        Color(invalid_hex)
