"""Verify Short 0006: St. George's Banner (Dudeney, Amusements in Mathematics, no. 185).

Checks, in code, every claim the video makes:
  * a 4 x 3 flag has area 12, so red and white must be 6 each
  * the cross is a full-width bar and a full-height bar of the same width x; the white is four equal corners
  * count the red directly: the long bar is 4x, the upright is 3x, and the centre square (x^2) is in both,
    so red = 4x + 3x - x^2 (checked against the actual shape)
  * red = 6 means 7x - x^2 = 6; try x = 1: 7 - 1 = 6, so the cross is 1 foot wide
  * that is the only width that fits on the flag: x^2 - 7x + 6 = (x - 1)(x - 6), and 6 is wider than the flag
  * white check: four corners, each 1.5 x 1, total 6
  * the too-thin hint: at x = 1/2 the red is 3 1/4, less than the white
  * Dudeney's own rule agrees: a quarter of the perimeter minus half the diagonal = 3.5 - 2.5 = 1
  * Level 2: a 12 x 5 flag, 17x - x^2 = 30; x = 2 gives 34 - 4 = 30, the other root 15 is too wide

The flag is centred at the origin, in feet. The scene imports the shapes and numbers below.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

from shapely.geometry import box as _box
from shapely.ops import unary_union


def box(x0, y0, x1, y1):
    return _box(float(x0), float(y0), float(x1), float(y1))


def widths(W, H, red):
    """Exact roots of W x + H x - x^2 = red, i.e. x^2 - (W + H) x + red = 0."""
    b, c = W + H, red
    disc = b * b - 4 * c
    r = math.isqrt(int(disc))
    assert r * r == disc, "irrational width"
    return sorted([F(b - r, 2), F(b + r, 2)])


FLAG_W, FLAG_H = 4, 3
ARM = 1                                  # the answer, in feet
L2_W, L2_H, L2_ARM = 12, 5, 2            # Level 2 flag and its answer
THIN = F(1, 2)                           # a too-thin cross, shown before the pause


def flag(W, H):
    return box(-F(W, 2), -F(H, 2), F(W, 2), F(H, 2))


def bar_h(W, x):
    """The full-width bar."""
    return box(-F(W, 2), -F(x, 2), F(W, 2), F(x, 2))


def bar_v(H, x):
    """The full-height bar."""
    return box(-F(x, 2), -F(H, 2), F(x, 2), F(H, 2))


def centre(x):
    """The square where the bars overlap."""
    return box(-F(x, 2), -F(x, 2), F(x, 2), F(x, 2))


def cross(W, H, x):
    """The red cross: a full-width bar and a full-height bar, both x wide, through the centre."""
    return unary_union([bar_h(W, x), bar_v(H, x)])


def corners(W, H, x):
    """The four white corners as (x0, y0, x1, y1), NE, NW, SW, SE."""
    W2, H2, x2 = F(W, 2), F(H, 2), F(x, 2)
    return [(x2, x2, W2, H2), (-W2, x2, -x2, H2), (-W2, -H2, -x2, -x2), (x2, -H2, W2, -x2)]


def area(rects):
    return sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects)


def red_area(W, H, x):
    return W * x + H * x - x * x


FLAG = flag(FLAG_W, FLAG_H)
CROSS = cross(FLAG_W, FLAG_H, ARM)
BAR_H = bar_h(FLAG_W, ARM)                         # 4 x 1
BAR_V = bar_v(FLAG_H, ARM)                         # 1 x 3
CENTRE = centre(ARM)                               # 1 x 1, counted twice
CORNERS = corners(FLAG_W, FLAG_H, ARM)             # each 1.5 x 1
HALF = F(FLAG_W * FLAG_H, 2)                       # 6
L2_HALF = F(L2_W * L2_H, 2)                        # 30


def check(W, H, x):
    """Every geometric claim for one flag and arm."""
    fl, cr, cs = flag(W, H), cross(W, H, x), corners(W, H, x)
    whites = [box(*c) for c in cs]
    # the cross and the four corners tile the flag
    assert math.isclose(cr.area + sum(b.area for b in whites), fl.area)
    assert unary_union([cr, *whites]).equals(fl)
    assert all(b.intersection(cr).area == 0 for b in whites)
    # the four corners are equal
    assert len({(c[2] - c[0], c[3] - c[1]) for c in cs}) == 1
    # the bars: W x and H x, overlapping exactly in the x by x centre square
    bh, bv = bar_h(W, x), bar_v(H, x)
    assert math.isclose(bh.area, W * x) and math.isclose(bv.area, H * x)
    assert bh.intersection(bv).equals(centre(x))
    # so the red is W x + H x - x^2
    assert math.isclose(cr.area, red_area(W, H, x))
    assert math.isclose(cr.area, bh.area + bv.area - centre(x).area)


def main() -> None:
    assert FLAG.area == 12 and HALF == 6

    check(FLAG_W, FLAG_H, ARM)
    # 4x + 3x - x^2 = 6 at x = 1: 7 - 1 = 6
    assert 4 * ARM + 3 * ARM - ARM ** 2 == 7 - 1 == HALF
    assert red_area(FLAG_W, FLAG_H, ARM) == HALF
    # white check: four 1.5 x 1 corners
    assert CORNERS[0] == (F(1, 2), F(1, 2), 2, F(3, 2))
    assert area(CORNERS) == 4 * F(3, 2) == HALF

    # x^2 - 7x + 6 = (x - 1)(x - 6): only 1 fits on the flag
    roots = widths(FLAG_W, FLAG_H, HALF)
    assert roots == [1, 6], roots
    assert all(r * r - 7 * r + 6 == 0 for r in roots)
    assert [r for r in roots if 0 < r < min(FLAG_W, FLAG_H)] == [ARM]

    # Dudeney's rule: quarter of the perimeter minus half the diagonal
    assert math.hypot(FLAG_W, FLAG_H) == 5
    assert F(2 * (FLAG_W + FLAG_H), 4) - F(5, 2) == ARM

    # the too-thin cross shown before the pause: red is less than white
    check(FLAG_W, FLAG_H, THIN)
    assert red_area(FLAG_W, FLAG_H, THIN) == F(13, 4)
    assert red_area(FLAG_W, FLAG_H, THIN) < HALF < area(corners(FLAG_W, FLAG_H, THIN))

    # Level 2: 12 x 5 flag, 17x - x^2 = 30
    check(L2_W, L2_H, L2_ARM)
    assert red_area(L2_W, L2_H, L2_ARM) == 24 + 10 - 4 == 34 - 4 == L2_HALF == 30
    roots2 = widths(L2_W, L2_H, L2_HALF)
    assert roots2 == [2, 15], roots2
    assert [r for r in roots2 if 0 < r < min(L2_W, L2_H)] == [L2_ARM], roots2
    assert area(corners(L2_W, L2_H, L2_ARM)) == L2_HALF
    assert math.hypot(L2_W, L2_H) == 13 and F(2 * (L2_W + L2_H), 4) - F(13, 2) == L2_ARM

    print(f"OK  4x3 flag: red 4x + 3x - x^2 = {HALF} at x = {ARM} ft; level2 12x5 -> {L2_ARM}")


if __name__ == "__main__":
    main()
