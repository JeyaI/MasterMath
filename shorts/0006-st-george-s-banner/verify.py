"""Verify Short 0006: St. George's Banner (Dudeney, Amusements in Mathematics, no. 185).

Checks, in code, every claim the video makes:
  * a 4 x 3 flag has area 12, so red and white must be 6 each
  * the cross is a full-width bar and a full-height bar of the same width w; the white is four equal corners
  * slide the four corners in until they touch: they close up, with no gap or overlap, into one
    (4 - w) x (3 - w) rectangle, the cross having been squeezed out
  * white = half the flag means (4 - w)(3 - w) = 6 = 3 x 2, so each side shrinks by 1: w = 1 foot
  * that is the only width that fits on the flag (the other root, 6, is wider than the flag)
  * the red cross is then 4 + 3 - 1 = 6 square feet, the same as the white
  * Dudeney's own rule agrees: a quarter of the perimeter minus half the diagonal = 3.5 - 2.5 = 1
  * Level 2: a 12 x 5 flag, white must be 30 = 10 x 3, so the arm is 2 feet

The flag is centred at the origin, in feet. The scene imports the shapes and numbers below.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

from shapely.geometry import box as _box
from shapely.ops import unary_union


def box(x0, y0, x1, y1):
    return _box(float(x0), float(y0), float(x1), float(y1))


def widths(W, H, white):
    """Exact roots of (W - w)(H - w) = white, i.e. w^2 - (W + H) w + (W H - white) = 0."""
    b, c = W + H, W * H - white
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


def cross(W, H, w):
    """The red cross: a full-width bar and a full-height bar, both w wide, through the centre."""
    return unary_union([box(-F(W, 2), -F(w, 2), F(W, 2), F(w, 2)),
                        box(-F(w, 2), -F(H, 2), F(w, 2), F(H, 2))])


def corners(W, H, w):
    """The four white corners as (x0, y0, x1, y1), NE, NW, SW, SE."""
    W2, H2, w2 = F(W, 2), F(H, 2), F(w, 2)
    return [(w2, w2, W2, H2), (-W2, w2, -w2, H2), (-W2, -H2, -w2, -w2), (w2, -H2, W2, -w2)]


def slid(W, H, w):
    """Each corner moved w/2 towards the centre, both ways: where they end up."""
    w2 = F(w, 2)
    out = []
    for x0, y0, x1, y1 in corners(W, H, w):
        dx = -w2 if x0 > 0 else w2
        dy = -w2 if y0 > 0 else w2
        out.append((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    return out


def area(rects):
    return sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects)


def red_area(W, H, w):
    return W * w + H * w - w * w


FLAG = flag(FLAG_W, FLAG_H)
CROSS = cross(FLAG_W, FLAG_H, ARM)
CORNERS = corners(FLAG_W, FLAG_H, ARM)
SLID = slid(FLAG_W, FLAG_H, ARM)
WHITE_W, WHITE_H = FLAG_W - ARM, FLAG_H - ARM      # 3 x 2 after the slide
HALF = F(FLAG_W * FLAG_H, 2)                       # 6
L2_HALF = F(L2_W * L2_H, 2)                        # 30


def check(W, H, w):
    """Every geometric claim for one flag and arm."""
    fl, cr, cs, sl = flag(W, H), cross(W, H, w), corners(W, H, w), slid(W, H, w)
    whites = [box(*c) for c in cs]
    # the cross and the four corners tile the flag
    assert math.isclose(cr.area + sum(b.area for b in whites), fl.area)
    assert unary_union([cr, *whites]).equals(fl)
    assert all(b.intersection(cr).area == 0 for b in whites)
    # the four corners are equal
    assert len({(c[2] - c[0], c[3] - c[1]) for c in cs}) == 1
    # sliding closes them into one (W - w) x (H - w) rectangle with no gap or overlap
    moved = [box(*c) for c in sl]
    target = box(-F(W - w, 2), -F(H - w, 2), F(W - w, 2), F(H - w, 2))
    assert unary_union(moved).equals(target)
    assert math.isclose(sum(b.area for b in moved), target.area)
    assert area(sl) == area(cs) == (W - w) * (H - w)
    # the red area formula matches the shape
    assert math.isclose(cr.area, red_area(W, H, w))


def main() -> None:
    assert FLAG.area == 12 and HALF == 6

    check(FLAG_W, FLAG_H, ARM)
    assert (WHITE_W, WHITE_H) == (3, 2) and WHITE_W * WHITE_H == HALF
    assert red_area(FLAG_W, FLAG_H, ARM) == 4 + 3 - 1 == HALF
    assert area(CORNERS) == HALF
    assert CORNERS[0] == (F(1, 2), F(1, 2), 2, F(3, 2))   # each corner is 1.5 x 1

    roots = widths(FLAG_W, FLAG_H, HALF)
    assert roots == [1, 6], roots
    assert all((FLAG_W - r) * (FLAG_H - r) == HALF for r in roots)
    assert [r for r in roots if 0 < r < min(FLAG_W, FLAG_H)] == [ARM]

    # Dudeney's rule: quarter of the perimeter minus half the diagonal
    assert math.hypot(FLAG_W, FLAG_H) == 5
    assert F(2 * (FLAG_W + FLAG_H), 4) - F(5, 2) == ARM

    # the too-thin cross shown before the pause: red is less than white
    check(FLAG_W, FLAG_H, THIN)
    assert red_area(FLAG_W, FLAG_H, THIN) < HALF < area(corners(FLAG_W, FLAG_H, THIN))

    # Level 2: 12 x 5 flag
    check(L2_W, L2_H, L2_ARM)
    assert L2_HALF == 30 == (L2_W - L2_ARM) * (L2_H - L2_ARM) == 10 * 3
    roots2 = widths(L2_W, L2_H, L2_HALF)
    assert [r for r in roots2 if 0 < r < min(L2_W, L2_H)] == [L2_ARM], roots2
    assert red_area(L2_W, L2_H, L2_ARM) == L2_HALF
    assert math.hypot(L2_W, L2_H) == 13 and F(2 * (L2_W + L2_H), 4) - F(13, 2) == L2_ARM

    print(f"OK  4x3 flag: arm {ARM} ft, white closes to {WHITE_W}x{WHITE_H} = {HALF}; level2 12x5 -> {L2_ARM}")


if __name__ == "__main__":
    main()
