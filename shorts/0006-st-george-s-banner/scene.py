"""Short 0006 - St. George's Banner (Dudeney no. 185).

Level 1 (solved on screen): a 4 x 3 flag with a red cross of arm width x. Count the red directly: the long bar
is 4x, the upright is 3x, and the middle square is in both bars, so it is counted twice: red = 4x + 3x - x^2.
Red must be half the flag, 6: 7x - x^2 = 6, and x = 1 works (checked against the four 1.5 x 1 white corners).
Level 2 (comment challenge): a 12 x 5 flag -> 2.

Nothing is cut or moved: the bars light up in place, the double-counted square is peeled off as "- x^2",
and the labels slide into one equation. Shapes and numbers come from verify.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO), str(HERE)]

from manim import (  # noqa: E402
    DOWN, UP, Create, FadeIn, FadeOut, GrowFromCenter, Indicate, Line, ManimColor, Rectangle,
    ReplacementTransform, Scene, ValueTracker, VGroup, always_redraw, there_and_back, Transform,
)

from lib.layout import ACCENT, BG, GOOD, INK, MUTED, PIECES, STAGE_Y  # noqa: E402
from lib.components import CENTRE_X, Captions, badge, beat, countdown, footer, hook, label  # noqa: E402
from lib.audio import write_sfx  # noqa: E402
from verify import (  # noqa: E402
    ARM, CORNERS, FLAG_H, FLAG_W, HALF, L2_ARM, L2_H, L2_W, THIN, red_area,
)

SFX = {k: str(v) for k, v in write_sfx(REPO / "assets" / "sfx").items()}
RED = ManimColor("#D93B3B")
WHITE = ManimColor("#FFFFFF")
C_H, C_V, C_C = PIECES[1], PIECES[2], ACCENT       # long bar, upright, middle square
K = 1.45                                           # frame units per foot
CY = 1.3
EQ_Y = -2.15
assert (HALF, red_area(FLAG_W, FLAG_H, ARM), L2_ARM) == (6, 6, 2)


def rect(x0, y0, x1, y1, k, cx, cy, **kw) -> Rectangle:
    """A rectangle given in feet (flag-centred), drawn at k units per foot around (cx, cy)."""
    x0, y0, x1, y1 = (float(v) for v in (x0, y0, x1, y1))
    return Rectangle(width=(x1 - x0) * k, height=(y1 - y0) * k, **kw).move_to(
        [cx + k * (x0 + x1) / 2, cy + k * (y0 + y1) / 2, 0])


def bars(W, H, x, k, cx, cy, **kw) -> VGroup:
    x = float(x)
    return VGroup(rect(-W / 2, -x / 2, W / 2, x / 2, k, cx, cy, **kw),
                  rect(-x / 2, -H / 2, x / 2, H / 2, k, cx, cy, **kw))


def solid(c, opacity=1.0):
    return dict(fill_color=c, fill_opacity=opacity, stroke_width=0)


def bracket(x, k, cx, cy, H, text, color=INK, size=44) -> VGroup:
    """A width bracket under the upright bar, `x` feet wide."""
    y = cy - k * H / 2 - 0.3
    w = float(x) * k
    ln = Line([cx - w / 2, y, 0], [cx + w / 2, y, 0], color=color, stroke_width=6)
    ticks = [Line([cx + s * w / 2, y - 0.14, 0], [cx + s * w / 2, y + 0.14, 0], color=color, stroke_width=6)
             for s in (-1, 1)]
    t = label(text, size, color).move_to([cx, y - 0.5, 0])
    return VGroup(ln, *ticks, t)


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        cx = CENTRE_X
        arm = ValueTracker(float(ARM))

        # ---------------- the flag ----------------
        flag = rect(-FLAG_W / 2, -FLAG_H / 2, FLAG_W / 2, FLAG_H / 2, K, cx, CY, **solid(WHITE))
        cross = always_redraw(lambda: bars(FLAG_W, FLAG_H, arm.get_value(), K, cx, CY, **solid(RED)))
        top = label("4 ft", 44, INK).move_to([cx, CY + K * FLAG_H / 2 + 0.45, 0])
        side = label("3 ft", 44, INK).rotate(1.5708).move_to([cx - K * FLAG_W / 2 - 0.35, CY, 0])
        dims = VGroup(top, side)

        # --- hook ---
        beat(self, "hook")
        self.add_sound(SFX["pop"])
        self.play(GrowFromCenter(flag), FadeIn(cross), FadeIn(dims), run_time=0.5)
        title = hook("How wide must the cross be", "for equal red and white?")
        credit = footer("After H. E. Dudeney, Amusements in Mathematics")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(credit), run_time=0.45)
        self.wait(2.0)

        # --- the problem builds ---
        cap.show("4 feet by 3 feet")
        self.play(Indicate(top, color=ACCENT), Indicate(side, color=ACCENT), run_time=1.0)
        self.wait(0.3)

        whites = VGroup(*[rect(*c, K, cx, CY, **solid(ACCENT, 0.9)) for c in CORNERS])
        cap.show("Red and white: equal amounts")
        self.play(FadeIn(whites), run_time=0.4)
        self.play(FadeOut(whites), run_time=0.3)
        self.play(Indicate(cross, color=ACCENT, scale_factor=1.03), run_time=0.8)
        self.wait(0.4)

        qline = always_redraw(lambda: bracket(arm.get_value(), K, cx, CY, FLAG_H, "x = ?", ACCENT))
        cap.show("How wide is the cross?")
        self.add(qline)
        self.wait(0.6)

        cap.show("Too thin: too much white")
        self.play(arm.animate.set_value(float(THIN)), run_time=0.8)
        note = label("red 3¼ of 6", 44, ACCENT).move_to([cx, CY - K * FLAG_H / 2 - 1.5, 0])
        self.play(FadeIn(note, shift=0.2 * UP), run_time=0.3)
        self.wait(0.7)
        self.play(arm.animate.set_value(float(ARM)), FadeOut(note), FadeOut(qline), run_time=0.7)
        self.remove(qline)

        # ---------------- pause and try ----------------
        plate = rect(-FLAG_W / 2, -FLAG_H / 2, FLAG_W / 2, FLAG_H / 2, K, cx, CY,
                     **solid(BG, 0.88))
        self.play(FadeIn(plate), run_time=0.25)
        cap.show("Pause and try it", ACCENT)
        countdown(self, 5, center=[cx, CY, 0], radius=0.95, tick_sound=SFX["tick"])
        self.play(FadeOut(plate), run_time=0.25)
        self.remove(plate)

        # ---------------- the solution ----------------
        half = label("12 ÷ 2 = 6", 48, INK).move_to([cx, CY - K * FLAG_H / 2 - 0.6, 0])
        cap.show("Red must be half: 6")
        self.play(FadeIn(half, shift=0.2 * UP), run_time=0.4)
        self.wait(0.5)

        # the equation line, laid out in advance: 4x + 3x - x^2 = 6
        tok = {n: label(t, 56, c) for n, t, c in (
            ("a", "4x", C_H), ("p", "+", INK), ("b", "3x", C_V), ("m", "−", INK), ("c", "x²", C_C), ("e", "= 6", INK))}
        line = VGroup(*tok.values()).arrange(buff=0.28).move_to([cx, EQ_Y, 0])
        if line.width > 6.8:
            line.scale_to_fit_width(6.8)

        # long bar
        hb = rect(-FLAG_W / 2, -ARM / 2, FLAG_W / 2, ARM / 2, K, cx, CY, **solid(C_H))
        ht = label("4 × x", 48, BG).move_to([cx - 1.9, CY, 0])
        cap.show("Long bar: 4 × x", extra=[FadeOut(half)])
        self.add_sound(SFX["pop"], gain=-3)
        self.play(FadeIn(hb), FadeIn(ht), FadeIn(tok["a"], shift=0.2 * DOWN), run_time=0.5)
        self.play(Indicate(hb, color=C_H, scale_factor=1.04), run_time=0.7)
        self.wait(0.3)

        # upright bar
        vb = rect(-ARM / 2, -FLAG_H / 2, ARM / 2, FLAG_H / 2, K, cx, CY, **solid(C_V))
        vt = label("3 × x", 38, BG).rotate(1.5708).move_to([cx, CY + K * 1.0, 0])
        cap.show("Upright bar: 3 × x")
        self.add_sound(SFX["pop"], gain=-3)
        self.play(FadeOut(ht), FadeIn(vb), FadeIn(vt), FadeIn(tok["p"]), FadeIn(tok["b"], shift=0.2 * DOWN),
                  run_time=0.5)
        self.play(Indicate(vb, color=C_V, scale_factor=1.04), run_time=0.7)
        self.wait(0.3)

        # the middle square is counted twice
        sq = rect(-ARM / 2, -ARM / 2, ARM / 2, ARM / 2, K, cx, CY, **solid(C_C))
        outer = rect(-ARM / 2, -ARM / 2, ARM / 2, ARM / 2, K, cx, CY, fill_opacity=0, stroke_color=C_C,
                     stroke_width=8).scale(1.18)
        twice = label("×2", 52, BG)
        twice_bg = rect(0.9, 0.9, 1.9, 1.5, K, cx, CY, **solid(C_C))
        twice.move_to(twice_bg)
        cap.show("Middle counted twice: − x²", extra=[FadeOut(vt)])
        self.add_sound(SFX["snip"], gain=-4)
        self.play(FadeIn(sq), Create(outer), FadeIn(twice_bg), FadeIn(twice), run_time=0.6)
        self.play(Indicate(sq, color=INK, scale_factor=1.15), run_time=0.7)
        peel = sq.copy().set_z_index(5)
        self.add(peel)
        self.play(FadeOut(outer), FadeOut(twice), FadeOut(twice_bg),
                  peel.animate.scale(0.5).move_to(tok["c"]), FadeIn(tok["m"]), run_time=0.8)
        self.play(FadeIn(tok["c"]), FadeOut(peel), run_time=0.25)
        self.wait(0.3)

        # one line
        cap.show("4x + 3x − x² = 6")
        self.play(FadeIn(tok["e"], shift=0.2 * DOWN), run_time=0.4)
        self.wait(0.5)
        tidy = label("7x − x² = 6", 60, INK).move_to([cx, EQ_Y, 0])
        self.play(ReplacementTransform(line, tidy), run_time=0.7)
        self.wait(0.5)

        # try x = 1
        chip = badge("x = 1", C_C).move_to([cx, CY - K * FLAG_H / 2 - 0.55, 0])
        cap.show("Try x = 1: 7 − 1 = 6")
        self.add_sound(SFX["pop"], gain=-3)
        self.play(FadeIn(chip, shift=0.8 * DOWN), run_time=0.45)
        ev = label("7 − 1 = 6 ✓", 60, GOOD).move_to([cx, EQ_Y, 0])
        self.play(Transform(tidy, ev), run_time=0.6)
        self.add_sound(SFX["chime"], gain=-8)
        self.wait(0.6)

        # white check
        self.play(*[FadeOut(m) for m in (hb, vb, sq, chip)], run_time=0.4)
        cap.show("White check: 4 × 1½ = 6")
        corners = [rect(*c, K, cx, CY, **solid(C_C, 0.95)) for c in CORNERS]
        tags = [label("1½ × 1", 40, BG).move_to(c) for c in corners]
        for c, t in zip(corners, tags):
            self.add_sound(SFX["pop"], gain=-6)
            self.play(FadeIn(c), FadeIn(t), run_time=0.22)
            self.wait(0.12)
        chk = label("4 × 1½ = 6 ✓", 60, GOOD).move_to([cx, EQ_Y, 0])
        self.play(Transform(tidy, chk), run_time=0.5)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (*corners, *tags)], run_time=0.3)

        # payoff
        beat(self, "payoff")
        br = bracket(ARM, K, cx, CY, FLAG_H, "1 ft", GOOD, 56)
        cap.show("1 foot ✓", GOOD, extra=[FadeIn(br), FadeOut(tidy)])
        self.add_sound(SFX["chime"])
        self.wait(1.2)

        # ---------------- Level 2 ----------------
        beat(self, "Level 2")
        cap.clear(run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        self.clear()

        tag = badge("LEVEL 2").move_to([cx, 6.45, 0])
        qs = VGroup(*[label(t, 46) for t in ("Same cross, bigger flag:", "12 ft by 5 ft.", "How wide is the cross?")]
                    ).arrange(DOWN, buff=0.16).move_to([cx, 4.7, 0])
        k2, cy2 = 0.5, 0.9
        f2 = rect(-L2_W / 2, -L2_H / 2, L2_W / 2, L2_H / 2, k2, cx, cy2, **solid(WHITE))
        c2 = bars(L2_W, L2_H, ARM, k2, cx, cy2, **solid(RED))
        t2 = label("12 ft", 40, INK).move_to([cx, cy2 + k2 * L2_H / 2 + 0.4, 0])
        s2 = label("5 ft", 40, INK).rotate(1.5708).move_to([cx - k2 * L2_W / 2 - 0.35, cy2, 0])
        br2 = bracket(ARM, k2, cx, cy2, L2_H, "x = ?", ACCENT, 48)
        rule = label("Red = white = half of 60", 44, MUTED).move_to([cx, -2.2, 0])
        self.add_sound(SFX["chime"], gain=-8)
        self.play(GrowFromCenter(tag), FadeIn(qs), FadeIn(f2), FadeIn(c2), FadeIn(t2), FadeIn(s2),
                  FadeIn(br2), FadeIn(rule), run_time=0.7)
        cap.show("Comment just the number ↓", ACCENT)
        ask = br2[-1]
        for _ in range(4):
            self.play(Indicate(ask, color=INK, scale_factor=1.2), run_time=1.0, rate_func=there_and_back)
            self.wait(1.75)
