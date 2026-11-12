"""Short 0021 - The Monk and the Bridges (Dudeney no. 261).

A map of three places joined by five bridges. Treat the twin bridges as interchangeable and the walk has
only four shapes (the places visited); naming the twins in 2 x 2 ways turns each shape into 4 routes,
4 x 4 = 16. Level 2: six bridges and a walk back to the start (8 shapes x 8 names = 64).

Every shape and number comes from verify.py (BRIDGES, SHAPES, ROUTES, TWINS, swap, ...).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, ArcBetweenPoints, Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate,
    LaggedStart, Line, MoveAlongPath, Scene, Transform, VGroup, linear, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, INK, MUTED, PIECES as COL  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    BRIDGES, BRIDGES2, ROUTES, ROUTES2, SHAPES, SHAPES2, TWINS, START, END, swap, walk,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
BLUE, ORANGE, GREEN, PINK = COL[1], COL[0], COL[2], COL[3]
TWIN_COLOR = {"a": BLUE, "b": BLUE, "c": GREEN, "d": GREEN, "e": ORANGE, "f": ORANGE}

POS1 = {"M": (-3.0, 1.7), "I": (-0.3, 6.3), "Y": (2.1, 1.7)}
POS2 = {"M": (-3.0, 0.4), "I": (-0.3, 4.1), "Y": (2.4, 0.4)}
GRID_PTS = [(CENTRE_X - 1.8, 0.0), (CENTRE_X + 1.8, 0.0), (CENTRE_X - 1.8, -0.95), (CENTRE_X + 1.8, -0.95)]
COUNTER_Y = -2.0


def v3(p):
    return np.array([p[0], p[1], 0.0])


class BridgeMap:
    """Nodes and bridge curves for a bridges dict (twins bow apart, a lone bridge is straight)."""

    def __init__(self, bridges, pos, ang=0.45, node_r=0.38):
        self.bridges, self.P = bridges, {k: v3(v) for k, v in pos.items()}
        groups: dict[tuple, list] = {}
        for name, key in bridges.items():
            groups.setdefault(key, []).append(name)
        self.base, self.label_at = {}, {}
        centroid = sum(self.P.values()) / 3
        for (p, q), names in groups.items():
            for k, name in enumerate(names):
                angle = 0 if len(names) == 1 else (ang if k == 0 else -ang)
                a, b = self.P[p], self.P[q]
                c = Line(a, b) if angle == 0 else ArcBetweenPoints(a, b, angle=angle)
                c.set_stroke(INK, 6)
                self.base[name] = c
                mid = (a + b) / 2
                cm = c.point_from_proportion(0.5)
                n = cm - mid
                if np.linalg.norm(n) < 1e-6:
                    n = mid - centroid
                n = n / np.linalg.norm(n)
                self.label_at[name] = cm + 0.42 * n
        self.curves = VGroup(*self.base.values())
        self.nodes = {}
        for k, p in self.P.items():
            circ = Circle(radius=node_r, stroke_color=INK, stroke_width=6, fill_color=BG, fill_opacity=1)
            circ.move_to(p)
            self.nodes[k] = VGroup(circ, label(k, 44, INK).move_to(p)).set_z_index(3)
        self.node_group = VGroup(*self.nodes.values())

    def oriented(self, name, frm):
        c = self.base[name].copy()
        if self.bridges[name][1] == frm:
            c.reverse_points()
        return c

    def labels(self, size=44):
        return VGroup(*[label(n, size, TWIN_COLOR[n]).move_to(self.label_at[n]).set_z_index(4)
                        for n in self.base])


WATER, GRASS, ISLAND, PLANK, EDGE, WALL = "#1F4E79", "#2F5233", "#4C7A45", "#C8A26B", "#5A4326", "#D9C7A0"
PIC_MONK, PIC_HOUSE = (-2.8, 1.95), (-2.4, 6.3)
# bridge ends (near bank / island edge / far bank) in the picture
PIC_BRIDGES = {"a": ((-1.2, 2.6), (-1.2, 3.9)), "b": ((0.6, 2.6), (0.6, 3.9)),
               "c": ((-1.2, 4.4), (-1.2, 5.7)), "d": ((0.6, 4.4), (0.6, 5.7)),
               "e": ((2.6, 2.6), (2.6, 5.7))}
PIC_LABEL = {"a": (-1.7, 3.25), "b": (1.1, 3.25), "c": (-1.7, 5.05), "d": (1.1, 5.05), "e": (2.95, 4.15)}


def picture():
    """A little river scene: monk's bank, river, island, far bank with the monastery, five real bridges."""
    from manim import Ellipse, Polygon, Rectangle
    water = Rectangle(width=7.0, height=3.0, fill_color=WATER, fill_opacity=1, stroke_width=0)
    water.move_to([-0.3, 4.15, 0])
    near = Rectangle(width=7.0, height=1.5, fill_color=GRASS, fill_opacity=1, stroke_width=0)
    near.move_to([-0.3, 1.95, 0])
    far = Rectangle(width=7.0, height=1.4, fill_color=GRASS, fill_opacity=1, stroke_width=0)
    far.move_to([-0.3, 6.3, 0])
    isl = Ellipse(width=3.2, height=1.1, fill_color=ISLAND, fill_opacity=1, stroke_width=0)
    isl.move_to([-0.3, 4.15, 0])
    planks, bridges = {}, VGroup()
    for n, (p, q) in PIC_BRIDGES.items():
        edge = Line(v3(p), v3(q)).set_stroke(EDGE, 30)
        plank = Line(v3(p), v3(q)).set_stroke(PLANK, 18)
        planks[n] = plank
        bridges.add(VGroup(edge, plank))
    wall = Rectangle(width=0.8, height=0.55, fill_color=WALL, fill_opacity=1, stroke_width=0)
    wall.move_to([PIC_HOUSE[0], PIC_HOUSE[1] - 0.15, 0])
    roof = Polygon([PIC_HOUSE[0] - 0.55, PIC_HOUSE[1] + 0.12, 0], [PIC_HOUSE[0] + 0.55, PIC_HOUSE[1] + 0.12, 0],
                   [PIC_HOUSE[0], PIC_HOUSE[1] + 0.65, 0], fill_color="#B5483A", fill_opacity=1, stroke_width=0)
    house = VGroup(wall, roof)
    pwords = VGroup(label("monk", 32, INK).move_to([PIC_MONK[0], PIC_MONK[1] - 0.6, 0]),
                    label("monastery", 32, INK).move_to([-0.2, 6.3, 0]),
                    label("island", 30, INK).move_to([-0.3, 4.15, 0]))
    scene = VGroup(near, far, water, isl, bridges)
    return scene, planks, scene, pwords, house


