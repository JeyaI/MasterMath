"""Verify Short 0009: An Easy Square Puzzle (Dudeney, Amusements in Mathematics, no. 147).

Checks, in code, every claim the video makes:
  * the piece: a 2 x 1 rectangle cut along its diagonal, a right triangle with legs 1 and 2, area 1
  * five of them have area 5, so a square made of them has side sqrt(5), exactly the hypotenuse
  * four whole triangles, right angles pointing in, make a tilted sqrt(5) square with a 1 x 1 hole
  * the fifth triangle, cut by one vertical line from the midpoint of its long leg, gives a
    trapezoid and a small triangle; moved into the hole they fill it exactly (no overlap, no gap)
  * only one piece is cut, and the final union is a square of area 5
  * Level 2: legs 3 and 6, same five pieces -> the square has area 45

The scene imports everything below.
"""
from __future__ import annotations

from math import isclose, sqrt

from shapely.affinity import rotate, translate
from shapely.geometry import Polygon
from shapely.ops import unary_union

# The piece (legs 1 and 2) with its right angle at the origin
PIECE = [(0, 0), (2, 0), (0, 1)]

# Four whole triangles around the 1 x 1 hole [1,2] x [1,2] (right angle of each at a hole corner)
WHOLE = [
    [(0, 1), (2, 0), (2, 1)],
    [(2, 0), (3, 2), (2, 2)],
    [(3, 2), (1, 3), (1, 2)],
    [(1, 3), (0, 1), (1, 1)],
]
HOLE = [(1, 1), (2, 1), (2, 2), (1, 2)]
BIG = [(2, 0), (3, 2), (1, 3), (0, 1)]          # the sqrt(5) square

# The fifth piece cut at x = 1 (from the midpoint of the long leg up to the hypotenuse)
TRAP_FROM = [(0, 0), (1, 0), (1, 0.5), (0, 1)]
TRI_FROM = [(1, 0), (2, 0), (1, 0.5)]
# Where they land in the hole: trapezoid slides by (1, 1); triangle turns half a turn about (1.5, 1)
TRAP_TO = [(1, 1), (2, 1), (2, 1.5), (1, 2)]
TRI_TO = [(2, 2), (1, 2), (2, 1.5)]
TRAP_SHIFT = (1, 1)
TRI_TURN_ABOUT = (1.5, 1.0)                     # 180 degrees about this point sends TRI_FROM to TRI_TO

# Level 2
L2_LEGS = (3, 6)
L2_AREA = 45


def poly(pts):
    return Polygon(pts)


def same(a: Polygon, b: Polygon) -> bool:
    return a.symmetric_difference(b).area < 1e-9


def main() -> None:
    piece = poly(PIECE)
    assert isclose(piece.area, 1.0)
    # twice as long as broad: the rectangle is 2 x 1 and the piece is half of it
    assert isclose(2 * piece.area, 2 * 1)
    hyp = sqrt(2 ** 2 + 1 ** 2)
    assert isclose(hyp, sqrt(5))
    assert isclose(5 * piece.area, sqrt(5) ** 2)

    big = poly(BIG)
    assert isclose(big.area, 5.0)
    side = [((BIG[i][0] - BIG[(i + 1) % 4][0]) ** 2 + (BIG[i][1] - BIG[(i + 1) % 4][1]) ** 2) for i in range(4)]
    assert all(isclose(s, 5.0) for s in side)     # four equal sides of sqrt(5)

    # the four whole triangles are congruent to the piece (area 1, legs 1 and 2, hypotenuse sqrt 5)
    for t in WHOLE:
        p = poly(t)
        assert isclose(p.area, 1.0)
        lens = sorted(((t[i][0] - t[(i + 1) % 3][0]) ** 2 + (t[i][1] - t[(i + 1) % 3][1]) ** 2) for i in range(3))
        assert [round(v, 9) for v in lens] == [1.0, 4.0, 5.0]

    hole = poly(HOLE)
    assert isclose(hole.area, 1.0)
    ring = unary_union([poly(t) for t in WHOLE])
    assert isclose(ring.area, 4.0)
    assert same(unary_union([ring, hole]), big)            # four triangles + hole = the square
    assert ring.intersection(hole).area < 1e-9            # triangles stay out of the hole

    # the cut: the two parts partition the fifth piece, no overlap
    trap, tri = poly(TRAP_FROM), poly(TRI_FROM)
    assert same(unary_union([trap, tri]), piece)
    assert trap.intersection(tri).area < 1e-9
    assert isclose(trap.area, 0.75) and isclose(tri.area, 0.25)

    # the moves
    trap_moved = translate(trap, *TRAP_SHIFT)
    tri_moved = rotate(tri, 180, origin=TRI_TURN_ABOUT)
    assert same(trap_moved, poly(TRAP_TO)) and same(tri_moved, poly(TRI_TO))
    assert trap_moved.intersection(tri_moved).area < 1e-9
    assert same(unary_union([trap_moved, tri_moved]), hole)  # the two parts fill the hole exactly

    # result: five pieces' worth, four whole, one cut in two, forming the square
    parts = [poly(t) for t in WHOLE] + [trap_moved, tri_moved]
    assert same(unary_union(parts), big)
    assert isclose(sum(p.area for p in parts), 5.0)

    # Level 2: legs 3 and 6, five triangles, area 5 * 9 = 45 = hypotenuse squared
    a, b = L2_LEGS
    assert b == 2 * a
    assert 5 * (a * b / 2) == L2_AREA == a * a + b * b == 45

    print("OK  4 triangles + hole; fifth piece cut in two fills the 1x1 hole; square area 5, side sqrt5; "
          "level2 area 45")


if __name__ == "__main__":
    main()
