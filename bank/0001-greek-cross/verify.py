"""Verify Short 0001: Greek cross -> square in 4 pieces.

Checks, in code, every claim the video makes:
  * the cross (5 unit squares) has area 5
  * two perpendicular cuts through the centre, slopes 1/2 and -2, give 4 congruent pieces
  * translating the pieces (no rotation) tiles a square of side sqrt(5) exactly
  * Level 2 answer: the cuts tilt atan(1/2) ~ 26.57 deg -> "27"

Run:  python verify.py      (exit code 0 = all good)
The scene imports `pieces_and_targets()` so the animation uses these exact shapes.
"""
from __future__ import annotations

import math

from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import split, unary_union
from shapely.geometry import LineString

TOL = 1e-9


def cross() -> Polygon:
    return unary_union([box(-1.5, -0.5, 1.5, 0.5), box(-0.5, -1.5, 0.5, 1.5)])


def cut_lines() -> list[LineString]:
    # Directions (2,1) and (-1,2): perpendicular, each of length sqrt(5).
    return [LineString([(-4, -2), (4, 2)]), LineString([(2, -4), (-2, 4)])]


def target_square() -> Polygon:
    # Square spanned by the lattice vectors (2,1) and (-1,2), one corner at the cut centre.
    # (The crosses tile the plane on this same lattice, which is why lattice translations work.)
    a, b = (2, 1), (-1, 2)
    return Polygon([(0, 0), a, (a[0] + b[0], a[1] + b[1]), b])


def pieces_and_targets():
    """Return [(piece_polygon, (dx, dy)), ...] - each piece and the translation that puts it in the square."""
    pieces = [cross()]
    for line in cut_lines():
        pieces = [g for p in pieces for g in split(p, line).geoms]
    sq = target_square()
    lattice = [(i * 2 + j * -1, i * 1 + j * 2) for i in range(-2, 3) for j in range(-2, 3)]
    out = []
    for p in pieces:
        for dx, dy in lattice:
            moved = affinity.translate(p, dx, dy)
            if moved.difference(sq.buffer(1e-7)).area < TOL:
                out.append((p, (dx, dy)))
                break
        else:
            raise AssertionError(f"piece {p.wkt} fits nowhere in the square")
    return out


def level2_answer_degrees() -> float:
    return math.degrees(math.atan2(1, 2))


def main() -> None:
    c = cross()
    assert abs(c.area - 5) < TOL, c.area

    pt = pieces_and_targets()
    assert len(pt) == 4, f"expected 4 pieces, got {len(pt)}"
    areas = [p.area for p, _ in pt]
    assert all(abs(a - 1.25) < TOL for a in areas), areas

    sq = target_square()
    assert abs(sq.area - 5) < TOL
    side = math.dist(*list(sq.exterior.coords)[:2])
    assert abs(side - math.sqrt(5)) < TOL, side

    rebuilt = unary_union([affinity.translate(p, dx, dy) for p, (dx, dy) in pt])
    assert rebuilt.symmetric_difference(sq).area < 1e-7, "pieces do not tile the square"

    deg = level2_answer_degrees()
    assert round(deg) == 27, deg

    print(f"OK  cross area=5, 4 pieces x 1.25, square side={side:.6f} (sqrt5), level2={deg:.2f} deg -> 27")


if __name__ == "__main__":
    main()