def route_mob(route, size=46):
    g = VGroup(*[label(ch, size, TWIN_COLOR[ch], weight="BOLD") for ch in route]).arrange(
        direction=np.array([1.0, 0, 0]), buff=0.2)
    return g


def counter(text, color=ACCENT, size=84):
    return label(text, size, color).move_to([CENTRE_X, COUNTER_Y, 0])


class Short(Scene):
    def construct(self):
        cap = Captions(self)

        # ---- checks that the picture matches verify.py ----
        keys = sorted(SHAPES)
        assert len(ROUTES) == 16 and len(keys) == 4
        assert all(len(SHAPES[k]) == 4 for k in keys)
        for k in keys:
            assert walk(SHAPES[k][0], BRIDGES, START) == k
        assert len(ROUTES2) == 64 and len(SHAPES2) == 8

        # ---------- hook: the map pops in ----------
        m = BridgeMap(BRIDGES, POS1)
        P = m.P
        monk = Dot(P["M"], radius=0.17, color=ACCENT).set_z_index(6)
        words = VGroup(label("monk", 32, MUTED).move_to(P["M"] + np.array([0, -0.75, 0])),
                       label("monastery", 32, MUTED).move_to(P["Y"] + np.array([-0.45, -0.75, 0])),
                       label("island", 32, MUTED).move_to(P["I"] + np.array([1.1, 0.0, 0])))

        # the real-life picture first: a river, an island and five actual bridges
        land, planks, pic, pwords, house = picture()
        monk.move_to(v3(PIC_MONK))
        pic_all = VGroup(pic, pwords, house)

        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(pic), run_time=0.9)
        self.play(FadeIn(VGroup(pwords, house)), run_time=0.3)
        cap.show("Can you count the routes that\ncross all five bridges exactly once?", run_time=0.5)
        self.wait(1.4)

        # ---------- problem ----------
        self.add_sound(SFX["pop"], gain=-4)
        cap.show("A monk wants to walk home to the monastery.",
                 extra=[GrowFromCenter(monk)], run_time=0.5)
        self.play(Indicate(monk, color=INK, scale_factor=1.8), run_time=0.8)
        self.wait(0.4)

        cap.show("Two bridges reach the island, two leave it, and one crosses directly.")
        pairs = [(("a", "b"), BLUE), (("c", "d"), GREEN), (("e",), ORANGE)]
        for names, col in pairs:
            self.play(*[planks[n].animate.set_stroke(col, 18) for n in names], run_time=0.5)
            self.wait(0.1)
        self.play(*[planks[n].animate.set_stroke(PLANK, 18) for n in planks], run_time=0.3)

        cap.show("He must cross every bridge once, and only once.")
        self.play(Indicate(VGroup(*planks.values()), color=ACCENT, scale_factor=1.04), run_time=1.0)
        self.wait(0.5)

        cap.show("How many different routes could he take?", ACCENT)
        self.wait(0.8)

        # ---------- pause and try ----------
        cap.show("Pause and try it.", ACCENT)
        everything = VGroup(pic_all, monk)
        self.play(FadeOut(everything), run_time=0.3)
        countdown(self, 5, center=[CENTRE_X, 3.5, 0], radius=1.1, tick_sound=SFX["tick"])
        self.play(FadeIn(everything), run_time=0.3)

        # ---------- start and end ----------
        cap.show("Every route has to start at the monk and end at the monastery.")
        self.play(Flash(v3(PIC_MONK), color=ACCENT, flash_radius=0.8, line_length=0.25),
                  Indicate(monk, color=ACCENT, scale_factor=1.8), run_time=0.9)
        self.play(Flash(v3(PIC_HOUSE), color=GOOD, flash_radius=0.8, line_length=0.25),
                  Indicate(house, color=GOOD, scale_factor=1.25), run_time=0.9)
        self.wait(0.4)

        plabs = VGroup(*[label(n, 44, TWIN_COLOR[n]).move_to(v3(PIC_LABEL[n])).set_z_index(4)
                         for n in planks])
        self.add_sound(SFX["pop"], gain=-6)
        cap.show("Let's call the bridges a, b, c, d and e.",
                 extra=[LaggedStart(*[FadeIn(x, scale=0.6) for x in plabs], lag_ratio=0.2)], run_time=0.9)
        self.wait(0.4)

        # ---------- twins ----------
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("The two bridges in each pair are twins, so ignore their names for now.",
                 extra=[FadeOut(plabs),
                        *[planks[n].animate.set_stroke(TWIN_COLOR[n], 18) for n in planks]], run_time=1.0)
        self.play(Indicate(VGroup(planks["a"], planks["b"]), color=INK, scale_factor=1.05), run_time=0.6)
        self.play(Indicate(VGroup(planks["c"], planks["d"]), color=INK, scale_factor=1.05), run_time=0.6)
        self.wait(0.4)

        # ---------- from the picture to a simple map ----------
        for n, c in m.base.items():
            c.set_stroke(TWIN_COLOR[n], 8)
        cap.show("Let's redraw it as a simple map: three places, joined by five bridges.",
                 extra=[FadeOut(pic_all), monk.animate.move_to(P["M"])], run_time=0.8)
        self.add_sound(SFX["pop"], gain=-6)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in m.curves], lag_ratio=0.12),
                  GrowFromCenter(m.node_group), run_time=0.9)
        self.play(FadeIn(words), run_time=0.3)
        self.wait(0.6)

        # ---------- four shapes ----------
        cap.show("Looking only at the places he visits, there are just four different shapes.")
        chips = []
        for i, key in enumerate(keys):
            route = SHAPES[key][0]
            col = COL[i]
            here = START
            trail = VGroup()
            for br in route:
                leg = m.oriented(br, here).set_stroke(col, 14).set_z_index(2)
                self.play(Create(leg), MoveAlongPath(monk, leg), run_time=0.22, rate_func=linear)
                trail.add(leg)
                p, q = BRIDGES[br]
                here = q if here == p else p
            assert here == END
            chip = label(" ".join(key), 44, col, weight="BOLD").move_to(v3(GRID_PTS[i]))
            chips.append(chip)
            self.add_sound(SFX["pop"], gain=-6)
            self.play(FadeIn(chip, shift=0.3 * DOWN), FadeOut(trail),
                      monk.animate.move_to(P["M"]), run_time=0.4)
        self.wait(0.6)

        # ---------- name the twins ----------
        base = SHAPES[keys[0]][0]
        grid_routes = {
            0: base,
            1: swap(base, TWINS[0]),
            2: swap(base, TWINS[1]),
            3: swap(swap(base, TWINS[0]), TWINS[1]),
        }
        assert set(grid_routes.values()) == set(SHAPES[keys[0]]) and len(set(grid_routes.values())) == 4
        rmobs = {i: route_mob(r).move_to(v3(GRID_PTS[i])) for i, r in grid_routes.items()}
        labs = m.labels()
        # show the first shape's trail again so the viewer connects it with the strings
        cap.show("In every shape, the first pair of twins can be named in two ways.",
                 extra=[FadeOut(VGroup(*chips)), FadeIn(labs), FadeIn(rmobs[0], shift=0.2 * UP)], run_time=0.8)
        self.play(Indicate(VGroup(m.base["a"], m.base["b"]), color=INK, scale_factor=1.06), run_time=0.7)
        self.add_sound(SFX["snip"])
        cp = rmobs[0].copy()
        self.play(Transform(cp, rmobs[1]), run_time=0.8)
        self.wait(0.5)

        cap.show("The second pair of twins can be named in two ways too.")
        self.play(Indicate(VGroup(m.base["c"], m.base["d"]), color=INK, scale_factor=1.06), run_time=0.7)
        self.add_sound(SFX["snip"])
        cp2, cp3 = rmobs[0].copy(), rmobs[1].copy()
        self.play(Transform(cp2, rmobs[2]), Transform(cp3, rmobs[3]), run_time=0.9)
        self.wait(0.7)

        cnt = counter("2 × 2 = 4 routes", INK, 64)
        self.add_sound(SFX["chime"], gain=-8)
        cap.show("So each shape gives 2 times 2, which is 4 routes.",
                 extra=[FadeIn(cnt, shift=0.3 * DOWN)], run_time=0.6)
        self.play(Indicate(VGroup(rmobs[0], cp, cp2, cp3), color=ACCENT, scale_factor=1.06), run_time=0.8)
        self.wait(0.8)

        # ---------- payoff ----------
        tagged = [label(" ".join(k) + "  ×4", 32, COL[i], weight="BOLD").move_to(v3(GRID_PTS[i]))
                  for i, k in enumerate(keys)]
        cap.show("Four shapes times four names makes 16 routes ✓", GOOD,
                 extra=[FadeOut(VGroup(rmobs[0], cp, cp2, cp3)), FadeOut(labs),
                        Transform(cnt, counter("4", ACCENT, 96))], run_time=0.8)
        for i, t in enumerate(tagged):
            self.add_sound(SFX["pop"], gain=-6)
            self.play(FadeIn(t, scale=0.7), Transform(cnt, counter(str(4 * (i + 1)), ACCENT, 96)),
                      run_time=0.5)
            self.wait(0.15)
        self.add_sound(SFX["chime"])
        self.play(Transform(cnt, counter("16 routes ✓", GOOD, 96)),
                  Flash(cnt, color=GOOD, flash_radius=1.6), run_time=0.8)
        self.wait(1.0)

        # ---------- Level 2 ----------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(x) for x in list(self.mobjects)], run_time=0.3)
        self.clear()
        m2 = BridgeMap(BRIDGES2, POS2)
        for n, c in m2.base.items():
            c.set_stroke(TWIN_COLOR[n], 8)
        tg = badge("LEVEL 2").move_to([CENTRE_X, 6.5, 0])
        sub = label("The same river, but with six bridges.\nHe ends where he started.", 44, INK)
        sub.move_to([CENTRE_X, 5.35, 0])
        ask = label("routes: ?", 72, ACCENT).move_to([CENTRE_X, -1.6, 0])
        monk2 = Dot(m2.P["M"], radius=0.17, color=ACCENT).set_z_index(6)
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tg), run_time=0.4)
        self.play(FadeIn(sub), LaggedStart(*[GrowFromCenter(c) for c in m2.curves], lag_ratio=0.12),
                  GrowFromCenter(m2.node_group), GrowFromCenter(monk2), run_time=1.0)
        cap.show("Level 2: the same river, with six bridges and a walk back to the start.",
                 run_time=0.5)
        self.wait(1.2)
        cap.show("Same trick: how many routes are there now?", run_time=0.5)
        self.wait(1.0)
        cap.show("Comment just the number ↓", ACCENT, extra=[FadeIn(ask, shift=0.2 * UP)])
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.1), run_time=1.0, rate_func=there_and_back)
            self.wait(1.8)
