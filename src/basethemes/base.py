from __future__ import annotations
from typing import Type, Callable
from pathlib import Path
from dataclasses import dataclass

import yaml
from basethemes.color import Color
from basethemes.terminal_colors import TerminalColors


@dataclass(frozen=True)
class BasePalette:
    _bases: dict[str, Color]
    _palette_length: int  # bases should always have _palette_length number of keys

    def __init__(self, **kwargs: str | Color) -> None:
        if missing_bases := [
            f"base{k}" for k in self.base_keys if f"base{k}" not in kwargs
        ]:
            raise ValueError(f"Missing the following base_keys: {missing_bases}")

        bases = {
            base_key: Color(kwargs[f"base{base_key}"]) for base_key in self.base_keys
        }

        object.__setattr__(self, "_bases", bases)

    def __len__(self) -> int:
        return self._palette_length

    @property
    def bases(self) -> dict[str, Color]:
        return dict(self._bases)

    @property
    def base_keys(self) -> list[str]:
        return [int_to_base_key(n) for n in range(self._palette_length)]

    def __repr__(self) -> str:
        base_kwargs = ",".join([f"base{k}='{v}'" for k, v in self.bases.items()])
        return f"{type(self).__name__}({base_kwargs})"

    def __str__(self) -> str:
        return ", ".join([f"{k}: {v}" for k, v in self.bases.items()])

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

    def to_terminal_colors(self) -> TerminalColors:
        raise NotImplementedError("Requires implementation by subclass")


class Base16Palette(BasePalette):
    _palette_length = 16

    def to_terminal_colors(self) -> TerminalColors:
        return TerminalColors(
            color0=self[0],
            color1=self[8],
            color2=self[11],
            color3=self[10],
            color4=self[13],
            color5=self[14],
            color6=self[12],
            color7=self[5],
            color8=self[3],
            color9=self[9],
            color10=self[1],
            color11=self[2],
            color12=self[4],
            color13=self[6],
            color14=self[15],
            color15=self[7],
        )


class Base24Palette(BasePalette):
    _palette_length = 24


@dataclass(frozen=True)
class BaseTheme:
    file: Path
    author: str
    name: str
    palette: BasePalette
    system: str
    variant: str
    slug: str | None = None

    def __str__(self) -> str:
        return f"{self.name}"

    def to_terminal_colors(self) -> TerminalColors:
        return self.palette.to_terminal_colors()


class BaseThemes:
    themes: dict[str, BaseTheme]
    palette_type: Type[
        BasePalette
    ]  # TODO: remove palette_type, allow BaseThemes to have themes with different palette_types

    def __init__(
        self,
        palette_type: Type[BasePalette],
        base_dir: Path | None = None,
        themes: dict[str, BaseTheme] | None = None,
    ) -> None:
        self.palette_type = palette_type

        if themes is not None:
            if base_dir is not None:
                raise ValueError(
                    f"Should only provide one of either `themes` or `base_dir`"
                )
            self.themes = themes
            return None

        elif base_dir is not None:
            self._init_themes_from_base_dir(base_dir)
            return None

        raise ValueError(f"Need to provide either `base_dir` or `themes`")

    def list_theme_names(self) -> list[str]:
        return list(self.themes.keys())

    def _init_themes_from_base_dir(self, base_dir: Path) -> None:
        if not base_dir.is_dir:
            raise FileNotFoundError("`base_dir` is required to be a directory")

        themes: dict[str, BaseTheme] = dict()
        for theme_file in base_dir.glob("*.yaml"):
            with open(theme_file, "r") as f:
                raw_theme = yaml.safe_load(f)

            theme_palette = self.palette_type(**raw_theme["palette"])
            metadata = {
                k: v
                for k, v in raw_theme.items()
                if k in ["author", "name", "system", "variant", "slug"]
            }

            theme = BaseTheme(file=theme_file, palette=theme_palette, **metadata)

            if theme.name in themes:
                raise ValueError(f"Duplicate theme name: {theme.name}")

            themes[metadata["name"]] = theme

        self.themes = themes
        return None

    def __len__(self) -> int:
        return len(self.themes)

    def __getitem__(self, key: str) -> BaseTheme:
        return self.themes[key]

    @property
    def variants(self) -> set[str]:
        return {theme.variant for theme in self.themes.values()}

    def filter(self, func: Callable[[BaseTheme], bool]) -> BaseThemes:
        return BaseThemes(
            palette_type=self.palette_type,
            themes={name: theme for name, theme in self.themes.items() if func(theme)},
        )

    def filtered(
        self, variant: str | None = None, system: str | None = None
    ) -> BaseThemes:
        skip_filter_variant = variant is None
        skip_filter_system = system is None

        return self.filter(
            lambda theme: ((theme.variant == variant) or skip_filter_variant)
            and ((theme.system == system) or skip_filter_system)
        )


def int_to_base_key(n: int) -> str:
    return format(n, "x").upper().zfill(2)
