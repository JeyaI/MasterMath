"""Short 0009 - An Easy Square Puzzle (Dudeney no. 147).

Level 1 (shown on screen): five identical right triangles (half of a 2 x 1 rectangle); make a square from all
five, cutting at most one of them once. A sample cut on the fifth triangle shows the rule (the pieces wiggle
apart and rejoin), then a 5 s pause. Area 5 means the side is the slanted edge, so four whole triangles swing
into a pinwheel round a 1 x 1 hole; the fifth is cut once from the middle of its long leg, the trapezoid
slides up and the small triangle makes a half turn into the hole. The square lights up with area 5.
Level 2 (comment challenge): short side 3, long side 6; what is the area of the square? (45)

All shapes and numbers (pieces, pinwheel, cut parts, moves, Level 2 legs) come from verify.py.
"""
from __future__ import annotations

import sys
from math import atan2
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

import numpy as np  # noqa: E402
from manim import (  # noqa: E402
    BOLD, DOWN, PI, UP, Create, DashedLine, FadeIn, FadeOut, GrowFromCenter, Indicate, LaggedStart, Polygon, Restore,
    Scene, UpdateFromAlphaFunc, VGroup, WHITE, there_and_back, smooth,
)

from lib.layout import ACCENT, BG, GOOD, INK, MUTED, PIECES  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    BIG, HOLE, L2_AREA, L2_LEGS, PIECE, TRAP_FROM, TRAP_SHIFT, TRAP_TO, TRI_FROM, TRI_TO, TRI_TURN_ABOUT, WHOLE,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
assert L2_AREA == 45 and L2_LEGS == (3, 6)

BLUE, ORANGE, PINK = PIECES[1], PIECES[0], PIECES[3]
S1 = 1.5                       # scale of the pieces in the opening layout
S2 = 1.7                       # scale of the pinwheel
C2 = np.array([CENTRE_X, 2.4, 0.0])        # screen position of the square's centre (1.5, 1.5)
T5 = (0.5, -1.25)              # where the fifth piece waits, below the square, in verify coordinates

# opening layout: right-angle corner of each piece (bottom-left of the triangle)
SLOTS = [
    np.array([CENTRE_X - 1.7 - 1.5, 3.5, 0.0]), np.array([CENTRE_X + 1.7 - 1.5, 3.5, 0.0]),
    np.array([CENTRE_X - 1.7 - 1.5, 1.35, 0.0]), np.array([CENTRE_X + 1.7 - 1.5, 1.35, 0.0]),
    np.array([CENTRE_X - 1.5, -0.5, 0.0]),
]


def at(pts, ra, s):
    """Polygon for verify points `pts`, drawn at scale s with verify origin sent to screen point ra."""
    return [ra + s * np.array([x, y, 0.0]) for x, y in pts]


def tri(pts, ra, s, color, op=0.92):
    return Polygon(*at(pts, ra, s), fill_color=color, fill_opacity=op, stroke_color=INK, stroke_width=4)


def sq(p):
    """Screen point of a pinwheel-frame point."""
    return C2 + S2 * (np.array([p[0], p[1], 0.0]) - np.array([1.5, 1.5, 0.0]))


def corner_pose(t):
    """(right-angle vertex, direction angle of the long leg) of a triangle congruent to PIECE."""
    pts = [np.array(p, float) for p in t]
    for i in range(3):
        a, b, c = pts[i], pts[(i + 1) % 3], pts[(i + 2) % 3]
        if abs(np.dot(b - a, c - a)) < 1e-9:
            far = b if np.linalg.norm(b - a) > np.linalg.norm(c - a) else c
            return a, atan2(far[1] - a[1], far[0] - a[0])
    raise ValueError("not a right triangle")


def pose(m, ra0, ra1, angle=0.0, k=1.0, run_time=1.0):
    """Rigid move of m: scale by k and turn by `angle` about ra0, then slide ra0 to ra1."""
    start = m.copy()
    ra0, ra1 = np.array(ra0, float), np.array(ra1, float)

    def f(mob, a):
        mob.become(start)
        mob.scale(1 + (k - 1) * a, about_point=ra0)
        mob.rotate(a * angle, about_point=ra0)
        mob.shift(a * (ra1 - ra0))

    return UpdateFromAlphaFunc(m, f, run_time=run_time, rate_func=smooth)


