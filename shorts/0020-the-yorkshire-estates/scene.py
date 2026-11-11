"""Short 0020 - The Yorkshire Estates (Dudeney no. 189).

Three square estates meet corner to corner round a triangle. Each area is a sum of two squares, so the
triangle's corners sit on grid points; box the triangle in, subtract the corner triangles and the
rectangle, and 11 acres is left. Level 2: squares of 26, 20 and 18 acres.

Every shape and number comes from verify.py (A, B, C, D, E, F, L2_PTS, ...).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, Create, DashedLine, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    Polygon, Scene, Transform, VGroup, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES as COL, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    A, AREA_A, AREA_B, AREA_C, B, C, D, E, F, L2_AREAS, L2_PTS, LEGS, sq,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
BLUE, ORANGE, GREEN, PINK = COL[1], COL[0], COL[2], COL[3]

S1, S2, S3 = 0.18, 0.37, 0.8            # scale of the squares figure, the grid view, the Level 2 card
O1 = np.array([CENTRE_X - 10.5 * S1, 1.25 - 8 * S1, 0.0])      # squares figure spans x -5..26, y -10..26
O2 = np.array([CENTRE_X - 17 * S2 / 2, 0.9, 0.0])
S3 = 0.42                                # Level 2 figure spans x -4..8, y -5..7
O3 = np.array([CENTRE_X - 2 * S3, -0.9 + 5 * S3, 0.0])
COUNTER_Y = -1.5


def pt(o, s, p):
    return o + s * np.array([p[0], p[1], 0.0])


def outward_square(p, q, away_from):
    """Corners of the square on segment p-q, standing on the side away from `away_from`."""
    d = np.array([q[0] - p[0], q[1] - p[1]])
    n = np.array([-d[1], d[0]])
    if np.dot(n, np.array(away_from) - np.array(p)) > 0:
        n = -n
    p, q = np.array(p), np.array(q)
    return [tuple(p), tuple(q), tuple(q + n), tuple(p + n)]


def counter(text, color=ACCENT, size=84):
    return label(text, size, color).move_to([CENTRE_X, COUNTER_Y, 0])


def tag(text, at, size=44, color=INK):
    return label(text, size, color).move_to(at)


class Short(Scene):
    def construct(self):
        cap = Captions(self)

        # ---------- figure 1: three squares round a triangle ----------
        P1 = lambda p: pt(O1, S1, p)
        sq_ab = outward_square(A, B, C)
        sq_cb = outward_square(C, B, A)
        sq_ac = outward_square(A, C, B)

        def square(corners, color):
            return Polygon(*[P1(c) for c in corners], stroke_color=color, stroke_width=4,
                           fill_color=color, fill_opacity=0.35)

        s_ab, s_cb, s_ac = square(sq_ab, BLUE), square(sq_cb, GREEN), square(sq_ac, PINK)
        tri1 = Polygon(P1(A), P1(B), P1(C), stroke_color=ACCENT, stroke_width=5,
                       fill_color=ACCENT, fill_opacity=0.9)

        def centre_of(corners):
            return P1(np.mean(np.array(corners), axis=0))

        n_ab = tag(str(AREA_A), centre_of(sq_ab), 64)
        n_cb = tag(str(AREA_B), centre_of(sq_cb), 56)
        n_ac = tag(str(AREA_C), centre_of(sq_ac), 52)
        nums = VGroup(n_ab, n_cb, n_ac)

        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(s_ab), GrowFromCenter(s_cb), GrowFromCenter(s_ac), run_time=0.6)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(GrowFromCenter(tri1), run_time=0.4)
        cap.show("How many acres is the triangle\nbetween these three square estates?", run_time=0.5)
        self.wait(1.8)

        cap.show("The three squares meet corner to corner and enclose a small triangle.")
        self.play(Indicate(tri1, color=INK, scale_factor=1.25), run_time=1.0)
        self.wait(1.4)

        self.add_sound(SFX["pop"])
        cap.show("The estates cover 370, 116 and 74 acres.",
                 extra=[LaggedStart(*[FadeIn(n, scale=0.6) for n in nums], lag_ratio=0.3)], run_time=0.9)
        self.wait(2.0)

        cap.show("How many acres does the triangle in the middle cover?", ACCENT)
        self.play(Indicate(tri1, color=INK, scale_factor=1.3), run_time=1.0)
        self.wait(0.5)

        # ---------- pause and try ----------
        cap.show("Pause and try it.", ACCENT)
        countdown(self, 5, center=[CENTRE_X, 5.6, 0], radius=0.9, tick_sound=SFX["tick"])

        # ---------- each area is a sum of two squares ----------
        cap.show("Each square's area is a sum of two squares, so look for whole numbers.")
        sums = [("370 = 17² + 9²", n_ab, 38), ("116 = 10² + 4²", n_cb, 32), ("74 = 7² + 5²", n_ac, 28)]
        new = []
        for text, old, size in sums:
            t = tag(text, old.get_center(), size)
            t.scale_to_fit_width(min(t.width, 1.9 if old is not n_ab else 3.0))
            new.append(Transform(old, t))
        self.add_sound(SFX["chime"], gain=-8)
        self.play(*new, run_time=1.0)
        self.wait(1.5)

        # ---------- grid view ----------
        P2 = lambda p: pt(O2, S2, p)
        grid = VGroup(*[Line(P2((x, 0)), P2((x, 9)), color=MUTED, stroke_width=1.2) for x in range(18)],
                      *[Line(P2((0, y)), P2((17, y)), color=MUTED, stroke_width=1.2) for y in range(10)])
        grid.set_stroke(opacity=0.45)
        tri2 = Polygon(P2(A), P2(B), P2(C), stroke_color=ACCENT, stroke_width=5,
                       fill_color=ACCENT, fill_opacity=0.9)
        # staircase for the long side: 9 down, then 17 across
        v_ad = DashedLine(P2(A), P2(D), color=BLUE, stroke_width=7)
        h_db = DashedLine(P2(D), P2(B), color=BLUE, stroke_width=7)
        l9 = tag("9", P2((-0.5, 4.5)), 44, BLUE)
        l17 = tag("17", P2((8.5, -0.9)), 56, BLUE)
        eq_ab = tag("370 = 17² + 9²", [CENTRE_X, 6.4, 0], 48, BLUE)
        eq_ac = tag("74 = 7² + 5²", [CENTRE_X, 5.6, 0], 48, PINK)
        eq_cb = tag("116 = 10² + 4²", [CENTRE_X, 4.8, 0], 48, GREEN)
        self.add_sound(SFX["snip"])
        cap.show("370 is 17 squared plus 9 squared: 17 across and 9 down.",
                 extra=[FadeOut(s_ab), FadeOut(s_cb), FadeOut(s_ac), FadeOut(nums),
                        Transform(tri1, tri2), FadeIn(grid), FadeIn(eq_ab)], run_time=1.2)
        self.add_sound(SFX["pop"])
        self.play(Create(v_ad), Create(h_db), FadeIn(l9), FadeIn(l17), run_time=1.0)
        self.wait(0.8)

        # the other two sides
        v_ae = DashedLine(P2(A), P2(E), color=PINK, stroke_width=7)
        h_ec = DashedLine(P2(E), P2(C), color=PINK, stroke_width=7)
        v_cf = DashedLine(P2(C), P2(F), color=GREEN, stroke_width=7)
        h_fb = DashedLine(P2(F), P2(B), color=GREEN, stroke_width=7)
        a5 = tag("5", P2((-0.5, 6.5)), 44, PINK)
        a7 = tag("7", P2((3.5, 4.75)), 50, PINK)
        c4 = tag("4", P2((7.8, 2.0)), 50, GREEN)
        c10 = tag("10", P2((12, 0.6)), 50, GREEN)
        # the 9 on the left edge now reads as the two parts 5 and 4
        self.add_sound(SFX["snip"])
        cap.show("74 is 7 squared plus 5 squared; 116 is 10 squared plus 4 squared.",
                 extra=[Create(v_ae), Create(h_ec), Create(v_cf), Create(h_fb),
                        FadeIn(a5), FadeIn(a7), FadeIn(c4), FadeIn(c10), FadeOut(l9),
                        FadeIn(eq_ac), FadeIn(eq_cb)], run_time=1.2)
        self.wait(1.2)

        self.add_sound(SFX["chime"], gain=-6)
        cap.show("Now every corner of the triangle sits on a grid point.")
        self.play(*[Flash(P2(p), color=INK, flash_radius=0.45, line_length=0.2) for p in (A, B, C)],
                  run_time=1.0)
        self.wait(0.8)

        # ---------- subtraction ----------
        def fill(pts, color, op=0.55):
            return Polygon(*[P2(p) for p in pts], stroke_color=color, stroke_width=0,
                           fill_color=color, fill_opacity=op).set_z_index(1)

        big = fill([A, D, B], BLUE, 0.45)
        tri2.set_z_index(3)
        tri1.set_z_index(3)
        cnt = counter("76.5")
        self.add_sound(SFX["pop"])
        cap.show("The big right triangle is half of 17 times 9, so 76 and a half.",
                 extra=[FadeIn(big), FadeIn(cnt, shift=0.3 * DOWN), FadeOut(l17), FadeOut(a5),
                        FadeOut(a7), FadeOut(c4), FadeOut(c10)], run_time=0.8)
        half = tag("½ × 17 × 9", P2((5.0, 1.5)), 44, INK)
        self.play(FadeIn(half), run_time=0.4)
        self.wait(1.0)

        aec = fill([A, E, C], PINK, 0.8)
        cfb = fill([C, F, B], GREEN, 0.8)
        self.add_sound(SFX["snip"])
        cap.show("Take away the two small corner triangles, 17 and a half and 20.",
                 extra=[FadeOut(half), FadeIn(aec), FadeIn(cfb),
                        Transform(cnt, counter("76.5 − 17.5 − 20"))], run_time=1.0)
        self.play(Indicate(aec, color=INK, scale_factor=1.08), run_time=0.7)
        self.play(Indicate(cfb, color=INK, scale_factor=1.08), run_time=0.7)
        self.wait(0.8)

        rect = fill([E, D, F, C], ORANGE, 0.8)
        self.add_sound(SFX["snip"])
        cap.show("Take away the 7 by 4 rectangle, which is 28 acres.",
                 extra=[FadeIn(rect), Transform(cnt, counter("76.5 − 17.5 − 20 − 28", size=72))],
                 run_time=1.0)
        self.play(Indicate(rect, color=INK, scale_factor=1.06), run_time=0.7)
        self.wait(1.2)

        # ---------- payoff ----------
        self.add_sound(SFX["chime"])
        cap.show("What is left is the triangle: exactly 11 acres ✓", GOOD,
                 extra=[FadeOut(big), FadeOut(aec), FadeOut(cfb), FadeOut(rect), FadeOut(v_ad),
                        FadeOut(h_db), FadeOut(eq_ab), FadeOut(eq_ac), FadeOut(eq_cb), FadeOut(v_ae), FadeOut(h_ec), FadeOut(v_cf), FadeOut(h_fb),
                        tri1.animate.set_fill(GOOD, 1).set_stroke(GOOD),
                        Transform(cnt, counter("= 11 acres", GOOD, 96))], run_time=1.0)
        self.play(Flash(P2((np.array(A) + np.array(B) + np.array(C)) / 3), color=GOOD, flash_radius=1.6),
                  Indicate(tri1, color=INK, scale_factor=1.1), run_time=1.0)
        self.wait(0.8)

        # ---------- Level 2 ----------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()
        P3 = lambda p: pt(O3, S3, p)
        p, q, r = L2_PTS
        tri3 = Polygon(*[P3(x) for x in L2_PTS], stroke_color=ACCENT, stroke_width=5,
                       fill_color=ACCENT, fill_opacity=0.9)
        l2_sq = []
        for (a, b), third, area, col in zip(((p, q), (q, r), (r, p)), (r, p, q), (26, 18, 20),
                                            (BLUE, GREEN, PINK)):
            corners = outward_square(a, b, third)
            assert sq(a, b) == area
            poly = Polygon(*[P3(c) for c in corners], stroke_color=col, stroke_width=4,
                           fill_color=col, fill_opacity=0.35)
            l2_sq.append((poly, tag(str(area), P3(np.mean(np.array(corners), axis=0)), 56, INK)))
        sq_labels = VGroup(*[t for _, t in l2_sq])
        assert sorted(L2_AREAS) == [18, 20, 26]
        tg = badge("LEVEL 2").move_to([CENTRE_X, 6.5, 0])
        sub = label("Three squares of 26, 20 and 18 acres\nsit on the sides of this triangle.", 44, INK)
        sub.move_to([CENTRE_X, 5.3, 0])
        ask = label("triangle: ? acres", 72, ACCENT).move_to([CENTRE_X, -1.6, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tg), run_time=0.4)
        self.play(FadeIn(sub), *[GrowFromCenter(s) for s, _ in l2_sq], run_time=0.8)
        self.play(GrowFromCenter(tri3), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in sq_labels], lag_ratio=0.25), run_time=0.8)
        cap.show("Level 2: squares of 26, 20 and 18 acres meet round a triangle.", run_time=0.5)
        self.wait(1.8)
        cap.show("Same trick: how many acres is the triangle?", run_time=0.5)
        self.wait(1.6)
        cap.show("Comment just the number ↓", ACCENT, extra=[FadeIn(ask, shift=0.2 * UP)])
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.1), run_time=1.0, rate_func=there_and_back)
            self.wait(1.8)
        assert LEGS["AB"] == (17, 9)
