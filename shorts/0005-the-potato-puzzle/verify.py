"""Verify Short 0005: The Potato Puzzle (Dudeney, Amusements in Mathematics, no. 164).

Checks, in code, every claim the video makes:
  * the grid (three cuts each way) really gives 16 pieces, in steps 2, 3, 4, 8, 12, 16
  * parallel cuts never cross, and the grid has only 9 of the 15 possible crossings
  * in the 22-piece figure every cut crosses every earlier cut, inside the slice, at its own point
  * so cut k runs through exactly k pieces and adds exactly k: 2, 4, 7, 11, 16, 22
  * pieces = 1 + cuts + crossings for any straight cuts, so 15 crossings (all pairs) is the ceiling: 22 is the maximum
  * Level 2: the 10-cut figure has 1 + (1 + 2 + ... + 10) = 56 pieces

The slice is the unit disc and a cut is (angle of its normal, distance from the centre). Pieces are
real shapely polygons, split one by one, and a second count that ignores the splitting has to agree.
The scene imports everything below.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from itertools import combinations

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, split, unary_union

Pt = tuple[float, float]
Cut = tuple[float, float]

N, MAX_PIECES = 6, 22
GRID_PIECES = 16
L2_N, L2_PIECES = 10, 56
DISC = Point(0, 0).buffer(1.0, quad_segs=48)   # the slice, as a 192-sided polygon
RIM = DISC.exterior

D = 0.5                                        # spacing of the grid, tilted like Dudeney's picture
GRID_CUTS: list[Cut] = [(a, d) for a in (math.pi / 4, 3 * math.pi / 4) for d in (-D, 0.0, D)]

# Found by a search that maximises the smallest piece, so none is a sliver. In the order they are cut.
CUTS: list[Cut] = [(0.107, 0.156), (1.623, -0.286), (0.992, 0.098), (2.68, 0.277), (0.587, -0.138), (2.143, 0.099)]
L2_CUTS: list[Cut] = [(0.063, -0.226), (0.402, -0.031), (0.625, 0.043), (1.128, -0.292), (1.25, -0.196),
                      (1.627, 0.02), (1.932, -0.077), (2.143, -0.191), (2.548, 0.162), (2.893, 0.077)]


def ends(c: Cut) -> tuple[Pt, Pt]:
    """Where a cut meets the rim of the unit disc."""
    t, d = c
    h = math.sqrt(1 - d * d)
    nx, ny = math.cos(t), math.sin(t)
    return (nx * d - ny * h, ny * d + nx * h), (nx * d + ny * h, ny * d - nx * h)


def crossing(a: Cut, b: Cut) -> Pt | None:
    """Where two cuts cross inside the slice, or None if they do not."""
    det = math.sin(b[0] - a[0])
    if abs(det) < 1e-9:
        return None
    x = (a[1] * math.sin(b[0]) - b[1] * math.sin(a[0])) / det
    y = (b[1] * math.cos(a[0]) - a[1] * math.cos(b[0])) / det
    return (x, y) if x * x + y * y < 1 else None


def past_rim(c: Cut) -> LineString:
    """A cut run slightly past both ends: the rim is a polygon, so it must not stop just short of it."""
    (ax, ay), (bx, by) = ends(c)
    return LineString([(ax * 1.01, ay * 1.01), (bx * 1.01, by * 1.01)])


def coords(p: Polygon) -> list[Pt]:
    return list(p.exterior.coords)[:-1]


@dataclass
class Step:
    """One cut: the stretches it runs along, and the piece each stretch splits."""
    cut: Cut
    points: list[Pt]                           # rim, crossings in order, rim
    splits: list[tuple[int, Polygon, Polygon]] # (index of the piece split, its two halves), one per stretch
    faces: list[Polygon]                       # all pieces afterwards; a split keeps its index for the first half


def make(cuts: list[Cut]) -> list[Step]:
    """Cut the slice one cut at a time."""
    faces, steps = [Polygon(RIM)], []
    for k, c in enumerate(cuts):
        a, b = ends(c)
        along = lambda p: (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])
        hits = sorted(filter(None, (crossing(c, e) for e in cuts[:k])), key=along)
        points = [a, *hits, b]
        knife = past_rim(c)
        faces, splits = list(faces), []
        for p, q in zip(points, points[1:]):
            mid = Point((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            i = next(i for i, f in enumerate(faces) if f.contains(mid))
            one, two = sorted(split(faces[i], knife).geoms, key=lambda g: -g.area)
            faces[i] = one
            faces.append(two)
            splits.append((i, one, two))
        steps.append(Step(c, points, splits, faces))
    return steps


def count(cuts: list[Cut]) -> int:
    """Count pieces a second way: overlay all the cuts at once, then find the enclosed regions."""
    return len(list(polygonize(unary_union([RIM] + [past_rim(c) for c in cuts]))))


def crossings(cuts: list[Cut]) -> int:
    return sum(crossing(a, b) is not None for a, b in combinations(cuts, 2))


STEPS = make(CUTS)
GRID_STEPS = make(GRID_CUTS)
L2_STEPS = make(L2_CUTS)
TOTALS = [len(s.faces) for s in STEPS]
GRID_TOTALS = [len(s.faces) for s in GRID_STEPS]


def main() -> None:
    assert GRID_TOTALS == [2, 3, 4, 8, 12, GRID_PIECES], GRID_TOTALS
    assert crossing(GRID_CUTS[0], GRID_CUTS[1]) is None, "grid cuts one way should be parallel"
    assert crossings(GRID_CUTS) == 9 and count(GRID_CUTS) == GRID_PIECES

    assert TOTALS == [2, 4, 7, 11, 16, MAX_PIECES], TOTALS
    for k, step in enumerate(STEPS, 1):
        assert len(step.points) == k + 1, f"cut {k} misses an earlier cut"
        assert len(step.splits) == k, f"cut {k} should run through {k} pieces"
    assert count(CUTS) == MAX_PIECES and crossings(CUTS) == 15

    points = [crossing(a, b) for a, b in combinations(CUTS, 2)]
    gap = min(math.dist(p, q) for p, q in combinations(points, 2))
    assert gap > 0.05, f"two crossings nearly coincide: {gap}"

    for steps, total in ((STEPS, MAX_PIECES), (GRID_STEPS, GRID_PIECES), (L2_STEPS, L2_PIECES)):
        faces = steps[-1].faces
        assert len(faces) == total
        assert math.isclose(sum(f.area for f in faces), Polygon(RIM).area, rel_tol=1e-9), "pieces do not fill the slice"
        assert all(f1.intersection(f2).area < 1e-9 for f1, f2 in combinations(faces, 2)), "pieces overlap"

    # The ceiling, not just one good example: every crossing adds exactly one piece, for any cuts.
    rng = random.Random(164)
    for _ in range(2000):
        cuts = [(rng.uniform(0, math.pi), rng.uniform(-0.95, 0.95)) for _ in range(N)]
        assert count(cuts) == 1 + N + crossings(cuts), cuts
        assert count(cuts) <= MAX_PIECES
    assert 1 + N + math.comb(N, 2) == MAX_PIECES == 1 + sum(range(1, N + 1))
    assert 1 + N + 9 == GRID_PIECES

    # Legibility: nothing the viewer has to see is a sliver. Radius 3 in the frame.
    smallest = min(f.area / f.length for f in STEPS[-1].faces)
    assert smallest > 0.02, smallest

    assert [len(s.points) - 1 for s in L2_STEPS] == list(range(1, L2_N + 1))
    assert count(L2_CUTS) == L2_PIECES == 1 + sum(range(1, L2_N + 1))

    print(f"OK  grid {GRID_TOTALS}; every cut crossing: {TOTALS}, ceiling {MAX_PIECES}; level2 {L2_PIECES}")


if __name__ == "__main__":
    main()
