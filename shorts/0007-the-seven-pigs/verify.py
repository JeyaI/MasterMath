"""Verify Short 0007: The Seven Pigs (Dudeney, Amusements in Mathematics, no. 165).

Checks, in code, every claim the video makes:
  * the pen is a 10 x 10 square holding 7 pigs; no fence passes through (or within 0.25 of) a pig
  * the "obvious" try, 3 parallel fences, makes only 4 sties, so some pigs must share
  * the 3 fences A, B, C cross each other pairwise inside the pen, at 3 different points
  * they split the pen into exactly 7 sties and every sty holds exactly one pig
  * 7 is the ceiling: n straight fences make at most 1 + n + C(n,2) sties (random fences never beat it)
  * the middle sty is a closed triangle that touches no wall
  * Level 2: 4 fences, every pair crossing inside the pen, make 11 sties, of which 3 touch no wall

The scene imports everything below.
"""
from __future__ import annotations

import math
import random
from itertools import combinations

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

Pt = tuple[float, float]
Fence = tuple[Pt, Pt]            # two points on the fence; it runs wall to wall

SIDE = 10.0
PEN = Polygon([(0, 0), (SIDE, 0), (SIDE, SIDE), (0, SIDE)])
MARGIN = 0.25                     # a fence passes at least this far from a pig

# (x, y) in pen units. Scattered so the answer is not obvious.
PIGS: list[Pt] = [(5.4, 4.6), (8.0, 8.0), (8.0, 2.0), (3.0, 5.0), (2.0, 1.5), (9.5, 4.5), (2.2, 8.5)]
CENTRE_PIG = 0

# Where each fence meets the wall (left/bottom end, right/top end), in the order they are built.
FENCES: list[Fence] = [((0, 2), (10, 6)), ((3, 0), (7, 10)), ((0, 8), (10, 3))]
# The tempting try: three fences side by side.
PARALLEL: list[Fence] = [((0, 3.2), (10, 3.2)), ((0, 6.2), (10, 6.2)), ((0, 7.0), (10, 7.0))]
# Level 2: a fourth fence added to the three, still crossing all of them inside the pen.
FOURTH: Fence = ((8, 0), (2, 10))
L2_FENCES: list[Fence] = FENCES + [FOURTH]
L2_STIES, L2_CLOSED = 11, 3


def side(f: Fence, p: Pt) -> float:
    """Signed distance of p from the fence (sign tells which side)."""
    (x0, y0), (x1, y1) = f
    return ((x1 - x0) * (p[1] - y0) - (y1 - y0) * (p[0] - x0)) / math.dist(f[0], f[1])


def crossing(a: Fence, b: Fence) -> Pt | None:
    """Where two fences cross inside the pen, or None."""
    (x1, y1), (x2, y2) = a
    (x3, y3), (x4, y4) = b
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    p = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return p if 0 < p[0] < SIDE and 0 < p[1] < SIDE else None


def sties(fences: list[Fence]) -> list[Polygon]:
    """The enclosed regions of the pen once every fence is built (fences are run a little past the wall)."""
    lines = [LineString([(x0 - (x1 - x0) * .01, y0 - (y1 - y0) * .01), (x1 + (x1 - x0) * .01, y1 + (y1 - y0) * .01)])
             for (x0, y0), (x1, y1) in fences]
    pieces = polygonize(unary_union([PEN.exterior, *lines]))
    return [p for p in pieces if PEN.contains(p.representative_point())]


def touches_wall(poly: Polygon) -> bool:
    return poly.boundary.intersection(PEN.exterior.buffer(1e-6)).length > 1e-6


def pigs_in(poly: Polygon) -> list[int]:
    return [i for i, p in enumerate(PIGS) if poly.contains(Point(p))]


STIES = sties(FENCES)
PARALLEL_STIES = sties(PARALLEL)
L2_ALL = sties(L2_FENCES)
CROSSINGS = [crossing(a, b) for a, b in combinations(FENCES, 2)]
L2_CROSSINGS = [crossing(a, b) for a, b in combinations(L2_FENCES, 2)]


def main() -> None:
    assert len(PIGS) == 7 and all(0 < x < SIDE and 0 < y < SIDE for x, y in PIGS)
    assert min(math.dist(p, q) for p, q in combinations(PIGS, 2)) > 1.5, "two pigs nearly touch"

    # no fence goes through a pig
    for f in FENCES + PARALLEL:
        assert min(abs(side(f, p)) for p in PIGS) > MARGIN, f

    # the parallel try
    assert len(PARALLEL_STIES) == 4
    assert max(len(pigs_in(s)) for s in PARALLEL_STIES) >= 2

    # the three crossing fences
    assert all(c is not None for c in CROSSINGS), "every pair must cross inside the pen"
    assert min(math.dist(p, q) for p, q in combinations(CROSSINGS, 2)) > 0.5, "crossings nearly coincide"
    assert len(STIES) == 7
    assert sorted(len(pigs_in(s)) for s in STIES) == [1] * 7, "each sty needs exactly one pig"
    assert math.isclose(sum(s.area for s in STIES), PEN.area, rel_tol=1e-6)
    closed = [s for s in STIES if not touches_wall(s)]
    assert len(closed) == 1 and pigs_in(closed[0]) == [CENTRE_PIG] and len(closed[0].exterior.coords) == 4
    assert min(s.area for s in STIES) > 1.0, "a sty is a sliver"

    # the ceiling: n lines make at most 1 + n + C(n,2); for 3 that is 7
    assert 1 + 3 + math.comb(3, 2) == 7
    rng = random.Random(165)
    for _ in range(1500):
        fs = [((0, rng.uniform(0, SIDE)), (SIDE, rng.uniform(0, SIDE))) if rng.random() < .5 else
              ((rng.uniform(0, SIDE), 0), (rng.uniform(0, SIDE), SIDE)) for _ in range(3)]
        assert len(sties(fs)) <= 7

    # Level 2
    assert all(c is not None for c in L2_CROSSINGS) and len(L2_CROSSINGS) == 6
    assert min(math.dist(p, q) for p, q in combinations(L2_CROSSINGS, 2)) > 0.3
    assert len(L2_ALL) == L2_STIES == 1 + 4 + math.comb(4, 2)
    assert sum(not touches_wall(s) for s in L2_ALL) == L2_CLOSED == math.comb(4 - 1, 2)

    print(f"OK  parallel {len(PARALLEL_STIES)} sties; crossing fences {len(STIES)} sties, 1 per pig; "
          f"level2 {L2_STIES} sties, {L2_CLOSED} closed")


if __name__ == "__main__":
    main()
