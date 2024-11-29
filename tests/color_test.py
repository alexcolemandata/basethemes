import pytest
from hypothesis import given, strategies as st

from basethemes.color import Color
from string import hexdigits


valid_hex_color = st.text(alphabet=hexdigits, min_size=6, max_size=6)


@given(hex=valid_hex_color)
def test_valid_hex(hex: str):
    assert Color(hex).hex == hex.upper()
    assert Color(hex.lower()).hex == hex.upper()
    assert Color(hex.upper()).hex == hex.upper()
    assert Color(f"#{hex}").hex == hex.upper()


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
    valid_hex=valid_hex_color,
    bad_char=st.characters(codec="utf-8", exclude_characters=hexdigits),
)
def test_invalid_chars(valid_hex: str, bad_char: str):
    invalid_hex = bad_char + valid_hex[1:]
    with pytest.raises(ValueError, match="invalid chars"):
        Color(invalid_hex)
