"""Short 0015 - The Tube Inspector's Puzzle (Dudeney no. 242).

Level 1 (solved on screen): dots count the lines at every station. The six odd stations (B, D, F, G, I, K)
each have one leftover line. Rule: any start/end is allowed. Fact: only an end can use a leftover.
Best: start and end at odd stations (B and K), then repeat D-G and F-I: 17 + 2 = 19.
Level 2 (comment challenge): 3 x 3 network, 12 lines -> 14.

The grid, the odd stations, the repeats and the route come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate, LaggedStart, Line,
    Scene, VGroup, ValueTracker, always_redraw, linear, there_and_back,
)
import numpy as np  # noqa: E402

from lib.layout import ACCENT, BG, GOOD, GRID, INK, MUTED, PIECES, STAGE_Y, TITLE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    COLS, END, L2_COLS, L2_MILES, L2_ROWS, LINES, MILES, ODD, REPEATED, ROUTE, ROWS, START, grid,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
HOT = PIECES[0]
SP = 2.0                       # station spacing
CY = STAGE_Y - 0.1
assert (MILES, L2_MILES, len(LINES)) == (19, 14, 17)


def key(a: str, b: str):
    return tuple(sorted((a, b)))


def unit(v):
    return v / np.linalg.norm(v)


def perp(v):
    u = unit(v)
    return np.array([-u[1], u[0], 0.0])


def wrap(text: str) -> str:
    """Break a long caption into two balanced lines so it stays big enough to read."""
    if len(text) <= 30:
        return text
    words = text.split(" ")
    best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
    return " ".join(words[:best]) + "\n" + " ".join(words[best:])


class Net:
    """A network of stations and lines, built from verify.grid()."""

    def __init__(self, cols: int, rows: int, sp: float, cx: float, cy: float, rad: float = 0.34, lw: float = 8):
        names, edges = grid(cols, rows)
        self.pos = {n: np.array([cx + (c - (cols - 1) / 2) * sp, cy + ((rows - 1) / 2 - r) * sp, 0.0])
                    for (c, r), n in names.items()}
        self.nbr = {n: [] for n in self.pos}
        for a, b in edges:
            self.nbr[a].append(b)
            self.nbr[b].append(a)
        self.lines = {e: Line(self.pos[e[0]], self.pos[e[1]], color=MUTED, stroke_width=lw).set_z_index(0)   # 0: the redrawn route trail (z 0, added later) sits on top
                      for e in edges}
        self.st = {n: Circle(radius=rad, fill_color=GRID, fill_opacity=1, stroke_color=MUTED,
                             stroke_width=5).move_to(p).set_z_index(3) for n, p in self.pos.items()}
        self.tx = {n: label(n, 34, INK).move_to(self.pos[n]).set_z_index(4) for n in self.pos}
        self.lg = VGroup(*self.lines.values())
        self.sg = VGroup(*[VGroup(self.st[n], self.tx[n]) for n in self.pos])
        self.dots = {(s, n): Dot(self.dot_at(s, n), radius=0.11, color=INK).set_z_index(5)
                     for s in self.pos for n in self.nbr[s]}
        self.dg = VGroup(*self.dots.values())

    def dot_at(self, s: str, n: str, d: float = 0.64):
        return self.pos[s] + d * unit(self.pos[n] - self.pos[s])

    def line(self, a: str, b: str):
        return self.lines[key(a, b)]


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        net = Net(COLS, ROWS, SP, CENTRE_X, CY)
        pos, st, dots = net.pos, net.st, net.dots
        self.ctr = None
        self.tag = None

        def ctr(text: str, color=ACCENT, size: float = 56):
            return label(text, size, color).move_to([CENTRE_X, 5.5, 0])

        def swap_ctr(text: str, color=ACCENT, size: float = 56):
            new = ctr(text, color, size)
            anims = [FadeIn(new)] + ([FadeOut(self.ctr)] if self.ctr is not None else [])
            self.ctr = new
            return anims

        def swap_tag(text: str, color):
            new = badge(text, color).scale(0.8).move_to([CENTRE_X, 6.55, 0])
            anims = [FadeIn(new, shift=0.2 * DOWN)] + ([FadeOut(self.tag)] if self.tag is not None else [])
            self.tag = new
            return anims

        def flag(text: str, color, station: str):
            return badge(text, color).scale(0.38).move_to(pos[station] + np.array([0.0, 0.78, 0.0])).set_z_index(9)

        mark = [None, 0.0]           # when the current caption appeared, and how long it needs

        def settle():
            """Hold the current caption long enough to read it (about 0.33 s a word plus 1 s)."""
            if mark[0] is not None:
                short = mark[1] - (self.renderer.time - mark[0])
                if short > 0.01:
                    self.wait(short)

        def say(text: str, color=INK, extra=(), run_time: float = 0.45):
            settle()
            mark[0], mark[1] = self.renderer.time, 1.0 + 0.33 * len(text.split())
            return cap.show(wrap(text), color, extra=extra, run_time=run_time)

        def hop(f, station: str, run_time: float = 0.8):
            return f.animate.move_to(pos[station] + np.array([0.0, 0.78, 0.0])).set_run_time(run_time)

        # --- hook: the network pops in, then the question ----------------------------------------
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(LaggedStart(*[Create(l) for l in net.lg], lag_ratio=0.06), run_time=0.8)
        self.add_sound(SFX["pop"], time_offset=0.1)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in net.sg], lag_ratio=0.06), run_time=0.7)
        self.remove(*net.sg)
        self.add(net.sg)
        title = VGroup(*[label(t, 56, INK) for t in
                         ("What is the fewest number", "of miles the inspector can", "travel to ride every line?")]
                       ).arrange(DOWN, buff=0.16).move_to([CENTRE_X, 5.55, 0])
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.5)
        self.wait(3.2)

        # --- the problem ---------------------------------------------------------------------------
        self.add_sound(SFX["pop"])
        say("Twelve stations are joined by seventeen lines, each a mile long.",
            extra=[FadeOut(title), FadeOut(credit)] + swap_ctr("17 lines"))
        self.play(LaggedStart(*[Indicate(l, color=ACCENT, scale_factor=1.0) for l in net.lg],
                              lag_ratio=0.05), run_time=1.1)

        runner = Dot(pos["A"], radius=0.17, color=ACCENT).set_z_index(8)
        self.add_sound(SFX["snip"])
        say("The inspector must ride along every single line.", extra=[FadeIn(runner)])
        self.play(runner.animate.move_to(pos["B"]), net.line("A", "B").animate.set_color(ACCENT),
                  run_time=0.7)
        self.wait(0.4)

        fs, fe = flag("START", GOOD, "G"), flag("END", HOT, "J")
        self.add_sound(SFX["pop"])
        say("He may start and finish wherever he likes.", extra=[
            FadeOut(runner), net.line("A", "B").animate.set_color(MUTED)])
        self.play(FadeIn(fs, shift=0.6 * DOWN), FadeIn(fe, shift=0.6 * DOWN), run_time=0.5)
        for a, b in (("A", "L"), ("K", "C"), ("F", "H")):
            self.wait(0.5)
            self.play(hop(fs, a), hop(fe, b))
        self.wait(0.5)

        # --- pause and try ---------------------------------------------------------------------------
        settle()
        mark[0] = None
        cap.show("Pause and try it", ACCENT, extra=[
            FadeOut(fs), FadeOut(fe), FadeOut(self.ctr),
            net.lg.animate.set_opacity(0.25), net.sg.animate.set_opacity(0.25)])
        countdown(self, 5, center=[CENTRE_X, CY, 0], radius=0.95, tick_sound=SFX["tick"])

        # --- 17 is not enough; count the lines at each station ----------------------------------------
        self.add_sound(SFX["snip"])
        say("Riding each line once would only be seventeen miles.", extra=[
            net.lg.animate.set_opacity(1), net.sg.animate.set_opacity(1)]
            + swap_ctr("17 miles"))
        self.wait(1.2)

        self.add_sound(SFX["pop"])
        say("Let's count how many lines meet at each station.")
        self.play(LaggedStart(*[GrowFromCenter(d) for d in net.dg], lag_ratio=0.025), run_time=1.2)
        self.remove(*net.dg)
        self.add(net.dg)
        self.wait(0.3)

        self.add_sound(SFX["chime"], gain=-10)
        say("Six stations have an odd number of lines.", extra=[
            st[s].animate.set_stroke(HOT, 9) for s in ODD])
        self.play(LaggedStart(*[Indicate(st[s], color=HOT, scale_factor=1.3) for s in ODD], lag_ratio=0.12),
                  run_time=1.2)

        # --- FACT: passing through uses two lines; an odd station keeps one over --------------------------
        run2 = Dot(pos["D"], radius=0.17, color=ACCENT).set_z_index(8)
        self.add_sound(SFX["pop"])
        say("Passing through a station always uses two of its lines.", extra=swap_tag("FACT", ACCENT) + [
            FadeIn(run2), net.line("D", "E").animate.set_color(ACCENT), net.line("E", "F").animate.set_color(ACCENT),
            dots[("E", "D")].animate.set_color(ACCENT), dots[("E", "F")].animate.set_color(ACCENT)])
        self.play(run2.animate.move_to(pos["E"]), run_time=0.6, rate_func=linear)
        self.play(run2.animate.move_to(pos["F"]), run_time=0.6, rate_func=linear)
        self.wait(0.2)

        left = dots[("B", "E")]
        self.add_sound(SFX["snip"])
        say("So at an odd station, one line is always left over.", extra=[
            FadeOut(run2),
            net.line("D", "E").animate.set_color(MUTED), net.line("E", "F").animate.set_color(MUTED),
            dots[("E", "D")].animate.set_color(INK), dots[("E", "F")].animate.set_color(INK),
            net.line("A", "B").animate.set_color(ACCENT), net.line("B", "C").animate.set_color(ACCENT),
            dots[("B", "A")].animate.set_color(ACCENT), dots[("B", "C")].animate.set_color(ACCENT),
            left.animate.set_color(HOT)])
        self.play(Indicate(left, color=HOT, scale_factor=2.2), run_time=0.9)

        fb = flag("START", GOOD, "B")
        self.add_sound(SFX["pop"])
        say("Only a start or an end can use up that leftover line.", extra=[FadeIn(fb, shift=0.6 * DOWN)])
        self.play(left.animate.set_color(GOOD), net.line("B", "E").animate.set_color(GOOD), run_time=0.6)
        self.wait(0.5)

        # --- RULE: any start is allowed -------------------------------------------------------------------
        fe1, fe2 = flag("START", GOOD, "E"), flag("END", HOT, "H")
        self.add_sound(SFX["pop"])
        say("The rules let him start and end anywhere he likes.", extra=swap_tag("RULE", INK) + [
            FadeOut(fb),
            net.line("A", "B").animate.set_color(MUTED), net.line("B", "C").animate.set_color(MUTED),
            net.line("B", "E").animate.set_color(MUTED),
            dots[("B", "A")].animate.set_color(INK), dots[("B", "C")].animate.set_color(INK),
            left.animate.set_color(INK)])
        self.play(FadeIn(fe1, shift=0.6 * DOWN), FadeIn(fe2, shift=0.6 * DOWN), run_time=0.5)
        for a, b in (("C", "J"), ("I", "A"), ("E", "H")):
            self.wait(0.5)
            self.play(hop(fe1, a), hop(fe2, b))
        self.wait(0.3)

        # --- BEST: odd ends -----------------------------------------------------------------------------------
        self.add_sound(SFX["chime"], gain=-8)
        say("But to travel the least, he should start and end at odd stations.", GOOD,
            extra=swap_tag("BEST", GOOD))
        self.wait(0.7)

        self.add_sound(SFX["snip"])
        say("Starting at an even station would create one more problem to fix.", extra=[
            st["E"].animate.set_stroke(HOT, 9), st["H"].animate.set_stroke(HOT, 9)])
        self.play(Indicate(st["E"], color=HOT, scale_factor=1.3), Indicate(st["H"], color=HOT, scale_factor=1.3),
                  run_time=0.8)

        fs2, fe3 = flag("START", GOOD, "B"), flag("END", HOT, "K")
        self.add_sound(SFX["pop"])
        say("So we start at B and end at K.", extra=[
            FadeOut(fe1), FadeOut(fe2), FadeIn(fs2, shift=0.6 * DOWN), FadeIn(fe3, shift=0.6 * DOWN),
            st["E"].animate.set_stroke(MUTED, 5), st["H"].animate.set_stroke(MUTED, 5),
            st[START].animate.set_stroke(GOOD, 9), st[END].animate.set_stroke(GOOD, 9)])
        self.wait(0.9)

        # --- pair up the other four ----------------------------------------------------------------------------------
        extra_dots, doubles = VGroup(), VGroup()

        def double(a: str, b: str):
            ln = net.line(a, b)
            off = perp(pos[b] - pos[a]) * 0.17
            twin = Line(pos[a] + off, pos[b] + off, color=ACCENT, stroke_width=8).set_z_index(2)
            nd = [Dot(net.dot_at(s, o, 0.85), radius=0.1, color=ACCENT).set_z_index(5)
                  for s, o in ((a, b), (b, a))]
            doubles.add(twin)
            extra_dots.add(*nd)
            self.add_sound(SFX["snip"])
            return [Create(twin), ln.animate.set_color(ACCENT), *[GrowFromCenter(d) for d in nd],
                    st[a].animate.set_stroke(GOOD, 9), st[b].animate.set_stroke(GOOD, 9)]

        (d1, g1), (f1, i1) = REPEATED
        say("Riding one short line twice fixes two stations at once.",
            extra=double(d1, g1) + swap_ctr("17 + 1 = 18 miles"))
        self.wait(1.0)
        say("Two repeated lines fix all four, so the extra cost is two miles.",
            extra=double(f1, i1) + swap_ctr("17 + 2 = 19 miles"))
        self.wait(1.2)

        # --- trace the route -----------------------------------------------------------------------------------------------
        steps = [key(a, b) for a, b in zip(ROUTE, ROUTE[1:])]
        t = ValueTracker(0.0)

        def seg(i: int):
            a, b = ROUTE[i], ROUTE[i + 1]
            off = perp(pos[b] - pos[a]) * (0.11 if steps.count(steps[i]) == 2 else 0.0)
            return pos[a] + off, pos[b] + off

        def point(v: float):
            i = min(int(v), len(steps) - 1)
            a, b = seg(i)
            return a + (b - a) * (v - i)

        def trail():
            v = t.get_value()
            g = VGroup()
            for i in range(len(steps)):
                if v <= i:
                    break
                a, b = seg(i)
                done = v >= i + 1
                end = b if done else point(v)
                # the line being ridden is bright yellow and thick; finished lines settle to thinner green
                current = int(v) == i
                g.add(Line(a, end, color=ACCENT if current else GOOD, stroke_width=13 if current else 8).set_z_index(6))
            return g.set_z_index(6)

        runner2 = always_redraw(lambda: Dot(point(t.get_value()), radius=0.18, color=INK).set_z_index(8))
        miles = always_redraw(lambda: label(f"{int(round(t.get_value() - 0.49))} miles", 56, GOOD)
                              .move_to([CENTRE_X, 5.5, 0]))
        path = always_redraw(trail).set_z_index(6)   # the container keeps its own z-index across redraws
        self.add_sound(SFX["chime"], gain=-10)
        say("That makes seventeen plus two, which is nineteen miles.", extra=[
            FadeOut(self.ctr), FadeOut(net.dg), FadeOut(extra_dots), FadeOut(doubles), FadeOut(self.tag), FadeOut(fs2), FadeOut(fe3),
            *[l.animate.set_color(MUTED) for l in net.lg],
            *[st[s].animate.set_stroke(MUTED, 5) for s in net.pos]])
        self.add(path, runner2, miles)
        self.play(t.animate.set_value(float(MILES)), run_time=9.5, rate_func=linear)
        path.clear_updaters(); runner2.clear_updaters(); miles.clear_updaters()

        # --- payoff ----------------------------------------------------------------------------------------------------------------
        beat(self, "payoff")
        big = label(f"{MILES} miles", 84, GOOD).move_to([CENTRE_X, 5.6, 0])
        self.add_sound(SFX["chime"])
        say(f"The shortest trip is {MILES} miles ✓", GOOD, extra=[
            FadeOut(miles), FadeIn(big), Flash(pos["F"], color=GOOD, flash_radius=1.6)])
        self.wait(2.0)

        # --- Level 2 -------------------------------------------------------------------------------------------------------------
        beat(self, "Level 2")
        cap.clear()
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.3)
        self.clear()

        net2 = Net(L2_COLS, L2_ROWS, 2.2, CENTRE_X, STAGE_Y + 0.4, rad=0.34, lw=8)
        tag2 = badge("LEVEL 2").move_to([CENTRE_X, 6.45, 0])
        q = VGroup(*[label(s, 44) for s in ("Same rules on a 3 by 3 network:", "9 stations, 12 lines of 1 mile.")]
                   ).arrange(DOWN, buff=0.14).move_to([CENTRE_X, 5.1, 0])
        ask = label("? miles", 80, ACCENT).move_to([CENTRE_X, STAGE_Y - 3.0, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag2), FadeIn(q), run_time=0.5)
        self.play(LaggedStart(*[Create(l) for l in net2.lg], lag_ratio=0.05), run_time=0.7)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in net2.sg], lag_ratio=0.05), FadeIn(ask), run_time=0.7)
        self.remove(*net2.sg)
        self.add(net2.sg)

        cap.show("Comment just the number ↓", ACCENT)
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
