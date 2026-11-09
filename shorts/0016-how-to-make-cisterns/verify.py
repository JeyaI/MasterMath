"""Verify Short 0016: How To Make Cisterns (Dudeney, Amusements in Mathematics, no. 201).

All work in feet. Claims checked in code:
  * an 8 ft x 3 ft sheet with squares of side x cut from the corners folds into an open box of volume
    V(x) = x(8 - 2x)(3 - 2x) = 4x^3 - 22x^2 + 24x cubic feet
  * V'(x) = 12x^2 - 44x + 24; quadratic formula x = (44 +- sqrt(44^2 - 4*12*24)) / 24
    = (44 +- sqrt(784)) / 24 = (44 +- 28)/24 -> x = 3 or x = 2/3
  * x = 3 is off the sheet (x must be under 1.5); V' goes from positive to negative at 2/3 -> maximum
  * best cut 2/3 ft = 8 in, volume 200/27 cubic ft (= 12800 cubic inches); Dudeney's formula agrees
  * Level 2: 12 ft square sheet -> 2 ft, volume 128; whole-foot table 1 ft: 100, 2 ft: 128, 3 ft: 108

The scene imports everything below.
"""
from __future__ import annotations

from fractions import Fraction
from math import isqrt

A, B = 8, 3                      # sheet in feet
BEST = Fraction(2, 3)            # feet
BEST_INCHES = 8
BEST_VOLUME = Fraction(200, 27)  # cubic feet
CRIT_1, CRIT_2 = Fraction(2, 3), 3   # roots of V'(x) = 12x^2 - 44x + 24
L2_SIDE_FT = 12
L2_BEST_FT = 2


def volume(x, a=A, b=B):
    return x * (a - 2 * x) * (b - 2 * x)


def dudeney(a, b):
    d = a * a + b * b - a * b
    r = isqrt(d)
    assert r * r == d
    return Fraction(a + b - r, 6)


def main() -> None:
    slope = lambda x: 12 * x * x - 44 * x + 24
    for x in range(-20, 40):
        assert volume(x) == 4 * x**3 - 22 * x**2 + 24 * x
    # quadratic formula
    disc = 44 * 44 - 4 * 12 * 24
    assert disc == 784 and isqrt(disc) ** 2 == disc and isqrt(disc) == 28
    r1, r2 = Fraction(44 - 28, 24), Fraction(44 + 28, 24)
    assert (r1, r2) == (CRIT_1, CRIT_2) == (Fraction(2, 3), 3)
    assert slope(r1) == 0 and slope(r2) == 0
    assert CRIT_2 > Fraction(min(A, B), 2)                  # 3 ft is off the sheet (x < 1.5)
    assert slope(Fraction(1, 2)) > 0 and slope(1) < 0       # rises then falls: maximum at 2/3
    assert 24 * BEST - 44 < 0                               # V''(2/3) = -28 < 0
    assert volume(BEST) == BEST_VOLUME == Fraction(200, 27)
    assert BEST * 12 == BEST_INCHES == 8
    assert volume(BEST) * 1728 == 12800
    assert dudeney(A, B) == BEST
    # no cut on a fine grid beats it
    for k in range(1, 48 * 3):
        x = Fraction(k, 96)
        if x < Fraction(3, 2):
            assert volume(x) <= BEST_VOLUME, x

    # Level 2: 12 ft square sheet, V = x(12-2x)^2, V' = (12-2x)(12-6x): zero at 2 (6 is off the sheet)
    a = L2_SIDE_FT
    assert (volume(1, a, a), volume(2, a, a), volume(3, a, a)) == (100, 128, 108)
    assert dudeney(a, a) == L2_BEST_FT
    assert all(volume(Fraction(k, 16), a, a) <= 128 for k in range(1, 96))

    print(f"OK  best cut {BEST} ft = {BEST_INCHES} in, volume {BEST_VOLUME} cu ft; level2: {L2_BEST_FT} ft")


if __name__ == "__main__":
    main()
