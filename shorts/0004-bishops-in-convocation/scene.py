"""Short 0004 - Bishops In Convocation (Dudeney no. 299).

Level 1 (solved on screen): every bishop is on the edge. A diagonal bounced off the edges closes into
a loop holding 2 bishops at opposite corners, so 2 settings. 6 loops and 2 long diagonals share no
line, so the choices multiply: 2^8 = 256.
Level 2 (comment challenge): 10 x 10 with 18 bishops -> 1024.

The board, tracks and placements come from verify.py, so what you see is exactly what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, Circle, Create, Dot, Ellipse, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart,
    Line, MathTex, Polygon, Rectangle, RoundedRectangle, Scene, Square as Cell, Transform, VGroup,
    interpolate_color, linear, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    L2_BISHOPS, L2_N, L2_START, LOOP, MAX_BISHOPS, N, OTHERS, RAY_FROM, START, TRACKS, WAYS,
    placement, seats, sides,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
CELL = 0.84
LIGHT = interpolate_color(GRID, MUTED, 0.4)
HOT = PIECES[0]
DARK_TRACK, LIGHT_TRACK = ACCENT, PIECES[1]
assert (MAX_BISHOPS, WAYS, L2_BISHOPS) == (14, 256, 18)


def stage(cell: float = CELL, n: int = N, x: float = CENTRE_X, y: float = STAGE_Y):
    """A function from a (column, row) square to its point in the frame."""
    origin = np.array([x - cell * (n - 1) / 2, y - cell * (n - 1) / 2, 0.0])
    return lambda s: origin + cell * np.array([s[0], s[1], 0.0])


def board(S, cell: float = CELL, n: int = N) -> tuple[VGroup, dict]:
    squares = {(c, r): Cell(side_length=cell, stroke_width=0, fill_opacity=1,
                            fill_color=GRID if (c + r) % 2 == 0 else LIGHT).move_to(S((c, r)))
               for c in range(n) for r in range(n)}
    return VGroup(*squares.values()), squares


def bishop(cell: float = CELL) -> VGroup:
    """A flat bishop, drawn in a unit box and scaled to the square."""
    ink = dict(fill_color=INK, fill_opacity=1, stroke_color=BG, stroke_width=1.5)
    base = RoundedRectangle(corner_radius=0.05, width=0.72, height=0.14, **ink).move_to([0, -0.4, 0])
    stem = Polygon([-0.24, -0.33, 0], [0.24, -0.33, 0], [0.11, -0.08, 0], [-0.11, -0.08, 0], **ink)
    collar = Rectangle(width=0.4, height=0.07, **ink).move_to([0, -0.1, 0])
    mitre = Ellipse(width=0.46, height=0.56, **ink).move_to([0, 0.17, 0])
    ball = Circle(radius=0.07, **ink).move_to([0, 0.47, 0])
    slit = Line([0.0, 0.14, 0], [0.13, 0.32, 0], color=BG, stroke_width=4)
    return VGroup(base, stem, collar, mitre, ball, slit).scale(cell * 0.92).set_z_index(10)


def men(S, squares, cell: float = CELL) -> dict:
    return {s: bishop(cell).move_to(S(s)) for s in sorted(squares)}


def track_path(track, S, color, width: float = 6) -> VGroup:
    return VGroup(*[Line(S(a), S(b), color=color, stroke_width=width).set_z_index(4) for a, b in sides(track)])


def track_color(i: int):
    (c, r) = TRACKS[i][0]
    return DARK_TRACK if (c + r) % 2 == 0 else LIGHT_TRACK


class Short(Scene):
    def top(self, text: str, color=INK, size: float = 84):
        """Swap the big line in the title slot."""
        new = label(text, size, color).move_to([CENTRE_X, TITLE_Y, 0])
        old = getattr(self, "_top", None)
        self._top = new
        return [FadeIn(new)] + ([FadeOut(old)] if old is not None else [])

    def construct(self):
        cap = Captions(self)
        S = stage()
        tiles, squares = board(S)
        rim = Cell(side_length=CELL * N, color=MUTED, stroke_width=4).move_to(tiles)

        # --- hook: the board and Dudeney's 14, then the question -------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(FadeIn(tiles), Create(rim), run_time=0.5)
        now = men(S, placement(TRACKS, START))
        bishops = VGroup(*now.values())
        self.add_sound(SFX["pop"], time_offset=0.3)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in bishops], lag_ratio=0.06), run_time=0.8)
        self.remove(*bishops)
        self.add(bishops)
        title = hook("How many ways can", "14 bishops sit safely?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        self.wait(0.75)

        # --- the rules --------------------------------------------------------------
        rays = VGroup(Line(S(RAY_FROM), S((0, 5)), color=ACCENT, stroke_width=8),
                      Line(S(RAY_FROM), S((7, 2)), color=ACCENT, stroke_width=8)).set_z_index(5)
        self.add_sound(SFX["pop"])
        cap.show("Bishops attack diagonally", extra=[Create(rays)])
        self.wait(1.0)
        cap.show("14 is the most that fit", extra=[FadeOut(rays)])
        self.wait(0.9)

        shown = bishops
        for text, settings in zip(("Another way", "And another"), OTHERS):
            group = VGroup(*men(S, placement(TRACKS, settings)).values())
            self.add_sound(SFX["pop"])
            cap.show(text, extra=[FadeOut(shown), FadeIn(group)], run_time=0.35)
            shown = group
            self.wait(0.7)
        cap.show("How many in all?", ACCENT)
        self.wait(0.8)

        # --- pause and try: the middle of the board is always empty -----------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X, STAGE_Y, 0], radius=0.95, tick_sound=SFX["tick"])

        # --- edge only ----------------------------------------------------------------
        inner = [q for (c, r), q in squares.items() if 0 < c < N - 1 and 0 < r < N - 1]
        self.add_sound(SFX["snip"])
        cap.show("Every bishop sits on the edge", extra=[
            FadeOut(title), *[q.animate.set_fill(opacity=0.28) for q in inner]])
        self.wait(1.1)

        # --- the loop ---------------------------------------------------------------
        self.play(FadeOut(shown), run_time=0.2)
        walker = Dot(S(LOOP[0]), radius=0.17, color=ACCENT).set_z_index(9)
        self.add_sound(SFX["pop"])
        cap.show("Bounce a line off the edges", extra=[GrowFromCenter(walker)])
        loop = track_path(LOOP, S, DARK_TRACK)
        for k, (side, (a, b)) in enumerate(zip(loop, sides(LOOP))):
            if k:
                self.add_sound(SFX["pop"], gain=-8)
            self.play(Create(side), walker.animate.move_to(S(b)), rate_func=linear,
                      run_time=0.13 * abs(a[0] - b[0]))
        self.add_sound(SFX["chime"], gain=-10)
        cap.show("It closes into a loop", extra=[Flash(S(LOOP[0]), color=ACCENT, flash_radius=0.5),
                                                 FadeOut(walker)])
        self.wait(0.6)

        # --- neighbours attack; opposite corners don't ------------------------------
        a, b = bishop().move_to(S(LOOP[0])), bishop().move_to(S(LOOP[1]))
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(a), GrowFromCenter(b), run_time=0.3)
        self.add_sound(SFX["snip"])
        cap.show("Neighbors attack", HOT, extra=[loop[0].animate.set_color(HOT).set_stroke(width=11)])
        self.wait(0.7)
        self.add_sound(SFX["pop"])
        cap.show("So: opposite corners", extra=[
            loop[0].animate.set_color(DARK_TRACK).set_stroke(width=6), b.animate.move_to(S(LOOP[2]))], run_time=0.55)
        self.wait(0.75)
        self.add_sound(SFX["pop"])
        cap.show("That's 2 choices", ACCENT, extra=[
            a.animate.move_to(S(LOOP[1])), b.animate.move_to(S(LOOP[3]))], run_time=0.55)
        self.wait(0.15)
        self.play(a.animate.move_to(S(LOOP[0])), b.animate.move_to(S(LOOP[2])), run_time=0.45)

        # --- every track doubles the count ------------------------------------------
        pieces = {0: [a, b]}
        for i, t in enumerate(TRACKS):
            if i:
                pieces[i] = [bishop().move_to(S(s)) for s in seats(t, 0)]
        rest = VGroup(*[p for i in pieces if i for p in pieces[i]])
        self.add_sound(SFX["pop"])
        cap.show("Now the other loops", extra=[FadeIn(rest), *self.top("2 ways", ACCENT)])
        self.wait(0.2)

        def light(i: int, ways: int, step: float = 0.72):
            path = track_path(TRACKS[i], S, track_color(i))
            moves = [p.animate.move_to(S(s)) for p, s in zip(pieces[i], seats(TRACKS[i], 1))]
            self.play(Create(path), *moves, run_time=step)
            self.add_sound(SFX["pop"], gain=-4)
            self.remove(self._top)                      # a hard cut: a cross-fade smears the digits
            self._top = label(f"{ways} ways", 84, ACCENT).move_to([CENTRE_X, TITLE_Y, 0])
            self.add(self._top)
            self.wait(0.1)

        cap_at = {2: "No two share a diagonal", 4: "So the choices multiply", 6: "Long diagonals: 2 ends each"}
        for i, ways in zip(range(1, len(TRACKS)), (4, 8, 16, 32, 64, 128, 256)):
            if i in cap_at:
                cap.show(cap_at[i], run_time=0.3)
            light(i, ways)

        # --- payoff -------------------------------------------------------------------
        total = MathTex(r"2^8 = 256", color=ACCENT, font_size=96)
        cap.show(total)
        self.wait(0.9)
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        cap.show("256 ways ✓", GOOD, extra=[*self.top("256 ways", GOOD),
                                            Flash(S((3.5, 3.5)), color=GOOD, flash_radius=1.0)])
        self.wait(1.2)

        # --- Level 2: the same trick on a bigger board --------------------------------
        beat(self, "Level 2")
        cap.clear()
        board_now = [m for m in self.mobjects if m is not None]
        self.play(*[FadeOut(m) for m in board_now], run_time=0.3)
        self.clear()

        mini_cell = 0.26
        Sm = stage(mini_cell, N, CENTRE_X - 2.45, 5.85)
        mini = board(Sm, mini_cell)[0]
        mini_paths = VGroup(*[track_path(t, Sm, track_color(i), 2.5) for i, t in enumerate(TRACKS)])
        recap = label("256 ways", 32, GOOD).next_to(mini, DOWN, buff=0.14)
        tag = badge("LEVEL 2").move_to([CENTRE_X + 0.85, 6.55, 0])
        q = VGroup(*[label(t, 34) for t in ("10 by 10 board,", "18 bishops.", "How many ways?")]).arrange(DOWN, buff=0.12)
        q.move_to([CENTRE_X + 0.85, 5.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(FadeIn(mini), FadeIn(mini_paths), FadeIn(recap), GrowFromCenter(tag), FadeIn(q), run_time=0.6)

        cell2 = 0.62
        S2 = stage(cell2, L2_N, y=STAGE_Y - 0.3)
        tiles2, _ = board(S2, cell2, L2_N)
        men2 = VGroup(*men(S2, L2_START, cell2).values())
        ask = label("? ways", 72, ACCENT).move_to(S2((4.5, 4.5)))
        self.play(FadeIn(tiles2), run_time=0.5)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in men2], lag_ratio=0.04), FadeIn(ask), run_time=0.8)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
