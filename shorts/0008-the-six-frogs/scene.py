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
    DOWN, PI, UP, Sector, TAU, ArcBetweenPoints, Circle, Ellipse, FadeIn, FadeOut, GrowFromCenter, Indicate, LaggedStart,
    ManimColor, MoveAlongPath, Dot, Rotate, Succession, RoundedRectangle, Scene, Text, VGroup, there_and_back, Transform, Arrow,
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
ROW_Y = 1.4
EVEN, ODD = PIECES[0], PIECES[1]
SQUARE_FILL = ManimColor("#1B2735")
assert (N, MOVES, len(RECIPE), len(BOARDS), sum(LEAPS)) == (4, 10, 10, 11, 6)


def frog_color(k: int):
    return EVEN if k % 2 == 0 else ODD


PAD_FILL, PAD_EDGE = ManimColor("#2E6B4F"), ManimColor("#4FA37A")


def sq_pos(i: int, y: float, pitch: float = SQ, n: int = N) -> np.ndarray:
    """Centre of a frog sitting on pad i."""
    return np.array([CENTRE_X + (i - n / 2) * pitch, y, 0.0])


def squares(n: int, y: float, pitch: float, r: float = 0.5, fill=PAD_FILL, stroke=PAD_EDGE) -> VGroup:
    """Top-down view: a row of round lily pads, each with a notch. `y` is the frog-centre height."""
    pads = []
    for i in range(n + 1):
        c = sq_pos(i, y, pitch, n)
        pads.append(Sector(radius=1.2 * r, angle=TAU - 0.5, start_angle=0.9, arc_center=c,
                           fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=3))
    return VGroup(*pads)


def frog(k: int, r: float, opacity: float = 1.0) -> VGroup:
    """A cute top-down cartoon frog (head up): round body, big shiny eyes, smile, blush, stubby legs.
    Only `shape` turns to face the way it hops; the number stays upright. `anchor` marks its centre."""
    col = frog_color(k)
    dark = ManimColor(col).interpolate(ManimColor("#000000"), 0.25)
    light = ManimColor(col).interpolate(ManimColor("#FFFFFF"), 0.35)
    u = 0.86 * r

    def ell(w, h, x, y, c, rot=0.0, sw=2):
        e = Ellipse(width=w * u, height=h * u, fill_color=c, fill_opacity=opacity,
                    stroke_color=BG, stroke_width=sw)
        return e.rotate(rot).move_to([x * u, y * u, 0])

    def dot(rad, x, y, c, sw=0):
        return Circle(radius=rad * u, fill_color=c, fill_opacity=opacity, stroke_color=BG,
                      stroke_width=sw).move_to([x * u, y * u, 0])

    parts = []
    for sx in (-1, 1):
        parts.append(ell(0.8, 0.55, sx * 0.85, -0.65, dark, sx * 0.7))    # back thigh
        parts.append(ell(0.7, 0.34, sx * 0.88, -1.05, dark, -sx * 0.4))   # back foot
        parts.append(ell(0.5, 0.32, sx * 0.85, 0.1, dark, -sx * 0.6))     # front arm
        parts.append(dot(0.2, sx * 1.0, 0.3, dark, 2))                    # hand
    legs = VGroup(*parts)
    body = ell(1.55, 1.8, 0, -0.05, col, 0, 3)
    belly = ell(0.95, 0.8, 0, -0.45, light, 0, 0)
    bumps = VGroup(*[dot(0.19, sx * 0.3, 0.53, col, 3) for sx in (-1, 1)])
    eyes = VGroup(*[dot(0.135, sx * 0.3, 0.55, ManimColor("#FFFFFF"), 2) for sx in (-1, 1)])
    pupils = VGroup(*[VGroup(dot(0.108, sx * 0.3, 0.55, BG),
                             dot(0.04, sx * 0.3 + 0.035, 0.585,ManimColor("#FFFFFF")))
                      for sx in (-1, 1)])
    cheeks = VGroup(*[ell(0.3, 0.18, sx * 0.62, 0.32, ManimColor("#FF8FA3")) .set_stroke(width=0)
                      for sx in (-1, 1)])
    nose = VGroup(*[dot(0.03, sx * 0.07, 0.72, BG) for sx in (-1, 1)])
    shape = VGroup(legs, body, belly, bumps, eyes, pupils, cheeks, nose)
    num = Text(str(k), font=FONT, weight=BOLD, font_size=int(r * 70), color=BG)
    num.move_to([0, 0, 0])  # on the rotation centre, so it stays inside the body whichever way the frog faces
    if opacity < 1:
        num.set_opacity(opacity + 0.15)
    anchor = Dot([0, 0, 0], radius=0.001).set_opacity(0)
    g = VGroup(shape, num, anchor).set_z_index(5)
    g.shape, g.pupils, g.anchor, g.facing = shape, pupils, anchor, 0.0
    return g


