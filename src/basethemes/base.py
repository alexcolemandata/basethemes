from dataclasses import dataclass

from basethemes.color import Color


@dataclass(frozen=True)
class BasePalette:
    bases: dict[str, Color]
    _palette_length: int  # bases should always have _palette_length number of keys

    def __init__(self, **kwargs: str | Color) -> None:
        if missing_bases := [k for k in self.base_keys if f"base{k}" not in kwargs]:
            raise ValueError(f"Missing the following base_keys: {missing_bases}")

        bases = {
            base_key: Color(kwargs[f"base{base_key}"]) for base_key in self.base_keys
        }

        object.__setattr__(self, "bases", bases)

    def __len__(self) -> int:
        return self._palette_length

    @property
    def base_keys(self) -> list[str]:
        return [int_to_base_key(n) for n in range(self._palette_length)]

    def __repr__(self) -> str:
        base_kwargs = ",".join([f"base{k}='{v}'" for k, v in self.bases.items()])
        return f"{type(self).__name__}({base_kwargs})"

    def __getitem__(self, key: int | str) -> Color:
        """Supports numeric indexing, or via hex code or base name"""
        if isinstance(key, int):
            if not (0 <= key < len(self)):
                raise IndexError(f"Base index out of range (0-{len(self) - 1})")

            base_key = int_to_base_key(key)

        else:
            base_key = key.lower().removeprefix("base").upper()

        if base_key not in self.base_keys:
            raise KeyError(f"Invalid key: {key}")

        return self.bases[base_key]


class Base16Palette(BasePalette):
    _palette_length = 16


class Base24Palette(BasePalette):
    _palette_length = 24


def int_to_base_key(n: int) -> str:
    return format(n, "x").upper().zfill(2)
