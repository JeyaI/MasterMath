"""Short 0013 - The Eight Rooks (Dudeney no. 295).

Level 1 (solved on screen): one rook per row and per column. Row by row the free columns shrink,
8, 7, 6, ... 1, and the choices multiply: 8! = 40,320.
Level 2 (comment challenge): 6 x 6 board, 6 rooks -> 720.

The board sizes, placements and the ladder come from verify.py, so what you see is what was checked.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, Circle, Create, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    Polygon, Rectangle, RoundedRectangle, Scene, Square as Cell, VGroup, interpolate_color, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    ANTI, DIAGONAL, L2_COLS, L2_N, L2_WAYS, LADDER, N, SCATTER, WAYS, rooks,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
CELL = 0.78
BX, BY = CENTRE_X - 0.3, STAGE_Y + 0.2      # board centre; the ladder sits to its right
LIGHT = interpolate_color(GRID, MUTED, 0.4)
HOT = PIECES[0]
assert (N, WAYS, L2_WAYS) == (8, 40320, 3628800)


def stage(cell: float, n: int, x: float = CENTRE_X, y: float = STAGE_Y):
    origin = np.array([x - cell * (n - 1) / 2, y - cell * (n - 1) / 2, 0.0])
    return lambda c, r: origin + cell * np.array([c, n - 1 - r, 0.0])      # r = row, 0 at the top


def board(P, cell: float, n: int):
    sq = {(c, r): Cell(side_length=cell, stroke_width=0, fill_opacity=1,
                       fill_color=GRID if (c + r) % 2 == 0 else LIGHT).move_to(P(c, r))
          for c in range(n) for r in range(n)}
    return VGroup(*sq.values()), sq


def rook(cell: float, color=INK) -> VGroup:
    ink = dict(fill_color=color, fill_opacity=1, stroke_color=BG, stroke_width=1.5)
    base = RoundedRectangle(corner_radius=0.05, width=0.74, height=0.15, **ink).move_to([0, -0.4, 0])
    body = Polygon([-0.27, -0.33, 0], [0.27, -0.33, 0], [0.18, 0.12, 0], [-0.18, 0.12, 0], **ink)
    top = Rectangle(width=0.54, height=0.12, **ink).move_to([0, 0.18, 0])
    teeth = [Rectangle(width=0.14, height=0.14, **ink).move_to([x, 0.31, 0]) for x in (-0.2, 0, 0.2)]
    return VGroup(base, body, top, *teeth).scale(cell * 0.92).set_z_index(10)


def rays(P, c: int, r: int, n: int, color=ACCENT, width: float = 7) -> VGroup:
    return VGroup(Line(P(0, r), P(n - 1, r), color=color, stroke_width=width),
                  Line(P(c, 0), P(c, n - 1), color=color, stroke_width=width)).set_z_index(5)


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        P = stage(CELL, N, BX, BY)
        tiles, sq = board(P, CELL, N)
        rim = Cell(side_length=CELL * N, color=MUTED, stroke_width=4).move_to(tiles)
        men = lambda cols: [rook(CELL).move_to(P(c, r)) for c, r in rooks(cols)]
        ROW = (3, 0)   # Dudeney's Fig. 1: all eight rooks along one rank

        # --- hook: the board, eight rooks in a row, then the question -----------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(FadeIn(tiles), Create(rim), run_time=0.5)
        row_rooks = VGroup(*[rook(CELL).move_to(P(c, 3)) for c in range(N)])
        self.add_sound(SFX["pop"], time_offset=0.3)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in row_rooks], lag_ratio=0.07), run_time=0.8)
        self.remove(*row_rooks)
        self.add(row_rooks)
        title = VGroup(*[label(t, 56, INK) for t in
                         ("Can you place 8 rooks", "so that none of them", "attack each other?")]
                       ).arrange(DOWN, buff=0.18).move_to([CENTRE_X, TITLE_Y, 0])
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(3.5)

        # --- the rules ----------------------------------------------------------------------
        lone = row_rooks[3]
        others = VGroup(*[m for i, m in enumerate(row_rooks) if i != 3])
        shoot = rays(P, 3, 3, N)
        self.add_sound(SFX["pop"])
        cap.show("A rook attacks along its row and column.", extra=[FadeOut(others), Create(shoot)])
        self.wait(2.4)

        tint = VGroup(*[Cell(side_length=CELL, stroke_width=0, fill_color=ACCENT, fill_opacity=0.32)
                        .move_to(P(c, r)) for c in range(N) for r in range(N)]).set_z_index(2)
        self.add_sound(SFX["snip"])
        cap.show("Every square must be covered.", extra=[FadeOut(shoot), FadeIn(others), FadeIn(tint)])
        self.wait(2.2)

        diag = VGroup(*men(DIAGONAL))
        diag_rays = VGroup(*[rays(P, c, r, N, width=5) for c, r in rooks(DIAGONAL)])
        self.add_sound(SFX["pop"])
        cap.show("Here, no rook attacks another one.", extra=[
            FadeOut(row_rooks), FadeOut(tint), FadeIn(diag), Create(diag_rays)])
        self.wait(2.3)

        anti, scatter = VGroup(*men(ANTI)), VGroup(*men(SCATTER))
        self.add_sound(SFX["pop"])
        cap.show("There are other ways, too.", extra=[FadeOut(diag_rays), FadeOut(diag), FadeIn(anti)],
                 run_time=0.4)
        self.wait(0.8)
        self.add_sound(SFX["pop"])
        self.play(FadeOut(anti), FadeIn(scatter), run_time=0.4)
        self.wait(0.6)
        cap.show("How many ways are there in all?", ACCENT, extra=[FadeOut(title)])
        self.wait(2.6)

        # --- pause and try (the question stays up as the caption) ---------------------------
        pause = label("Pause and try it", 64, ACCENT).move_to([CENTRE_X, TITLE_Y, 0])
        beat(self, "Pause and try it")
        self.play(FadeIn(pause, shift=0.25 * UP), FadeOut(scatter), run_time=0.45)
        countdown(self, 5, center=[BX, BY, 0], radius=0.95, tick_sound=SFX["tick"])

        # --- two in a row attack ------------------------------------------------------------
        a, b = rook(CELL).move_to(P(1, 2)), rook(CELL).move_to(P(5, 2))
        beam = Line(P(1, 2), P(5, 2), color=HOT, stroke_width=9).set_z_index(6)
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(a), GrowFromCenter(b), run_time=0.3)
        self.add_sound(SFX["snip"])
        cap.show("Two rooks in a row would attack each other.", HOT, extra=[
            FadeOut(pause), Create(beam), a.animate.set_color(HOT), b.animate.set_color(HOT)])
        self.play(Flash(P(3, 2), color=HOT, flash_radius=0.6), run_time=0.5)
        self.wait(0.5)

        def band(vertical: bool, k: int):
            w, h = (CELL, CELL * N) if vertical else (CELL * N, CELL)
            box = Rectangle(width=w, height=h, stroke_width=0, fill_color=ACCENT, fill_opacity=0.3)
            c = np.array([P(k, 0)[0], tiles.get_center()[1], 0]) if vertical else \
                np.array([tiles.get_center()[0], P(0, k)[1], 0])
            return box.move_to(c).set_z_index(2)

        row_bands = VGroup(*[band(False, k) for k in range(N)])
        self.add_sound(SFX["chime"], gain=-10)
        cap.show("So each row has exactly one rook.", extra=[
            FadeOut(beam), FadeOut(VGroup(a, b)),
            LaggedStart(*[FadeIn(x) for x in row_bands], lag_ratio=0.12)], run_time=1.2)
        self.wait(0.6)
        col_bands = VGroup(*[band(True, k) for k in range(N)])
        self.add_sound(SFX["chime"], gain=-10)
        cap.show("And each column has exactly one, too.", extra=[
            FadeOut(row_bands), LaggedStart(*[FadeIn(x) for x in col_bands], lag_ratio=0.12)], run_time=1.2)
        self.wait(0.3)
        self.play(FadeOut(col_bands), run_time=0.3)

        # --- row by row: 8, 7, 6, ... 1 -----------------------------------------------------
        lx = P(N - 1, 0)[0] + CELL / 2 + 0.38
        ladder = [label(str(k), 44, ACCENT).move_to([lx, P(0, r)[1], 0]) for r, k in enumerate(LADDER)]
        wall: list = []
        placed: list = []

        def step(r: int, glow: float, move: float, say: str | None = None):
            used = set(SCATTER[:r])
            free = VGroup(*[Cell(side_length=CELL, stroke_width=0, fill_color=ACCENT, fill_opacity=0.45)
                            .move_to(P(c, r)).set_z_index(3) for c in range(N) if c not in used])
            num = ladder[r]
            extra = [FadeIn(free), FadeIn(num, shift=0.2 * UP)]
            self.add_sound(SFX["pop"], gain=-6)
            if say:
                cap.show(say, extra=extra, run_time=min(0.45, glow))
            else:
                self.play(*extra, run_time=glow)
            piece = rook(CELL).move_to(P(SCATTER[r], r))
            self.add_sound(SFX["pop"])
            self.play(FadeIn(piece, shift=0.8 * DOWN), run_time=move)
            cover = Rectangle(width=CELL, height=CELL * N, stroke_width=0, fill_color=HOT,
                              fill_opacity=0.32).move_to(
                np.array([P(SCATTER[r], 0)[0], tiles.get_center()[1], 0])).set_z_index(4)
            picked = Cell(side_length=CELL, stroke_width=0, fill_color=HOT, fill_opacity=0.85
                          ).move_to(P(SCATTER[r], r)).set_z_index(5)      # the picked square, in red
            lane = Rectangle(width=CELL * N, height=CELL, stroke_width=0, fill_color=HOT,
                             fill_opacity=0.32).move_to(
                np.array([tiles.get_center()[0], P(0, r)[1], 0])).set_z_index(4)   # the attacked row
            self.play(FadeOut(free), FadeIn(cover), FadeIn(lane), FadeIn(picked), run_time=move)
            placed.append(piece)
            wall.extend([cover, lane, picked])

        step(0, 0.9, 0.45, "In row 1, you can choose any of 8 columns.")
        self.wait(0.3)
        step(1, 0.9, 0.45, "In row 2, only 7 columns are left.")
        self.wait(0.3)
        step(2, 0.35, 0.2, "Then 6 choices, then 5, then 4, and so on.")
        for r in range(3, N - 1):
            step(r, 0.3, 0.2)
        self.wait(0.3)
        step(N - 1, 0.7, 0.4, "The last row has only one choice.")
        self.wait(0.4)

        # --- multiply -------------------------------------------------------------------------
        parts = VGroup(*[label(str(k), 56, ACCENT) for k in LADDER])
        for i in range(N - 1):
            parts.add(label("×", 56, INK))
        order = []
        for i in range(N):
            order.append(parts[i])
            if i < N - 1:
                order.append(parts[N + i])
        eq = VGroup(*order)
        eq.arrange(buff=0.16).move_to([CENTRE_X, TITLE_Y, 0])
        if eq.width > 7.0:
            eq.scale_to_fit_width(7.0)
        flights = [ladder[i].animate.move_to(parts[i].get_center()) for i in range(N)]
        self.add_sound(SFX["snip"])
        cap.show("We multiply all the choices together.", extra=flights, run_time=1.0)
        self.add(parts)
        self.remove(*ladder)
        self.play(*[FadeIn(x) for x in parts[N:]], run_time=0.4)
        self.wait(0.5)
        cap.show("8 × 7 × 6 × ... × 1", ACCENT)
        self.wait(0.6)

        # --- payoff -----------------------------------------------------------------------------
        beat(self, "payoff")
        big = label("40,320", 120, GOOD).move_to([CENTRE_X, TITLE_Y, 0])
        self.add_sound(SFX["chime"])
        cap.show("There are 40,320 ways ✓", GOOD, extra=[
            FadeOut(parts), FadeIn(big), Flash(tiles.get_center(), color=GOOD, flash_radius=1.6)])
        self.wait(1.2)

        # --- Level 2 ----------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()

        c2 = 0.58
        P2 = stage(c2, L2_N, y=STAGE_Y + 0.5)
        tiles2, _ = board(P2, c2, L2_N)
        men2 = VGroup(*[rook(c2).move_to(P2(c, r)) for c, r in rooks(L2_COLS)])
        ask = label("? ways", 72, ACCENT).move_to([CENTRE_X, P2(0, L2_N - 1)[1] - c2 / 2 - 0.75, 0])
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.45, 0])
        q = VGroup(*[label(t, 44) for t in ("Same rules: a 10 by 10 board", "and 10 rooks.")]).arrange(DOWN, buff=0.12)
        q.move_to([CENTRE_X, 5.3, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(q), FadeIn(tiles2), run_time=0.6)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in men2], lag_ratio=0.1), FadeIn(ask), run_time=0.9)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
