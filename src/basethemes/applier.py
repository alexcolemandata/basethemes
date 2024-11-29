"""Tools for applying a theme to various applications"""

from pathlib import Path

from dataclasses import dataclass
from functools import partial

from basethemes.terminal_colors import TerminalColor, TerminalColors


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


@dataclass
class KittyTheme:
    mapping: KittyColorMapping
    colors: TerminalColors


kitty_theme = partial(KittyTheme, mapping=basic_mapping)


class KittyApplier(ThemeApplier):
    app_name = "kitty"
    settings: list[KittySetting]
    updated_settings: list[KittySetting]

    def __init__(self, config_file: Path | str) -> None:
        config_file = Path(config_file)

        if not config_file.is_file:
            raise FileNotFoundError(f"could not locate config file {config_file}")

        self.config_file = config_file
        self.settings = self.read_config()

    def read_config(self) -> list[KittySetting]:
        """Read the config, skipping over any lines marked with '#:'"""
        with open(self.config_file, "r") as f:
            conf_lines = f.readlines()

        settings: list[KittySetting] = []
        for line_no, line in enumerate(conf_lines):
            stripped = line.strip()
            if stripped.startswith("#:") or not stripped:
                continue

            is_commented_out = line.startswith("#")
            line = line.lstrip(" #")

            name, _, value = line.partition(" ")

            if name == "map":
                # consider key mappings to have the keyboard shortcut as part of name
                shortcut, _, value = value.partition(" ")
                name = f"{name} {shortcut}"

            settings.append(
                KittySetting(
                    name=name,
                    line_no=line_no,
                    is_commented_out=is_commented_out,
                    value=value.strip(),
                )
            )

        return settings

    def get_setting(self, name: str) -> KittySetting:
        results = [setting for setting in self.settings if setting.name == name]

        if not results:
            raise KeyError(f"Could not find setting {name}")

        if len(results) > 1:
            raise KeyError(f"There were {len(results)} settings that matched {name}")

        return results[0]

    def updated_settings_from_theme(self, theme: KittyTheme) -> list[KittySetting]:
        breakpoint()
        # terminal colors are easy
