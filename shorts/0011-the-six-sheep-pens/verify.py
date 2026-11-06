"""Verify Short 0011: The Six Sheep-Pens (Dudeney, Amusements in Mathematics, no. 205).

Checks, in code, every claim the video makes:
  * twelve matches of equal length (1), each a segment
  * they meet only at their ends: no overlaps, no duplicated match, no loose end (every end is
    shared by at least two matches)
  * they enclose exactly six pens, all of the same area (equilateral triangles of side 1)
  * the pens are the hexagon's six triangles: 6 rim matches + 6 spokes
  * Level 2: a triangle of side 3, cut into unit triangles by lines parallel to its sides, takes
    3 * (3 + 2 + 1) = 18 matches and makes 9 pens

The scene imports everything below.
"""
from __future__ import annotations

from collections import Counter
from math import cos, isclose, pi, sin, sqrt

from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union

N = 6
CORNERS = [(cos(pi * k / 3), sin(pi * k / 3)) for k in range(N)]
CENTRE = (0.0, 0.0)
RIM = [(CORNERS[k], CORNERS[(k + 1) % N]) for k in range(N)]
SPOKES = [(CENTRE, c) for c in CORNERS]
MATCHES = RIM + SPOKES                       # the twelve matches

# Alternate solution: two unit squares touching at one corner, each cut by 2 internal matches
# (parallel to a side, a third of the way across) into three equal pens: 2 * (4 + 2) = 12 matches
def _square(x0, y0, flip=False):
    c = [(x0, y0), (x0 + 1, y0), (x0 + 1, y0 + 1), (x0, y0 + 1)]
    sides = [(c[k], c[(k + 1) % 4]) for k in range(4)]
    cuts = [((x0, y0 + t), (x0 + 1, y0 + t)) for t in (1 / 3, 2 / 3)]
    return sides + cuts


ALT_MATCHES = _square(0.0, 0.0) + _square(1.0, 1.0)     # share the vertex (1, 1)
ALT_PENS = 6

# Level 2: big triangle of side 3 (matches of length 1)
L2_SIDE = 3
L2_MATCHES = 18
L2_PENS = 9


def length(m):
    (x1, y1), (x2, y2) = m
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def key(p):
    return (round(p[0], 6), round(p[1], 6))


def pens(matches):
    return list(polygonize(unary_union([LineString(m) for m in matches])))


def main() -> None:
    assert len(MATCHES) == 12
    assert all(isclose(length(m), 1.0) for m in MATCHES)

    # no duplicated match
    ids = {frozenset((key(a), key(b))) for a, b in MATCHES}
    assert len(ids) == 12

    # no loose ends: every end is shared with at least one other match
    ends = Counter(key(p) for m in MATCHES for p in m)
    assert min(ends.values()) >= 2, ends
    assert ends[key(CENTRE)] == 6 and all(ends[key(c)] == 3 for c in CORNERS)

    # no overlaps: two matches only ever touch at a shared end
    for i, (a, b) in enumerate(MATCHES):
        for c, d in MATCHES[i + 1:]:
            inter = LineString([a, b]).intersection(LineString([c, d]))
            assert inter.is_empty or inter.geom_type == "Point"
            if not inter.is_empty:
                assert key((inter.x, inter.y)) in {key(a), key(b)} & {key(c), key(d)}

    # six pens of equal size
    ps = pens(MATCHES)
    assert len(ps) == 6
    area = sqrt(3) / 4
    assert all(isclose(p.area, area) for p in ps)
    assert isclose(unary_union(ps).area, 6 * area)

    # Alternate: two squares sharing a vertex, 2 internal matches each
    assert len(ALT_MATCHES) == 12
    assert all(isclose(length(m), 1.0) for m in ALT_MATCHES)
    alt_ids = {frozenset((key(a), key(b))) for a, b in ALT_MATCHES}
    assert len(alt_ids) == 12
    alt_ends = Counter(key(p) for m in ALT_MATCHES for p in m)
    assert alt_ends[(1.0, 1.0)] == 4                      # the shared vertex
    for i, (a, b) in enumerate(ALT_MATCHES):
        for c, d in ALT_MATCHES[i + 1:]:
            inter = LineString([a, b]).intersection(LineString([c, d]))
            assert inter.is_empty or inter.geom_type == "Point"   # touch, never overlap
    # no loose end: each match end touches another match
    for m in ALT_MATCHES:
        for p in m:
            others = [LineString(o) for o in ALT_MATCHES if o is not m]
            assert any(o.distance(__import__("shapely").geometry.Point(p)) < 1e-9 for o in others), p
    alt = pens(ALT_MATCHES)
    assert len(alt) == ALT_PENS == 6
    assert all(isclose(p.area, 1 / 3) for p in alt)

    # Level 2: triangle of side 3 with its lines parallel to the sides
    n = L2_SIDE
    assert 3 * sum(range(1, n + 1)) == L2_MATCHES
    h = sqrt(3) / 2

    def pt(i, j):                                    # row i from the top, j along the row
        return (j - i / 2, -i * h)
    segs = []
    for i in range(n + 1):
        for j in range(i + 1):
            if j < i:
                segs.append((pt(i, j), pt(i, j + 1)))        # horizontal
            if i < n:
                segs.append((pt(i, j), pt(i + 1, j)))        # down-left
                segs.append((pt(i, j), pt(i + 1, j + 1)))    # down-right
    uniq = {frozenset((key(a), key(b))) for a, b in segs}
    assert len(uniq) == L2_MATCHES, len(uniq)
    assert all(isclose(length(s), 1.0) for s in segs)
    l2 = pens(segs)
    assert len(l2) == L2_PENS
    assert all(isclose(p.area, area) for p in l2)

    print("OK  hexagon + 6 spokes: 12 matches, no loose ends, 6 equal pens; level2: 18 matches, 9 pens")


if __name__ == "__main__":
    main()
