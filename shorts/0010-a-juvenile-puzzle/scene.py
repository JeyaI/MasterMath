"""Short 0010 - A Juvenile Puzzle (Dudeney no. 239, the rub-out form).

The figure sits on a touchscreen and is wiped off with swipes. Ordinary swipes need 4 (8 odd points,
2 ends per swipe); two fingers on the two parallel uprights wipe both at once: 1 + 2 = 3 swipes.
Level 2: a 3 x 5 grid, one finger only (answer held in short.yaml, not shown).

Shapes and numbers come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP,
    Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line, RoundedRectangle,
    Scene, UpdateFromAlphaFunc, VGroup, linear, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, SIZE_CAPTION, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    EDGES, FOLD_PAIR, GRID_COLS, GRID_ROWS, L2_ANSWER, PTS, STROKES, odd_points, grid_edges, key,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
RED = PIECES[3]
assert L2_ANSWER == 6                      # not shown on the card; the yaml holds it

SCREEN_C = np.array([CENTRE_X, 1.2, 0.0])
SCALE = 0.97                               # figure is 6 x 4 units


def P(name) -> np.ndarray:
    x, y = PTS[name]
    return SCREEN_C + SCALE * np.array([x - 3, y - 2, 0.0])


def finger(p, color=INK, r=0.24) -> VGroup:
    """A fingertip on the glass: a solid dot with a soft ring."""
    ring = Dot(p, radius=r * 1.9, color=color).set_opacity(0.28)
    return VGroup(ring, Dot(p, radius=r, color=color)).set_z_index(8)


class Short(Scene):
    def top(self, text, color=INK, size=64):
        new = label(text, size, color).move_to([CENTRE_X, 5.5, 0])
        old = getattr(self, "_top", None)
        self._top = new
        return [FadeIn(new)] + ([FadeOut(old)] if old is not None else [])

    def wipe(self, fingers, paths, lines, step, colors):
        """Each finger follows its node path; the line behind it wipes off. All fingers move in sync."""
        n = len(paths[0])
        for i in range(n - 1):
            moving, upd = [], []
            for f, path, col in zip(fingers, paths, colors):
                a, b = P(path[i]), P(path[i + 1])
                ln = lines[key((path[i], path[i + 1]))]
                ln.set_color(col)
                moving.append(ln)
                upd.append((f, a, b, ln))

            def update(_, al, upd=upd):
                for f, a, b, ln in upd:
                    cur = a + al * (b - a)
                    f.move_to(cur)
                    if al < 0.999:
                        ln.put_start_and_end_on(cur, b)
                    else:
                        ln.set_stroke(opacity=0)

            self.add_sound(SFX["tick"], gain=-14)
            self.play(UpdateFromAlphaFunc(VGroup(*fingers, *moving), update), run_time=step, rate_func=linear)

    def construct(self):
        cap = Captions(self)
        self._top = None

        # --- screen + figure --------------------------------------------------------------
        screen = RoundedRectangle(corner_radius=0.45, width=7.0, height=6.4, stroke_color=MUTED, stroke_width=8,
                                  fill_color=GRID, fill_opacity=0.35).move_to(SCREEN_C)
        lines = {key(e): Line(P(e[0]), P(e[1]), color=INK, stroke_width=11).set_z_index(2) for e in EDGES}
        fig = VGroup(*lines.values())
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(FadeIn(screen), GrowFromCenter(fig), run_time=0.7)
        title = hook("Can you wipe this off", "in three swipes?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(1.2)

        # --- the rules ---------------------------------------------------------------------
        cap.show("Wipe it off in three swipes")
        self.wait(1.0)
        cap.show("Finger stays down. No repeats")
        f = finger(P("TL"), ACCENT)
        self.play(GrowFromCenter(f), run_time=0.3)
        top_path = ["TL", "C", "E", "TR"]
        tint = [Line(P(a), P(b), color=ACCENT, stroke_width=11).set_z_index(3)
                for a, b in zip(top_path, top_path[1:])]
        for ln, (a, b) in zip(tint, zip(top_path, top_path[1:])):
            self.play(f.animate.move_to(P(b)), Create(ln), run_time=0.35, rate_func=linear)
        # a repeat: back over a wiped line
        cross1 = label("✗ no repeats", 52, RED).move_to(SCREEN_C + np.array([0, -2.65, 0]))
        self.play(f.animate.move_to(P("E")).set_color(RED), FadeIn(cross1), run_time=0.5)
        self.wait(0.4)
        # a lift: the finger leaves the glass
        cross2 = label("✗ no lifting", 52, RED).move_to(SCREEN_C + np.array([0, -2.65, 0]))
        self.play(FadeOut(f), FadeOut(cross1), FadeIn(cross2), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(cross2), FadeOut(VGroup(*tint)), FadeOut(title), run_time=0.4)

        # --- pause and try ----------------------------------------------------------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X, 5.6, 0], radius=0.8, tick_sound=SFX["tick"])

        # --- odd points ---------------------------------------------------------------------
        odd = odd_points(EDGES)
        dots = {n: Dot(P(n), radius=0.27, color=ACCENT).set_z_index(6) for n in odd}
        halos = {n: Dot(P(n), radius=0.44, color=ACCENT).set_opacity(0.25).set_z_index(5) for n in odd}
        order = ["A", "C", "D", "G", "H", "F", "E", "B"]
        assert sorted(order) == odd
        self.play(fig.animate.set_color(MUTED), run_time=0.3)
        cap.show("Odd points are swipe ends", extra=self.top("Odd points: 0"))
        for k, n in enumerate(order, 1):
            self.add_sound(SFX["pop"], gain=-8)
            self.play(GrowFromCenter(dots[n]), FadeIn(halos[n]), *self.top(f"Odd points: {k}"),
                      run_time=0.3)
            self.wait(0.1)
        self.wait(0.4)

        # --- pairs: 2 ends per swipe -------------------------------------------------------
        pairs = [("A", "B"), ("C", "E"), ("D", "F"), ("G", "H")]
        cols = [PIECES[0], PIECES[1], PIECES[2], PIECES[3]]
        recolor = []
        for (a, b), c in zip(pairs, cols):
            for n in (a, b):
                recolor += [dots[n].animate.set_color(c), halos[n].animate.set_color(c)]
        self.add_sound(SFX["pop"])
        cap.show("Eight odd points: four swipes", extra=[*recolor, *self.top("8 ends ÷ 2 = 4 swipes", ACCENT, 56)])
        self.wait(1.2)

        # --- two fingers --------------------------------------------------------------------
        (c, d), (e, f2) = FOLD_PAIR
        self.play(FadeOut(VGroup(*dots.values(), *halos.values())), fig.animate.set_color(INK),
                  *self.top("Swipes: 0 of 3"), run_time=0.4)
        for ln in (lines[key(FOLD_PAIR[0])], lines[key(FOLD_PAIR[1])]):
            ln.set_color(PIECES[1])
        fa, fb = finger(P(c), PIECES[1]), finger(P(e), PIECES[1])
        same = label("parallel, same length", 44, PIECES[1]).move_to(SCREEN_C + np.array([0, -2.65, 0]))
        self.add_sound(SFX["pop"])
        cap.show("Use two fingers", extra=[GrowFromCenter(fa), GrowFromCenter(fb), FadeIn(same),
                                           Flash(P(c), color=PIECES[1], flash_radius=0.6),
                                           Flash(P(e), color=PIECES[1], flash_radius=0.6)])
        self.wait(1.0)

        # --- both slide down in one swipe ----------------------------------------------------
        cap.show("Two lines, one swipe", extra=self.top("Swipes: 1 of 3", GOOD), run_time=0.4)
        self.wipe([fa, fb], [[c, d], [e, f2]], lines, 1.2, [PIECES[1], PIECES[1]])
        self.add_sound(SFX["snip"])
        self.play(FadeOut(fa), FadeOut(fb), FadeOut(same), run_time=0.4)
        self.wait(0.4)

        # --- the other two swipes -----------------------------------------------------------
        one = finger(P(STROKES[0][0]), PIECES[0])
        self.play(GrowFromCenter(one), run_time=0.3)
        beat(self, "swipe two")
        self.play(*self.top("Swipes: 2 of 3", GOOD), run_time=0.4)
        for i, (path, col) in enumerate(zip(STROKES, (PIECES[0], PIECES[2]))):
            if i:
                one.move_to(P(path[0]))
                beat(self, "swipe three")
                self.play(GrowFromCenter(one), *self.top("Swipes: 3 of 3", GOOD), run_time=0.3)
            self.wipe([one], [path], lines, 0.3 if len(path) > 6 else 0.35, [col])
            self.play(FadeOut(one), run_time=0.25)
            self.wait(0.1)

        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        ok = badge("CLEAN ✓", GOOD).move_to(SCREEN_C)
        cap.show("Three swipes ✓", GOOD, extra=[FadeIn(ok), Flash(SCREEN_C, color=GOOD, flash_radius=1.2)])
        self.wait(1.2)

        # --- Level 2 -------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(FadeOut(ok), FadeOut(self._top), FadeOut(credit), run_time=0.3)
        self._top = None
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.5, 0])
        sub = label("3 × 5 grid", 56, INK).move_to([CENTRE_X, 5.5, 0])
        cell = 1.15
        g0 = SCREEN_C + np.array([-cell * GRID_COLS / 2, cell * GRID_ROWS / 2, 0])
        glines = VGroup(*[
            Line(g0 + cell * np.array([a[1], -a[0], 0]), g0 + cell * np.array([b[1], -b[0], 0]),
                 color=INK, stroke_width=9).set_z_index(2)
            for a, b in grid_edges(GRID_ROWS, GRID_COLS)])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(sub), Create(glines, lag_ratio=0.02), run_time=1.1)
        fing = finger(g0, ACCENT)
        one_f = label("one finger only", 44, ACCENT).move_to(SCREEN_C + np.array([0, -2.65, 0]))
        self.play(GrowFromCenter(fing), FadeIn(one_f), run_time=0.4)
        cap.show("One finger: how many swipes?")
        ask = label("? swipes", 72, ACCENT).move_to([CENTRE_X, -2.4, 0])
        self.play(FadeIn(ask), run_time=0.3)
        self.wait(1.2)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(2.0)
