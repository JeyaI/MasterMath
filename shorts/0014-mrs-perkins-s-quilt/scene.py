"""Short 0014 - Mrs. Perkins's Quilt (Dudeney no. 173).

Level 1 (solved on screen): 169 single patches is the obvious answer; merge them. Big squares whose
sides add up to 13 go along the edges (7 + 6, then 6 above the 7), leaving a 7 x 7 corner minus one
patch (169 - 121 = 48), which eight smaller squares fill. 3 + 8 = 11 squares, and 10 is impossible.
Level 2 (comment challenge): the same quilt, 5 x 5 -> 8.

The squares and numbers come from verify.py (QUILT, SIZES, N, L2_N, ...), so what you see was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    BOLD, DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    Rectangle, Scene, Square as Cell, Transform, VGroup, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import L2_ANSWER, L2_N, MIN_SQUARES, N, QUILT, SIZES  # noqa: E402

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
CELL = 0.52
GX, GY = CENTRE_X, STAGE_Y - 0.2          # grid centre
RED = PIECES[3]
BIG = QUILT[:3]                           # 7, 6, 6
SMALL = QUILT[3:]                         # 4, 3, 3, 2, 2, 2, 1, 1
assert (N, MIN_SQUARES, len(QUILT)) == (13, 11, 11) and tuple(s for _, _, s in BIG) == SIZES[:3] == (7, 6, 6)
assert BIG[0][:2] == (0, 0) and BIG[1][:2] == (7, 0) and BIG[2][:2] == (0, 7)
assert N * N - sum(s * s for _, _, s in BIG) == 48


def stage(cell: float, n: int, x: float, y: float):
    """(column, row) of a patch -> its centre; row 0 is the bottom, as in verify.py."""
    o = np.array([x - cell * (n - 1) / 2, y - cell * (n - 1) / 2, 0.0])
    return lambda c, r: o + cell * np.array([c, r, 0.0])


def patches(P, cell: float, n: int):
    d = {(c, r): Cell(side_length=cell, stroke_color=MUTED, stroke_width=1.6, fill_color=GRID,
                      fill_opacity=1).move_to(P(c, r)) for c in range(n) for r in range(n)}
    return VGroup(*d.values()), d


def piece(P, cell: float, q, color, text: bool = True) -> VGroup:
    x, y, s = q
    box = Cell(side_length=cell * s, stroke_color=BG, stroke_width=5, fill_color=color, fill_opacity=1)
    box.move_to((P(x, y) + P(x + s - 1, y + s - 1)) / 2)
    g = VGroup(box)
    if text:
        g.add(label(str(s), 30 if s == 1 else min(40 + 12 * s, 96), BG, BOLD).move_to(box))
    return g.set_z_index(4)


def counter(n: int, word: str = "pieces") -> VGroup:
    g = VGroup(label(str(n), 110, ACCENT, BOLD), label(word, 52, INK)).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
    return g.move_to([CENTRE_X, 6.15, 0])


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        P = stage(CELL, N, GX, GY)
        base, cells = patches(P, CELL, N)
        rim = Cell(side_length=CELL * N, color=MUTED, stroke_width=4).move_to(base).set_z_index(6)
        hue = [PIECES[1], PIECES[0], PIECES[0]] + [PIECES[2 + i % 2] for i in range(len(SMALL))]
        tiles = [piece(P, CELL, q, hue[i]) for i, q in enumerate(QUILT)]
        eq_y = GY + CELL * N / 2 + 0.85

        # --- hook: the quilt pops in, then the question -------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(c) for c in base], lag_ratio=0.004), FadeIn(rim), run_time=1.0)
        self.remove(*base)
        self.add(base)
        title = VGroup(*[label(t, 56, INK) for t in
                         ("What is the fewest square pieces", "a 13 by 13 quilt", "can be cut into?")]
                       ).arrange(DOWN, buff=0.18).move_to([CENTRE_X, TITLE_Y, 0])
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(2.2)

        # --- the rules ------------------------------------------------------------------------
        cnt = counter(169, "patches")
        self.add_sound(SFX["pop"])
        cap.show("This quilt is sewn from 169 small square patches.", extra=[
            FadeOut(title), FadeIn(cnt, shift=0.3 * DOWN),
            LaggedStart(*[Indicate(c, scale_factor=1.15, color=ACCENT) for c in base], lag_ratio=0.006)],
            run_time=1.4)
        self.wait(1.0)

        cut = Line(P(4, 0) + [-CELL / 2, -CELL / 2, 0], P(4, N - 1) + [-CELL / 2, CELL / 2, 0],
                   color=ACCENT, stroke_width=10).set_z_index(7)
        self.add_sound(SFX["snip"])
        cap.show("You may cut only along the stitches.", extra=[Create(cut)], run_time=0.9)
        self.wait(0.9)

        whole = Cell(side_length=CELL * N, color=RED, stroke_width=12).move_to(base).set_z_index(7)
        tr, br = whole.get_corner(UP + RIGHT), whole.get_corner(DOWN + RIGHT)
        tl, bl = whole.get_corner(UP + LEFT), whole.get_corner(DOWN + LEFT)
        cross = VGroup(Line(tl, br, color=RED, stroke_width=12), Line(bl, tr, color=RED, stroke_width=12)).set_z_index(7)
        self.add_sound(SFX["snip"])
        cap.show("Every piece must be a square, but not the whole quilt.", extra=[FadeOut(cut), Create(whole)],
                 run_time=0.9)
        self.play(Create(cross), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(whole), FadeOut(cross), run_time=0.3)

        cap.show("How few squares can you cut it into?", ACCENT)
        self.wait(1.2)

        # --- pause and try --------------------------------------------------------------------
        pause = label("Pause and try it", 64, ACCENT).move_to([CENTRE_X, TITLE_Y, 0])
        beat(self, "Pause and try it")
        disc = Cell(side_length=2.3, stroke_width=0, fill_color=BG, fill_opacity=0.9).move_to([GX, GY, 0])
        self.play(FadeIn(pause, shift=0.25 * UP), FadeIn(disc), FadeOut(cnt), run_time=0.45)
        countdown(self, 5, center=[GX, GY, 0], radius=0.95, tick_sound=SFX["tick"])
        self.play(FadeOut(disc), FadeOut(pause), FadeIn(cnt), run_time=0.3)

        # --- 169 works, but it is far too many --------------------------------------------------
        shade = [Cell(side_length=CELL, stroke_width=0, fill_color=PIECES[(c + 2 * r) % 4], fill_opacity=0.55)
                 .move_to(P(c, r)).set_z_index(2) for r in range(N) for c in range(N)]
        shade = VGroup(*shade)
        self.add_sound(SFX["pop"])
        cap.show("Using all 169 single patches works, but it's far too many.", extra=[
            LaggedStart(*[FadeIn(s) for s in shade], lag_ratio=0.004), Indicate(cnt[0], color=RED, scale_factor=1.25)],
            run_time=1.5)
        self.wait(1.0)

        # --- big squares along the edges --------------------------------------------------------
        edge = VGroup(Line(P(0, 0) + [-CELL / 2, -CELL / 2, 0], P(N - 1, 0) + [CELL / 2, -CELL / 2, 0]),
                      Line(P(0, 0) + [-CELL / 2, -CELL / 2, 0], P(0, N - 1) + [-CELL / 2, CELL / 2, 0])
                      ).set_color(ACCENT).set_stroke(width=12).set_z_index(7)
        self.add_sound(SFX["snip"])
        cap.show("Let's start with big squares along the edges.", extra=[FadeOut(shade), Create(edge)], run_time=0.8)
        self.wait(0.9)

        eq =label("7 + 6 = 13", 72, ACCENT).move_to([CENTRE_X, eq_y, 0])
        three = Transform(cnt, counter(3, "pieces"))
        self.add_sound(SFX["pop"])
        cap.show("A 7 square and a 6 square together fill one whole side.", extra=[FadeIn(eq, shift=0.2 * UP)])
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(tiles[0]), run_time=0.5)
        self.add_sound(SFX["pop"], time_offset=0.1)
        self.play(GrowFromCenter(tiles[1]), run_time=0.5)
        self.play(Indicate(eq, color=INK, scale_factor=1.2), run_time=0.8)
        self.wait(0.8)

        self.add_sound(SFX["pop"], time_offset=0.3)
        cap.show("A second 6 square fills the other side.", extra=[Indicate(eq, color=INK, scale_factor=1.1)])
        self.play(GrowFromCenter(tiles[2]), three, FadeOut(edge), run_time=0.6)
        self.wait(0.9)

        # --- the gap --------------------------------------------------------------------------
        covered = {(x + i, y + j) for x, y, s in BIG for i in range(s) for j in range(s)}
        gap = VGroup(*[v for k, v in cells.items() if k not in covered])
        assert len(gap) == 48
        eq2 = label("169 − 121 = 48", 72, ACCENT).move_to([CENTRE_X, eq_y, 0])
        self.add_sound(SFX["chime"], gain=-10)
        cap.show("That leaves a 7 by 7 corner with one patch missing.", extra=[
            gap.animate.set_fill(ACCENT, 0.5), Transform(eq, eq2)])
        self.wait(1.8)

        # --- fill it with eight squares -----------------------------------------------------------
        cap.show("We fill that corner with eight more squares, from 4 down to 1.", extra=[FadeOut(eq)])
        for i, t in enumerate(tiles[3:]):
            self.add_sound(SFX["pop"], gain=-4)
            self.play(GrowFromCenter(t), Transform(cnt, counter(4 + i, "pieces")), run_time=0.45)
            self.wait(0.2 if i < 7 else 0.5)

        # --- 11, and nothing smaller -----------------------------------------------------------
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("In the end, we have used 11 squares.", extra=[Indicate(cnt, color=INK, scale_factor=1.15)])
        self.wait(1.0)

        no =VGroup(label("10 or fewer", 64, RED), label("✗", 64, RED)).arrange(RIGHT, buff=0.3)
        no.move_to([CENTRE_X, eq_y, 0])
        self.add_sound(SFX["snip"])
        cap.show("A full search shows that 10 squares are not enough.", extra=[FadeIn(no, shift=0.2 * UP)])
        self.wait(1.8)

        # --- payoff ----------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        cap.show("The fewest is 11 squares ✓", GOOD, extra=[
            FadeOut(no), cnt.animate.set_color(GOOD), Flash(P(6, 6), color=GOOD, flash_radius=2.2)])
        self.wait(1.6)

        # --- Level 2 -----------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()

        c2 = 1.05
        P2 = stage(c2, L2_N, CENTRE_X, STAGE_Y + 0.2)
        base2, _ = patches(P2, c2, L2_N)
        rim2 = Cell(side_length=c2 * L2_N, color=MUTED, stroke_width=4).move_to(base2)
        ask = label("? squares", 84, ACCENT).move_to([CENTRE_X, STAGE_Y + 0.2 - c2 * L2_N / 2 - 0.8, 0])
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.45, 0])
        q = VGroup(*[label(t, 50) for t in ("Same rules on a", "5 by 5 quilt.")]).arrange(DOWN, buff=0.12)
        q.move_to([CENTRE_X, 5.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(q), run_time=0.5)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in base2], lag_ratio=0.02), FadeIn(rim2), run_time=1.0)
        self.play(FadeIn(ask, shift=0.2 * UP), run_time=0.4)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.15), run_time=1.0, rate_func=there_and_back)
            self.wait(1.5)
        assert L2_ANSWER == 8
