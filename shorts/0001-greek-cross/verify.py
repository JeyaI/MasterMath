"""Verify Short 0001: Greek cross -> square in 4 pieces.

Checks, in code, every claim the video makes:
  * the cross (5 unit squares) has area 5
  * two perpendicular cuts through the centre, slopes 1/2 and -2, give 4 identical pieces
  * translating the pieces (no rotation) tiles a square of side sqrt(5) exactly
  * Level 2 answer: the yellow cut (the one drawn on the Level 2 card) has slope 1/2

Run:  python verify.py      (exit code 0 = all good)
The scene imports `pieces_and_targets()` so the animation uses these exact shapes.
"""
from __future__ import annotations

import math
from fractions import Fraction

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


def cuts() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Each cut as drawn on screen: its two endpoints, clipped to the cross."""
    return [tuple(c.intersection(cross()).coords) for c in cut_lines()]


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


def level2_slope() -> Fraction:
    """Rise over run of the yellow cut, the first one."""
    (x0, y0), (x1, y1) = cuts()[0]
    return Fraction(y1 - y0).limit_denominator(100) / Fraction(x1 - x0).limit_denominator(100)


def main() -> None:
    c = cross()
    assert abs(c.area - 5) < TOL, c.area

    pt = pieces_and_targets()
    assert len(pt) == 4, f"expected 4 pieces, got {len(pt)}"
    areas = [p.area for p, _ in pt]
    assert all(abs(a - 1.25) < TOL for a in areas), areas

    # "4 identical pieces": a quarter turn about the centre maps the set of pieces onto itself.
    polys = [p for p, _ in pt]
    for p in polys:
        turned = affinity.rotate(p, 90, origin=(0, 0))
        assert any(turned.symmetric_difference(q).area < 1e-7 for q in polys), "pieces are not identical"
    assert unary_union([affinity.rotate(polys[0], 90 * k, origin=(0, 0)) for k in range(4)]).symmetric_difference(c).area < 1e-7

    # The cuts run corner-free across the arms and are the diagonal of a 2x1 box.
    for (x0, y0), (x1, y1) in cuts():
        assert abs(math.dist((x0, y0), (x1, y1)) - math.sqrt(5)) < TOL
    assert sorted((abs(cuts()[0][1][0] - cuts()[0][0][0]), abs(cuts()[0][1][1] - cuts()[0][0][1]))) == [1, 2]

    sq = target_square()
    assert abs(sq.area - 5) < TOL
    side = math.dist(*list(sq.exterior.coords)[:2])
    assert abs(side - math.sqrt(5)) < TOL, side

    rebuilt = unary_union([affinity.translate(p, dx, dy) for p, (dx, dy) in pt])
    assert rebuilt.symmetric_difference(sq).area < 1e-7, "pieces do not tile the square"

    slope = level2_slope()
    assert slope == Fraction(1, 2), slope

    print(f"OK  cross area=5, 4 identical pieces x 1.25, square side={side:.6f} (sqrt5), level2 slope={slope}")


if __name__ == "__main__":
    main()
