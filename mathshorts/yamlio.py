"""Round-trip YAML (keeps comments and key order) with atomic writes.

Every write goes to a temp file and is renamed into place, so a crash or a
concurrent reader never sees a half-written file.
"""
from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

from ruamel.yaml import YAML


def _yaml() -> YAML:
    y = YAML()  # round-trip mode
    y.preserve_quotes = True
    y.width = 100
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return _yaml().load(f)


def dump_str(data) -> str:
    buf = io.StringIO()
    _yaml().dump(data, buf)
    return buf.getvalue()


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def save(path: Path, data) -> None:
    write_atomic(path, dump_str(data))
