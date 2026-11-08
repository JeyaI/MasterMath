"""`ms check`: format rules and on-screen match, from a dry run of the scene (see probe.py).

Errors make a Short wrong or unpublishable; warnings are style targets a Short may miss on purpose.
Each finding says when it happens and in which beat.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import paths
from .shorts import Short

SAFE = (-3.8, -4.6, 3.2, 7.0)          # x0, y0, x1, y1; mirrors lib/layout.py
EDGE_TOL = 0.1                         # about 12 px; labels are scaled to exactly the safe width
OVERLAP_MIN = 0.02                     # square units of text-on-text before it counts
DURATION = (40.0, 50.0)                # target, not a cap: a warning
CAPTION_WORDS = (1, 14)                # warning: an upper bound for phone readability, not a target
COUNTDOWN_S = 5
COMMENT = "comment just the number"
COMMENT_HOLD_MIN = 10.0
YAML_SKIP = {"id", "video_id", "url", "published_at", "built_at", "catalog_id", "last_error", "status"}


@dataclass
class Finding:
    level: str          # "error" | "warning"
    rule: str
    message: str
    t: float | None = None
    beat: str | None = None

    def line(self) -> str:
        where = f"{int(self.t // 60)}:{self.t % 60:04.1f} " if self.t is not None else ""
        beat = f"[{self.beat}] " if self.beat else ""
        return f"{self.level.upper():7} {self.rule:9} {where}{beat}{self.message}"


# --- running the probe ---------------------------------------------------------------------
def probe(short: Short) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "probe.json"
        r = subprocess.run([sys.executable, "-m", "mathshorts.probe", str(short.folder), str(out)],
                           capture_output=True, text=True, cwd=paths.REPO)
        if r.returncode != 0 or not out.exists():
            tail = "\n".join(r.stderr.strip().splitlines()[-15:])
            raise RuntimeError(f"the scene did not run:\n{tail}")
        return json.loads(out.read_text())


# --- helpers ------------------------------------------------------------------------------
NUM = re.compile(r"\d+(?:\.\d+)?")
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")


def numbers_in(text: str) -> list[str]:
    return [n.rstrip("0").rstrip(".") if "." in n else n for n in NUM.findall(text.replace(",", ""))]


def words(text: str) -> int | None:
    """Words and numbers; None for a pure equation such as '1 + 2 = 3', which has no length target."""
    text = re.sub(r"\\[a-zA-Z]+", " ", text)                 # LaTeX commands such as \frac
    n = sum(len(w) > 1 for w in WORD.findall(text))           # a lone x or y is a variable
    return n + len(NUM.findall(text)) if n else None


def yaml_strings(v, key: str | None = None):
    if key in YAML_SKIP:
        return
    if isinstance(v, dict):
        for k, x in v.items():
            yield from yaml_strings(x, k)
    elif isinstance(v, list):
        for x in v:
            yield from yaml_strings(x, key)
    elif v is not None:
        yield str(v)


SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def norm(text: str) -> str:
    """Compare captions ignoring spaces, and '2⁸' as the LaTeX '2^8'."""
    text = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", lambda m: "^" + m.group().translate(SUPERSCRIPT), text)
    return re.sub(r"\s+", "", text)


def music_credit_problem(short: Short) -> str | None:
    """Why the YouTube description fails to credit the Short's music, or None if it does."""
    from . import render
    try:
        credit = f"Music: {render.music_piece(short).credit}"
    except ValueError as e:
        return str(e)
    if credit not in ((short.data().get("youtube") or {}).get("description") or ""):
        return f"the YouTube description must credit its music: \"{credit}\""
    return None


# --- rules --------------------------------------------------------------------------------
def check_duration(p: dict) -> list[Finding]:
    d = p["duration"]
    lo, hi = DURATION
    if lo <= d <= hi:
        return []
    return [Finding("warning", "duration", f"{d:.1f} s, outside the {lo:.0f}–{hi:.0f} s target")]


def check_safe_zone(p: dict) -> list[Finding]:
    x0, y0, x1, y1 = SAFE
    out, seen = [], set()
    for s in p["snapshots"]:
        for o in s["objects"]:
            bx0, by0, bx1, by1 = o["bounds"]
            sides = [n for n, bad in (("left", bx0 < x0 - EDGE_TOL), ("bottom", by0 < y0 - EDGE_TOL),
                                      ("right", bx1 > x1 + EDGE_TOL), ("top", by1 > y1 + EDGE_TOL)) if bad]
            if not sides:
                continue
            name = next((t["text"] for t in o["texts"] if t["text"]), None) or describe_shape(o)
            key = (name, tuple(sides))
            if key in seen:
                continue
            seen.add(key)
            out.append(Finding("error", "safe-zone", f"{name!r} goes past the {', '.join(sides)} edge "
                               f"(bounds {o['bounds']})", s["t"], s["beat"]))
    return out


def describe_shape(o: dict) -> str:
    parts = ", ".join(f"{n} {k}" for k, n in sorted(o.get("parts", {}).items(), key=lambda kv: -kv[1])[:3])
    return f"{o['kind']} ({parts})" if parts else o["kind"]


