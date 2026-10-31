"""Verify Short 0002: the Crescent Puzzle (Dudeney, Amusements in Mathematics, no. 191).

Checks, in code, every claim the video makes:
  * (x-5)^2 = x(x-9) has exactly one root, x = 25: the x^2 terms cancel
  * so the diameters are 50 and 41
  * that figure really has width 9 at the widest point and 5 straight above the centre,
    with the small circle touching the big one on the inside
  * the angle at E is 90 degrees (semicircle)
  * a quarter turn about C, then a scale-up about C, lands triangle ECD exactly on ACE,
    so the two have the same shape
  * Level 2: big circle 32 across, widest part 7 -> gap above the centre is 4

Puzzle coordinates: C is the origin, A is on the right, F is straight up.
The scene imports `crescent()`, `quarter_turn()`, `similarity_scale()` and the numbers below.
"""
from __future__ import annotations

import math
from fractions import Fraction as Fr

WIDE, GAP = 9, 5                 # Level 1 givens
L2_DIAMETER, L2_WIDE = 32, 7     # Level 2 givens


def polymul(p: list, q: list) -> list:
    """Multiply polynomials given as coefficient lists, lowest power first."""
    out = [Fr(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


def solve_radius(wide: int, gap: int) -> Fr:
    """Solve (x - gap)^2 = x(x - wide), exactly."""
    left = polymul([Fr(-gap), Fr(1)], [Fr(-gap), Fr(1)])
    right = polymul([Fr(0), Fr(1)], [Fr(-wide), Fr(1)])
    c0, c1, c2 = (a - b for a, b in zip(left, right))
    assert c2 == 0, "the x^2 terms should cancel"
    assert c1 != 0, "no single answer"
    return -c0 / c1


def crescent(R: Fr, wide: Fr) -> dict:
    """Every point of the figure, for big radius R and widest part `wide`."""
    R, wide = Fr(R), Fr(wide)
    cd = R - wide                                    # C to D
    r = (R + cd) / 2                                 # small radius: AD is its diameter
    ce2 = R * cd                                     # EC^2 = AC * CD
    ce = Fr(math.isqrt(ce2.numerator), math.isqrt(ce2.denominator))
    assert ce * ce == ce2, f"CE is not rational for R={R}, wide={wide}"
    return {
        "R": R, "r": r,
        "C": (Fr(0), Fr(0)), "A": (R, Fr(0)), "B": (-R, Fr(0)),
        "D": (-cd, Fr(0)), "E": (Fr(0), ce), "F": (Fr(0), R),
        "O": (R - r, Fr(0)),                         # centre of the small circle
    }


def quarter_turn(p: tuple) -> tuple:
    """Clockwise quarter turn about C."""
    return (p[1], -p[0])


def similarity_scale(g: dict) -> Fr:
    """The scale about C that takes the turned triangle ECD onto ACE."""
    return g["A"][0] / g["E"][1]


def dist2(p: tuple, q: tuple) -> Fr:
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def dot(u: tuple, v: tuple) -> Fr:
    return u[0] * v[0] + u[1] * v[1]


def sub(p: tuple, q: tuple) -> tuple:
    return (p[0] - q[0], p[1] - q[1])


def check_figure(g: dict, wide: Fr, gap: Fr) -> None:
    R, r = g["R"], g["r"]
    A, B, C, D, E, F, O = (g[k] for k in "ABCDEFO")
    assert dist2(B, D) == wide ** 2, "width at the widest point"
    assert dist2(E, F) == gap ** 2, "width above the centre"
    assert dist2(F, C) == R ** 2 and dist2(B, C) == R ** 2 and dist2(A, C) == R ** 2
    for p in (A, D, E):
        assert dist2(p, O) == r ** 2, "A, D and E lie on the small circle"
    assert dist2(O, C) == (R - r) ** 2 and r < R, "circles touch inside, at A"
    assert dot(sub(F, C), sub(A, C)) == 0, "CF is perpendicular to CA"
    assert dot(sub(A, E), sub(D, E)) == 0, "the angle at E is 90 degrees"

    # BD really is the widest point of the crescent: sample the big circle.
    R_f, r_f, ox = float(R), float(r), float(O[0])
    widths = [math.hypot(R_f * math.cos(t) - ox, R_f * math.sin(t)) - r_f
              for t in (k * math.tau / 3600 for k in range(3600))]
    assert abs(max(widths) - float(wide)) < 1e-6, max(widths)


def check_similar(g: dict) -> None:
    A, C, D, E = g["A"], g["C"], g["D"], g["E"]
    D2, E2 = quarter_turn(D), quarter_turn(E)
    assert D2[0] == 0 and D2[1] > 0 and E2[1] == 0 and E2[0] > 0, "lands on the two legs of ACE"
    a, b = sub(E2, D2), sub(A, E)
    assert a[0] * b[1] - a[1] * b[0] == 0, "long sides are parallel"
    k = similarity_scale(g)
    assert (k * E2[0], k * E2[1]) == A and (k * D2[0], k * D2[1]) == E, "scale-up lands on ACE"
    ac, ce, cd = A[0], E[1], -D[0]
    assert ac / ce == ce / cd, "same ratio"
    assert ce * ce == ac * cd


def main() -> None:
    x = solve_radius(WIDE, GAP)
    assert x == 25, x
    g = crescent(x, WIDE)
    check_figure(g, Fr(WIDE), Fr(GAP))
    check_similar(g)
    assert 2 * g["R"] == 50 and 2 * g["r"] == 41

    h = crescent(Fr(L2_DIAMETER, 2), L2_WIDE)
    gap2 = h["F"][1] - h["E"][1]
    check_figure(h, Fr(L2_WIDE), gap2)
    check_similar(h)
    assert gap2 == 4 and h["D"][0] == -9 and h["E"][1] == 12, gap2
    assert solve_radius(L2_WIDE, 4) == 16, "Level 2 agrees with the forward equation"

    print(f"OK  x=25 unique, diameters 50 and 41, figure and quarter turn check; level2 gap={gap2}")


if __name__ == "__main__":
    main()
