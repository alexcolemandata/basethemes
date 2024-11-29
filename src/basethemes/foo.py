from __future__ import annotations
from git import Repo
from pathlib import Path
from os import getenv
import yaml

from .base import Base16Palette, BaseTheme, BaseThemes, Base24Palette

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

    base16_themes_dir = Path(repo.git_dir).parent / "base16"
    base16_themes = BaseThemes(base_dir=base16_themes_dir, palette_type=Base16Palette)

    base24_themes_dir = Path(repo.git_dir).parent / "base24"
    base_24_themes = BaseThemes(base_dir=base24_themes_dir, palette_type=Base24Palette)
