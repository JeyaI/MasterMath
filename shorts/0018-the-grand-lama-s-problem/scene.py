"""Short 0018 - The Grand Lama's Problem (Dudeney no. 291).

Level 1 (solved on screen): four quarters and straight strips fail (the gems crowd the corner), so one long
hook is drawn around the first gem; a ghost copy of it turns a quarter turn at a time and lands exactly on
each of the other three pieces. Four identical 16-square hooks, one gem each.
Level 2 (comment challenge): a 12 x 12 board cut into 9 equal parts -> 16 squares each.

Shapes and numbers come from verify.py (PIECES, GEMS, MAPS, N, L2_*), so what you see was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, PI, Circle, RIGHT, UP, Create, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    Polygon, Rotate, Scene, Square as Cell, VGroup, there_and_back, BOLD,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import GEMS, L2_EACH, L2_PIECES, L2_SIZE, MAPS, N, PIECES as CUTS  # noqa: E402

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
CELL = 0.85
GX, GY = CENTRE_X, STAGE_Y + 0.3
RED = "#FF4D4D"
assert N == 8 and MAPS == ["same", "turn 90", "turn 180", "turn 270"] and (L2_SIZE, L2_PIECES, L2_EACH) == (12, 9, 16)
TURNS = [0, 1, 2, 3]                     # quarter turns, clockwise on screen (verify.py's "turn 90" etc.)


def at(r: int, c: int, cell: float = CELL, gx: float = GX, gy: float = GY, n: int = N):
    """Centre of the square in row r (0 = top), column c."""
    return np.array([gx + cell * (c - (n - 1) / 2), gy - cell * (r - (n - 1) / 2), 0.0])


def sq(r, c, color, opacity=1.0, stroke=BG, sw=2.5, cell=CELL) -> Cell:
    return Cell(side_length=cell, stroke_color=stroke, stroke_width=sw, fill_color=color,
                fill_opacity=opacity).move_to(at(r, c, cell))


def piece_group(cells, color, opacity=1.0) -> VGroup:
    return VGroup(*[sq(r, c, color, opacity) for r, c in sorted(cells)])


def gem(r, c) -> Polygon:
    d = CELL * 0.3
    p = at(r, c)
    return Polygon(p + [0, d, 0], p + [d, 0, 0], p + [0, -d, 0], p + [-d, 0, 0], fill_color="#FFFFFF",
                   fill_opacity=1, stroke_color=ACCENT, stroke_width=5).set_z_index(10)


def grid_line(a, b, color=ACCENT, w=10):
    """Line between lattice points (row, col) of the board's corners, (0,0) = top-left corner."""
    def pt(rc):
        return at(0, 0) + np.array([-CELL / 2 + CELL * rc[1], CELL / 2 - CELL * rc[0], 0.0])
    return Line(pt(a), pt(b), color=color, stroke_width=w).set_z_index(8)


