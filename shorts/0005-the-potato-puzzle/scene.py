"""Short 0005 - The Potato Puzzle (Dudeney no. 164).

Level 1 (solved on screen): a cut gains one piece per piece it runs through. A grid wastes its parallel
cuts and stops at 16. Rebuilt so each cut crosses every earlier one, the cuts add 1, 2, ..., 6: 22 pieces.
Level 2 (comment challenge): 10 cuts -> 56.

The cuts and every piece come from verify.py, so what you see is exactly what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line, ManimColor,
    Polygon, RoundedRectangle, Scene, VGroup, linear, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, INK, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import DISC, GRID_STEPS, GRID_PIECES, L2_CUTS, L2_PIECES, MAX_PIECES, STEPS, coords, ends  # noqa: E402

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
RADIUS = 3.0
POTATO = ManimColor("#EFD9A0")
SKIN = ManimColor("#A9743F")
NEW = PIECES[0]
LIVE = BG
assert (GRID_PIECES, MAX_PIECES, L2_PIECES) == (16, 22, 56)


def stage(radius: float = RADIUS, x: float = CENTRE_X, y: float = STAGE_Y):
    """A function from a point of the unit disc to its point in the frame."""
    return lambda p: np.array([x + radius * p[0], y + radius * p[1], 0.0])


def piece(face, S, color=POTATO, stroke: float = 5) -> Polygon:
    return Polygon(*[S(p) for p in coords(face)], fill_color=color, fill_opacity=1,
                   stroke_color=BG, stroke_width=stroke).set_z_index(1)


def skin(radius: float = RADIUS, x: float = CENTRE_X, y: float = STAGE_Y, width: float = 13) -> Circle:
    return Circle(radius=radius, stroke_color=SKIN, stroke_width=width).move_to([x, y, 0]).set_z_index(3)


def knife() -> VGroup:
    """A kitchen knife pointing along +x, with its tip at the origin."""
    blade = Polygon([0, 0, 0], [-1.25, 0.26, 0], [-1.25, -0.07, 0], fill_color=INK, fill_opacity=1,
                    stroke_color=BG, stroke_width=2)
    handle = RoundedRectangle(corner_radius=0.06, width=0.7, height=0.21, fill_color=SKIN, fill_opacity=1,
                              stroke_color=BG, stroke_width=2).move_to([-1.57, 0.08, 0])
    return VGroup(blade, handle).set_z_index(8)


class Short(Scene):
    def count(self, n: int, color=INK):
        """Show the running total. A hard cut: a cross-fade smears the digits."""
        if getattr(self, "_count", None) is not None:
            self.remove(self._count)
        self._count = label(f"{n} piece{'s' if n != 1 else ''}", 84, color).move_to([CENTRE_X, TITLE_Y, 0])
        self.add(self._count)

    def slice(self, step, pieces: list, total: int, S, pace: float, dots: bool = True) -> int:
        """One cut, stretch by stretch: each stretch splits one piece and the total ticks up."""
        a, b = np.array(step.points[0]), np.array(step.points[-1])
        heading = np.arctan2(*(b - a)[::-1])
        blade = knife().rotate(heading, about_point=np.zeros(3)).shift(S(step.points[0]))
        self.play(FadeIn(blade), run_time=0.08)
        lines, marks = [], []
        for (p, q), (i, one, two) in zip(zip(step.points, step.points[1:]), step.splits):
            line = Line(S(p), S(q), color=LIVE, stroke_width=7).set_z_index(6)
            lines.append(line)
            self.play(Create(line), blade.animate.shift(S(q) - S(p)), run_time=pace, rate_func=linear)
            self.add_sound(SFX["pop"], gain=-3)
            self.remove(pieces[i])
            pieces[i] = piece(one, S)
            fresh = piece(two, S, NEW)
            pieces.append(fresh)
            self.add(pieces[i], fresh)
            total += 1
            self.count(total)
            if dots and q != step.points[-1]:
                dot = Dot(S(q), radius=0.14, color=PIECES[1]).set_z_index(7)
                marks.append(dot)
                self.add(dot)
        self.play(FadeOut(blade), *[FadeOut(m) for m in (*lines, *marks)],
                  *[p.animate.set_fill(POTATO) for p in pieces[-len(step.splits):]], run_time=0.18)
        return total

    def construct(self):
        cap = Captions(self)
        S = stage()
        whole = Circle(radius=RADIUS, fill_color=POTATO, fill_opacity=1, stroke_width=0).move_to(S((0, 0))).set_z_index(1)
        rim = skin()

        # --- hook: the slice, then the question --------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(whole), GrowFromCenter(rim), run_time=0.5)
        title = hook("What's the most pieces", "with 6 straight cuts?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        self.wait(1.6)

        # --- the rules ---------------------------------------------------------------
        cap.show("Straight cuts only")
        self.wait(0.65)
        cap.show("No moving the pieces")
        self.wait(0.65)

        # --- the 16 to beat, before the pause -----------------------------------------
        self.play(FadeOut(title), run_time=0.2)
        self.remove(whole)
        pieces = [piece(DISC, S, stroke=0)]
        self.add(pieces[0])
        self.count(1)
        total = 1
        cap.show("Three cuts one way", run_time=0.3)
        for step in GRID_STEPS[:3]:
            total = self.slice(step, pieces, total, S, 0.24, dots=False)
        cap.show("Three cuts the other way", run_time=0.3)
        for step in GRID_STEPS[3:]:
            total = self.slice(step, pieces, total, S, 0.09, dots=False)
        self.add_sound(SFX["chime"], gain=-10)
        cap.show("16 pieces. Can you beat it?", ACCENT)
        self.wait(1.0)

        # --- pause and try --------------------------------------------------------------
        grid = VGroup(*pieces)
        grid.set_z_index(-2)                            # under the countdown, which sits at z 0
        plate = Circle(radius=1.1, fill_color=BG, fill_opacity=1, stroke_width=0).move_to(S((0, 0))).set_z_index(-1)
        self.play(grid.animate.set_fill(opacity=0.25), FadeIn(plate), run_time=0.25)
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X, STAGE_Y, 0], radius=0.95, tick_sound=SFX["tick"])
        self.play(grid.animate.set_fill(opacity=1), FadeOut(plate), run_time=0.25)
        grid.set_z_index(1)

        # --- why the grid stops: parallel cuts ---------------------------------------------
        par = VGroup(*[Line(*(S(p) for p in ends(s.cut)), color=PIECES[1], stroke_width=9).set_z_index(6)
                       for s in GRID_STEPS[:3]])
        self.add_sound(SFX["snip"])
        cap.show("Parallel cuts never cross", extra=[Create(par)])
        self.wait(0.8)

        # --- start again: every cut crosses every earlier cut ---------------------------------
        fresh = piece(DISC, S, stroke=0)
        cap.show("So cross every cut", extra=[FadeOut(par), FadeOut(grid), FadeIn(fresh)])
        self.count(1)
        self.wait(0.35)
        pieces, total = [fresh], 1
        texts = ("First cut: 2 pieces", "Cross it: 2 more", "Cross 2 cuts: 3 more",
                 "Cross 3 cuts: 4 more", "Cross 4 cuts: 5 more", "Cross 5 cuts: 6 more")
        for k, (step, text) in enumerate(zip(STEPS, texts)):
            cap.show(text, run_time=0.3)
            total = self.slice(step, pieces, total, S, (0.5, 0.42, 0.36, 0.3, 0.26, 0.24)[k])
            self.wait(0.1)

        # --- payoff --------------------------------------------------------------------------
        cap.show("No cut can cross more", run_time=0.3)
        self.wait(0.8)
        cap.show("1 + 1 + 2 + 3 + 4 + 5 + 6 = 22", ACCENT, run_time=0.3)
        self.wait(1.0)
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        centre = S((0, 0))
        spread = []
        for i, p in enumerate(pieces):
            away = p.get_center() - centre
            spread.append(p.animate.shift(0.13 * away).set_fill(PIECES[i % 4]))
        self.remove(rim)
        cap.show("22 pieces ✓", GOOD, extra=spread, run_time=0.6)
        self.count(22, GOOD)
        self.wait(1.1)

        # --- Level 2: same trick, more cuts ---------------------------------------------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.25)
        self.clear()

        Sm = stage(0.72, CENTRE_X - 2.45, 5.75)
        mini = VGroup(*[piece(f, Sm, stroke=1.5) for f in STEPS[-1].faces], skin(0.72, CENTRE_X - 2.45, 5.75, 4))
        recap = label("22 pieces", 32, GOOD).next_to(mini, DOWN, buff=0.14)
        tag = badge("LEVEL 2").move_to([CENTRE_X + 0.85, 6.55, 0])
        q = VGroup(*[label(t, 34) for t in ("Same potato,", "10 straight cuts.", "How many pieces?")]).arrange(DOWN, buff=0.12)
        q.move_to([CENTRE_X + 0.85, 5.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(FadeIn(mini), FadeIn(recap), GrowFromCenter(tag), FadeIn(q), run_time=0.6)

        S2 = stage(2.75, y=STAGE_Y - 0.1)
        disc2 = piece(DISC, S2, stroke=0)
        rim2 = skin(2.75, y=STAGE_Y - 0.1)
        self.play(GrowFromCenter(disc2), GrowFromCenter(rim2), run_time=0.3)
        cuts = [Line(*(S2(p) for p in ends(c)), color=BG, stroke_width=4).set_z_index(2) for c in L2_CUTS]
        self.add_sound(SFX["snip"])
        self.play(LaggedStart(*[Create(c) for c in cuts], lag_ratio=0.3), run_time=0.8)
        ask = label("?", 110, ACCENT)
        back = Circle(radius=0.62, fill_color=BG, fill_opacity=1, stroke_width=0)
        mark = VGroup(back, ask.move_to(back)).move_to(S2((0, 0))).set_z_index(5)
        self.play(GrowFromCenter(mark), run_time=0.25)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)