def _area(a, b) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def check_overlaps(p: dict) -> list[Finding]:
    out, seen = [], set()
    for s in p["snapshots"]:
        texts = [t for o in s["objects"] for t in o["texts"]]
        for i, a in enumerate(texts):
            for b in texts[i + 1:]:
                if _area(a["bounds"], b["bounds"]) < OVERLAP_MIN:
                    continue
                key = tuple(sorted((str(a["text"]), str(b["text"]))))
                if key in seen:
                    continue
                seen.add(key)
                out.append(Finding("error", "overlap", f"{a['text']!r} overlaps {b['text']!r}", s["t"], s["beat"]))
    return out


def check_beats(p: dict) -> list[Finding]:
    beats, out = p["beats"], []
    names = [b["name"].lower() for b in beats]

    def first(pred, after=-1):
        return next((i for i, n in enumerate(names) if i > after and pred(n)), None)

    if not beats or names[0] != "hook" or beats[0]["t"] > 0.5:
        out.append(Finding("error", "beats", "the first beat must be \"hook\", at 0:00"))
    pause = first(lambda n: "pause and try" in n)
    if pause is None:
        out.append(Finding("error", "beats", "no \"Pause and try it\" beat"))
    cds = p["countdowns"]
    if pause is not None and not any(c["seconds"] == COUNTDOWN_S and c["t"] >= beats[pause]["t"] for c in cds):
        out.append(Finding("error", "beats", f"no {COUNTDOWN_S} s countdown after \"Pause and try it\"",
                           beats[pause]["t"], beats[pause]["name"]))
    payoff = first(lambda n: "✓" in n, pause if pause is not None else -1)
    if payoff is None:
        out.append(Finding("error", "beats", "no ✓ payoff caption after the pause"))
    level2 = first(lambda n: n.startswith("level 2"), payoff if payoff is not None else -1)
    if level2 is None:
        out.append(Finding("error", "beats", "no \"Level 2\" beat after the payoff"))
    if not names or COMMENT not in names[-1]:
        out.append(Finding("error", "beats", "the last beat must be \"Comment just the number ↓\""))
    else:
        hold = p["duration"] - beats[-1]["t"]
        if hold < COMMENT_HOLD_MIN:
            out.append(Finding("error", "beats", f"\"Comment just the number\" is held {hold:.1f} s; "
                               f"hold it at least {COMMENT_HOLD_MIN:.0f} s", beats[-1]["t"], beats[-1]["name"]))
    return out


def check_captions(p: dict, data: dict) -> list[Finding]:
    out = []
    lo, hi = CAPTION_WORDS
    for c in p["captions"]:
        n = words(c["text"])
        if n is not None and not lo <= n <= hi:
            out.append(Finding("warning", "caption", f"{c['text']!r} is {n} word{'s' * (n != 1)}; "
                               f"keep it under about {hi} so it reads on a phone", c["t"]))
    listed = [str(x) for x in data.get("captions") or []]
    shown = {norm(c["text"]) for c in p["captions"]}
    for c in p["captions"]:
        if norm(c["text"]) not in {norm(x) for x in listed}:
            out.append(Finding("error", "match", f"caption {c['text']!r} is not in short.yaml captions", c["t"]))
    for x in listed:
        if norm(x) not in shown:
            out.append(Finding("error", "match", f"short.yaml caption {x!r} never appears on screen"))
    return out


def check_numbers(p: dict, data: dict) -> list[Finding]:
    """Numbers in on-screen sentences must come from short.yaml or verify.py.

    Checks captions, the hook and the Level 2 card. Text with no words (a lone "3" on a figure,
    a move counter) is a label, not a claim, and is skipped.
    """
    out = []
    allowed = {n for s in yaml_strings(data) for n in numbers_in(s)} | set(p["verify_numbers"])
    l1 = set(numbers_in(str((data.get("level1") or {}).get("answer") or "")))
    payoff = next((c for c in p["captions"] if "✓" in c["text"]), None)
    wrong = [n for n in numbers_in(payoff["text"]) if n not in l1] if payoff else []
    if wrong:
        out.append(Finding("error", "match", f"the payoff {payoff['text']!r} shows {', '.join(wrong)}, "
                           "which isn't in level1's answer", payoff["t"]))

    seen = set()

    def look(text, t, beat):
        if not text or not WORD.search(text) or text in seen:
            return
        seen.add(text)
        bad = [n for n in numbers_in(text) if n not in allowed]
        if bad:
            out.append(Finding("error", "match", f"{text!r} shows {', '.join(bad)}, which is in neither "
                               "short.yaml nor verify.py", t, beat))

    for c in p["captions"]:
        look(c["text"], c["t"], None)
    for s in p["snapshots"]:
        b = (s["beat"] or "").lower()
        if b == "hook" or b.startswith("level 2"):
            for o in s["objects"]:
                for t in o["texts"]:
                    look(t["text"], s["t"], s["beat"])
    return out


def run(short: Short) -> list[Finding]:
    data = short.data()
    findings = []
    if problem := music_credit_problem(short):
        findings.append(Finding("error", "music", problem))
    try:
        p = probe(short)
    except RuntimeError as e:
        return findings + [Finding("error", "scene", str(e))]
    for rule in (check_beats, check_safe_zone, check_overlaps, check_duration):
        findings += rule(p)
    findings += check_captions(p, data) + check_numbers(p, data)
    return findings
