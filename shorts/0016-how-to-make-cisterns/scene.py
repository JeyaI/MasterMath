"""Short 0016 - How To Make Cisterns (Dudeney no. 201).

Level 1 (solved on screen): an 8 ft x 3 ft sheet, squares of side x cut from the corners, sides folded up.
V = x(8-2x)(3-2x) = 4x^3 - 22x^2 + 24x; V' = 12x^2 - 44x + 24 = 0; quadratic formula gives x = 3 or 2/3;
3 is off the sheet, so the peak is at 2/3 ft (8 in), V = 200/27 cubic feet.
Level 2 (comment challenge): 12 ft square sheet -> 2 ft.

The numbers come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

import numpy as np  # noqa: E402
from manim import (  # noqa: E402
    BOLD, DOWN, RIGHT, UP, Axes, Rectangle, Create, DashedLine, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, Line, Polygon,
    Scene, Square, Transform, VGroup, ValueTracker, always_redraw, linear, there_and_back, smooth,
)

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, SAFE_LEFT, STAGE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    A, B, BEST, BEST_INCHES, BEST_VOLUME, CRIT_2, L2_BEST_FT, L2_SIDE_FT, volume,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
assert (A, B, BEST, BEST_INCHES, CRIT_2, L2_BEST_FT, L2_SIDE_FT) == (8, 3, BEST, 8, 3, 2, 12)
assert BEST_VOLUME == volume(BEST)

BEST_F = float(BEST)
SHOW_X = 0.9                    # the cut drawn on the sheet (just to illustrate; the answer is not it)
SHEET_C = np.array([CENTRE_X, 2.3, 0.0])
SC = 0.84                       # units per foot on the flat sheet
BOX_SC = 0.7
SHEET_BLUE = PIECES[1]
HOT = PIECES[0]


def slope(x: float) -> float:
    return 12 * x * x - 44 * x + 24


class Caps(Captions):
    """Captions at one steady size (two balanced lines) so they do not shrink and grow from beat to beat."""

    def _make(self, content, color):
        return super()._make(label(content, 46, color) if isinstance(content, str) else content, color)


def wrap(text: str) -> str:
    if len(text) <= 32:
        return text
    words = text.split(" ")
    best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
    return " ".join(words[:best]) + "\n" + " ".join(words[best:])


def flat_sheet(a: float, b: float, x: float, sc: float, centre, xlabel: bool = True, dims: bool = True) -> VGroup:
    """A flat rectangle a by b feet with squares of side x cut from the four corners."""
    cx, cy = centre[0], centre[1]
    w, h, s = a * sc, b * sc, x * sc
    rect = Polygon([-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0],
                   fill_color=SHEET_BLUE, fill_opacity=0.85, stroke_color=INK, stroke_width=4)
    g = VGroup(rect)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = np.array([sx * (w / 2 - s / 2), sy * (h / 2 - s / 2), 0.0])
            sq = Square(s, fill_color=BG, fill_opacity=1, stroke_color=ACCENT, stroke_width=4).move_to(c)
            g.add(sq)
            if xlabel and s > 0.5:
                g.add(label("x", 34, ACCENT).move_to(c))
    if dims:
        g.add(dim_labels(a, b, sc))
    return g.shift(np.array([cx, cy, 0.0]))


def dim_labels(a: float, b: float, sc: float) -> VGroup:
    """'8 ft by 3 ft' in the middle of a sheet centred at the origin."""
    return VGroup(label(f"{a} ft × {b} ft", 46, BG, BOLD).move_to([0, 0, 0]))


def box_shape(x: float, h: float, a: float, b: float, centre, sc: float = BOX_SC) -> VGroup:
    """Open box of base (a-2x) by (b-2x) and wall height h, in a simple oblique view."""
    L, W = a - 2 * x, b - 2 * x
    kx, ky = 0.5, 0.35

    def p(l, w, hh):
        return np.array([sc * (l + kx * w), sc * (hh + ky * w), 0.0])

    faces = [
        ("bottom", [(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)], GRID, 1.0),
        ("back", [(0, W, 0), (L, W, 0), (L, W, h), (0, W, h)], SHEET_BLUE, 0.55),
        ("left", [(0, 0, 0), (0, W, 0), (0, W, h), (0, 0, h)], SHEET_BLUE, 0.7),
        ("front", [(0, 0, 0), (L, 0, 0), (L, 0, h), (0, 0, h)], SHEET_BLUE, 0.9),
        ("right", [(L, 0, 0), (L, W, 0), (L, W, h), (L, 0, h)], SHEET_BLUE, 0.8),
    ]
    g = VGroup()
    for _, pts, col, op in faces:
        g.add(Polygon(*[p(*q) for q in pts], fill_color=col, fill_opacity=op, stroke_color=INK, stroke_width=3))
    return g.move_to([centre[0], centre[1], 0])


class Short(Scene):
    def construct(self):
        cap = Caps(self)
        mark = [None, 0.0]

        def settle():
            if mark[0] is not None:
                short = mark[1] - (self.renderer.time - mark[0])
                if short > 0.01:
                    self.wait(short)

        def say(text: str, color=INK, extra=(), run_time: float = 0.45):
            settle()
            mark[0], mark[1] = self.renderer.time, 0.3 + 0.18 * len(text.split())
            return cap.show(wrap(text), color, extra=extra, run_time=run_time)

        # --- hook: the sheet pops in, then the question ---------------------------------------------
        beat(self, "hook")
        sheet = flat_sheet(A, B, SHOW_X, SC, SHEET_C[:2], dims=False)
        sheet_dims = dim_labels(A, B, SC).shift(SHEET_C)
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(sheet), run_time=0.6)
        title = VGroup(*[label(t, 40, INK) for t in
                         ("How big should the corner squares", "be to make the cistern hold", "the most water?")]
                       ).arrange(DOWN, buff=0.16).move_to([CENTRE_X, 5.55, 0])
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(2.2)

        # --- the problem builds ---------------------------------------------------------------------
        self.add_sound(SFX["pop"])
        say("A man has a flat zinc sheet, eight feet by three feet.",
            extra=[FadeOut(title), FadeOut(credit), FadeIn(sheet_dims)])
        self.wait(0.2)

        hot = [m for m in sheet if isinstance(m, Square)]
        self.add_sound(SFX["snip"])
        say("He cuts a square out of each of the four corners.")
        self.play(*[Indicate(m, color=ACCENT, scale_factor=1.3) for m in hot], run_time=0.9)

        # fold up into a box
        xt, ht = ValueTracker(SHOW_X), ValueTracker(0.0)
        box = always_redraw(lambda: box_shape(xt.get_value(), ht.get_value() * xt.get_value(), A, B,
                                              [CENTRE_X, 2.3], 0.9))
        self.add_sound(SFX["whoosh"] if "whoosh" in SFX else SFX["pop"])
        say("Then he folds up the sides to make a cistern.", extra=[FadeOut(sheet), FadeOut(sheet_dims)])
        self.add(box)
        self.play(ht.animate.set_value(1.0), run_time=1.4, rate_func=smooth)
        self.wait(0.3)

        # --- pause and try ----------------------------------------------------------------------------
        settle()
        mark[0] = None
        box.clear_updaters()
        self.remove(box)
        sheet3 = flat_sheet(A, B, SHOW_X, SC, [CENTRE_X, 2.1])
        task = VGroup(label("Find x, in feet,", 56, ACCENT), label("for the biggest box.", 56, ACCENT)
                      ).arrange(DOWN, buff=0.16).move_to([CENTRE_X, 5.55, 0])
        note = label("Squares of side x are cut from the corners.", 36, MUTED).move_to([CENTRE_X, 4.5, 0])
        cap.show("Pause and try it", ACCENT, extra=[FadeIn(sheet3), FadeIn(task), FadeIn(note)])
        countdown(self, 5, center=[CENTRE_X, -0.8, 0], radius=0.9, tick_sound=SFX["tick"])

        # --- tiny and big squares ---------------------------------------------------------------------
        xt.set_value(0.15)
        ht.set_value(1.0)
        box = always_redraw(lambda: box_shape(xt.get_value(), xt.get_value(), A, B, [CENTRE_X, 2.3]))
        xr = always_redraw(lambda: label(f"x = {xt.get_value():.2f} ft", 60, ACCENT).move_to([CENTRE_X, 5.8, 0]))
        vr = always_redraw(lambda: label(f"{volume(xt.get_value()):.1f} cubic feet", 60, GOOD)
                           .move_to([CENTRE_X, 4.8, 0]))
        # a bar whose length is the volume, so the eye sees "more" and "less" as x changes
        bar = always_redraw(lambda: Rectangle(width=max(0.05, 0.75 * volume(xt.get_value())), height=0.6,
                                              fill_color=GOOD, fill_opacity=1, stroke_width=0)
                            .move_to([SAFE_LEFT + 0.05 + max(0.05, 0.75 * volume(xt.get_value())) / 2, -0.6, 0]))
        bar_tag = label("volume", 34, MUTED).move_to([CENTRE_X, -1.35, 0])
        self.add_sound(SFX["pop"])
        say("Tiny squares make a wide cistern, but it is very shallow.",
            extra=[FadeOut(sheet3), FadeOut(task), FadeOut(note)])
        self.add(box, xr, vr, bar)
        self.add(bar_tag)
        self.wait(0.6)

        self.add_sound(SFX["snip"])
        say("Big squares make a deep cistern, but it is tall and thin.")
        self.play(xt.animate.set_value(1.3), run_time=1.8, rate_func=smooth)
        box.clear_updaters(); xr.clear_updaters(); vr.clear_updaters(); bar.clear_updaters()

        # --- the volume as a cubic ---------------------------------------------------------------------
        def eq(text: str, y: float, color=INK, size: float = 46):
            return label(text, size, color).move_to([CENTRE_X, y, 0])

        e1 = eq("V = x(8 − 2x)(3 − 2x)", 6.6)
        e2 = eq("V = 4x³ − 22x² + 24x", 5.85)
        e3 = eq("V′ = 12x² − 44x + 24 = 0", 5.1, ACCENT)
        e4a = eq("x = (44 ± √784) / 24", 4.35)
        e4b = eq("x = (44 ± 28) / 24", 4.35)

        self.add_sound(SFX["chime"], gain=-10)
        say("With side x, the volume is x times the length times the width.",
            extra=[FadeOut(box), FadeOut(xr), FadeOut(vr), FadeOut(bar), FadeOut(bar_tag),
                   FadeIn(e1, shift=0.2 * DOWN)])
        self.wait(0.4)
        self.add_sound(SFX["pop"])
        self.play(FadeIn(e2, shift=0.2 * DOWN), run_time=0.6)

        # graph of the cubic
        ax = Axes(x_range=[0, 1.6, 0.5], y_range=[0, 9, 3], x_length=6.2, y_length=3.5,
                  axis_config={"color": MUTED, "stroke_width": 4, "include_ticks": False, "include_tip": False},
                  ).move_to([CENTRE_X, 0.15, 0])
        curve = ax.plot(lambda x: 4 * x**3 - 22 * x**2 + 24 * x, x_range=[0, 1.5], color=INK, stroke_width=7)
        yl = label("V", 38, MUTED).next_to(ax.c2p(0, 9), RIGHT, buff=0.15)
        ticks = VGroup(*[label(s, 32, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15)
                         for s, v in (("0", 0), ("1 ft", 1), ("1.5 ft", 1.5))])
        tt = ValueTracker(0.15)

        def tangent():
            x = tt.get_value()
            p = ax.c2p(x, volume(x))
            sl = slope(x) * (3.5 / 9) / (6.2 / 1.6)
            d = np.array([1.0, sl, 0.0])
            d = d / np.linalg.norm(d)
            return Line(p - 1.3 * d, p + 1.3 * d, color=ACCENT, stroke_width=7)

        tang = always_redraw(tangent)
        pdot = always_redraw(lambda: Dot(ax.c2p(tt.get_value(), volume(tt.get_value())), radius=0.14, color=ACCENT)
                             .set_z_index(5))
        self.add_sound(SFX["chime"], gain=-10)
        say("That is a cubic, so its peak is where the slope is zero.",
            extra=[FadeIn(ax), FadeIn(yl), FadeIn(ticks)])
        self.play(Create(curve), run_time=1.0)
        self.add(tang, pdot)
        self.play(tt.animate.set_value(1.35), run_time=1.6, rate_func=smooth)

        # slope formula
        self.add_sound(SFX["snip"])
        say("The slope is twelve x squared minus 44x plus 24, set to zero.",
            extra=[FadeIn(e3, shift=0.2 * DOWN)])
        self.play(tt.animate.set_value(0.4), run_time=1.0, rate_func=smooth)

        # quadratic formula
        self.add_sound(SFX["pop"])
        say("The quadratic formula gives x as 44 plus or minus 28, over 24.",
            extra=[FadeIn(e4a, shift=0.2 * DOWN)])
        self.wait(0.6)
        self.play(Transform(e4a, e4b), run_time=0.7)

        # the two roots
        r3 = VGroup(eq("x = 3", 0, MUTED, 50), label("too big", 30, HOT)).arrange(DOWN, buff=0.08)
        strike = Line(r3[0].get_left() + 0.0 * UP, r3[0].get_right(), color=HOT, stroke_width=6)
        r3.add(strike)
        r23 = eq("x = 2/3", 0, GOOD, 56)
        orw = label("or", 40, INK)
        row = VGroup(r3, orw, r23).arrange(np.array([1.0, 0, 0]), buff=0.45, aligned_edge=UP)
        row.move_to([CENTRE_X, 3.3, 0])
        self.add_sound(SFX["snip"])
        say("So x is 3 or two thirds, but 3 feet is too big.",
            extra=[FadeIn(row, shift=0.2 * DOWN)])

        # sign change and the peak
        plus = badge("slope > 0", GOOD).scale(0.45).move_to(ax.c2p(0.5, 2.0))
        minus = badge("slope < 0", HOT).scale(0.45).move_to(ax.c2p(1.3, 4.2) + np.array([0.15, 0.7, 0]))
        self.add_sound(SFX["chime"], gain=-8)
        say("The slope turns from positive to negative at two thirds: the peak.",
            extra=[FadeIn(plus, shift=0.2 * UP), FadeIn(minus, shift=0.2 * UP)])
        self.play(tt.animate.set_value(BEST_F), run_time=1.5, rate_func=smooth)
        peak = ax.c2p(BEST_F, float(BEST_VOLUME))
        drop = DashedLine(peak, ax.c2p(BEST_F, 0), color=GOOD, stroke_width=5)
        pk = label("2/3 ft", 38, GOOD).next_to(ax.c2p(BEST_F, 0), DOWN, buff=0.15)
        self.play(Create(drop), FadeIn(pk), Flash(peak, color=GOOD, flash_radius=0.5), run_time=0.7)

        # the value
        vtxt = VGroup(label("V = 200/27", 38, GOOD), label("cubic feet", 34, GOOD)
                      ).arrange(DOWN, buff=0.06).move_to(ax.c2p(1.35, 8.0))
        self.add_sound(SFX["pop"])
        say("At two thirds of a foot, the volume is 200 over 27 cubic feet.",
            extra=[FadeIn(vtxt, shift=0.2 * UP), FadeOut(plus), FadeOut(minus)])

        # --- payoff -------------------------------------------------------------------------------------
        settle()
        beat(self, "payoff")
        big = label(f"x = 2/3 ft = {BEST_INCHES} inches", 62, GOOD).move_to([CENTRE_X, 4.6, 0])
        self.add_sound(SFX["chime"])
        say("The squares should be two thirds of a foot, or eight inches ✓", GOOD, extra=[
            FadeOut(e1), FadeOut(e2), FadeOut(e3), FadeOut(e4a), FadeOut(row), FadeIn(big)])
        self.wait(2.0)

        # --- Level 2 ---------------------------------------------------------------------------------------
        beat(self, "Level 2")
        mark[0] = None
        cap.clear()
        tang.clear_updaters(); pdot.clear_updaters()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()

        tag2 = badge("LEVEL 2").move_to([CENTRE_X, 6.45, 0])
        q = VGroup(*[label(s, 46) for s in ("Same idea with a square", "sheet, 12 feet on each side.")]
                   ).arrange(DOWN, buff=0.14).move_to([CENTRE_X, 5.1, 0])
        sq = flat_sheet(L2_SIDE_FT, L2_SIDE_FT, 2.4, 0.42, [CENTRE_X, 1.7])
        ask = label("How many feet should each", 46, INK)
        ask2 = label("cut-out square be?", 46, INK)
        askg = VGroup(ask, ask2).arrange(DOWN, buff=0.14).move_to([CENTRE_X, -1.75, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag2), FadeIn(q), run_time=0.5)
        self.play(GrowFromCenter(sq), FadeIn(askg), run_time=0.8)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(askg, color=ACCENT, scale_factor=1.1), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
