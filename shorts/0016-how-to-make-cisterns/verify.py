"""Verify Short 0016: How To Make Cisterns (Dudeney, Amusements in Mathematics, no. 201).

Checks, in code, every claim the video makes:
  * a 96 in x 36 in sheet (8 ft x 3 ft) with squares of side x cut from the corners folds into an open
    box of volume x * (96 - 2x) * (36 - 2x) cubic inches
  * Dudeney's formula (a + b - sqrt(a^2 + b^2 - ab)) / 6 gives exactly 8 in for this sheet
  * at every whole inch from 1 to 17 the volume is computed (the table the scene shows), and 8 in is
    the unique best: 12800 cubic inches
  * 8 in is the true maximum, not just the best whole inch: the slope 12x^2 - 4(a+b)x + ab is zero at 8,
    its other root is beyond 18 in (outside the sheet), and every 1/32 inch step stays at or below 12800
    (exact Fractions)
  * Level 2: a 12 ft x 12 ft square sheet -> cut squares of 2 ft (24 in), volume 128 cubic ft, whole-foot
    table 1 ft: 100, 2 ft: 128, 3 ft: 108

The scene imports everything below.
"""
from __future__ import annotations

from fractions import Fraction
from math import isqrt

A, B = 96, 36                    # sheet in inches
BEST = 8                         # inches
BEST_VOLUME = 12800              # cubic inches
L2_SIDE_FT = 12                  # square sheet, feet
L2_BEST_FT = 2


def volume(x, a=A, b=B):
    return x * (a - 2 * x) * (b - 2 * x)


def table(a=A, b=B):
    """Volume for every whole cut size that leaves a box."""
    return {x: volume(x, a, b) for x in range(1, min(a, b) // 2)}


def dudeney(a, b):
    d = a * a + b * b - a * b
    r = isqrt(d)
    assert r * r == d, "formula is exact only when a^2 + b^2 - ab is a perfect square"
    return Fraction(a + b - r, 6)


def main() -> None:
    t = table()
    assert max(t, key=t.get) == BEST and t[BEST] == BEST_VOLUME
    assert sorted(t.values())[-2] < BEST_VOLUME             # unique best whole inch
    assert (t[6], t[7], t[8], t[9], t[10]) == (12096, 12628, 12800, 12636, 12160)
    assert dudeney(A, B) == BEST

    # Exact rational grid
    for k in range(1, 16 * 4 * 8):
        x = Fraction(k, 32)                                 # 1/32 in steps from 1/32 to 17.97
        if x < 18:
            assert volume(x) <= BEST_VOLUME, x
    assert volume(Fraction(15, 2)) < BEST_VOLUME and volume(Fraction(17, 2)) < BEST_VOLUME
    # Slope check: V'(x) = 12x^2 - 4(a+b)x + ab, zero at 8; the other root is > 18
    slope = lambda x: 12 * x * x - 4 * (A + B) * x + A * B
    assert slope(BEST) == 0
    other = Fraction(A * B, 12 * BEST)                      # product of roots = ab/12
    assert other > 18                                       # outside the range, so 8 is the maximum

    # Level 2: 12 ft square sheet, work in feet
    a = L2_SIDE_FT
    t2 = table(a, a)
    assert max(t2, key=t2.get) == L2_BEST_FT and t2[2] == 128
    assert (t2[1], t2[2], t2[3]) == (100, 128, 108)
    assert dudeney(a, a) == L2_BEST_FT
    assert all(volume(Fraction(k, 16), a, a) <= 128 for k in range(1, 96))

    print(f"OK  best cut {BEST} in, volume {BEST_VOLUME} cu in; level2 12 ft square: {L2_BEST_FT} ft")


if __name__ == "__main__":
    main()
