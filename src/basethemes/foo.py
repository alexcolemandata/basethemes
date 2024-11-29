from __future__ import annotations
from git import Repo
from pathlib import Path
from os import getenv
import yaml

from .base import Base16Palette, BaseTheme, BaseThemes, Base24Palette
from .applier import kitty_theme, KittyApplier

THEME_REPO_URL = "https://github.com/tinted-theming/schemes"

# TODO: via env/config
REPO_DIR = Path("/Users/alex/repos/tinted-theming")
BASE_16_THEME = getenv("THEME_BASE16")


def init_repo(repo_url: str, clone_dir: Path) -> Repo:
    if clone_dir.exists():
        return Repo(clone_dir)

    return Repo.clone_from(repo_url, to_path=clone_dir, depth=1)


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

    kitty = KittyApplier(config_file="/Users/alex/.config/kitty/kitty.conf")
    kitty_theme_3024 = kitty_theme(colors=base16_themes["3024"].to_terminal_colors())
    # WIP: updated = kitty.updated_settings_from_theme(kitty_theme_3024)
