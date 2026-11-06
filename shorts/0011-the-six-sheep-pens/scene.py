"""Short 0011 - The Six Sheep-Pens (Dudeney no. 205, the 12-match form).

Twelve matches. A 2 x 3 block of squares needs 17 (too many). Triangles share walls: a hexagon of
6 matches plus 6 spokes makes six equal pens. A second layout: two squares sharing a corner, each
cut by 2 inner matches into 3 pens. Level 2: a big triangle, 3 matches per side, cut into unit
triangles (answer held in short.yaml, not shown).

Shapes and numbers come from verify.py.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, RIGHT,
    Circle, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, GrowFromPoint, Indicate, LaggedStart, Line,
    Polygon, Scene, VGroup, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, INK, MUTED, PIECES  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    ALT_MATCHES, CENTRE, CORNERS, L2_MATCHES, L2_PENS, L2_SIDE, MATCHES, RIM, SPOKES,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
WOOD = "#E8C48A"
HEAD = "#E5484D"
assert L2_MATCHES == 18 and L2_PENS == 9 and L2_SIDE == 3       # answer is in short.yaml, not shown
assert len(MATCHES) == 12 and len(ALT_MATCHES) == 12

STAGE_Y = 1.9


def wrap(text: str, width: int = 30) -> str:
    return "\n".join(textwrap.wrap(text, width))


def stick(a, b, color=WOOD, w=15) -> VGroup:
    """A matchstick from a to b: wooden body, red head at the start."""
    a, b = np.array(a, float), np.array(b, float)
    body = Line(a, b, color=color, stroke_width=w)
    d = (b - a) / max(np.linalg.norm(b - a), 1e-6)
    head = Dot(a + d * 0.1, radius=0.13, color=HEAD)
    return VGroup(body, head)


class Short(Scene):
    # ---- helpers ------------------------------------------------------------------------------
    def set_top(self, text, color=ACCENT, size=52):
        new = label(text, size, color).move_to([CENTRE_X, 5.7, 0])
        old = getattr(self, "_top", None)
        if old is not None:
            self.remove(old)
        self.add(new)
        self._top = new

    def clear_top(self):
        if getattr(self, "_top", None) is not None:
            self.remove(self._top)
            self._top = None

    def cap(self, text, color=INK, width=30, **kw):
        return self.captions.show(wrap(text, width), color, **kw)

    # ---- the scene ----------------------------------------------------------------------------
    def construct(self):
        self.captions = Captions(self, y=-3.0)
        self._top = None
        H = np.array([CENTRE_X, STAGE_Y, 0.0])
        U = 3.0                                              # hexagon match length on screen

        def hp(p):                                           # verify.py hexagon point -> screen
            return H + U * np.array([p[0], p[1], 0.0])

        # ---- hook: a pile of twelve matches ----------------------------------------------------
        beat(self, "hook")
        rng = np.random.RandomState(11)
        pile = VGroup()
        for k in range(12):                                  # 2 tall x 6 wide, pointing up, slightly jittered
            row, col = divmod(k, 6)
            c = H + np.array([(col - 2.5) * 1.0 + rng.uniform(-0.05, 0.05),
                              (0.5 - row) * 2.5 + rng.uniform(-0.1, 0.1), 0])
            ang = np.pi / 2 + np.radians(rng.uniform(-12, 12))
            d = 1.1 * np.array([np.cos(ang), np.sin(ang), 0])
            pile.add(stick(c - d, c + d))
        title = hook("12 matches")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in pile], lag_ratio=0.12), run_time=1.3)
        self.remove(*pile)
        self.add(pile)
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.cap("Can you make 6 equally sized pens with 12 matches?")
        self.wait(1.5)

        # ---- the rules -------------------------------------------------------------------------
        self.cap("Use every match: no overlaps, no loose ends")
        self.play(Indicate(pile, color=ACCENT, scale_factor=1.05), run_time=1.0)
        self.wait(0.4)

        # ---- pause and try ---------------------------------------------------------------------
        self.play(FadeOut(title), run_time=0.3)
        self.cap("Pause and try it", ACCENT)
        countdown(self, 5, center=[CENTRE_X, 5.6, 0], radius=0.8, tick_sound=SFX["tick"])

        # ---- first try: a 2 x 3 block of squares needs 17 -------------------------------------
        self.cap("A 2 by 3 block of squares needs 17 matches: too many")
        cell = 1.95
        g0 = np.array([CENTRE_X - 1.5 * cell, STAGE_Y - cell, 0.0])
        segs = []
        for r in range(3):                                   # horizontals, 3 rows of 3
            for c in range(3):
                segs.append((g0 + cell * np.array([c, r, 0]), g0 + cell * np.array([c + 1, r, 0])))
        for c in range(4):                                   # verticals, 4 columns of 2
            for r in range(2):
                segs.append((g0 + cell * np.array([c, r, 0]), g0 + cell * np.array([c, r + 1, 0])))
        assert len(segs) == 17
        block = VGroup(*[stick(a, b, w=13 if False else 15, color=WOOD if i < 12 else HEAD)
                         for i, (a, b) in enumerate(segs)])
        self.play(FadeOut(pile), run_time=0.3)
        for i, s in enumerate(block):
            if i == 0:
                self.set_top("Matches used: 0 / 12", ACCENT)
        self.add_sound(SFX["pop"], gain=-8)
        for chunk, (lo, hi) in enumerate([(0, 6), (6, 12), (12, 17)]):
            self.play(LaggedStart(*[GrowFromCenter(block[i]) for i in range(lo, hi)], lag_ratio=0.18),
                      run_time=0.7 if hi < 17 else 0.8)
            self.remove(*block[lo:hi])
            self.add(*block[lo:hi])
            over = hi > 12
            self.set_top(f"Matches used: {hi} / 12", HEAD if over else ACCENT)
        self.play(Indicate(self._top, color=HEAD, scale_factor=1.15), run_time=0.6)
        self.wait(0.2)

        # ---- triangles share walls ---------------------------------------------------------------
        self.cap("Triangles share more walls, so try those")
        self.play(FadeOut(block), run_time=0.4)
        self.set_top("Matches used: 0 / 12", ACCENT)
        s_a = [stick(hp(CENTRE), hp(CORNERS[0])), stick(hp(CORNERS[0]), hp(CORNERS[1])),
               stick(hp(CORNERS[1]), hp(CENTRE))]
        self.play(LaggedStart(*[GrowFromCenter(s) for s in s_a], lag_ratio=0.3), run_time=0.8)
        self.set_top("Matches used: 3 / 12", ACCENT)
        s_b = [stick(hp(CORNERS[1]), hp(CORNERS[2])), stick(hp(CORNERS[2]), hp(CENTRE))]
        tri_a = Polygon(hp(CENTRE), hp(CORNERS[0]), hp(CORNERS[1]), stroke_width=0,
                        fill_color=PIECES[0], fill_opacity=0.4)
        self.play(FadeIn(tri_a), run_time=0.3)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in s_b], lag_ratio=0.3), run_time=0.8)
        self.set_top("Matches used: 5 / 12", ACCENT)
        shared = Line(hp(CENTRE), hp(CORNERS[1]), color=ACCENT, stroke_width=22).set_opacity(0.6)
        self.play(Indicate(s_a[2], color=ACCENT, scale_factor=1.0), FadeIn(shared), run_time=0.7)
        self.play(FadeOut(shared), run_time=0.2)
        self.play(FadeOut(VGroup(*s_a, *s_b, tri_a)), run_time=0.4)

        # ---- the hexagon ------------------------------------------------------------------------
        self.set_top("Matches used: 0 / 12", ACCENT)
        self.add_sound(SFX["pop"], gain=-8)
        self.cap("Six matches make a hexagon")
        rim = VGroup(*[stick(hp(a), hp(b)) for a, b in RIM])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in rim], lag_ratio=0.2), run_time=1.3)
        self.remove(*rim)
        self.add(rim)
        self.set_top("Matches used: 6 / 12", ACCENT)
        self.wait(0.3)

        # ---- the spokes -------------------------------------------------------------------------
        self.cap("Six spokes to the centre: each is a wall for two pens")
        spokes = VGroup(*[stick(hp(CENTRE), hp(c), color="#F4D9A6") for _, c in SPOKES])
        fills = []
        for k in range(6):
            a, b = CORNERS[k], CORNERS[(k + 1) % 6]
            tri = Polygon(hp(CENTRE), hp(a), hp(b), stroke_width=0, fill_color=PIECES[k % 4], fill_opacity=0.42)
            cen = (hp(CENTRE) + hp(a) + hp(b)) / 3
            fills.append(tri)
        self.add_sound(SFX["pop"], gain=-6)
        for k in range(6):
            self.play(GrowFromPoint(spokes[k], hp(CENTRE)), run_time=0.4)
            self.add(spokes[k])
            self.set_top(f"Matches used: {7 + k} / 12", ACCENT)
            if k >= 1:
                self.add_sound(SFX["tick"], gain=-8)
                self.play(FadeIn(fills[k - 1]), run_time=0.3)
        self.add_sound(SFX["tick"], gain=-8)
        self.play(FadeIn(fills[5]), run_time=0.3)

        # ---- payoff -------------------------------------------------------------------------------
        beat(self, "payoff")
        self.add_sound(SFX["chime"])
        hexa = VGroup(*fills, rim, spokes)
        self.set_top("Matches used: 12 / 12", GOOD)
        self.cap("6 equal pens, 12 matches ✓", GOOD, extra=[Flash(hp(CENTRE), color=GOOD, flash_radius=2.4)])
        self.play(Indicate(VGroup(*fills), color=GOOD, scale_factor=1.04), run_time=0.8)
        self.wait(0.5)

        # ---- second way: two squares sharing a corner -------------------------------------------
        self.cap("Another way: two squares sharing a corner")
        self.play(FadeOut(hexa), run_time=0.4)
        S = 2.6
        A0 = np.array([CENTRE_X - S, STAGE_Y - S, 0.0])

        def ap(p):                                           # verify.py alt point -> screen
            return A0 + S * np.array([p[0], p[1], 0.0])

        squares = VGroup(*[stick(ap(a), ap(b)) for a, b in ALT_MATCHES[:4] + ALT_MATCHES[6:10]])
        self.set_top("Matches used: 0 / 12", ACCENT)
        self.add_sound(SFX["pop"], gain=-8)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in squares], lag_ratio=0.12), run_time=1.3)
        self.remove(*squares)
        self.add(squares)
        self.set_top("Matches used: 8 / 12", ACCENT)
        self.play(Flash(ap((1, 1)), color=ACCENT, flash_radius=0.5), run_time=0.5)

        # ---- two matches inside each square ------------------------------------------------------
        self.cap("Two matches inside each square make 3 pens each")
        cuts = VGroup(*[stick(ap(a), ap(b), color="#F4D9A6") for a, b in ALT_MATCHES[4:6] + ALT_MATCHES[10:12]])
        shifts = [RIGHT * 3, RIGHT * 3, RIGHT * 3, RIGHT * 3]
        self.add_sound(SFX["tick"], gain=-8)
        for i, (c, sh) in enumerate(zip(cuts, shifts)):
            self.play(FadeIn(c, shift=-1.8 * sh / 3), run_time=0.35)
            self.set_top(f"Matches used: {9 + i} / 12", ACCENT)
        pens = []
        for x0, y0 in ((0.0, 0.0), (1.0, 1.0)):
            for j in range(3):
                ya, yb = y0 + j / 3, y0 + (j + 1) / 3
                poly = Polygon(ap((x0, ya)), ap((x0 + 1, ya)), ap((x0 + 1, yb)), ap((x0, yb)), stroke_width=0,
                               fill_color=PIECES[(j + (x0 > 0) * 2) % 4], fill_opacity=0.42)
                pens.append(VGroup(poly))
        self.add_sound(SFX["chime"], gain=-6)
        self.play(LaggedStart(*[FadeIn(p) for p in pens], lag_ratio=0.12), run_time=1.0)
        self.set_top("Matches used: 12 / 12", GOOD)
        self.wait(0.8)

        # ---- Level 2 ------------------------------------------------------------------------------
        self.clear_top()
        self.play(FadeOut(VGroup(squares, cuts, *pens)), FadeOut(credit), run_time=0.4)
        tag = badge("LEVEL 2").move_to([CENTRE_X, 6.3, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.cap("Level 2: a triangle with 3 matches on each side, cut into small triangles of 1 match per side",
                 width=34, extra=[GrowFromCenter(tag)])
        T = 1.75
        top = np.array([CENTRE_X, STAGE_Y + 2.8, 0.0])
        h = np.sqrt(3) / 2

        def tp(i, j):
            return top + T * np.array([j - i / 2, -i * h, 0.0])

        l2 = []
        n = L2_SIDE
        for i in range(n + 1):
            for j in range(i + 1):
                if j < i:
                    l2.append((tp(i, j), tp(i, j + 1)))
                if i < n:
                    l2 += [(tp(i, j), tp(i + 1, j)), (tp(i, j), tp(i + 1, j + 1))]
        assert len(l2) == L2_MATCHES
        tri = VGroup(*[stick(a, b, w=12) for a, b in l2])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in tri], lag_ratio=0.05), run_time=1.6)
        self.remove(*tri)
        self.add(tri)
        ask = label("? matches", 66, ACCENT).move_to([CENTRE_X, -1.05, 0])
        self.cap("How many matches in all?", ACCENT, extra=[FadeIn(ask)])
        self.wait(1.0)

        self.cap("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(2.0)