def counter(text: str, color=ACCENT) -> VGroup:
    return label(text, 84, color, BOLD).move_to([CENTRE_X, TITLE_Y, 0])


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        base = VGroup(*[sq(r, c, GRID) for r in range(N) for c in range(N)])
        rim = Cell(side_length=CELL * N, color=MUTED, stroke_width=4).move_to([GX, GY, 0]).set_z_index(6)
        gems = [gem(r, c) for r, c in GEMS]

        # --- hook ---------------------------------------------------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(c) for c in base], lag_ratio=0.008), FadeIn(rim), run_time=1.0)
        self.remove(*base)
        self.add(base)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(g) for g in gems], lag_ratio=0.15), run_time=0.7)
        title = hook("The Grand Lama's Problem")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        cap.show("Can you cut this board into four identical parts, one gem in each?")
        self.wait(2.0)

        # --- the rules ----------------------------------------------------------------------------
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("A Grand Lama has a golden chessboard with four gems.", extra=[
            FadeOut(title), *[Flash(g, color=ACCENT, flash_radius=0.7, line_length=0.25) for g in gems]],
            run_time=0.8)
        self.wait(1.8)

        diag = grid_line((0, 0), (4, 4), INK, 7)
        cap.show("The gems sit in a row along the diagonal.", extra=[Create(diag)], run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(diag), run_time=0.3)

        sketch = VGroup(grid_line((0, 3), (8, 3), ACCENT, 8), grid_line((5, 3), (5, 8), ACCENT, 8),
                        grid_line((2, 0), (2, 3), ACCENT, 8))
        self.add_sound(SFX["snip"])
        cap.show("Cut along the lines into four parts of the same size and shape.", extra=[
            LaggedStart(*[Create(s) for s in sketch], lag_ratio=0.4)], run_time=1.4)
        self.wait(2.0)
        cap.show("Every part must hold exactly one gem.", extra=[FadeOut(sketch)], run_time=0.5)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(*[Indicate(g, color=ACCENT, scale_factor=1.5) for g in gems], run_time=0.9)
        self.wait(1.4)

        # --- a failed attempt, shown before the audience tries ------------------------------------
        quarter = VGroup(*[sq(r, c, PIECES[0], 0.45) for r in range(4) for c in range(4)]).set_z_index(3)
        cross = VGroup(grid_line((0, 4), (8, 4), INK, 9), grid_line((4, 0), (4, 8), INK, 9))
        self.add_sound(SFX["snip"])
        cap.show("Let me try the obvious cut: four equal quarters.", extra=[Create(cross)], run_time=1.2)
        self.wait(1.8)
        cap.show("That fails, because one quarter holds every gem.")
        self.add_sound(SFX["pop"], gain=-4)
        self.play(FadeIn(quarter), *[Indicate(g, color=RED, scale_factor=1.6) for g in gems], run_time=0.9)
        self.wait(1.8)
        self.play(FadeOut(cross), FadeOut(quarter), run_time=0.4)

        # --- pause and try ------------------------------------------------------------------------
        disc = Circle(radius=1.3, stroke_width=0, fill_color=BG, fill_opacity=0.95).move_to([GX, GY, 0])
        disc.set_z_index(12)
        cap.show("Pause and try it.", ACCENT, extra=[FadeIn(disc)])
        countdown(self, 5, center=[GX, GY, 0], radius=1.0, tick_sound=SFX["tick"], z_index=13)
        self.play(FadeOut(disc), run_time=0.3)

        # --- obvious cuts fail ---------------------------------------------------------------------
        strips = VGroup(*[grid_line((k, 0), (k, 8), INK, 9) for k in (2, 4, 6)])
        redo = VGroup(*[sq(r, c, RED, 0.4) for r in range(4) for c in range(N)]).set_z_index(3)
        self.add_sound(SFX["snip"])
        cap.show("Straight strips fail as well, so the parts must bend.", extra=[Create(strips)], run_time=0.9)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(FadeIn(redo), *[Indicate(g, color=RED, scale_factor=1.6) for g in gems[:2]], run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(strips), FadeOut(redo), run_time=0.4)

        # --- the hook ------------------------------------------------------------------------------
        first = piece_group(CUTS[0], PIECES[0]).set_z_index(2)
        cnt = counter("16 squares")
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("Start with a long hook that wraps around the first gem.", extra=[
            LaggedStart(*[GrowFromCenter(s) for s in first], lag_ratio=0.05), FadeIn(cnt, shift=0.3 * DOWN)],
            run_time=1.5)
        self.remove(*first)
        self.add(first)
        self.wait(0.6)

        # --- the ghost turns and lands on each of the other pieces -----------------------------------
        done = [first]
        for k in (1, 2, 3):
            target = piece_group(CUTS[k], PIECES[k]).set_z_index(2)
            ghost = piece_group(CUTS[0], INK, 0.85).set_z_index(9)
            for s in ghost:
                s.set_stroke(ACCENT, 3)
            if k == 1:
                text = "Turn the hook a quarter turn, and it fits around the next gem."
                self.add_sound(SFX["pop"], gain=-4)
                cap.show(text, extra=[FadeIn(ghost)], run_time=0.5)
            elif k == 2:
                self.add_sound(SFX["pop"], gain=-4)
                cap.show("Turn it again and again, until the board is full.", extra=[FadeIn(ghost)], run_time=0.5)
            else:
                self.play(FadeIn(ghost), run_time=0.3)
            self.play(ghost.animate.scale(0.7), run_time=0.25)      # shrink so the turn stays on screen
            self.play(Rotate(ghost, -k * PI / 2, about_point=ghost.get_center()), run_time=0.8 if k == 1 else 0.6)
            dest = np.array([(min(s.get_center()[0] for s in target) + max(s.get_center()[0] for s in target)) / 2,
                             (min(s.get_center()[1] for s in target) + max(s.get_center()[1] for s in target)) / 2, 0])
            here = np.array([(min(s.get_center()[0] for s in ghost) + max(s.get_center()[0] for s in ghost)) / 2,
                             (min(s.get_center()[1] for s in ghost) + max(s.get_center()[1] for s in ghost)) / 2, 0])
            self.play(ghost.animate.scale(1 / 0.7).shift(dest - here), run_time=0.8 if k == 1 else 0.6)
            self.add_sound(SFX["pop"], gain=-2)
            self.add(target)
            self.remove(ghost)
            self.play(FadeOut(ghost), run_time=0.15)
            done.append(target)
            self.wait(0.3)

        # --- payoff ---------------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        cap.show("Four identical hooks of 16 squares, one gem each ✓", GOOD, extra=[
            cnt.animate.set_color(GOOD), Flash(np.array([GX, GY, 0]), color=GOOD, flash_radius=3.2)])
        self.play(*[Indicate(d, color=INK, scale_factor=1.03) for d in done], run_time=1.2)
        self.wait(0.6)

        # --- Level 2 ----------------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()

        c2, y2 = 0.52, 1.6
        base2 = VGroup(*[Cell(side_length=c2, stroke_color=BG, stroke_width=2, fill_color=GRID, fill_opacity=1)
                         .move_to(at(r, c, c2, CENTRE_X, y2, L2_SIZE)) for r in range(L2_SIZE) for c in range(L2_SIZE)])
        rim2 = Cell(side_length=c2 * L2_SIZE, color=MUTED, stroke_width=4).move_to([CENTRE_X, y2, 0])
        ask = label("? squares each", 76, ACCENT).move_to([CENTRE_X, y2 - c2 * L2_SIZE / 2 - 0.75, 0])
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.6, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), run_time=0.4)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in base2], lag_ratio=0.005), FadeIn(rim2), run_time=1.0)
        cap.show("Level 2: a 12 by 12 board is cut into 9 equal parts.", extra=[FadeIn(label("9 equal parts", 60, INK)
                 .move_to([CENTRE_X, 5.4, 0]), shift=0.2 * DOWN)])
        self.wait(1.5)
        cap.show("How many squares does each part hold?", extra=[FadeIn(ask, shift=0.2 * UP)])
        self.wait(1.2)
        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.12), run_time=1.0, rate_func=there_and_back)
            self.wait(1.55)
