import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A throwaway repo root with the real config and source registry, no Shorts, no catalog data."""
    (tmp_path / "catalog").mkdir()
    shutil.copy(REPO / "catalog" / "sources.yaml", tmp_path / "catalog" / "sources.yaml")
    shutil.copytree(REPO / "config", tmp_path / "config")
    (tmp_path / "shorts").mkdir()
    monkeypatch.setenv("MS_ROOT", str(tmp_path))
    monkeypatch.setenv("MS_OUT", str(tmp_path / "out"))
    monkeypatch.setenv("MS_CACHE", str(tmp_path / "cache"))
    return tmp_path
