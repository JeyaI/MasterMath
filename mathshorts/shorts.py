"""Productions: one folder per Short under shorts/, and the status machine.

    shorts/0007-slug/
        short.yaml   content + status (the only state file)
        verify.py    checks every answer; must pass before approval
        scene.py     the Manim scene, class Short
        NOTES.md     review notes, a checklist; open items block approval

Status flow (every change goes through `transition`, never hand-edit `status`):

    drafting --approve--> approved --batch--> ready --published--> published
        ^                     |                 |
        |                     +--batch fails--> failed
        +------- reject (from approved / ready / failed) ----------+
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import paths, yamlio

STATUSES = ["drafting", "approved", "ready", "failed", "published"]

# action -> (allowed current statuses, new status)
TRANSITIONS = {
    "approve": ({"drafting", "failed"}, "approved"),
    "batch_ok": ({"approved"}, "ready"),
    "batch_fail": ({"approved"}, "failed"),
    "reject": ({"approved", "ready", "failed"}, "drafting"),
    "publish": ({"ready"}, "published"),
}


class StatusError(RuntimeError):
    pass


@dataclass
class Short:
    folder: Path

    @property
    def name(self) -> str:          # "0007-slug"
        return self.folder.name

    @property
    def number(self) -> str:        # "0007"
        return self.folder.name.split("-", 1)[0]

    @property
    def yaml_path(self) -> Path:
        return self.folder / "short.yaml"

    @property
    def notes_path(self) -> Path:
        return self.folder / "NOTES.md"

    def data(self):
        return yamlio.load(self.yaml_path)

    @property
    def status(self) -> str:
        return self.data()["status"]

    def update(self, **fields) -> None:
        """Set top-level or dotted fields (e.g. youtube.video_id) and save atomically."""
        d = self.data()
        for key, value in fields.items():
            node, *rest = key.split(".")
            if rest:
                d.setdefault(node, {})
                d[node][rest[0]] = value
            else:
                d[node] = value
        yamlio.save(self.yaml_path, d)

    def transition(self, action: str, force: bool = False) -> str:
        allowed, new = TRANSITIONS[action]
        cur = self.status
        if cur not in allowed and not force:
            raise StatusError(f"{self.name}: can't {action} from {cur!r} (needs {' or '.join(sorted(allowed))})")
        self.update(status=new)
        return new

    # --- notes -------------------------------------------------------------------
    def add_note(self, text: str, beat: str | None = None, source: str = "review") -> str:
        today = dt.date.today().isoformat()
        where = f" · {beat}" if beat else ""
        line = f"- [ ] {today} · {source}{where} · {text}\n"
        if not self.notes_path.exists():
            self.notes_path.write_text(f"# Notes: {self.name}\n\nTick items `- [x]` when done. Open items block `ms approve`.\n\n")
        with open(self.notes_path, "a", encoding="utf-8") as f:
            f.write(line)
        return line.strip()

    def open_notes(self) -> list[str]:
        if not self.notes_path.exists():
            return []
        return [l.strip() for l in self.notes_path.read_text().splitlines() if l.lstrip().startswith("- [ ]")]

    # --- verify ------------------------------------------------------------------
    def verify(self) -> tuple[bool, str]:
        r = subprocess.run([sys.executable, "verify.py"], cwd=self.folder, capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr).strip()


def all_shorts() -> list[Short]:
    base = paths.shorts()
    if not base.exists():
        return []
    return [Short(p) for p in sorted(base.iterdir()) if (p / "short.yaml").exists()]


def find(ref: str) -> Short:
    """Accept '7', '0007', or '0007-slug'."""
    ref = ref.strip()
    if ref.isdigit():
        ref = f"{int(ref):04d}"
    hits = [s for s in all_shorts() if s.name == ref or s.number == ref]
    if len(hits) != 1:
        raise SystemExit(f"ms: no single Short matches {ref!r} (found {[h.name for h in hits]})")
    return hits[0]


def next_number() -> str:
    nums = [int(s.number) for s in all_shorts() if s.number.isdigit()]
    return f"{(max(nums) + 1) if nums else 1:04d}"


def slugify(title: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:max_len].rstrip("-") or "untitled"


def used_catalog_ids() -> set[str]:
    out = set()
    for s in all_shorts():
        cid = s.data().get("catalog_id")
        if cid:
            out.add(str(cid))
    return out