def place(board, y: float, r: float, pitch: float, n: int, opacity: float = 1.0) -> dict:
    return {k: frog(k, r, opacity).shift(sq_pos(i, y, pitch, n)) for i, k in enumerate(board) if k}


def turn(f: VGroup, target: float):
    """Turn the frog's body (not its number) to face `target` (0 = up, -PI/2 = right, PI/2 = left)."""
    delta = (target - f.facing + PI) % TAU - PI
    f.facing = target
    return Rotate(f.shape, delta, about_point=f.anchor.get_center())


def hop(f: VGroup, dest: np.ndarray, leap: bool):
    """Turn to face the way it is going, then slide as a small hop or leap in a high arc."""
    start = f.anchor.get_center()
    sign = 1 if dest[0] > start[0] else -1
    t = turn(f, -sign * PI / 2)
    t.run_time = 0.25
    m = MoveAlongPath(f, ArcBetweenPoints(start, dest, angle=-sign * (2.2 if leap else 1.0)))
    m.run_time = 1.0
    return Succession(t, m)


def face_up(frogs):
    return [turn(f, 0.0) for f in frogs]


def blink(frogs):
    return LaggedStart(*[p.animate(rate_func=there_and_back).stretch(0.1, 1)
                         for f in frogs for p in f.pupils], lag_ratio=0.05)


def jump_for_joy(frogs):
    return LaggedStart(*[f.animate(rate_func=there_and_back).shift(0.4 * UP)
                         for f in sorted(frogs, key=lambda f: f.anchor.get_center()[0])], lag_ratio=0.2)


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
        title = hook("Reverse the frogs!", "Can you do it in 10 moves?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        cap.show("4 frogs, 1 empty pad")
        self.play(jump_for_joy(group), run_time=1.0)
        self.play(blink(group), run_time=0.5)

        # --- the goal -------------------------------------------------------------------------
        gy = -1.3
        gboard = squares(N, gy, 0.95, 0.36, fill=BG, stroke=MUTED)
        gfrogs = VGroup(*place(goal(N), gy, 0.36, 0.95, N, 0.55).values())
        glabel = label("Goal: reverse the order", 44, MUTED).move_to([CENTRE_X, gy + 0.95, 0])
        cap.show("Reverse them in 10 moves?", extra=[FadeIn(gboard), FadeIn(gfrogs), FadeIn(glabel)])
        self.wait(2.0)

        # --- the rules: one slide, one leap ----------------------------------------------------
        # the rules stay up through the demo and the countdown (that frame is the thumbnail)
        rules = VGroup(label("Frogs can move 1 or 2 squares", 46, INK),
                       label("to the empty square", 46, ACCENT)).arrange(DOWN, buff=0.2)
        rules.move_to([CENTRE_X, 3.6, 0])
        cap.show("Slide: move 1 square", GOOD, extra=[FadeIn(rules, shift=0.2 * DOWN)])
        self.add_sound(SFX["tick"])
        self.play(hop(frogs[1], sq_pos(0, ROW_Y), False), run_time=0.6)
        self.wait(0.4)
        self.play(hop(frogs[1], sq_pos(1, ROW_Y), False), run_time=0.5)
        cap.show("Leap: over 1 frog", ACCENT)
        self.add_sound(SFX["pop"])
        self.play(hop(frogs[2], sq_pos(0, ROW_Y), True), run_time=0.8)
        self.wait(0.4)
        self.play(hop(frogs[2], sq_pos(2, ROW_Y), True), run_time=0.8)
        self.play(blink(group), run_time=0.5)

        # --- pause and try ------------------------------------------------------------------------
        cap.show("Pause and try it", ACCENT, extra=[FadeOut(gboard), FadeOut(gfrogs), FadeOut(glabel)])
        countdown(self, 5, center=[CENTRE_X, -0.75, 0], radius=0.95, tick_sound=SFX["tick"])

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

        cap.show("Here is one way", extra=[FadeOut(title), FadeOut(rules), FadeIn(chips), FadeIn(chips_lab)])
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
        self.play(*face_up(frogs.values()), run_time=0.3)
        self.counter("10 moves ✓", GOOD)
        cap.show("10 moves. Fewest possible ✓", GOOD)
        self.play(jump_for_joy(frogs.values()), run_time=1.2)
        self.play(blink(frogs.values()), run_time=0.5)
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
        b6 = squares(L2_N, 2.4, p2, 0.37)
        f6 = VGroup(*place(start(L2_N), 2.4, 0.37, p2, L2_N).values())
        g6 = squares(L2_N, -0.4, p2, 0.37, fill=BG, stroke=MUTED)
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
