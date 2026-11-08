"""Reusable building blocks: hook title, synced captions, countdown, Level 2 card, footer credit.

Every Short should be assembled from these so the channel has a consistent look,
while the puzzle animation in the middle is what changes (and what makes each
video original).
"""
from __future__ import annotations

import json
import os

from manim import (
    DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP,
    Arc, Circle, FadeIn, FadeOut, RoundedRectangle, Scene, Text, ValueTracker,
    VGroup, VMobject, always_redraw, linear, BOLD, SEMIBOLD, MEDIUM,
)

from .layout import (
    ACCENT, BG, CAPTION_Y, FONT, FOOTER_Y, INK, MUTED, SAFE_LEFT, SAFE_RIGHT,
    SAFE_W, SIZE_BADGE, SIZE_CAPTION, SIZE_SMALL, SIZE_TITLE, TITLE_Y,
)

CENTRE_X = (SAFE_LEFT + SAFE_RIGHT) / 2


def beat(scene: Scene, name: str) -> None:
    """Mark the start of a beat. `ms preview` writes these to beats.json so review notes like
    "0:12 too fast" map to a spot in the scene, and `ms preview --at 0:12` re-renders just that beat.
    Captions.show() calls this automatically; call it yourself for beats without a caption."""
    r = scene.renderer
    beats = getattr(scene, "_ms_beats", [])
    beats.append({"t": round(float(r.time), 2), "anim": int(r.num_plays), "name": name})
    scene._ms_beats = beats
    path = os.environ.get("MS_BEATS_PATH")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(beats, f, indent=1, ensure_ascii=False)


def label(text: str, size: float = SIZE_CAPTION, color=INK, weight=SEMIBOLD) -> Text:
    t = Text(text, font=FONT, font_size=size, color=color, weight=weight)
    if t.width > SAFE_W:
        t.scale_to_fit_width(SAFE_W)
    return t


def hook(line1: str, line2: str | None = None) -> VGroup:
    """Big title at the top. Optional second line in the accent colour."""
    parts = [label(line1, SIZE_TITLE, INK, BOLD)]
    if line2:
        parts.append(label(line2, SIZE_CAPTION, ACCENT, SEMIBOLD))
    g = VGroup(*parts).arrange(DOWN, buff=0.3)
    g.move_to([CENTRE_X, TITLE_Y, 0])
    return g


def footer(text: str) -> Text:
    t = label(text, SIZE_SMALL, MUTED, MEDIUM)
    t.move_to([CENTRE_X, FOOTER_Y, 0])
    return t


class Captions:
    """One caption on screen at a time, cross-faded on each beat.

    Each call to show() is a beat (see beat()); write captions as natural spoken English
    (one idea each, roughly 14 words at most), not headline-style fragments.
    """

    def __init__(self, scene: Scene, y: float = CAPTION_Y):
        self.scene, self.y, self.current = scene, y, None

    def _make(self, content, color) -> VMobject:
        m = content if isinstance(content, VMobject) else label(content, SIZE_CAPTION, color)
        if m.width > SAFE_W:
            m.scale_to_fit_width(SAFE_W)
        return m.move_to([CENTRE_X, self.y, 0])

    def show(self, content, color=INK, run_time: float = 0.45, extra=()):
        beat(self.scene, content if isinstance(content, str) else "caption")
        new = self._make(content, color)
        anims = [FadeIn(new, shift=0.25 * UP)]
        if self.current is not None:
            anims.append(FadeOut(self.current, shift=0.25 * UP))
        self.scene.play(*anims, *extra, run_time=run_time)
        self.current = new
        return new

    def clear(self, run_time: float = 0.3):
        if self.current is not None:
            self.scene.play(FadeOut(self.current), run_time=run_time)
            self.current = None


def countdown(scene: Scene, seconds: int, center, radius: float = 0.9, tick_sound: str | None = None):
    """'Pause and try it' timer: a draining ring with the number in the middle."""
    t = ValueTracker(1.0)
    track = Circle(radius=radius, color=MUTED, stroke_width=8, stroke_opacity=0.35).move_to(center)
    ring = always_redraw(lambda: Arc(
        radius=radius, start_angle=PI / 2, angle=max(t.get_value(), 1e-4) * TAU,
        color=ACCENT, stroke_width=12,
    ).move_arc_center_to(center))
    num = always_redraw(lambda: label(
        str(max(1, int(-(-t.get_value() * seconds // 1)))), SIZE_TITLE, INK, BOLD,
    ).move_to(center))
    scene.play(FadeIn(track), FadeIn(ring), FadeIn(num), run_time=0.3)
    if tick_sound:
        for k in range(seconds):
            scene.add_sound(tick_sound, time_offset=k)
    scene.play(t.animate.set_value(0.0), run_time=seconds, rate_func=linear)
    ring.clear_updaters(); num.clear_updaters()
    scene.play(FadeOut(VGroup(track, ring, num)), run_time=0.3)


def badge(text: str, color=ACCENT) -> VGroup:
    t = label(text, SIZE_BADGE, BG, BOLD)
    box = RoundedRectangle(corner_radius=0.25, width=t.width + 0.8, height=t.height + 0.45,
                           fill_color=color, fill_opacity=1, stroke_width=0)
    return VGroup(box, t.move_to(box))
