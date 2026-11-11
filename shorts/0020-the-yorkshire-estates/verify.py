"""Verify Short 0020: The Yorkshire Estates (Dudeney, Amusements in Mathematics, no. 189).

Checks, in code, every claim the video makes:
  * three square estates of 370, 116 and 74 acres meet corner to corner round a triangle A B C
  * on a grid (D at the origin, x to the right, y up) the corners are A (0, 9), B (17, 0), C (7, 4),
    so each side of the triangle is the diagonal of a whole-number step:
      A->B: 17 across, 9 down  -> 17^2 + 9^2 = 370
      A->C:  7 across, 5 down  ->  7^2 + 5^2 = 74
      C->B: 10 across, 4 down  -> 10^2 + 4^2 = 116
  * area of the triangle = big triangle A D B (153/2) - triangle A E C (35/2) - triangle C F B (20)
    - rectangle E D F C (28) = 11
  * the same answer comes from the shoelace formula and from Dudeney's quarter-root formula
  * the three squares really stand on the three sides (their areas are the squared side lengths)
  * Level 2: squares of 26, 20 and 18 acres: corners (0,0), (5,1), (2,4); area 9

The scene imports everything below. Coordinates are in grid units (1 unit = a "step"), y up.
"""
from __future__ import annotations

from fractions import Fraction
from math import isqrt

# the triangle, on the grid
D = (0, 0)
A = (0, 9)
B = (17, 0)
C = (7, 4)
E = (0, 4)       # foot of C on the left edge
F = (7, 0)       # foot of C on the bottom edge

AREA_A, AREA_B, AREA_C = 370, 116, 74    # the estates: A on side AB... named as the book names them
# Dudeney's names: estate A = 370 (on side A-B), estate B = 116 (on side C-B), estate C = 74 (on side A-C)
LEGS = {"AB": (17, 9), "CB": (10, 4), "AC": (7, 5)}

# Level 2
L2_PTS = [(0, 0), (5, 1), (2, 4)]
L2_AREAS = (26, 20, 18)
L2_BOX = (5, 4)


def sq(p, q) -> int:
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def shoelace(pts) -> Fraction:
    n = len(pts)
    s = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    return Fraction(abs(s), 2)


def tri(w, h) -> Fraction:
    return Fraction(w * h, 2)


def main() -> None:
    # the squares on the sides
    assert sq(A, B) == AREA_A == 370
    assert sq(C, B) == AREA_B == 116
    assert sq(A, C) == AREA_C == 74
    assert LEGS["AB"][0] ** 2 + LEGS["AB"][1] ** 2 == 370
    assert LEGS["CB"][0] ** 2 + LEGS["CB"][1] ** 2 == 116
    assert LEGS["AC"][0] ** 2 + LEGS["AC"][1] ** 2 == 74
    assert (B[0] - A[0], A[1] - B[1]) == LEGS["AB"]
    assert (B[0] - C[0], C[1] - B[1]) == LEGS["CB"]
    assert (C[0] - A[0], A[1] - C[1]) == LEGS["AC"]

    # none of the sides is a whole number (Dudeney: "incommensurate")
    for s in (370, 116, 74):
        assert isqrt(s) ** 2 != s

    # the subtraction
    big = tri(17, 9)
    aec = tri(7, 5)
    cfb = tri(10, 4)
    rect = Fraction(7 * 4)
    assert (E[1], F[0]) == (4, 7) and C == (F[0], E[1])
    assert big == Fraction(153, 2) and aec == Fraction(35, 2) and cfb == 20 and rect == 28
    assert aec + cfb + rect == Fraction(131, 2)
    assert big - aec - cfb - rect == 11

    # independent checks
    assert shoelace([A, B, C]) == 11
    assert Fraction(isqrt(4 * 370 * 116 - (370 + 116 - 74) ** 2), 4) == 11
    assert isqrt(4 * 370 * 116 - (370 + 116 - 74) ** 2) ** 2 == 1936 and 44 * 44 == 1936

    # the outer corner points are the two big squares' shared corners: C is strictly inside the box A D B
    assert 0 < C[0] < 17 and 0 < C[1] < 9
    # C is below the line A-B (inside triangle ADB), so subtraction is valid
    assert C[0] * 9 + C[1] * 17 < 17 * 9

    # Level 2
    p, q, r = L2_PTS
    assert sorted((sq(p, q), sq(q, r), sq(p, r))) == sorted(L2_AREAS) == [18, 20, 26]
    assert max(x for x, _ in L2_PTS) == L2_BOX[0] and max(y for _, y in L2_PTS) == L2_BOX[1]
    box = L2_BOX[0] * L2_BOX[1]
    # box minus the three corner triangles
    corners = tri(5, 1) + tri(3, 3) + tri(2, 4)
    # (0,0)-(5,1): corner triangle legs 5,1 ; (5,1)-(2,4): legs 3,3 ; (2,4)-(0,0): legs 2,4
    assert shoelace(L2_PTS) == 9
    assert box - corners == 9
    assert Fraction(isqrt(4 * 26 * 20 - (26 + 20 - 18) ** 2), 4) == 9
    # decompositions into two squares are unique, so the legs are forced
    for n, legs in ((26, (1, 5)), (20, (2, 4)), (18, (3, 3))):
        ways = [(a, b) for a in range(1, 6) for b in range(a, 6) if a * a + b * b == n]
        assert ways == [legs], (n, ways)

    print("OK  squares 370/116/74 on A(0,9) B(17,0) C(7,4);",
          "big 76.5 - 17.5 - 20 - 28 = 11; level2 26/20/18 -> 9")


if __name__ == "__main__":
    main()
