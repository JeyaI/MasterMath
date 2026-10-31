"""Short 0001 - Turn a plus-shaped cross into a square with 4 pieces.

Level 1 (solved on screen): 2 cuts at slopes 1/2 and -2 -> 4 pieces slide into a sqrt(5) square.
Level 2 (comment challenge): what's the slope of the yellow cut?  -> 1/2

Geometry comes from verify.py, so what you see is exactly what was checked.
Render via the CLI:  ms preview 0001   /   ms render 0001
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, LEFT, PI, RIGHT, UL, UP, UR,
    Create, DashedVMobject, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate,
    Line, MathTex, Polygon, Rectangle, Scene, Square, VGroup, Write, there_and_back, smooth,
    LaggedStart, AnimationGroup,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import cross, cuts, pieces_and_targets  # noqa: E402

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
S = 1.45                                   # puzzle units -> frame units
STAGE = np.array([CENTRE_X, STAGE_Y, 0.0])
SQUARE_CENTRE = np.array([0.5, 1.5])       # centre of the target square in puzzle units
(CUT1_A, CUT1_B), (CUT2_A, CUT2_B) = cuts()


def P(x: float, y: float) -> np.ndarray:
    return STAGE + S * np.array([x, y, 0.0])


def poly(coords, **kw) -> Polygon:
    pts = list(coords)[:-1]                # shapely repeats the first point at the end
    return Polygon(*[P(x, y) for x, y in pts], **kw)


class Short(Scene):
    def construct(self):
        cap = Captions(self)

        # --- 0-3 s  hook: the cross pops in, then the question ------------------
        beat(self, "hook")
        title = hook("Can you cut this cross", "into 4 pieces that make a square?")
        cells = VGroup(*[
            Square(side_length=S, fill_color=GRID, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(P(x, y))
            for x, y in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1))
        ])
        credit = footer("Classic dissection · after H. E. Dudeney")
        for i, c in enumerate(cells):
            self.add_sound(SFX["pop"], time_offset=0.14 * i)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in cells], lag_ratio=0.35), run_time=1.2)
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(1.0)

        # --- 3-6 s  the setup ---------------------------------------------------
        cap.show("5 squares, each 1×1")
        self.wait(1.4)
        cap.show("Cut it into 4 pieces…")
        self.wait(1.2)

        # --- 6-12 s  pause and try ---------------------------------------------
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X + 2.45, STAGE_Y + 2.45, 0], radius=0.62, tick_sound=SFX["tick"])

        # --- 12-19 s  the insight: area 5 -> side sqrt(5) = diagonal of a 2x1 box ---------
        cap.show("A square of area 5…")
        self.wait(1.2)
        box = DashedVMobject(Rectangle(width=2 * S, height=S, color=ACCENT, stroke_width=5).move_to(P(0, 0)),
                             num_dashes=40)
        two = label("2", 48, ACCENT).next_to(box, DOWN, buff=0.15)
        one = label("1", 48, ACCENT).next_to(box, RIGHT, buff=0.15)
        diag = Line(P(*CUT1_A), P(*CUT1_B), color=ACCENT, stroke_width=9)
        root5 = MathTex(r"\sqrt{5}", color=ACCENT, font_size=72).move_to(P(-0.5, 0.2))
        cap.show("has side √5", extra=[Create(box), FadeIn(two), FadeIn(one)])
        self.wait(0.6)
        self.play(Create(diag), run_time=0.8)
        self.play(Write(root5), run_time=0.6)
        cap.show("…the diagonal of a 2×1 box!", ACCENT)
        self.wait(1.4)

        # --- 19-23 s  two cuts --------------------------------------------------
        pieces_data = pieces_and_targets()
        pieces = VGroup(*[
            poly(p.exterior.coords, fill_color=GRID, fill_opacity=1, stroke_color=INK, stroke_width=3)
            for p, _ in pieces_data
        ])
        # LaggedStart added each cell individually, so remove them individually.
        self.remove(*cells); self.add(pieces, box, two, one, diag, root5)
        cut1 = Line(P(*CUT1_A), P(*CUT1_B), color=ACCENT, stroke_width=9)
        cut2 = Line(P(*CUT2_A), P(*CUT2_B), color=ACCENT, stroke_width=9)
        self.play(FadeOut(box), FadeOut(two), FadeOut(one), FadeOut(root5), run_time=0.4)
        self.add(cut1); self.remove(diag)
        cap.show("Cut along it…")
        self.add_sound(SFX["snip"])
        self.play(Indicate(cut1, color=INK, scale_factor=1.0), run_time=0.6)
        cap.show("…and once more at 90°")
        self.add_sound(SFX["snip"])
        self.play(Create(cut2), run_time=0.6)
        self.wait(0.5)

        # --- 23-31 s  pieces separate, then slide into the square ---------------
        self.play(
            *[pc.animate.set_fill(col, opacity=1) for pc, col in zip(pieces, PIECES)],
            FadeOut(cut1), FadeOut(cut2), run_time=0.5,
        )
        explode = []
        for pc, (p, _) in zip(pieces, pieces_data):
            c = np.array([p.centroid.x, p.centroid.y])
            explode.append(0.35 * c / np.linalg.norm(c))
        cap.show("4 identical pieces")
        self.play(*[pc.animate.shift(S * np.array([*e, 0])) for pc, e in zip(pieces, explode)], run_time=0.7)
        self.wait(0.4)

        cap.show("Slide them over…")
        moves = []
        for k, (pc, (_, (dx, dy)), e) in enumerate(zip(pieces, pieces_data, explode)):
            delta = np.array([dx, dy]) - SQUARE_CENTRE - e   # land the square centred on the stage
            moves.append(pc.animate.shift(S * np.array([*delta, 0])))
            self.add_sound(SFX["pop"], time_offset=0.55 + 0.45 * k)
        self.play(LaggedStart(*moves, lag_ratio=0.45), run_time=2.6, rate_func=smooth)

        sq_corners = [P(x - 0.5, y - 1.5) for x, y in ((0, 0), (2, 1), (1, 3), (-1, 2))]
        outline = Polygon(*sq_corners, color=GOOD, stroke_width=8)
        side = MathTex(r"\sqrt{5}", color=GOOD, font_size=72)
        mid = (sq_corners[0] + sq_corners[1]) / 2
        side.move_to(mid + 0.6 * np.array([0.45, -0.9, 0]))
        self.add_sound(SFX["chime"])
        cap.show("One perfect square ✓", GOOD, extra=[Create(outline), Write(side)])
        self.play(Flash(outline.get_center(), color=GOOD, flash_radius=2.6, num_lines=16), run_time=0.8)
        self.wait(1.6)

        # --- 31-46 s  Level 2: comment challenge ---------------------------------
        beat(self, "Level 2")
        solved = VGroup(pieces, outline, side)
        self.play(FadeOut(title), solved.animate.scale(0.42).move_to([CENTRE_X - 2.3, 5.9, 0]), run_time=0.8)
        tag = badge("LEVEL 2").move_to([CENTRE_X + 1.1, 6.35, 0])
        q1 = label("What's the slope", 60)
        q2 = label("of the yellow cut?", 60)
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.2)
        if qs.width > 4.6:
            qs.scale_to_fit_width(4.6)
        qs.move_to([CENTRE_X + 1.1, 5.0, 0])
        self.add_sound(SFX["chime"], gain=-8)
        cap.clear()
        self.play(GrowFromCenter(tag), FadeIn(q1), FadeIn(q2), run_time=0.6)

        # big diagram: the 5 unit squares, so rise and run can be counted, and one cut
        grid = VGroup(*[
            Square(side_length=S, fill_opacity=0, stroke_color=MUTED, stroke_width=4).move_to(P(x, y))
            for x, y in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1))
        ])
        cut = Line(P(*CUT1_A), P(*CUT1_B), color=ACCENT, stroke_width=9)
        diagram = VGroup(grid, cut).shift(0.4 * DOWN)
        ask = label("slope = ?", 76, ACCENT).move_to([CENTRE_X, -2.3, 0])
        self.play(Create(grid), run_time=0.6)
        self.play(Create(cut), run_time=0.6)
        self.play(Write(ask), run_time=0.6)

        cap.show("Comment just the number ↓", ACCENT)
        hint = label("rise ÷ run", 34, MUTED)
        hint.move_to([CENTRE_X, credit.get_y() + 0.02, 0])
        self.play(FadeOut(credit), FadeIn(hint), run_time=0.4)   # credit stays in the description
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.1), run_time=1.0, rate_func=there_and_back)
            self.wait(1.6)
        self.wait(1.0)
