"""Where everything lives. One place, so tests and the cloud box can point elsewhere.

MS_ROOT  repo root holding catalog/, shorts/, config/   (default: this checkout)
MS_OUT   generated files: previews, renders, ready kits, logs (default: <root>/out)
MS_CACHE downloaded raw source files                    (default: ~/.cache/mathshorts)
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def root() -> Path:
    return Path(os.environ.get("MS_ROOT", REPO))


def out() -> Path:
    return Path(os.environ.get("MS_OUT", root() / "out"))


def cache() -> Path:
    return Path(os.environ.get("MS_CACHE", Path.home() / ".cache" / "mathshorts"))


def catalog() -> Path:
    return root() / "catalog"


def shorts() -> Path:
    return root() / "shorts"


def config() -> Path:
    return root() / "config"
