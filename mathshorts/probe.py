"""Run a Short's scene without rendering and record what is on screen. Used by `ms check`.

    python -m mathshorts.probe <short folder> <out.json>

Manim's dry run plays every animation but writes no frames. After each play() and wait(), this
records the time, the current beat and every visible object's bounds and text. It wraps
lib.components' countdown and Captions.show from outside, so lib itself is unchanged.

Writes {"duration", "beats", "captions", "countdowns", "snapshots", "verify_numbers"}.
"""
from __future__ import annotations

import importlib.util
import json
import numbers
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

TEXT_TYPES = ("Text", "MarkupText", "Paragraph", "Tex", "MathTex", "SingleStringMathTex")


def text_of(m) -> str | None:
    name = type(m).__name__
    if name in ("Text", "MarkupText", "Paragraph"):
        return getattr(m, "original_text", None) or getattr(m, "text", None)
    if name in ("Tex", "MathTex", "SingleStringMathTex"):
        return getattr(m, "tex_string", None)
    return None


def is_text(m) -> bool:
    return type(m).__name__ in TEXT_TYPES


def _visible_leaf(m) -> bool:
    import numpy as np
    from manim import VMobject
    if not isinstance(m, VMobject) or len(m.points) == 0:
        return False
    fill = float(np.max(m.get_fill_opacities())) if len(m.get_fill_opacities()) else 0.0
    stroke = float(np.max(m.get_stroke_opacities())) if len(m.get_stroke_opacities()) else 0.0
    return fill > 0.01 or (stroke > 0.01 and m.get_stroke_width() > 0)


def _bounds(leaves) -> list[float] | None:
    import numpy as np
    pts = [l.points for l in leaves if len(l.points)]
    if not pts:
        return None
    a = np.concatenate(pts)
    return [round(float(v), 3) for v in (a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max())]


def describe(top) -> dict | None:
    """One on-screen object: its bounds, plus the text objects inside it."""
    leaves = [m for m in top.get_family() if _visible_leaf(m)]
    if not leaves:
        return None
    texts, inside = [], set()
    for m in top.get_family():
        if is_text(m) and id(m) not in inside:
            inside.update(id(x) for x in m.get_family()[1:])   # MathTex holds its own parts
            visible = [l for l in m.get_family() if _visible_leaf(l)]
            b = _bounds(visible)
            if b:
                texts.append({"text": text_of(m), "bounds": b, "id": id(m)})
    parts: dict[str, int] = {}
    for l in leaves:
        parts[type(l).__name__] = parts.get(type(l).__name__, 0) + 1
    return {"kind": type(top).__name__, "bounds": _bounds(leaves), "texts": texts, "parts": parts}


def verify_numbers(module) -> list[str]:
    """Every number reachable from verify.py's module-level values, as strings."""
    seen: set[str] = set()

    def walk(v, depth):
        if depth > 4 or len(seen) > 5000:
            return
        if isinstance(v, bool):
            return
        if isinstance(v, (Fraction,)):
            seen.update({str(v), str(v.numerator), str(v.denominator)})
            if v.denominator == 1:
                seen.add(str(v.numerator))
            return
        if isinstance(v, numbers.Integral):
            seen.add(str(int(v)))
        elif isinstance(v, numbers.Real):
            f = float(v)
            seen.add(repr(f))
            if f == int(f):
                seen.add(str(int(f)))
            seen.add(f"{f:g}")
        elif isinstance(v, str):
            return
        elif isinstance(v, dict):
            for k, x in list(v.items())[:2000]:
                walk(k, depth + 1)
                walk(x, depth + 1)
        elif isinstance(v, (list, tuple, set, frozenset)):
            for x in list(v)[:2000]:
                walk(x, depth + 1)

    for k, v in vars(module).items():
        if not k.startswith("_"):
            walk(v, 0)
    return sorted(seen)


def run(folder: Path) -> dict:
    sys.path[:0] = [str(folder.parents[1]), str(folder)]
    from manim import Scene, config

    import lib.components as comp

    tmp = tempfile.mkdtemp(prefix="ms-check-")
    config.dry_run = True
    config.disable_caching = True
    config.media_dir = tmp
    config.pixel_width, config.pixel_height, config.frame_rate = 270, 480, 15
    config.verbosity = "ERROR"
    config.progress_bar = "none"

    state = {"scene": None, "captions": [], "countdowns": [], "snapshots": []}

    def now(scene) -> float:
        return round(float(scene.renderer.time), 3)

    def current_beat(scene) -> str | None:
        beats = getattr(scene, "_ms_beats", [])
        return beats[-1]["name"] if beats else None

    def snapshot(scene, what):
        objs = [d for m in scene.mobjects if (d := describe(m))]
        state["snapshots"].append({"t": now(scene), "beat": current_beat(scene), "after": what, "objects": objs})

    orig_play, orig_wait = Scene.play, Scene.wait

    def play(self, *a, **k):
        r = orig_play(self, *a, **k)
        snapshot(self, "play")
        return r

    def wait(self, *a, **k):
        r = orig_wait(self, *a, **k)
        snapshot(self, "wait")
        return r

    Scene.play, Scene.wait = play, wait

    orig_show = comp.Captions.show

    def show(self, content, *a, **k):
        t = now(self.scene)
        m = orig_show(self, content, *a, **k)
        text = content if isinstance(content, str) else " ".join(
            x for x in (text_of(s) for s in m.get_family() if is_text(s)) if x)
        state["captions"].append({"t": t, "text": text, "string": isinstance(content, str)})
        return m

    comp.Captions.show = show

    orig_countdown = comp.countdown

    def countdown(scene, seconds, *a, **k):
        state["countdowns"].append({"t": now(scene), "seconds": seconds})
        return orig_countdown(scene, seconds, *a, **k)

    comp.countdown = countdown

    spec = importlib.util.spec_from_file_location("ms_scene", folder / "scene.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scene = mod.Short()
    scene.render()

    verify = sys.modules.get("verify")
    return {
        "duration": now(scene),
        "beats": getattr(scene, "_ms_beats", []),
        "captions": state["captions"],
        "countdowns": state["countdowns"],
        "snapshots": state["snapshots"],
        "verify_numbers": verify_numbers(verify) if verify else [],
    }


if __name__ == "__main__":
    folder, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    out.write_text(json.dumps(run(folder), ensure_ascii=False))
