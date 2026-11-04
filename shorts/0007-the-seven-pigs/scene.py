"""Short 0007 - The Seven Pigs (Dudeney no. 165).

Level 1 (solved on screen): the pigs never move, the fences do. Three parallel fences make only 4 sties, so
pigs crowd. Fences that cross each other add 2, 2, 3 sties: 7, the most 3 lines can make, one pig in each.
Level 2 (comment challenge): 4 crossing fences shut in 3 sties that touch no wall.

Pen, pigs, fences and sties all come from verify.py, so what you see is exactly what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, Circle, Create, FadeIn, FadeOut, GrowFromCenter, Indicate, LaggedStart, Line, ManimColor,
    Polygon, Scene, Square, Uncreate, VGroup, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, INK, MUTED, PIECES  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    CENTRE_PIG, FENCES, L2_ALL, L2_CLOSED, L2_FENCES, PARALLEL, PARALLEL_STIES, PIGS, SIDE, STIES, sties,
    pigs_in, touches_wall,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
K = 6.4 / SIDE                      # screen units per pen unit
X0, Y0 = CENTRE_X - 3.2, 0.8 - 3.2  # screen position of the pen's lower-left corner
RED = ManimColor("#FF5252")
PEN_FILL = ManimColor("#1B2735")
PIG = ManimColor("#F7A8BC")
STY_COLORS = [*PIECES, ACCENT, GOOD, ManimColor("#B39DDB")]
assert (len(PIGS), len(STIES), len(PARALLEL_STIES), L2_CLOSED) == (7, 7, 4, 3)


def S(p) -> np.ndarray:
    return np.array([X0 + K * p[0], Y0 + K * p[1], 0.0])


def fence(f, color=INK, width: float = 9) -> Line:
    return Line(S(f[0]), S(f[1]), color=color, stroke_width=width).set_z_index(4)


def region(poly, color, opacity: float = 0.55) -> Polygon:
    return Polygon(*[S(c) for c in list(poly.exterior.coords)[:-1]], fill_color=color, fill_opacity=opacity,
                   stroke_width=0).set_z_index(1)


def pig() -> VGroup:
    body = Circle(radius=0.16, fill_color=PIG, fill_opacity=1, stroke_color=BG, stroke_width=2)
    snout = Circle(radius=0.075, fill_color=ManimColor("#E8869F"), fill_opacity=1, stroke_width=0).shift(0.07 * DOWN)
    eyes = VGroup(*[Circle(radius=0.025, fill_color=BG, fill_opacity=1, stroke_width=0).shift([dx, 0.06, 0])
                    for dx in (-0.06, 0.06)])
    return VGroup(body, snout, eyes).set_z_index(6)


class Short(Scene):
    def count(self, n: int, color=INK):
        """Running total in the title area. A hard cut: a cross-fade smears the digits."""
        if getattr(self, "_count", None) is not None:
            self.remove(self._count)
        self._count = label(f"{n} sties", 84, color).move_to([CENTRE_X, 5.6, 0])
        self.add(self._count)

    def construct(self):
        cap = Captions(self)
        pen = Square(side_length=6.4, fill_color=PEN_FILL, fill_opacity=1, stroke_color=MUTED,
                     stroke_width=10).move_to(S((SIDE / 2, SIDE / 2))).set_z_index(0)
        pigs = VGroup(*[pig().move_to(S(p)) for p in PIGS])

        # --- hook: pop in the pen, then the question --------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(pen), run_time=0.35)
        self.add_sound(SFX["pop"], gain=-4)
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pigs], lag_ratio=0.12), run_time=0.7)
        self.remove(*pigs)
        self.add(pigs)
        title = hook("Seven pigs, one pen", "Can 3 fences give each pig a sty?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        self.wait(1.5)

        # --- the rules ------------------------------------------------------------------------
        sweep = fence(((1, 0), (1, 10)), ACCENT)
        cap.show("3 straight fences", extra=[Create(sweep)])
        self.play(sweep.animate.shift(K * 8 * np.array([1.0, 0, 0])), run_time=1.3)
        self.play(FadeOut(sweep), run_time=0.2)
        self.play(FadeOut(title), run_time=0.2)

        bad = fence(((PIGS[3][0], 0), (PIGS[3][0], 10)), RED)
        self.add_sound(SFX["snip"])
        cap.show("One pig per sty", extra=[Create(bad)])
        self.play(Indicate(pigs[3], color=RED, scale_factor=1.8), run_time=0.6)
        no = label("No fence may touch a pig", 40, RED).move_to([CENTRE_X, 5.6, 0])
        self.play(FadeIn(no), run_time=0.3)
        self.wait(1.2)
        self.play(FadeOut(bad), FadeOut(no), run_time=0.3)

        # --- the failed try: three parallel fences ----------------------------------------------
        par = [fence(f, INK) for f in PARALLEL]
        self.add_sound(SFX["snip"])
        cap.show("Parallel fences: 4 sties",
                 extra=[LaggedStart(*[Create(p) for p in par], lag_ratio=0.35, run_time=1.2)])
        self.wait(0.2)
        self.count(4)
        self.wait(0.6)

        tints = [region(s, RED, 0.5) for s in PARALLEL_STIES if len(pigs_in(s)) >= 2]
        self.add_sound(SFX["tick"])
        cap.show("Pigs still share", RED, extra=[FadeIn(t) for t in tints])
        self.play(*[Indicate(t, color=RED, scale_factor=1.0) for t in tints], run_time=0.7)
        self.play(*[Indicate(t, color=RED, scale_factor=1.0) for t in tints], run_time=0.7)
        self.play(*[FadeOut(t) for t in tints], *[Uncreate(p) for p in par], run_time=0.6)
        self.remove(self._count)
        self._count = None

        # --- pause and try ------------------------------------------------------------------------
        cap.show("Pause and try it", ACCENT)
        others = VGroup(*[p for i, p in enumerate(pigs) if i != CENTRE_PIG])
        self.play(others.animate.set_opacity(0.3), pigs[CENTRE_PIG].animate.set_opacity(0), run_time=0.25)
        countdown(self, 5, center=S((5, 5)), radius=0.95, tick_sound=SFX["tick"])
        self.play(pigs.animate.set_opacity(1), run_time=0.25)

        # --- the solution: fences cross ------------------------------------------------------------
        sols = [fence(f, INK) for f in FENCES]
        cap.show("So make fences cross")
        self.wait(0.5)

        def flash(k: int):
            """Tint the sties that fence k has just split, then fade them."""
            line = LineLike(FENCES[k])
            hit = [s for s in sties(FENCES[: k + 1]) if s.intersection(line).length > 1e-6 or s.boundary.distance(line) < 1e-6]
            return [region(s, STY_COLORS[i % 7], 0.55) for i, s in enumerate(hit)]

        totals = (2, 4, 7)
        texts = ("First fence: 2 sties", "Second crosses it: 4", "Third crosses both: 7")
        for k, text in enumerate(texts):
            self.add_sound(SFX["snip"])
            cap.show(text, run_time=0.3, extra=[Create(sols[k], run_time=0.9)])
            tints = flash(k)
            self.add_sound(SFX["pop"], gain=-3)
            self.add(*tints)
            self.count(totals[k])
            self.wait(0.7)
            self.play(*[FadeOut(t) for t in tints], run_time=0.3)
            self.wait(0.2)

        # --- the triangle ---------------------------------------------------------------------------
        tri = next(s for s in STIES if not touches_wall(s))
        around = [s for s in STIES if s is not tri and s.boundary.intersection(tri.boundary).length > 1e-6]
        tri_r = region(tri, ACCENT, 0.8)
        around_r = [region(s, PIECES[1], 0.45) for s in around]
        cap.show("A triangle in the middle", extra=[FadeIn(tri_r), *[FadeIn(r) for r in around_r]])
        self.play(Indicate(tri_r, color=INK, scale_factor=1.3), Indicate(pigs[CENTRE_PIG], scale_factor=1.8), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(tri_r), *[FadeOut(r) for r in around_r], run_time=0.3)

        # --- sort the pigs: every sty its colour -------------------------------------------------------
        final = [region(s, STY_COLORS[i], 0.55) for i, s in enumerate(STIES)]
        self.add_sound(SFX["chime"], gain=-6)
        cap.show("Sort the pigs", extra=[LaggedStart(*[FadeIn(r) for r in final], lag_ratio=0.12, run_time=1.2)])
        self.wait(0.4)
        marks = []
        for i, s in enumerate(STIES):
            p = pigs[pigs_in(s)[0]]
            m = label("✓", 34, GOOD).move_to(p.get_center() + 0.34 * UP).set_z_index(8)
            marks.append(m)
        self.play(LaggedStart(*[Indicate(p, scale_factor=1.7) for p in pigs], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(m, scale=1.5) for m in marks], lag_ratio=0.1), run_time=1.2)
        self.wait(0.5)

        # --- payoff -------------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        self.remove(self._count)
        self._count = None
        cap.show("Every pig has a sty ✓", GOOD)
        done = label("7 sties, 7 pigs", 84, GOOD).move_to([CENTRE_X, 5.6, 0])
        self.play(FadeIn(done), run_time=0.4)
        self.wait(1.6)

        # --- Level 2: four fences ----------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.25)
        self.clear()

        pen2 = pen.copy()
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.6, 0])
        q = VGroup(*[label(t, 42) for t in ("4 fences, all crossing.", "How many sties are shut in,", "touching no wall?")])
        q.arrange(DOWN, buff=0.15).move_to([CENTRE_X, 5.1, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(q), FadeIn(pen2), run_time=0.6)
        l2 = [fence(f, INK) for f in L2_FENCES]
        self.add_sound(SFX["snip"])
        self.play(LaggedStart(*[Create(f) for f in l2], lag_ratio=0.3), run_time=1.4)
        dots = VGroup(*[Circle(radius=0.07, fill_color=ACCENT, fill_opacity=1, stroke_width=0).move_to(S(c)).set_z_index(5)
                        for c in __import__("verify").L2_CROSSINGS])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1), run_time=0.6)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(dots, color=INK, scale_factor=1.5), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)


def LineLike(f):
    """The fence as a shapely line, run a little past the walls."""
    from shapely.geometry import LineString
    (x0, y0), (x1, y1) = f
    return LineString([(x0 - (x1 - x0) * .01, y0 - (y1 - y0) * .01), (x1 + (x1 - x0) * .01, y1 + (y1 - y0) * .01)])
