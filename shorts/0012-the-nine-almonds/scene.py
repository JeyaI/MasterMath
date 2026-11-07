"""Short 0012 - The Nine Almonds (Dudeney no. 229).

Level 1 (on screen): nine almonds on the middle of a 5x5 board; remove eight, leave the centre one, in 4 moves.
A jump over a neighbour (diagonals too) removes it; jumps in a row by one almond are one move.
The solution plays Dudeney's four moves: one almond sweeps four jumps and leaves a glowing trail, three short
moves follow, and the four coloured trails are the payoff. Counters track moves and jumps (4 and 8).
Level 2: no chains, one jump per move; fewest moves? (8)

The board, almond numbering, the moves (start, jumped squares, landing squares) come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, PI, UP, ArcBetweenPoints, Circle, Create, Ellipse, FadeIn, FadeOut, GrowFromCenter,
    Indicate, LaggedStart, ManimColor, MoveAlongPath, RoundedRectangle, Scene, Square, VGroup,
    VMobject, there_and_back, BOLD, Text,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, FONT, GOOD, GRID, INK, MUTED, PIECES  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    CENTRE, L2_ANSWER, MOVES, NUMBERED, N_JUMPS, N_MOVES, SIZE, START,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
assert (N_MOVES, N_JUMPS, SIZE, L2_ANSWER) == (4, 8, 5, 8)

P = 1.1                       # square pitch
BY = 1.0                      # board centre y
SHELL = ManimColor("#A66B3B")
SHELL_EDGE = ManimColor("#5A3118")
MOVE_COLORS = [PIECES[0], PIECES[1], PIECES[2], ACCENT]


def pos(p, pitch: float = P, by: float = BY) -> np.ndarray:
    return np.array([CENTRE_X + (p[0] - 2) * pitch, by + (p[1] - 2) * pitch, 0.0])


def board(pitch: float = P, by: float = BY) -> VGroup:
    cells = []
    for x in range(SIZE):
        for y in range(SIZE):
            inner = (1 <= x <= 3) and (1 <= y <= 3)
            c = Square(side_length=pitch, fill_color=GRID if inner else BG, fill_opacity=1,
                       stroke_color=MUTED, stroke_width=3).move_to(pos((x, y), pitch, by))
            cells.append(c)
    return VGroup(*cells)


def almond(k: int, pitch: float = P) -> VGroup:
    s = pitch / P
    def pt(x, y):
        return np.array([x * s, y * s, 0.0])

    # teardrop with a pointed tip, like a real almond kernel
    body = VMobject(fill_color=SHELL, fill_opacity=1, stroke_color=SHELL_EDGE, stroke_width=4)
    body.start_new_path(pt(0.0, 0.50))
    body.add_cubic_bezier_curve_to(pt(0.22, 0.34), pt(0.44, 0.10), pt(0.42, -0.10))
    body.add_cubic_bezier_curve_to(pt(0.40, -0.36), pt(0.22, -0.48), pt(0.0, -0.48))
    body.add_cubic_bezier_curve_to(pt(-0.22, -0.48), pt(-0.40, -0.36), pt(-0.42, -0.10))
    body.add_cubic_bezier_curve_to(pt(-0.44, 0.10), pt(-0.22, 0.34), pt(0.0, 0.50))
    body.close_path() if hasattr(body, "close_path") else None
    shine = Ellipse(width=0.12 * s, height=0.34 * s, fill_color=ManimColor("#F3D9AE"), fill_opacity=0.5,
                    stroke_width=0).rotate(0.25).move_to(pt(-0.17, 0.0))
    num = Text(str(k), font=FONT, weight=BOLD, font_size=int(38 * s), color=ManimColor("#FFF4E0")
               ).move_to(pt(0.02, -0.12))
    return VGroup(body, shine, num).set_z_index(5)


def place(pitch: float = P, by: float = BY) -> dict:
    return {k: almond(k, pitch).move_to(pos(p, pitch, by)) for k, p in NUMBERED.items()}


def arc_to(a, dest: np.ndarray, color=None):
    start = a.get_center()
    sign = 1 if dest[0] >= start[0] else -1
    return MoveAlongPath(a, ArcBetweenPoints(start, dest, angle=-sign * 1.4))


class Short(Scene):
    def counter(self, moves: int, jumps: int, color=INK):
        """Hard-cut counter (a cross-fade smears digits)."""
        if getattr(self, "_ctr", None) is not None:
            self.remove(self._ctr)
        self._ctr = label(f"Moves {moves}/{N_MOVES}  ·  Jumps {jumps}/{N_JUMPS}", 52, color)
        self._ctr.move_to([CENTRE_X, 4.7, 0])
        self.add(self._ctr)

    def construct(self):
        cap = Captions(self)
        grid = board()
        al = place()
        group = VGroup(*al.values())

        # --- hook: pop in the board and the almonds, then the question -----------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(c) for c in grid], lag_ratio=0.02), run_time=0.6)
        self.remove(*grid)
        self.add(grid)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(a) for a in group], lag_ratio=0.1), run_time=0.7)
        self.remove(*group)
        self.add(group)
        title = hook("Remove 8 almonds", "in just 4 moves?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        cap.show("9 almonds, 5x5 board")
        self.play(LaggedStart(*[a.animate(rate_func=there_and_back).shift(0.18 * UP) for a in group],
                              lag_ratio=0.1), run_time=1.1)

        # --- the rules: one demo jump ---------------------------------------------------------------
        rules = VGroup(label("Jump over a neighbour", 50, INK),
                       label("(diagonals too) and take it off", 46, ACCENT)).arrange(DOWN, buff=0.2)
        rules.move_to([CENTRE_X, 4.7, 0])
        cap.show("Jump over one, take it off", extra=[FadeOut(title), FadeIn(rules, shift=0.2 * DOWN)])
        self.wait(0.4)
        self.add_sound(SFX["pop"])
        dest = pos((1, 4))
        self.play(arc_to(al[4], dest), FadeOut(al[1], scale=0.5), run_time=0.9)
        self.wait(0.9)
        self.add_sound(SFX["tick"], gain=-3)
        self.play(arc_to(al[4], pos((1, 2))), FadeIn(al[1], scale=0.5), run_time=0.8)
        rules2 = VGroup(label("Jumps in a row by the same", 46, INK),
                        label("almond count as ONE move", 46, ACCENT)).arrange(DOWN, buff=0.2)
        rules2.move_to([CENTRE_X, 4.7, 0])
        self.play(FadeOut(rules, shift=0.2 * UP), FadeIn(rules2, shift=0.2 * DOWN), run_time=0.5)
        self.wait(1.4)

        # --- the goal -------------------------------------------------------------------------------
        cap.show("Leave just the centre")
        ring = Circle(radius=0.62, color=GOOD, stroke_width=8).move_to(pos(CENTRE)).set_z_index(6)
        self.play(Create(ring), run_time=0.6)
        self.play(Indicate(ring, color=GOOD, scale_factor=1.25), run_time=0.8)
        self.wait(0.8)
        cap.show("Remove 8 almonds in 4 moves?", ACCENT, extra=[FadeOut(ring)])
        self.wait(1.0)

        # --- pause and try ----------------------------------------------------------------------------
        cap.show("Pause and try it", ACCENT, extra=[FadeOut(rules2)])
        countdown(self, 5, center=[CENTRE_X, 4.9, 0], radius=0.95, tick_sound=SFX["tick"])

        # --- the solution -------------------------------------------------------------------------------
        chips = VGroup(*[
            VGroup(RoundedRectangle(corner_radius=0.12, width=1.1, height=0.6, fill_color=BG, fill_opacity=1,
                                    stroke_color=MOVE_COLORS[i], stroke_width=5),
                   label(f"{i + 1}", 44, MOVE_COLORS[i])).arrange(DOWN, buff=0)
            for i in range(N_MOVES)])
        for c in chips:
            c[1].move_to(c[0])
        chips.arrange(buff=0.25).move_to([CENTRE_X, -2.3, 0])
        self.counter(0, 0, MUTED)
        self.play(FadeIn(chips), run_time=0.4)

        live = {k: al[k] for k in NUMBERED}                 # almond number -> mobject
        sq_of = dict(NUMBERED)                              # almond number -> square
        trails = VGroup()
        jumps_done = 0
        captions = [
            "Move 1: one almond, four jumps",
            "Move 2: 7 over 4",
            "Move 3: 6 over 2, 7",
            "Move 4: 5 over 6",
        ]
        for mi, mv in enumerate(MOVES):
            color = MOVE_COLORS[mi]
            a = live[mv["almond"]]
            cap.show(captions[mi], color)
            cur = mv["start"]
            self.play(a[0].animate.set_stroke(color, 8), run_time=0.3)
            for vsq, land in zip(mv["jumped"], mv["path"]):
                victim = next(k for k, s in sq_of.items() if s == vsq and k in live and k != mv["almond"])
                seg = VMobject().set_points_as_corners([pos(cur), pos(land)]).set_stroke(color, 9, opacity=0.85)
                seg.set_z_index(3)
                trails.add(seg)
                jumps_done += 1
                self.add_sound(SFX["pop"], gain=-3)
                self.counter(mi + 1, jumps_done, color)
                self.play(arc_to(a, pos(land)), FadeOut(live.pop(victim), scale=0.4), Create(seg),
                          run_time=0.8 if mi == 0 else 0.9)
                cur = land
            sq_of[mv["almond"]] = cur
            self.play(chips[mi][0].animate.set_fill(color, 1), chips[mi][1].animate.set_color(BG),
                      a[0].animate.set_stroke(SHELL_EDGE, 4), run_time=0.4)
            self.wait(0.6 if mi == 0 else 0.5)

        # --- payoff -----------------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        self.counter(N_MOVES, N_JUMPS, GOOD)
        cap.show("4 moves. Fewest possible ✓", GOOD)
        final = live[5]
        self.play(Indicate(final, color=GOOD, scale_factor=1.4), run_time=1.0)
        self.play(trails.animate.set_stroke(opacity=1.0), run_time=0.4)
        self.wait(1.5)

        # --- Level 2 -------------------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.25)
        self.clear()

        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.55, 0])
        q = VGroup(label("Same board, but no chains:", 50, INK),
                   label("ONE jump per move.", 50, ACCENT),
                   label("Fewest moves to leave", 50, INK),
                   label("a single almond?", 50, INK)).arrange(DOWN, buff=0.2).move_to([CENTRE_X, 4.4, 0])
        p2, by2 = 1.0, -0.4
        g2 = board(p2, by2)
        a2 = VGroup(*place(p2, by2).values())
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(q), FadeIn(g2), run_time=0.7)
        self.play(LaggedStart(*[GrowFromCenter(a) for a in a2], lag_ratio=0.08), run_time=0.6)
        self.remove(*a2)
        self.add(a2)
        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(q[1], color=INK, scale_factor=1.15), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
