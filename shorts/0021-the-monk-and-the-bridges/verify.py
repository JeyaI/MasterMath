"""Verify Short 0021: The Monk and the Bridges (Dudeney, Amusements in Mathematics, no. 261).

Checks, in code, every claim the video makes:
  * the map is a graph on M (monk), I (island), Y (monastery): bridges a, b join M-I,
    c, d join I-Y, and e joins M-Y
  * a route is an order of all five bridges, each crossed once, starting at M, ending at Y
  * there are exactly 16 routes (Dudeney's list matches ours)
  * the insight: swapping the twin bridges (a<->b, c<->d) never changes where the monk walks
    (the "shape" of the route, the list of places visited), and every route has all 4 of its
    relabellings in the list. So the 16 routes are 4 shapes x 2 x 2 labellings.
  * Level 2: M-I twins, I-Y twins and M-Y twins (6 bridges), start and end at M.
    The shapes and the count are computed below.

The scene imports everything below.
"""
from __future__ import annotations

from itertools import permutations

# Level 1 map
BRIDGES = {"a": ("M", "I"), "b": ("M", "I"), "c": ("I", "Y"), "d": ("I", "Y"), "e": ("M", "Y")}
START, END = "M", "Y"
TWINS = (("a", "b"), ("c", "d"))

# Level 2 map: the same, with a second direct bridge f between M and Y; the monk walks round and
# finishes where he started.
BRIDGES2 = {"a": ("M", "I"), "b": ("M", "I"), "c": ("I", "Y"), "d": ("I", "Y"),
            "e": ("M", "Y"), "f": ("M", "Y")}
START2, END2 = "M", "M"
TWINS2 = (("a", "b"), ("c", "d"), ("e", "f"))

# Dudeney's printed list
BOOK = """a b e c d | b c d a e
a b e d c | b c e a d
a c d b e | b d c a e
a c e b d | b d e a c
a d e b c | e c a b d
a d c b e | e c b a d
b a e c d | e d a b c
b a e d c | e d b a c"""


def walk(order, bridges, start):
    """Places visited if the monk crosses the bridges in this order; None if not a legal walk."""
    here = start
    places = [here]
    for br in order:
        p, q = bridges[br]
        if here == p:
            here = q
        elif here == q:
            here = p
        else:
            return None
        places.append(here)
    return "".join(places)


def routes(bridges, start, end):
    out = []
    for order in permutations(sorted(bridges)):
        w = walk(order, bridges, start)
        if w is not None and w[-1] == end:
            out.append("".join(order))
    return out


def swap(order, pair):
    x, y = pair
    return order.translate(str.maketrans({x: y, y: x}))


def shapes(bridges, start, end):
    """Group routes by the places visited. Returns {places: [routes]}."""
    groups: dict[str, list[str]] = {}
    for r in routes(bridges, start, end):
        groups.setdefault(walk(r, bridges, start), []).append(r)
    return groups


ROUTES = routes(BRIDGES, START, END)
SHAPES = shapes(BRIDGES, START, END)
ROUTES2 = routes(BRIDGES2, START2, END2)
SHAPES2 = shapes(BRIDGES2, START2, END2)


def main() -> None:
    # Level 1: the count
    assert len(ROUTES) == 16
    book = {w for line in BOOK.splitlines() for part in line.split("|") for w in ["".join(part.split())]}
    assert len(book) == 16 and book == set(ROUTES)

    # only M and Y have an odd number of bridges, so every route runs M -> Y
    deg = {}
    for p, q in BRIDGES.values():
        deg[p] = deg.get(p, 0) + 1
        deg[q] = deg.get(q, 0) + 1
    assert deg == {"M": 3, "I": 4, "Y": 3}
    assert not routes(BRIDGES, "M", "M") and not routes(BRIDGES, "M", "I")

    # the insight: swapping twins keeps the places visited, and 4 labellings per shape
    assert len(SHAPES) == 4
    for places, rs in SHAPES.items():
        assert len(rs) == 4
        for r in rs:
            for pair in TWINS:
                assert swap(r, pair) in rs
            assert swap(swap(r, TWINS[0]), TWINS[1]) in rs
        # the four labellings are all different
        assert len(set(rs)) == 4
    assert sum(len(r) for r in SHAPES.values()) == 16

    # first-bridge split, as the scene may show it: 6 + 6 + 4
    first = {}
    for r in ROUTES:
        first[r[0]] = first.get(r[0], 0) + 1
    assert first == {"a": 6, "b": 6, "e": 4}

    # Level 2
    assert len(ROUTES2) == len(SHAPES2) * 8
    for places, rs in SHAPES2.items():
        assert len(rs) == 8
        for r in rs:
            for pair in TWINS2:
                assert swap(r, pair) in rs

    print("OK  level1 16 routes =", len(SHAPES), "shapes x 4:", sorted(SHAPES),
          "| level2", len(ROUTES2), "routes =", len(SHAPES2), "shapes x 8:", sorted(SHAPES2))


if __name__ == "__main__":
    main()
