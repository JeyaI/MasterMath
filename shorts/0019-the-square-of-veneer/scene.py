"""Short 0019 - The Square of Veneer (Dudeney no. 159).

Level 1: re-grid the 5 inch board as 13 x 13 (169 = 144 + 25). The 5 x 5 corner comes out whole; the
L-shape left is cut along grid lines into B, C, D, and C slides, D turns, and they close into 12 x 12.
Cuts sit at multiples of 5/13 inch, so no nail is touched. A second construction uses 17 x 17
(289 = 225 + 64). Level 2: the same cut on a 26 cm square.

Every shape and number comes from verify.py (PIECES, MOVES, C_MOVED, D_MOVED, PIECES2, ...).
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, PI, UP, Create, DashedVMobject, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate,
    LaggedStart, Line, Rectangle, Rotate, Scene, Square, Transform, VGroup, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES as COL, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    A, B, BIG, C, C_MOVED, CELL as CELL_IN, D, D_MOVED, L2_BIG, L2_SIDE, L2_SMALL, N, N2, NAILS, PIECES2,
    P1_MOVED, P2_MOVED, Q1_MOVED, Q2_MOVED, SIDE_IN, SMALL,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}

CELL, GX, GY = 0.44, -0.9, 0.7            # 13 x 13 board
CELL2, GX2, GY2 = 0.32, -0.9, 0.5         # 17 x 17 board
TOP_NUM_Y = 6.5
BLUE, ORANGE, GREEN, PINK = COL[1], COL[0], COL[2], COL[3]
assert (N, N2, BIG, SMALL) == (13, 17, 12, 5) and len(NAILS) == 16 and SIDE_IN == 5


def wrap(text: str) -> str:
    return text if len(text) <= 28 else textwrap.fill(text, width=28 if len(text) <= 56 else 24)


def grid_fn(cell, gx, gy, n):
    h = (n - 1) / 2
    return lambda c, r: np.array([gx + (c - h) * cell, gy + (h - r) * cell, 0.0])


def centre(P, cells):
    return (P(min(c for c, _ in cells), min(r for _, r in cells)) + P(max(c for c, _ in cells), max(r for _, r in cells))) / 2


def piece(P, cell, cells, color, text=None) -> VGroup:
    """A piece = its cell squares plus a thick dark edge wherever a neighbour is not in the piece."""
    sq = VGroup(*[Square(cell, stroke_color=BG, stroke_width=1.2, fill_color=color, fill_opacity=1).move_to(P(c, r))
                  for c, r in sorted(cells)])
    h, edges = cell / 2, []
    for c, r in cells:
        o = P(c, r)
        for dc, dr, a, b in ((1, 0, (1, 1), (1, -1)), (-1, 0, (-1, 1), (-1, -1)),
                             (0, 1, (-1, -1), (1, -1)), (0, -1, (-1, 1), (1, 1))):
            if (c + dc, r + dr) not in cells:
                edges.append(Line(o + h * np.array([*a, 0]), o + h * np.array([*b, 0]), color=BG, stroke_width=5))
    g = VGroup(sq, VGroup(*edges))
    if text:
        g.add(label(text, 44, BG).move_to(centre(P, cells)))
    return g


def cut_lines(P, cell, cells, others) -> VGroup:
    """Highlight edges of `cells` that touch another piece in `others` (a cut), not the outside."""
    h, out = cell / 2, []
    for c, r in cells:
        o = P(c, r)
        for dc, dr, a, b in ((1, 0, (1, 1), (1, -1)), (-1, 0, (-1, 1), (-1, -1)),
                             (0, 1, (-1, -1), (1, -1)), (0, -1, (-1, 1), (1, 1))):
            if (c + dc, r + dr) in others:
                out.append(Line(o + h * np.array([*a, 0]), o + h * np.array([*b, 0]), color=ACCENT, stroke_width=9))
    return VGroup(*out).set_z_index(8)


def nail(pos, color=INK) -> Dot:
    return Dot(pos, radius=0.1, color=color).set_stroke(BG, 2).set_z_index(9)


def counter(text: str, color=ACCENT):
    return label(text, 88, color).move_to([CENTRE_X, TOP_NUM_Y, 0])


class Short(Scene):
    def construct(self):
        cap = Captions(self)

        def say(text, color=INK, **kw):
            return cap.show(wrap(text), color, **kw)

        P = grid_fn(CELL, GX, GY, N)
        W = N * CELL
        # --- the board with 16 nails (5 x 5 inch grid) -----------------------------------------
        board = Rectangle(width=W, height=W, stroke_color=MUTED, stroke_width=4, fill_color=GRID,
                          fill_opacity=1).move_to([GX, GY, 0])
        inch = W / SIDE_IN
        five = VGroup(*[Line([GX - W / 2 + k * inch, GY - W / 2, 0], [GX - W / 2 + k * inch, GY + W / 2, 0],
                             color=MUTED, stroke_width=2) for k in range(1, SIDE_IN)],
                      *[Line([GX - W / 2, GY - W / 2 + k * inch, 0], [GX + W / 2, GY - W / 2 + k * inch, 0],
                             color=MUTED, stroke_width=2) for k in range(1, SIDE_IN)])
        nails = VGroup(*[nail([GX - W / 2 + i * inch, GY - W / 2 + j * inch, 0]) for i, j in NAILS])

        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(board), FadeIn(five), run_time=0.5)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(n) for n in nails], lag_ratio=0.04), run_time=0.7)
        title = label("Can you cut this square\ninto four pieces that\nmake two squares?", 56, INK)
        title.move_to([CENTRE_X, TITLE_Y, 0])
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(1.4)

        # --- rules -------------------------------------------------------------------------------
        say("This 5 inch board has 16 nails, and the saw must not touch any.",
            extra=[FadeOut(title), FadeOut(credit)], run_time=0.5)
        self.play(LaggedStart(*[Indicate(n, color=ACCENT, scale_factor=2.0) for n in nails], lag_ratio=0.07),
                  run_time=1.4)

        big_g = Square(2.2, stroke_color=ACCENT, stroke_width=5).move_to([-1.9, 4.85, 0])
        small_g = Square(2.2 * SMALL / BIG, stroke_color=ACCENT, stroke_width=5).move_to([0.55, 4.85 - 0.6, 0])
        ghost = VGroup(DashedVMobject(big_g, num_dashes=40), DashedVMobject(small_g, num_dashes=20))
        self.add_sound(SFX["pop"])
        say("The four pieces must fit together into two perfect squares.", extra=[FadeIn(ghost, shift=0.2 * UP)])
        self.wait(0.9)
        say("Can you find one way, and give the exact sides of the two squares?", ACCENT)
        self.wait(1.0)

        # --- pause and try ---------------------------------------------------------------------
        disc = Square(2.3, stroke_width=0, fill_color=BG, fill_opacity=0.92).move_to([GX, GY, 0]).set_z_index(10)
        say("Pause and try it.", ACCENT, extra=[FadeIn(disc), FadeOut(ghost)])
        countdown(self, 5, center=[GX, GY, 0], radius=0.95, tick_sound=SFX["tick"])
        self.play(FadeOut(disc), run_time=0.3)

        # --- re-grid as 13 x 13 ----------------------------------------------------------------
        gl = VGroup(*[Line(P(k - 0.5, -0.5), P(k - 0.5, N - 0.5), color=MUTED, stroke_width=1.6) for k in range(1, N)],
                    *[Line(P(-0.5, k - 0.5), P(N - 0.5, k - 0.5), color=MUTED, stroke_width=1.6) for k in range(1, N)])
        self.add_sound(SFX["snip"])
        say("Slice the board into a 13 by 13 grid of small squares.", extra=[
            FadeOut(five), FadeOut(nails),
            LaggedStart(*[Create(g) for g in gl], lag_ratio=0.03)], run_time=1.6)
        self.wait(0.5)

        cnt = counter("169")
        L = B | C | D
        Lp = piece(P, CELL, L, BLUE)
        Ap = piece(P, CELL, A, PINK)
        lab144 = label("144", 72, BG).move_to(P(3, 4))
        lab25 = label("25", 44, BG).move_to(centre(P, A))
        self.add_sound(SFX["pop"])
        say("Notice that 169 is 144 plus 25, which is 12 squared plus 5 squared.", extra=[
            FadeIn(cnt, shift=0.3 * DOWN)], run_time=0.6)
        self.wait(0.4)
        self.add_sound(SFX["chime"], gain=-10)
        self.play(FadeOut(gl), FadeIn(Lp), FadeIn(Ap), FadeIn(lab144), FadeIn(lab25),
                  Transform(cnt, counter("169 = 144 + 25")), run_time=1.0)
        self.wait(0.6)

        # --- cut the 5 x 5 out whole -------------------------------------------------------------
        target = np.array([1.9, 4.85, 0.0])
        lift = target - centre(P, A)
        frame12 = Rectangle(width=BIG * CELL, height=BIG * CELL, stroke_color=ACCENT, stroke_width=5)
        frame12.move_to(centre(P, set((c, r) for c in range(BIG) for r in range(BIG)))).set_z_index(5)
        frame12 = DashedVMobject(frame12, num_dashes=60)
        self.add_sound(SFX["snip"])
        say("Cut out a 5 by 5 square whole; the rest must become 12 by 12.", extra=[
            Ap.animate.shift(lift), lab25.animate.shift(lift), FadeIn(frame12)], run_time=1.1)
        self.wait(0.5)

        # --- cut the L into B, C, D -------------------------------------------------------------
        Bp, Cp, Dp = (piece(P, CELL, B, BLUE), piece(P, CELL, C, BLUE), piece(P, CELL, D, BLUE))
        cuts = VGroup(cut_lines(P, CELL, C, B | D), cut_lines(P, CELL, D, B | C))
        self.remove(Lp)
        self.add(Bp, Cp, Dp)
        self.add_sound(SFX["snip"])
        say("Cut the L into two staircases and one thin strip.", extra=[
            FadeOut(lab144), FadeOut(lab25), Create(cuts),
            Cp[0].animate.set_fill(ORANGE),
            Dp[0].animate.set_fill(GREEN)], run_time=1.2)
        self.wait(0.3)
        self.play(FadeOut(cuts), run_time=0.3)

        # --- slide, turn, close up -----------------------------------------------------------------
        dC = centre(P, C_MOVED) - centre(P, C)
        c_D, t_D = centre(P, D), centre(P, D_MOVED)

        def assemble(t1=0.7, t2=0.4, t3=0.5):
            self.play(Cp.animate.shift(dC), run_time=t1)
            self.play(Rotate(Dp, PI / 2), run_time=t2)
            self.play(Dp.animate.move_to(t_D), run_time=t3)

        def disassemble(t1=0.7, t2=0.35):
            self.play(Dp.animate.move_to(c_D), Cp.animate.shift(-dC), Ap.animate.shift(-lift), run_time=t1)
            self.play(Rotate(Dp, -PI / 2), run_time=t2)

        self.add_sound(SFX["snip"])
        say("Slide the staircase down, stand the strip upright, and it all fits.", extra=[], run_time=0.5)
        assemble()
        self.add_sound(SFX["chime"], gain=-8)
        self.play(FadeOut(frame12), Indicate(VGroup(Bp, Cp, Dp), color=INK, scale_factor=1.03), run_time=0.6)

        # --- the nails are all clear ---------------------------------------------------------------
        nails13 = VGroup(*[nail(P(-0.5 + i * N / SIDE_IN, -0.5 + j * N / SIDE_IN)) for i, j in NAILS])
        self.add_sound(SFX["snip"], gain=-4)
        say("The grid lines are 5/13 inch apart, so no cut ever meets a nail.", extra=[
            Transform(cnt, counter("each cell is 5/13 inch", INK).scale(0.8))], run_time=0.5)
        disassemble()
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(n) for n in nails13], lag_ratio=0.04), run_time=0.7)
        self.play(*[n.animate.set_color(GOOD) for n in nails13], run_time=0.4)
        self.wait(0.2)

        # --- payoff -----------------------------------------------------------------------------------
        big_lab = label("60/13 in", 60, BG).move_to(P(4, 3))
        small_lab = label("25/13 in", 38, BG).move_to(target)
        self.add_sound(SFX["chime"])
        say("So one answer is 25/13 inch and 60/13 inch ✓", GOOD, extra=[
            FadeOut(nails13), Ap.animate.shift(lift)], run_time=0.8)
        assemble(0.6, 0.35, 0.45)
        self.play(FadeIn(big_lab, shift=0.2 * UP), FadeIn(small_lab, shift=0.2 * UP),
                  Flash(centre(P, D_MOVED | C_MOVED), color=GOOD, flash_radius=2.2), run_time=0.6)
        self.wait(1.0)

        # --- a second construction: 17 x 17 ---------------------------------------------------------
        beat(self, "second construction")
        old = [m for m in self.mobjects if m is not cap.current]
        P2 = grid_fn(CELL2, GX2, GY2, N2)
        W2 = N2 * CELL2
        names = {"A": PINK, "B": BLUE, "P1": ORANGE, "P2": ORANGE, "Q1": GREEN, "Q2": GREEN}
        pcs = {k: piece(P2, CELL2, PIECES2[k], names[k]) for k in PIECES2}
        cnt2 = counter("289 = 225 + 64")
        say("Another way: use a 17 by 17 grid, since 289 is 225 plus 64.", extra=[
            *[FadeOut(m) for m in old], *[FadeIn(g) for g in pcs.values()], FadeIn(cnt2, shift=0.3 * DOWN)],
            run_time=0.9)
        self.remove(*old)
        nails17 = VGroup(*[nail(P2(-0.5 + i * N2 / SIDE_IN, -0.5 + j * N2 / SIDE_IN), GOOD) for i, j in NAILS])
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(n) for n in nails17], lag_ratio=0.04), run_time=0.7)
        self.wait(0.2)
        target2 = np.array([1.75, 4.68, 0.0])
        lift2 = target2 - centre(P2, PIECES2["A"])
        self.add_sound(SFX["snip"])
        self.play(FadeOut(nails17), pcs["A"].animate.shift(lift2), run_time=0.8)

        moved = {"P1": P1_MOVED, "P2": P2_MOVED, "Q1": Q1_MOVED, "Q2": Q2_MOVED}
        self.add_sound(SFX["snip"])
        say("Stack the cut strips into a 15 by 15 square: 40/17 and 75/17 ✓", GOOD, run_time=0.5)
        self.play(*[pcs[k].animate.shift(centre(P2, moved[k]) - centre(P2, PIECES2[k])) for k in ("P1", "P2")],
                  run_time=0.8)
        self.play(Rotate(pcs["Q1"], PI / 2), Rotate(pcs["Q2"], PI / 2), run_time=0.4)
        self.play(*[pcs[k].animate.move_to(centre(P2, moved[k])) for k in ("Q1", "Q2")], run_time=0.7)
        sq15 = set((c, r) for c in range(15) for r in range(15))
        l2big = label("75/17 in", 60, BG).move_to(centre(P2, sq15) + [-0.5, 0.8, 0])
        l2small = label("40/17 in", 36, BG).move_to(target2)
        self.play(FadeIn(l2big, shift=0.2 * UP), FadeIn(l2small, shift=0.2 * UP),
                  Flash(centre(P2, sq15), color=GOOD, flash_radius=2.0), run_time=0.6)
        self.wait(1.0)

        # --- Level 2 -------------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()
        c3 = 5.8 / N
        P3 = grid_fn(c3, CENTRE_X, 1.3, N)
        base3 = VGroup(*[Square(c3, stroke_color=MUTED, stroke_width=1.4, fill_color=GRID, fill_opacity=1).move_to(P3(c, r))
                         for c in range(N) for r in range(N)])
        side = label(f"{L2_SIDE} cm", 80, INK)
        box = Rectangle(width=side.width + 0.7, height=side.height + 0.5, stroke_width=0, fill_color=BG,
                        fill_opacity=0.9).move_to(P3(6, 6))
        side.move_to(box)
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.45, 0])
        ask = label("larger square: ? cm", 56, ACCENT).move_to([CENTRE_X, -2.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), run_time=0.4)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in base3], lag_ratio=0.003), run_time=0.9)
        self.play(FadeIn(box), FadeIn(side), run_time=0.3)
        say(f"Level 2: a {L2_SIDE} cm square is cut the same way.", run_time=0.5)
        self.wait(1.2)
        say("It makes two whole number squares. How long is the larger side, in cm?", run_time=0.5)
        self.wait(2.6)
        say("Comment just the number ↓", ACCENT, extra=[FadeIn(ask, shift=0.2 * UP)])
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.12), run_time=1.0, rate_func=there_and_back)
            self.wait(1.8)
        assert (L2_BIG, L2_SMALL) == (24, 10)
