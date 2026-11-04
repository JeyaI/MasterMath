"""Short 0008 - The Six Frogs (Dudeney no. 214).

Level 1 (shown on screen): 4 frogs on 5 squares must reverse to 4 3 2 1 in 10 moves, the fewest possible.
Hook, a demo slide and leap, a 5 s pause, then Dudeney's order (2 4 3 1, 2 4 3 1, 2 4) plays move by move:
slides hop along the row, leaps arc over a neighbour, a counter ticks and a strip of chips tracks the order.
Level 2 (comment challenge): 6 frogs, 21 moves; how many are leaps? (15)

The start/goal boards, the recipe, the boards after each move and the leap flags all come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, PI, UP, ArcBetweenPoints, Circle, FadeIn, FadeOut, GrowFromCenter, Indicate, LaggedStart,
    ManimColor, MoveAlongPath, RoundedRectangle, Scene, Text, VGroup, there_and_back, Transform, Arrow,
)
import numpy as np  # noqa: E402

from manim import BOLD  # noqa: E402
from lib.layout import ACCENT, BG, FONT, GOOD, INK, MUTED, PIECES  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    BOARDS, L2_LEAPS, L2_MOVES, L2_N, LEAPS, MOVES, N, RECIPE, goal, start,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
SQ = 1.3                      # square pitch, level 1
ROW_Y = 1.7
EVEN, ODD = PIECES[0], PIECES[1]
SQUARE_FILL = ManimColor("#1B2735")
assert (N, MOVES, len(RECIPE), len(BOARDS), sum(LEAPS)) == (4, 10, 10, 11, 6)


def frog_color(k: int):
    return EVEN if k % 2 == 0 else ODD


def sq_pos(i: int, y: float, pitch: float = SQ, n: int = N) -> np.ndarray:
    return np.array([CENTRE_X + (i - n / 2) * pitch, y, 0.0])


def squares(n: int, y: float, pitch: float, fill=SQUARE_FILL, stroke=MUTED) -> VGroup:
    return VGroup(*[RoundedRectangle(corner_radius=0.12, width=pitch * 0.92, height=pitch * 0.92,
                                     fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=4)
                    .move_to(sq_pos(i, y, pitch, n)) for i in range(n + 1)])


def frog(k: int, r: float, opacity: float = 1.0) -> VGroup:
    body = Circle(radius=r, fill_color=frog_color(k), fill_opacity=opacity, stroke_color=BG, stroke_width=3)
    num = Text(str(k), font=FONT, weight=BOLD, font_size=int(r * 110), color=BG)
    num.move_to(body)
    if opacity < 1:
        num.set_opacity(opacity + 0.15)
    return VGroup(body, num).set_z_index(5)


def place(board, y: float, r: float, pitch: float, n: int, opacity: float = 1.0) -> dict:
    return {k: frog(k, r, opacity).move_to(sq_pos(i, y, pitch, n)) for i, k in enumerate(board) if k}


def hop(f: VGroup, dest: np.ndarray, leap: bool, height: float = 2.6):
    if not leap:
        return f.animate.move_to(dest)
    sign = 1 if dest[0] > f.get_center()[0] else -1
    return MoveAlongPath(f, ArcBetweenPoints(f.get_center(), dest, angle=-sign * height))


class Short(Scene):
    def counter(self, text: str, color=INK):
        """Move counter. A hard cut: a cross-fade smears the digits."""
        if getattr(self, "_ctr", None) is not None:
            self.remove(self._ctr)
        self._ctr = label(text, 76, color).move_to([CENTRE_X, 4.3, 0])
        self.add(self._ctr)

    def construct(self):
        cap = Captions(self)
        board = squares(N, ROW_Y, SQ)
        frogs = place(start(N), ROW_Y, 0.5, SQ, N)
        group = VGroup(*frogs.values())

        # --- hook: pop in the row, then the question ------------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in board], lag_ratio=0.1), run_time=0.6)
        self.remove(*board)
        self.add(board)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(f) for f in group], lag_ratio=0.15), run_time=0.7)
        self.remove(*group)
        self.add(group)
        title = hook("Reverse these frogs", "Can you do it in 10 moves?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        cap.show("4 frogs, 1 empty square")
        self.wait(1.4)

        # --- the goal -------------------------------------------------------------------------
        gy = -0.35
        gboard = squares(N, gy, 0.95, fill=BG, stroke=MUTED)
        gfrogs = VGroup(*place(goal(N), gy, 0.36, 0.95, N, 0.55).values())
        glabel = label("Goal: reverse the order", 44, MUTED).move_to([CENTRE_X, gy + 1.0, 0])
        cap.show("Reverse them in 10 moves?", extra=[FadeIn(gboard), FadeIn(gfrogs), FadeIn(glabel)])
        self.wait(2.0)

        # --- the rules: one slide, one leap ----------------------------------------------------
        cap.show("Slide or leap one frog")
        tag = label("Slide: next square", 54, GOOD).move_to([CENTRE_X, 3.3, 0])
        self.play(FadeIn(tag), run_time=0.25)
        self.add_sound(SFX["tick"])
        self.play(hop(frogs[1], sq_pos(0, ROW_Y), False), run_time=0.6)
        self.wait(0.4)
        self.play(hop(frogs[1], sq_pos(1, ROW_Y), False), run_time=0.5)
        tag2 = label("Leap: over one frog", 54, ACCENT).move_to([CENTRE_X, 3.3, 0])
        self.play(Transform(tag, tag2), run_time=0.3)
        self.add_sound(SFX["pop"])
        self.play(hop(frogs[2], sq_pos(0, ROW_Y), True), run_time=0.8)
        self.wait(0.4)
        self.play(hop(frogs[2], sq_pos(2, ROW_Y), True), run_time=0.8)
        self.play(FadeOut(tag), run_time=0.25)
        self.wait(0.3)

        # --- pause and try ------------------------------------------------------------------------
        cap.show("Pause and try it", ACCENT, extra=[FadeOut(gboard), FadeOut(gfrogs), FadeOut(glabel)])
        countdown(self, 5, center=[CENTRE_X, -0.2, 0], radius=0.95, tick_sound=SFX["tick"])

        # --- the solution ---------------------------------------------------------------------------
        chips = VGroup(*[
            VGroup(RoundedRectangle(corner_radius=0.1, width=0.58, height=0.7, fill_color=SQUARE_FILL,
                                    fill_opacity=1, stroke_color=frog_color(k), stroke_width=4),
                   label(str(k), 40, frog_color(k))).arrange(DOWN, buff=0)
            for k in RECIPE])
        for c in chips:
            c[1].move_to(c[0])
        chips.arrange(buff=0.12).move_to([CENTRE_X, -1.5, 0])
        chips_lab = label("Order of moves", 40, MUTED).move_to([CENTRE_X, -0.7, 0])

        cap.show("Here is one way", extra=[FadeOut(title), FadeIn(chips), FadeIn(chips_lab)])
        self.counter("Move 0 of 10", MUTED)
        self.wait(0.8)

        for k, f in enumerate(RECIPE, start=1):
            if k == 1:
                cap.show("Evens go up, odds come back")
            if k == 9:
                cap.show("Last two: 2, then 4")
            leap = LEAPS[k - 1]
            before, after = BOARDS[k - 1], BOARDS[k]
            dest = sq_pos(after.index(f), ROW_Y)
            self.add_sound(SFX["pop"] if leap else SFX["tick"], gain=-3)
            self.counter(f"Move {k}: {'leap' if leap else 'slide'}", ACCENT if leap else GOOD)
            chip = chips[k - 1]
            self.play(hop(frogs[f], dest, leap), chip[0].animate.set_fill(frog_color(f), 1),
                      chip[1].animate.set_color(BG), run_time=0.85 if leap else 0.55)
            self.wait(0.15)
            if k % 4 == 0 and k < MOVES:
                self.wait(0.2)

        # --- payoff -------------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        self.counter("10 moves ✓", GOOD)
        cap.show("10 moves. Fewest possible ✓", GOOD)
        self.play(*[Indicate(f, color=GOOD, scale_factor=1.25) for f in frogs.values()], run_time=1.0)
        self.wait(1.6)

        # --- Level 2: six frogs ---------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.25)
        self.clear()

        tagl = badge("LEVEL 2").move_to([CENTRE_X, 6.55, 0])
        q = VGroup(*[label(t, 46) for t in (f"{L2_N} frogs, {L2_MOVES} moves.", "How many of the moves",
                                           "are leaps?")])
        q.arrange(DOWN, buff=0.18).move_to([CENTRE_X, 4.9, 0])
        p2 = 0.92
        b6 = squares(L2_N, 2.4, p2)
        f6 = VGroup(*place(start(L2_N), 2.4, 0.37, p2, L2_N).values())
        g6 = squares(L2_N, -0.4, p2, fill=BG)
        gf6 = VGroup(*place(goal(L2_N), -0.4, 0.37, p2, L2_N, 0.8).values())
        arrow = Arrow([CENTRE_X, 1.4, 0], [CENTRE_X, 0.6, 0], color=ACCENT, buff=0, stroke_width=10)
        alab = label(f"{L2_MOVES} moves", 44, ACCENT).move_to([CENTRE_X + 1.9, 1.0, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tagl), FadeIn(q), FadeIn(b6), FadeIn(f6), run_time=0.7)
        self.play(FadeIn(g6), FadeIn(gf6), FadeIn(arrow), FadeIn(alab), run_time=0.6)
        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(alab, color=INK, scale_factor=1.25), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
