"""Short 0003 - Inspecting a Mine (Dudeney no. 247).

Level 1 (solved on screen): a junction with 3 passages traps you, and so does starting at a 2-passage
corner. That makes 11 stuck spots, the finish absorbs one, and each repeated passage clears two, so
5 repeats: 31 + 5 = 36 miles. A dot then walks Dudeney's actual route.
Level 2 (comment challenge): finish back at A -> 38.

The mine, the route and the numbers come from verify.py, so what you see is exactly what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP,
    Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    MathTex, Scene, Square, Text, UpdateFromAlphaFunc, VGroup,
    linear, there_and_back, BOLD,
)
import numpy as np  # noqa: E402

from lib.layout import (  # noqa: E402
    ACCENT, FONT, GOOD, GRID, INK, MUTED, PIECES, SIZE_CAPTION, STAGE_Y, TITLE_Y,
)
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    COLS, EDGES, FINISH, L2_MILES, MILES, NAIVE_TRIES, ODD, REPEATS, ROUTE, ROWS, START, TRAP_WALK, edge, pos,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
STUCK = PIECES[0]
assert L2_MILES == 38                      # the Level 2 card must not give it away; the yaml holds it


def stage(cell: float = 1.5, y: float = STAGE_Y) -> callable:
    """A function from a junction letter to its point in the frame."""
    origin = np.array([CENTRE_X - cell * (COLS - 1) / 2, y + cell * (ROWS - 1) / 2, 0.0])

    def J(letter: str) -> np.ndarray:
        c, r = pos(letter)
        return origin + cell * np.array([c, -r, 0.0])
    return J


def mine(J, cell: float = 1.5, width: float = 9, color=INK) -> tuple[VGroup, dict]:
    """The rock between the passages, and the passages themselves keyed by edge name."""
    rock = VGroup()
    for r in range(ROWS - 1):
        for c in range(COLS - 1):
            sq = Square(side_length=cell * 0.74, stroke_width=0, fill_color=GRID, fill_opacity=1)
            rock.add(sq.move_to(J("ABCDEFGHIJKLMNOPQRST"[r * COLS + c]) + cell / 2 * np.array([1, -1, 0])))
    lines = {e: Line(J(e[0]), J(e[1]), color=color, stroke_width=width).set_z_index(2) for e in EDGES}
    return rock, lines


def stuck_dot(p, color=STUCK) -> Dot:
    return Dot(p, radius=0.2, color=color).set_z_index(6)


class Short(Scene):
    def top(self, text: str, color=INK, size: float = 72):
        """Swap the big line in the title slot."""
        new = label(text, size, color).move_to([CENTRE_X, TITLE_Y, 0])
        old = getattr(self, "_top", None)
        anims = [FadeIn(new)] + ([FadeOut(old)] if old is not None else [])
        self._top = new
        return anims

    def walk(self, route, walker, J, step: float, colors, sounds=()):
        """Move the walker along junctions, drawing a trail behind it. Returns the trail."""
        pts = [J(v) for v in route]
        n = len(pts) - 1
        trail = [Line(pts[i], pts[i + 1], color=colors(i), stroke_width=11, stroke_opacity=0)
                 .set_z_index(3 + i / 100) for i in range(n)]
        for i, name in sounds:
            self.add_sound(SFX[name], time_offset=i * step)
        miles = self._miles or []

        def update(_, a):
            t = a * n
            i = min(int(t), n - 1)
            f = t - i
            walker.move_to(pts[i] + f * (pts[i + 1] - pts[i]))
            for k, line in enumerate(trail):
                if k < i or (k == i and f > 0.98):
                    line.put_start_and_end_on(pts[k], pts[k + 1]).set_stroke(opacity=1)
                elif k == i and f > 0.02:
                    line.put_start_and_end_on(pts[k], walker.get_center()).set_stroke(opacity=1)
                else:
                    line.set_stroke(opacity=0)
            for k, text in enumerate(miles):
                text.set_opacity(1 if k == int(t + 1e-6) else 0)

        # Everything that changes goes in one group: Manim only redraws what an animation targets.
        moving = VGroup(walker, *trail, *miles)
        self.play(UpdateFromAlphaFunc(moving, update), run_time=n * step, rate_func=linear)
        self.remove(moving)
        group = VGroup(*trail)
        self.add(group, walker, *miles[-1:])
        return group

    def construct(self):
        cap = Captions(self)
        self._miles = None
        J = stage()
        rock, lines = mine(J)
        all_lines = VGroup(*lines.values())

        # --- hook: the mine draws itself, then the question ----------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(FadeIn(rock), Create(all_lines), run_time=1.1)
        title = hook("What's the shortest route", "through all 31 passages?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(1.1)

        # --- the rules -----------------------------------------------------------
        one = Line(J("A"), J("B"), color=ACCENT, stroke_width=13).set_z_index(3)
        mile = label("1 mile", 44, ACCENT).next_to(one, UP, buff=0.14).shift(0.25 * UP)
        self.add_sound(SFX["pop"])
        cap.show("Each passage: 1 mile", extra=[Create(one), FadeIn(mile)])
        self.wait(0.6)

        a_lbl = label("A", 52, ACCENT).move_to(J(START) + np.array([-0.42, 0.42, 0]))
        a_dot = Dot(J(START), radius=0.2, color=ACCENT).set_z_index(6)
        self.add_sound(SFX["pop"])
        cap.show("Start here, at A", extra=[FadeOut(one), FadeOut(mile), GrowFromCenter(a_dot), FadeIn(a_lbl)])
        self.wait(0.6)
        cap.show("Finish anywhere")
        self.wait(0.7)

        # --- naive tries: this is what an answer looks like, and repeats cost miles --
        for text, attempt in zip(("One try…", "Another…"), NAIVE_TRIES):
            walker = Dot(J(START), radius=0.2, color=INK).set_z_index(8)
            tally = [Text(f"{k} miles" if k != 1 else "1 mile", font=FONT, font_size=56, weight=BOLD,
                          color=INK).move_to([CENTRE_X, -1.8, 0]).set_opacity(0) for k in range(len(attempt))]
            self.add_sound(SFX["pop"])
            cap.show(text, extra=[GrowFromCenter(walker), all_lines.animate.set_color(MUTED)], run_time=0.3)
            steps = [edge(a, b) for a, b in zip(attempt, attempt[1:])]
            first = {e: steps.index(e) for e in set(steps)}
            self._miles = tally
            trail = self.walk(attempt, walker, J, 0.075,
                              lambda i: PIECES[1] if first[steps[i]] == i else ACCENT)
            self._miles = None
            self.wait(0.5)
            if attempt is not NAIVE_TRIES[-1]:
                self.play(FadeOut(trail), FadeOut(walker), FadeOut(tally[-1]), run_time=0.2)
        cap.show("Can you beat that?", ACCENT)
        self.wait(0.7)
        self.play(FadeOut(trail), FadeOut(walker), FadeOut(tally[-1]),
                  all_lines.animate.set_color(INK), run_time=0.25)

        # --- pause and try -------------------------------------------------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X + 2.6, STAGE_Y + 2.95, 0], radius=0.55, tick_sound=SFX["tick"])

        # --- the trap: a walk through C that uses all 3 of its passages ----------
        walker = Dot(J(TRAP_WALK[0]), radius=0.2, color=INK).set_z_index(8)
        self.play(FadeOut(title), all_lines.animate.set_color(MUTED), FadeOut(a_dot), run_time=0.3)
        self.add_sound(SFX["pop"])
        cap.show("Take a 3-way junction",
                 extra=[GrowFromCenter(walker), Flash(J("C"), color=ACCENT, flash_radius=0.4, num_lines=10)])
        self.wait(0.4)
        cap.show("In, out, in…")
        trail = self.walk(TRAP_WALK, walker, J, 0.34, lambda i: ACCENT)
        here = J("C")
        self.add_sound(SFX["snip"])
        cap.show("…and you're stuck", STUCK,
                 extra=[walker.animate.set_color(STUCK).scale(1.3), Flash(here, color=STUCK, flash_radius=0.5)])
        self.wait(0.6)

        # --- count the stuck spots ------------------------------------------------
        dots = {v: stuck_dot(J(v)) for v in ODD}
        self.remove(walker, trail)
        self.add(dots["C"])
        self.add_sound(SFX["pop"])
        cap.show("10 junctions like that", extra=[
            LaggedStart(*[GrowFromCenter(dots[v]) for v in ODD if v != "C"], lag_ratio=0.1, run_time=0.8),
            *self.top("Stuck spots: 10")], run_time=0.8)
        self.wait(0.5)

        dots[START] = stuck_dot(J(START))
        self.add_sound(SFX["pop"])
        cap.show("A too: out, in, stuck", extra=[GrowFromCenter(dots[START]), *self.top("Stuck spots: 11")])
        self.wait(1.0)

        flag = stuck_dot(J(FINISH), GOOD)
        finish_lbl = label("finish", 40, GOOD).next_to(flag, DOWN, buff=0.14)
        self.add_sound(SFX["pop"])
        cap.show("The finish saves one", extra=[FadeOut(dots[FINISH]), FadeIn(flag), FadeIn(finish_lbl),
                                                *self.top("Stuck spots: 10")])
        self.wait(0.8)

        # --- each repeat clears two ------------------------------------------------
        repeated = []

        def repeat(e: str, left: int):
            bar = Line(J(e[0]), J(e[1]), color=ACCENT, stroke_width=13).set_z_index(5)
            repeated.append(bar)
            self.add_sound(SFX["snip"])
            return [Create(bar), FadeOut(dots[e[0]]), FadeOut(dots[e[1]]),
                    *self.top(f"Stuck spots: {left}")]

        cap.show("A repeat clears two", extra=repeat(REPEATS[0], 8), run_time=0.5)
        self.wait(0.7)
        for e, left in zip(REPEATS[1:], (6, 4, 2)):
            self.play(*repeat(e, left), run_time=0.32)
            self.wait(0.06)
        cap.show("So 5 repeats, at least", extra=repeat(REPEATS[4], 0), run_time=0.4)
        self.wait(0.6)
        total = MathTex(r"31 + 5 = 36", color=ACCENT, font_size=84)
        cap.show(total)
        self.wait(0.9)

        # --- the route itself: the proof that 36 can be done ------------------------
        cap.show("Now walk it")
        walker = Dot(J(START), radius=0.2, color=INK).set_z_index(8)
        miles = [Text(f"{k} miles" if k != 1 else "1 mile", font=FONT, font_size=72, weight=BOLD, color=INK)
                 .move_to([CENTRE_X, TITLE_Y, 0]).set_opacity(0) for k in range(MILES + 1)]
        self.play(FadeOut(self._top), FadeOut(VGroup(*repeated)), GrowFromCenter(walker), run_time=0.3)
        self._top = None
        self._miles = miles
        seen, sounds = set(), []
        steps = [edge(a, b) for a, b in zip(ROUTE, ROUTE[1:])]
        again = set()
        for i, e in enumerate(steps):
            if e in seen:
                again.add(i)
                sounds.append((i, "snip"))
            seen.add(e)
        trail = self.walk(ROUTE, walker, J, 0.17, lambda i: ACCENT if i in again else GOOD, sounds)
        self._miles = None

        # --- payoff ----------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        cap.show("36 miles ✓", GOOD, extra=[Flash(J(FINISH), color=GOOD, flash_radius=0.6)])
        self.wait(1.2)

        # --- Level 2: same mine, back to the start ----------------------------------
        beat(self, "Level 2")
        cap.clear()
        done = VGroup(rock, all_lines, trail, walker, flag, finish_lbl, a_lbl, miles[-1])
        self.play(FadeOut(done), FadeOut(credit), run_time=0.3)

        Jm = stage(0.5, 5.75)
        mini_rock, mini_lines = mine(Jm, 0.5, 4, GOOD)
        mini = VGroup(mini_rock, *mini_lines.values()).shift(1.95 * np.array([-1, 0, 0]))
        recap = label("36 miles", 40, GOOD).next_to(mini, DOWN, buff=0.2)
        tag = badge("LEVEL 2").move_to([CENTRE_X + 1.4, 6.6, 0])
        q = VGroup(*[label(t, 42) for t in ("What if we have", "to end back", "at A too?")]).arrange(DOWN, buff=0.14)
        q.move_to([CENTRE_X + 1.4, 5.0, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(FadeIn(mini), FadeIn(recap), GrowFromCenter(tag), FadeIn(q), run_time=0.6)

        J2 = stage(1.3, 1.0)
        rock2, lines2 = mine(J2, 1.3, 8)
        self.play(FadeIn(rock2), Create(VGroup(*lines2.values())), run_time=0.8)
        start2 = Dot(J2(START), radius=0.2, color=ACCENT).set_z_index(6)
        a2 = label("A", 52, ACCENT).move_to(J2(START) + np.array([-0.42, 0.42, 0]))
        ask = label("? miles", SIZE_CAPTION, ACCENT).move_to([CENTRE_X, -1.75, 0])
        self.play(GrowFromCenter(start2), FadeIn(a2), FadeIn(ask), run_time=0.5)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.8)
