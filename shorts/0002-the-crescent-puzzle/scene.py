"""Short 0002 - The Crescent Puzzle (Dudeney no. 191).

Level 1 (solved on screen): a quarter turn and a scale-up land one half of a right triangle on the other,
so (x-5)^2 = x(x-9), the x^2 terms cancel, x = 25 -> diameters 50 and 41.
Level 2 (comment challenge): the same figure run backwards -> 4.

Geometry comes from verify.py, so what you see is exactly what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, PI, UP,
    Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, Line,
    MathTex, Polygon, RightAngle, Rotate, Scene, VGroup, Write,
    there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    GAP, L2_DIAMETER, L2_WIDE, WIDE, crescent, quarter_turn, similarity_scale, solve_radius,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
STAGE = np.array([CENTRE_X, STAGE_Y, 0.0])
FIG = crescent(solve_radius(WIDE, GAP), WIDE)
S = 3.3 / float(FIG["R"])                  # puzzle units -> frame units


def P(p, y=None, scale=S, origin=STAGE) -> np.ndarray:
    x, y = p if y is None else (p, y)
    return origin + scale * np.array([float(x), float(y), 0.0])


def circles(g, scale, origin, width=5):
    """Big and small circle, as outlines. Both start drawing at the point where they touch."""
    big = Circle(radius=float(g["R"]) * scale, stroke_color=INK, stroke_width=width).move_to(origin)
    small = Circle(radius=float(g["r"]) * scale, stroke_color=INK, stroke_width=width)
    small.move_to(P(g["O"], scale=scale, origin=origin))
    return big, small


def dimension(x0, x1, y, text, color):
    """A drafting-style dimension line with end ticks and the number sitting in a gap."""
    t = MathTex(text, color=color, font_size=50).move_to([(x0 + x1) / 2, y, 0])
    gap = t.width / 2 + 0.14
    mid = (x0 + x1) / 2
    parts = [Line([x0, y, 0], [mid - gap, y, 0]), Line([mid + gap, y, 0], [x1, y, 0]),
             Line([x0, y - 0.13, 0], [x0, y + 0.13, 0]), Line([x1, y - 0.13, 0], [x1, y + 0.13, 0])]
    return VGroup(*[p.set_color(color).set_stroke(width=5) for p in parts], t)


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        g = FIG
        A, B, C, D, E, F = (P(g[k]) for k in "ABCDEF")

        # --- 0-3 s  hook: the crescent draws itself, then the question ----------
        beat(self, "hook")
        big, small = circles(g, S, STAGE)
        self.add_sound(SFX["pop"])
        self.play(Create(big), Create(small), run_time=1.1)
        self.play(big.animate.set_fill(GRID, 1), small.animate.set_fill(BG, 1), run_time=0.3)
        title = hook("Can you figure out", "the diameters of the two circles?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(1.0)

        # --- 3-9 s  the setup: what the figure must say out loud ----------------
        touch = Dot(A, color=ACCENT, radius=0.13).set_z_index(6)
        centre = Dot(C, color=INK, radius=0.1).set_z_index(6)
        cap.show("They touch at this point", extra=[GrowFromCenter(touch)])
        self.play(Flash(A, color=ACCENT, flash_radius=0.45, num_lines=10), run_time=0.5)
        self.wait(0.3)
        cap.show("Centre of the big circle", extra=[GrowFromCenter(centre)])
        self.wait(0.8)

        across = Line(B, A, color=MUTED, stroke_width=3).set_z_index(1)
        wide_bar = Line(B, D, color=ACCENT, stroke_width=10).set_z_index(3)
        wide_lbl = MathTex(str(WIDE), color=ACCENT, font_size=60).move_to(
            (B + D) / 2 + 0.36 * UP).set_z_index(5)
        self.add_sound(SFX["pop"])
        cap.show("Widest part: 9 inches", extra=[Create(across), Create(wide_bar), Write(wide_lbl)])
        self.wait(1.1)

        up = Line(C, F, color=MUTED, stroke_width=3).set_z_index(1)
        gap_bar = Line(E, F, color=ACCENT, stroke_width=10).set_z_index(3)
        gap_lbl = MathTex(str(GAP), color=ACCENT, font_size=60).next_to(gap_bar, direction=[1, 0, 0],
                                                                        buff=0.16).set_z_index(5)
        tick = RightAngle(Line(C, A), Line(C, F), length=0.3, color=MUTED, stroke_width=3).set_z_index(2)
        self.add_sound(SFX["pop"])
        cap.show("Straight up: 5 inches",
                 extra=[Create(up), Create(gap_bar), Write(gap_lbl), Create(tick)])
        self.wait(1.4)

        # --- 9-15 s  pause and try ----------------------------------------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X + 2.9, STAGE_Y + 2.95, 0], radius=0.55, tick_sound=SFX["tick"])

        # --- the insight ---------------------------------------------------------
        def along(p, q, off):                       # midpoint of pq, nudged by `off` frame units
            return (p + q) / 2 + np.array([*off, 0.0])

        x_lbl = MathTex("x", color=INK, font_size=60).move_to(along(C, A, (0, -0.36))).set_z_index(5)
        cd_lbl = MathTex("x-9", color=INK, font_size=52).move_to(along(C, D, (0, -0.36))).set_z_index(5)
        ce_lbl = MathTex("x-5", color=INK, font_size=52).move_to(along(C, E, (-0.7, -0.74))).set_z_index(5)
        ac_line = Line(C, A, color=INK, stroke_width=6).set_z_index(2)
        cd_line = Line(C, D, color=INK, stroke_width=6).set_z_index(2)
        ce_line = Line(C, E, color=INK, stroke_width=6).set_z_index(2)
        cap.show("Call the big radius x", extra=[Create(ac_line), Write(x_lbl), FadeOut(touch)])
        self.wait(0.8)
        cap.show("So this is x − 9", extra=[Create(cd_line), Write(cd_lbl)])
        self.wait(0.7)
        cap.show("And this is x − 5", extra=[Create(ce_line), Write(ce_lbl)])
        self.wait(0.7)

        hyp = VGroup(Line(D, E, color=ACCENT, stroke_width=6), Line(E, A, color=ACCENT, stroke_width=6))
        hyp.set_z_index(3)
        corner = RightAngle(Line(E, D), Line(E, A), length=0.3, color=ACCENT, stroke_width=5).set_z_index(4)
        self.add_sound(SFX["snip"])
        cap.show("Semicircle = right angle!", ACCENT, extra=[Create(hyp)])
        self.play(Create(corner), small.animate.set_stroke(ACCENT), run_time=0.5)
        self.wait(1.0)

        right_tri = Polygon(A, C, E, stroke_width=0, fill_color=PIECES[0], fill_opacity=0.55).set_z_index(1)
        left_tri = Polygon(E, C, D, stroke_width=0, fill_color=PIECES[1], fill_opacity=0.55).set_z_index(1)
        cap.show("Two triangles…", extra=[FadeIn(right_tri), FadeIn(left_tri),
                                          small.animate.set_stroke(INK), FadeOut(corner)])
        self.wait(0.3)

        # The quarter turn about C: D lands on CE, E lands on CA.
        spin = Polygon(E, C, D, stroke_color=PIECES[1], stroke_width=5, fill_color=PIECES[1],
                       fill_opacity=0.9).set_z_index(3)
        self.add(spin)
        self.add_sound(SFX["pop"], time_offset=1.0)
        cap.show("Turn one…", extra=[Rotate(spin, angle=-PI / 2, about_point=C)], run_time=1.1)
        spun_ce = MathTex("x-5", color=BG, font_size=50).move_to(P(10.5, 2.3)).set_z_index(5)
        spun_cd = MathTex("x-9", color=BG, font_size=50).move_to(P(4.9, 6.6)).set_z_index(5)
        self.play(FadeIn(spun_ce), FadeIn(spun_cd), run_time=0.3)
        self.wait(0.4)

        # Scale up about C: the copy lands exactly on the brown triangle (checked in verify.py).
        k = float(similarity_scale(g))
        self.add_sound(SFX["pop"], time_offset=0.8)
        cap.show("…and scale it up", extra=[spin.animate.scale(k, about_point=C),
                                            FadeOut(spun_ce), FadeOut(spun_cd)], run_time=0.9)
        assert np.allclose(spin.get_vertices()[0], A) and np.allclose(spin.get_vertices()[2], E)
        self.wait(0.3)
        cap.show("Same shape, same ratio", extra=[FadeOut(spin)])
        self.wait(0.7)

        # --- the algebra, in the caption slot ------------------------------------
        same = MathTex(r"\frac{x}{x-5}", "=", r"\frac{x-5}{x-9}", color=INK, font_size=64)
        same[0].set_color(PIECES[0]); same[2].set_color(PIECES[1])
        cap.show(same)
        self.wait(1.3)
        cross = MathTex(r"(x-5)^2 = x(x-9)", color=INK, font_size=64)
        cap.show(cross)
        self.wait(0.8)
        expanded = MathTex("x^2", "-10x+25", "=", "x^2", "-9x", color=INK, font_size=64)
        cap.show(expanded)
        strikes = VGroup(*[Line(expanded[i].get_corner(DOWN + np.array([-1, 0, 0])),
                                expanded[i].get_corner(UP + np.array([1, 0, 0])),
                                color=ACCENT, stroke_width=6) for i in (0, 3)])
        self.add_sound(SFX["snip"])
        self.play(Create(strikes), run_time=0.4)
        self.wait(0.5)
        self.remove(strikes)
        answer = MathTex("x = 25", color=GOOD, font_size=80)
        self.add_sound(SFX["pop"])
        cap.show(answer)
        self.wait(0.6)

        # --- payoff --------------------------------------------------------------
        beat(self, "payoff")
        self.play(*[FadeOut(m) for m in (
            right_tri, left_tri, hyp, x_lbl, cd_lbl, ce_lbl, ac_line, cd_line, ce_line,
            gap_bar, gap_lbl, tick, up, wide_bar, wide_lbl, across, centre)], run_time=0.4)
        d_small = Line(D, A, color=GOOD, stroke_width=8).set_z_index(3)
        lbl_small = MathTex("41", color=GOOD, font_size=64).move_to((D + A) / 2 + 0.42 * UP).set_z_index(5)
        dim_big = dimension(B[0], A[0], STAGE_Y - 3.3 - 0.34, "50", GOOD)
        self.add_sound(SFX["chime"])
        cap.show("Diameters: 50 and 41 ✓", GOOD,
                 extra=[Create(d_small), Write(lbl_small), FadeIn(dim_big)])
        self.play(big.animate.set_stroke(GOOD), small.animate.set_stroke(GOOD), run_time=0.7)
        self.wait(1.0)

        # --- Level 2: the same figure, run backwards ------------------------------
        beat(self, "Level 2")
        solved = VGroup(big, small, d_small)
        recap = label("50 and 41", 40, GOOD).move_to([CENTRE_X - 2.35, 4.72, 0])
        cap.clear()
        self.play(FadeOut(title), FadeOut(credit), FadeOut(lbl_small), FadeOut(dim_big), run_time=0.3)
        self.play(solved.animate.scale(0.3).move_to([CENTRE_X - 2.35, 6.0, 0]), run_time=0.7)
        tag = badge("LEVEL 2").move_to([CENTRE_X + 1.25, 6.45, 0])
        q = VGroup(label("How big is", 56), label("the gap?", 56)).arrange(DOWN, buff=0.18)
        q.move_to([CENTRE_X + 1.25, 5.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(q), FadeIn(recap), run_time=0.6)

        h = crescent(solve_radius(L2_WIDE, 4), L2_WIDE)
        s2 = 2.75 / float(h["R"])
        o2 = np.array([CENTRE_X, 0.75, 0.0])
        Q = lambda k: P(h[k], scale=s2, origin=o2)  # noqa: E731
        big2, small2 = circles(h, s2, o2)
        self.play(Create(big2), Create(small2), run_time=0.8)
        self.play(big2.animate.set_fill(GRID, 1), small2.animate.set_fill(BG, 1), run_time=0.25)
        dim2 = dimension(Q("B")[0], Q("A")[0], o2[1] - 2.75 - 0.34, str(L2_DIAMETER), INK)
        bar2 = Line(Q("B"), Q("D"), color=ACCENT, stroke_width=10)
        lbl2 = MathTex(str(L2_WIDE), color=ACCENT, font_size=60).move_to(
            (Q("B") + Q("D")) / 2 + 0.36 * UP)
        up2 = Line(Q("C"), Q("E"), color=MUTED, stroke_width=3)
        gap2 = Line(Q("E"), Q("F"), color=ACCENT, stroke_width=10)
        ask = MathTex("?", color=ACCENT, font_size=72).next_to(gap2, direction=[1, 0, 0], buff=0.16)
        dot2 = Dot(Q("C"), color=INK, radius=0.09)
        self.play(FadeIn(dim2), Create(bar2), Write(lbl2), run_time=0.5)
        self.play(FadeIn(dot2), Create(up2), Create(gap2), Write(ask), run_time=0.5)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.25), run_time=1.0, rate_func=there_and_back)
            self.wait(1.8)
