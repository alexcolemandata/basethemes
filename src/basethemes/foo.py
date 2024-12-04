from __future__ import annotations
from git import Repo
from pathlib import Path
from os import getenv
import yaml

from .base import Base16Palette, BaseTheme, BaseThemes, Base24Palette
from .applier import (
    KittyTheme,
    KittyApplier,
    NeoVimApplier,
    SketchyBarApplier,
    LazyBordersApplier,
)

THEME_REPO_URL = "https://github.com/tinted-theming/schemes"

# TODO: via env/config
REPO_DIR = Path("/Users/alex/repos/tinted-theming")
DOT_CONFIG = Path("/Users/alex/.config")

DEFAULT_THEME = "Gotham"


def init_repo(repo_url: str, clone_dir: Path) -> Repo:
    if clone_dir.exists():
        return Repo(clone_dir)

    return Repo.clone_from(repo_url, to_path=clone_dir, depth=1)


def apply_theme(base_themes: BaseThemes, theme_name: str) -> None:
    print(f"applying theme {theme_name}")

    theme = base_themes[theme_name]

    # lazyborders
    lazyborders = LazyBordersApplier(config_file=DOT_CONFIG / "borders/bordersrc")
    lazyborders.apply_theme(theme)

    # sketchybar
    sketchybar = SketchyBarApplier(config_file=DOT_CONFIG / "sketchybar/colors.lua")
    sketchybar.apply_theme(theme)

    # neovim
    nvim = NeoVimApplier(config_file=DOT_CONFIG / "nvim/lua/plugins/base16.lua")
    nvim.apply_theme(theme)

    # kitty
    kitty = KittyApplier(config_file=DOT_CONFIG / "kitty/kitty.conf")
    kitty.apply_theme(theme)

    return None


if __name__ == "__main__":
    repo = init_repo(repo_url=THEME_REPO_URL, clone_dir=REPO_DIR)

    themes_dir = Path(repo.git_dir).parent

    base16_themes = BaseThemes(
        base_dir=themes_dir / "base16", palette_type=Base16Palette
    )
    print(f"{len(base16_themes)=}")

    base24_themes = BaseThemes(
        base_dir=themes_dir / "base24", palette_type=Base24Palette
    )
    print(f"{len(base24_themes)=}")

    base16_catppuccin = base16_themes.filter(
        lambda theme: "catppuccin" in theme.name.lower()
    )
    print(f"{len(base16_catppuccin)=}")

    base24_light = base24_themes.filtered(variant="light")
    print(f"{len(base24_light)=}")

    print("base16_themes: " + "\n\t".join(sorted(base16_themes.list_theme_names())))

    apply_theme(base_themes=base16_themes, theme_name=DEFAULT_THEME)
