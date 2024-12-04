"""Tools for applying a theme to various applications"""
from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass, field
from functools import partial

from basethemes.terminal_colors import TerminalColor, TerminalColors, Color


DOT_CONFIG = Path("/Users/alex/.config")


class ThemeApplier:
    app_name: str
    config_file: Path


@dataclass
class KittyColorMapping:
    background: TerminalColor
    foreground: TerminalColor
    selection_background: TerminalColor
    selection_foreground: TerminalColor
    url_color: TerminalColor
    cursor: TerminalColor
    active_border_color: TerminalColor
    inactive_border_color: TerminalColor
    active_tab_background: TerminalColor
    active_tab_foreground: TerminalColor
    inactive_tab_background: TerminalColor
    inactive_tab_foreground: TerminalColor
    tab_bar_background: TerminalColor

    def map_terminal_colors(self, terminal_colors: TerminalColors) -> dict[str, Color]:
        return {
            name: terminal_colors[terminal_color]
            for name, terminal_color in self.__dict__.items()
        }


basic_mapping = KittyColorMapping(
    background=TerminalColor.COLOR_0,
    foreground=TerminalColor.COLOR_7,
    selection_background=TerminalColor.COLOR_7,
    selection_foreground=TerminalColor.COLOR_0,
    url_color=TerminalColor.COLOR_12,
    cursor=TerminalColor.COLOR_7,
    active_border_color=TerminalColor.COLOR_8,
    inactive_border_color=TerminalColor.COLOR_10,
    active_tab_background=TerminalColor.COLOR_0,
    active_tab_foreground=TerminalColor.COLOR_7,
    inactive_tab_background=TerminalColor.COLOR_10,
    inactive_tab_foreground=TerminalColor.COLOR_12,
    tab_bar_background=TerminalColor.COLOR_10,
)


@dataclass
class KittySetting:
    name: str
    line_no: int
    is_commented_out: bool
    value: str
    raw_line: str

    def make_updated_setting(
        self, is_commented_out: bool | None = None, value: str | None = None
    ) -> KittySetting:
        if is_commented_out is None:
            is_commented_out = self.is_commented_out

        if value is None:
            value = self.value

        return type(self)(
            name=self.name,
            line_no=self.line_no,
            is_commented_out=is_commented_out,
            value=value or value,
            raw_line=self.raw_line,
        )

    @property
    def formatted_line(self) -> str:
        comment = "# " if self.is_commented_out else ""
        return f"{comment}{self.name} {self.value}\n"


@dataclass
class KittyTheme:
    colors: TerminalColors
    mapping: KittyColorMapping = field(default_factory=lambda: basic_mapping)

    def to_settings(self) -> dict[str, Color]:
        base_colors = self.colors.to_dict()
        derived_colors = self.mapping.map_terminal_colors(self.colors)

        return base_colors | derived_colors


class KittyApplier(ThemeApplier):
    app_name = "kitty"
    settings: dict[int, KittySetting]

    def __init__(self, config_file: Path | str) -> None:
        config_file = Path(config_file)

        if not config_file.is_file:
            raise FileNotFoundError(f"could not locate config file {config_file}")

        self.config_file = config_file
        self.settings = self.parse_config()

        return None

    def read_config(self) -> list[str]:
        with open(self.config_file, "r") as f:
            lines = f.readlines()

        return lines

    def parse_config(self) -> dict[int, KittySetting]:
        """Read the config, skipping over any lines marked with '#:'"""

        settings: dict[int, KittySetting] = dict()
        for line_no, line in enumerate(self.read_config()):
            stripped = line.strip()
            if stripped.startswith("#:") or not stripped:
                continue

            is_commented_out = stripped.startswith("#")
            stripped = stripped.lstrip(" #")

            name, _, value = stripped.partition(" ")

            if name == "map":
                # consider key mappings to have the keyboard shortcut as part of name
                shortcut, _, value = value.partition(" ")
                name = f"{name} {shortcut}"

            settings[line_no] = KittySetting(
                name=name,
                line_no=line_no,
                is_commented_out=is_commented_out,
                value=value.strip(),
                raw_line=line,
            )

        return settings

    def get_setting_by_name(self, name: str) -> KittySetting:
        results = [
            setting for setting in self.settings.values() if setting.name == name
        ]

        if not results:
            raise KeyError(f"Could not find setting {name}")

        if len(results) > 1:
            raise KeyError(f"There were {len(results)} settings that matched {name}")

        return results[0]

    def updated_settings_from_theme(self, theme: KittyTheme) -> dict[int, KittySetting]:
        theme_settings = theme.to_settings()

        result: dict[int, KittySetting] = dict()
        for setting, color in theme_settings.items():
            updated = self.get_setting_by_name(setting).make_updated_setting(
                is_commented_out=False, value=str(color).lower()
            )
            result[updated.line_no] = updated

        return result

    def apply_theme(self, theme: KittyTheme) -> None:
        updated_settings = self.updated_settings_from_theme(theme)

        lines = []
        for line_no, line in enumerate(self.read_config()):
            if line_no in updated_settings:
                line = updated_settings[line_no].formatted_line
            lines.append(line)

        with open(self.config_file, "w") as f:
            f.writelines(lines)

        print(f"wrote updated to {self.config_file}")

        return None
