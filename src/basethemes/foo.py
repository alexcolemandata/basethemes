from __future__ import annotations
from git import Repo
from pathlib import Path
from os import getenv
import yaml

from .base import Base16Palette

THEME_REPO_URL = "https://github.com/tinted-theming/schemes"

# TODO: via env/config
REPO_DIR = Path("/Users/alex/repos/tinted-theming")
BASE_16_THEME = getenv("THEME_BASE16")

if REPO_DIR.exists():
    print(f"repo exists at {REPO_DIR}")
    repo = Repo(REPO_DIR)
else:
    print(f"repo didn't exist, cloning to {REPO_DIR}")
    repo = Repo.clone_from(url=THEME_REPO_URL, to_path=REPO_DIR, depth=1)


base16_themes_dir = Path(repo.git_dir).parent / "base16"

theme_file = base16_themes_dir / f"{BASE_16_THEME}.yaml"

if not theme_file.exists:
    raise FileNotFoundError(
        f"could not find theme {BASE_16_THEME} in {base16_themes_dir}"
    )

print(repo)

with open(theme_file, "r") as f:
    theme = yaml.safe_load(f)

print(theme)


palette = Base16Palette(
    base00="#1C1E26",
    base01="#232530",
    base02="#2E303E",
    base03="#6F6F70",
    base04="#9DA0A2",
    base05="#CBCED0",
    base06="#DCDFE4",
    base07="#E3E6EE",
    base08="#E95678",
    base09="#FAB795",
    base0A="#FAC29A",
    base0B="#29D398",
    base0C="#59E1E3",
    base0D="#26BBD9",
    base0E="#EE64AC",
    base0F="#F09383",
)

print(f"{palette[3]=}")
print(f"{palette['0E']=}")
print(f"{palette['base0A']=}")
print(f"{palette['BASE0D']=}")
print(f"{palette['0b']=}")
