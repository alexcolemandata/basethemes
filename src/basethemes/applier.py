"""Tools for applying a theme to various applications"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from dataclasses import dataclass, field
import os
import signal
from functools import partial
import subprocess
import re

from basethemes.terminal_colors import TerminalColor, TerminalColors, Color
from basethemes.base import BaseTheme


DOT_CONFIG = Path("/Users/alex/.config")


class ThemeApplier:
    app_name: str
    config_file: Path

    def __init__(self, config_file: Path | str) -> None:
        config_file = Path(config_file)

        if not config_file.is_file:
            raise FileNotFoundError(f"could not locate config file {config_file}")

        self.config_file = config_file

        return None

    def read_config(self) -> list[str]:
        with open(self.config_file, "r") as f:
            lines = f.readlines()

        return lines

    def apply_theme(self, theme: BaseTheme) -> None:
        raise NotImplementedError("Requires implementation by subclass")


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


basic_kitty_mapping = KittyColorMapping(
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
    mapping: KittyColorMapping = field(default_factory=lambda: basic_kitty_mapping)

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

    def apply_theme(self, theme: BaseTheme) -> None:
        kitty_theme = KittyTheme(colors=theme.to_terminal_colors())
        updated_settings = self.updated_settings_from_theme(kitty_theme)

        lines = []
        for line_no, line in enumerate(self.read_config()):
            if line_no in updated_settings:
                line = updated_settings[line_no].formatted_line
            lines.append(line)

        with open(self.config_file, "w") as f:
            f.writelines(lines)

        print(f"wrote updated to {self.config_file}")
        self.reload_config()

        return None

    def reload_config(self) -> None:
        kitty_pid = os.getenv("KITTY_PID")

        if not kitty_pid:
            raise EnvironmentError(f"Could not determine env var $KITTY_PID")

        try:
            kitty_pid = int(kitty_pid)
        except ValueError:
            raise EnvironmentError(f"$KITTY_PID was not an integer: {kitty_pid}")

        # reload https://sw.kovidgoyal.net/kitty/conf/
        os.kill(kitty_pid, signal.SIGUSR1)


class NeoVimApplier(ThemeApplier):
    app_name = "neovim"

    def apply_theme(self, theme: BaseTheme) -> None:
        lines = []
        has_updated = False
        for line in self.read_config():
            if line.startswith("local base16_theme ="):
                var, equals, _ = line.partition(" = ")
                lines.append(f'{var}{equals}"{theme.lower_name}"\n')
                has_updated = True

            else:
                lines.append(line)

        if not has_updated:
            raise ValueError(
                f"Could not find base16_theme variable defined in {self.config_file}"
            )

        with open(self.config_file, "w") as f:
            f.writelines(lines)

        print(f"wrote updated to {self.config_file}")

        return None


@dataclass
class SketchyBarColorMapping(TypedDict):
    black: str
    white: str
    red: str
    green: str
    blue: str
    yellow: str
    orange: str
    magenta: str
    grey: str
    bar_bg: str
    bar_border: str
    popup_bg: str
    popup_border: str
    bg1: str
    bg2: str


basic_sketchy_mapping: SketchyBarColorMapping = {
    "black": "base00",
    "white": "base07",
    "red": "base08",
    "green": "base0B",
    "blue": "base0D",
    "yellow": "base0A",
    "orange": "base09",
    "magenta": "base0E",
    "grey": "base02",
    "bar_bg": "base00",
    "bar_border": "base05",
    "popup_bg": "base00",
    "popup_border": "base06",
    "bg1": "base01",
    "bg2": "base02",
}


class SketchyBarApplier(ThemeApplier):
    app_name = "sketchybar"

    def reload_config(self) -> None:
        subprocess.run(
            "sketchybar --reload && sleep 1 && sketchybar --update", shell=True
        )

        return None

    def apply_theme(self, theme: BaseTheme) -> None:
        config_lines = self.read_config()

        SCALAR_SETTINGS = [
            "black",
            "white",
            "red",
            "green",
            "blue",
            "yellow",
            "orange",
            "magenta",
            "grey",
            "bg1",
            "bg2",
        ]

        TABLE_SECTIONS = ["bar", "popup"]
        TABLE_PARTS = ["bg", "border"]

        lines = []
        in_table_section: None | str = None

        for line in config_lines:
            stripped = line.strip()

            if in_table_section:
                if stripped.startswith("}"):
                    in_table_section = None

                    lines.append(line)
                    continue

                for part in TABLE_PARTS:
                    if not stripped.startswith(part):
                        continue

                    setting = f"{in_table_section}_{part}"
                    base = basic_sketchy_mapping[setting]

                    pre, hex, config_value = line.partition("0x")
                    opacity = config_value[:2]

                    new_color = str(theme.palette[base]).lower().removeprefix("#")
                    newline = pre + hex + opacity + new_color + ",\n"

                    lines.append(newline)
                    break

                else:
                    lines.append(line)
                    continue

            # not part of table, check scalar settings
            else:
                for setting in SCALAR_SETTINGS:
                    if not stripped.startswith(setting):
                        continue

                    base = basic_sketchy_mapping[setting]

                    pre, hex, config_value = line.partition("0x")
                    opacity = config_value[:2]

                    new_color = str(theme.palette[base]).lower().removeprefix("#")
                    newline = pre + hex + opacity + new_color + ",\n"

                    lines.append(newline)
                    break

                else:
                    # check if we have started reading a table section
                    for table_section in TABLE_SECTIONS:
                        if not stripped.startswith(table_section):
                            continue

                        if in_table_section:
                            raise Exception(
                                f"started reading new table without closing existing section: {in_table_section}"
                            )

                        in_table_section = table_section

                    # append regardless, as not modifying this line
                    lines.append(line)

        with open(self.config_file, "w") as f:
            f.writelines(lines)

        print(f"wrote updated to {self.config_file}")
        self.reload_config()

        return None


class LazyBordersApplier(ThemeApplier):
    app_name = "lazyborder"

    def reload_config(self) -> None:
        subprocess.run(f"{self.config_file.resolve()}", shell=True)
        return None

    def apply_theme(self, theme: BaseTheme) -> None:
        config_lines = self.read_config()

        lines = []

        SETTINGS = ["active_color", "inactive_color"]
        for line in config_lines:
            stripped = line.strip()

            for setting in SETTINGS:
                if not stripped.startswith(setting):
                    continue

                if setting == "active_color":
                    theme_color = theme.palette["base0B"]
                else:
                    theme_color = theme.palette["base01"]

                new_color = str(theme_color).lower().removeprefix("#")

                pre, hex, value = line.partition("0x")
                opacity = value[:2]
                newline = f"{pre}{hex}{opacity}{new_color}\n"

                lines.append(newline)
                break

            else:
                lines.append(line)

        with open(self.config_file, "w") as f:
            f.writelines(lines)

        print(f"wrote updated to {self.config_file}")
        self.reload_config()

        return None