class Short(Scene):
    def construct(self):
        cap = Captions(self)

        # --- hook: five triangles pop in, then the question ---------------------------------------
        beat(self, "hook")
        cols = [BLUE, BLUE, BLUE, BLUE, ORANGE]
        pieces = [tri(PIECE, SLOTS[i], S1, cols[i]) for i in range(5)]
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pieces], lag_ratio=0.15), run_time=1.0)
        self.remove(*pieces)
        self.add(*pieces)
        # side lengths sit outside the triangle (standard notation), smaller and white
        one = label("1", 40, WHITE, weight=BOLD).move_to(SLOTS[0] + np.array([-0.3, S1 * 0.5, 0]))
        two = label("2", 40, WHITE, weight=BOLD).move_to(SLOTS[0] + np.array([S1 * 1.0, -0.24, 0]))
        title = hook("An Easy Square Puzzle")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), FadeIn(one), FadeIn(two), run_time=0.45)
        cap.show("Can you make a square?")
        self.wait(2.0)

        # --- the rule: one cut on the fifth triangle, the pieces wiggle apart ----------------------------
        cap.show("You may cut one, once")
        ra5 = SLOTS[4]
        cutline = DashedLine(*at([(0.5, -0.12), (0.5, 0.95)], ra5, S1), color=ACCENT, stroke_width=7)
        self.add_sound(SFX["tick"])
        self.play(Create(cutline), run_time=0.7)
        pa = tri([(0, 0), (0.5, 0), (0.5, 0.75), (0, 1)], ra5, S1, ORANGE)
        pb = tri([(0.5, 0), (2, 0), (0.5, 0.75)], ra5, S1, PINK)
        self.remove(pieces[4])
        self.add(pa, pb)
        pa.save_state(); pb.save_state()
        self.play(pa.animate.shift(0.22 * np.array([-1, 0.4, 0])).rotate(0.12),
                  pb.animate.shift(0.22 * np.array([1, -0.2, 0])).rotate(-0.12), FadeOut(cutline), run_time=0.5)
        for sgn in (1, -1, 1):
            self.play(pa.animate.rotate(-0.28 * sgn), pb.animate.rotate(0.28 * sgn), run_time=0.3)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(Restore(pa), Restore(pb), run_time=0.5)
        self.remove(pa, pb)
        self.add(pieces[4])
        self.wait(0.5)

        # --- pause and try ----------------------------------------------------------------------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X, -1.85, 0], radius=0.8, tick_sound=SFX["tick"])

        # --- area 5, so the side is the slanted edge ---------------------------------------------------------
        slants = VGroup(*[DashedLine(*at([PIECE[1], PIECE[2]], SLOTS[i], S1), color=ACCENT, stroke_width=9,
                                     dash_length=0.001, dashed_ratio=1.0) for i in range(5)])
        t1 = label("5 pieces × area 1 = area 5", 46).move_to([CENTRE_X, -1.2, 0])
        t2 = label("Side of the square = √5", 46, ACCENT).move_to([CENTRE_X, -2.0, 0])
        cap.show("Slanted edges form the outside",
                 extra=[FadeOut(title), FadeOut(credit), FadeOut(one), FadeOut(two), FadeIn(t1)])
        self.play(Create(slants), run_time=0.8)
        self.play(FadeIn(t2, shift=0.2 * UP), run_time=0.5)
        self.wait(1.8)

        # --- four around a hole ---------------------------------------------------------------------------------
        cap.show("Four around a hole", extra=[FadeOut(t1), FadeOut(t2), FadeOut(slants)])
        moves = []
        for i, t in enumerate(WHOLE):
            ra, ang = corner_pose(t)
            moves.append(pose(pieces[i], SLOTS[i], sq(ra), ang, S2 / S1, run_time=1.1))
        ra5_new = sq((T5[0], T5[1]))
        moves.append(pose(pieces[4], SLOTS[4], ra5_new, 0.0, S2 / S1, run_time=1.1))
        for i in range(5):
            self.add_sound(SFX["tick"], time_offset=0.2 * i, gain=-6)
        self.play(LaggedStart(*moves, lag_ratio=0.18), run_time=2.6)
        self.wait(0.6)

        # --- the hole is 1 by 1 ---------------------------------------------------------------------------------------
        hole = Polygon(*[sq(p) for p in HOLE], fill_color=ACCENT, fill_opacity=0.28, stroke_color=ACCENT,
                       stroke_width=8)
        hole_lab = label("1 × 1", 56, ACCENT).move_to(sq((1.5, 1.5)))
        cap.show("The hole is 1 by 1", extra=[FadeIn(hole), FadeIn(hole_lab)])
        self.add_sound(SFX["pop"], gain=-4)
        self.play(Indicate(hole, color=ACCENT, scale_factor=1.12), run_time=0.9)
        self.wait(1.2)

        # --- cut the fifth triangle and fill the hole --------------------------------------------------------------------
        ra5s = ra5_new
        cap.show("Cut the fifth triangle", extra=[FadeOut(hole_lab)])
        cut = DashedLine(sq((1 + T5[0], -0.12 + T5[1])), sq((1 + T5[0], 0.7 + T5[1])), color=ACCENT, stroke_width=8)
        self.add_sound(SFX["tick"])
        self.play(Create(cut), run_time=0.7)
        trap = tri(TRAP_FROM, ra5s, S2, ORANGE)
        small = tri(TRI_FROM, ra5s, S2, PINK)
        self.remove(pieces[4])
        self.add(trap, small)
        self.play(trap.animate.shift(0.18 * np.array([-1, 0, 0])), small.animate.shift(0.18 * np.array([1, 0, 0])),
                  FadeOut(cut), run_time=0.6)
        self.wait(0.3)
        # the trapezoid slides up into the hole, then the small triangle makes a half turn
        tr0 = sq((TRAP_FROM[0][0] + T5[0] - 0.0, TRAP_FROM[0][1] + T5[1]))
        tr1 = sq(TRAP_TO[0])
        self.add_sound(SFX["pop"], gain=-3)
        # undo the sideways nudge while sliding: the end point is the exact filled position
        self.play(pose(trap, tr0 - 0.18 * np.array([1, 0, 0]), tr1, 0.0, 1.0, run_time=1.3))
        q0 = sq((TRI_TURN_ABOUT[0] + T5[0], TRI_TURN_ABOUT[1] + T5[1])) + 0.18 * np.array([1, 0, 0])
        q1 = sq(TRI_TURN_ABOUT)
        self.add_sound(SFX["pop"], gain=-3)
        self.play(pose(small, q0, q1, PI, 1.0, run_time=1.5))
        self.wait(0.4)

        # --- fits exactly -----------------------------------------------------------------------------------------------------
        outline = Polygon(*[sq(p) for p in BIG], fill_opacity=0, stroke_color=GOOD, stroke_width=12)
        area = badge("Area 5", GOOD).move_to([CENTRE_X, -1.5, 0])
        cap.show("It fits exactly ✓", GOOD, extra=[FadeOut(hole), Create(outline)])
        self.add_sound(SFX["chime"])
        self.play(GrowFromCenter(area), Indicate(outline, color=GOOD, scale_factor=1.04), run_time=0.8)
        self.wait(1.8)

        # --- Level 2 -----------------------------------------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        self.clear()
        a, b = L2_LEGS
        k3 = 0.85
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.55, 0])
        q = VGroup(label("Five triangles make a square.", 46), label("What is its area?", 46, ACCENT))
        q.arrange(DOWN, buff=0.2).move_to([CENTRE_X, 5.2, 0])
        base = np.array([CENTRE_X - b * k3 / 2, 1.6, 0.0])
        big_tri = Polygon(*at([(0, 0), (b, 0), (0, a)], base, k3), fill_color=BLUE, fill_opacity=0.92,
                          stroke_color=INK, stroke_width=4)
        # side lengths sit outside the triangle (standard notation), smaller and white
        l_short = label(str(a), 40, WHITE, BOLD).move_to(base + np.array([-0.45, k3 * a / 2, 0]))
        l_long = label(str(b), 40, WHITE, BOLD).move_to(base + np.array([k3 * b / 2, -0.45, 0]))
        # a small copy of the solved square, to show the same shape in the same arrangement
        k4 = 0.85
        C4 = np.array([CENTRE_X, -0.4, 0.0])

        def sq4(p):
            return C4 + k4 * (np.array([p[0], p[1], 0.0]) - np.array([1.5, 1.5, 0.0]))

        shapes = [Polygon(*[sq4(p) for p in t], fill_color=BLUE, fill_opacity=0.92, stroke_color=INK,
                          stroke_width=3) for t in WHOLE]
        shapes.append(Polygon(*[sq4(p) for p in TRAP_TO], fill_color=ORANGE, fill_opacity=0.92,
                              stroke_color=INK, stroke_width=3))
        shapes.append(Polygon(*[sq4(p) for p in TRI_TO], fill_color=PINK, fill_opacity=0.92,
                              stroke_color=INK, stroke_width=3))
        mini = VGroup(*shapes)
        ask = label("Area = ?", 60, ACCENT).move_to([CENTRE_X, -2.3, 0])
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("Short side 3, long side 6", extra=[GrowFromCenter(tag), FadeIn(q)])
        self.play(GrowFromCenter(big_tri), FadeIn(l_short), FadeIn(l_long), run_time=0.7)
        self.play(FadeIn(mini, shift=0.2 * UP), FadeIn(ask), run_time=0.7)
        self.wait(2.0)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.9)
