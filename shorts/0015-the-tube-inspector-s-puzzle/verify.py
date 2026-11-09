"""Verify Short 0015: The Tube Inspector's Puzzle (Dudeney, Amusements in Mathematics, no. 242).

Checks, in code, every claim the video makes:
  * the poster plan is a 3-wide, 4-high grid of 12 stations A..L with 17 lines
  * Dudeney's route BADGDEFIFCBEHKLIHGJK walks every line, uses real lines only, and is 19 miles
  * the odd stations (an odd number of lines meet there) are B, D, F, G, I, K
  * a walk over every line can have at most two odd stations (its start and end), so repeating the
    lines D-G and F-I leaves exactly B and K odd, and the walk runs from B to K
  * brute force over every set of lines to repeat: at least 2 repeats are needed, so 19 is the minimum
    (each line repeated once is enough: repeating a line twice never helps)
  * Level 2: the 3 x 3 grid of 9 stations and 12 lines -> 14 miles

Stations are (column, row) with row 0 at the top. The scene imports everything below.
"""
from __future__ import annotations

from itertools import combinations
from string import ascii_uppercase

COLS, ROWS = 3, 4
ROUTE = "BADGDEFIFCBEHKLIHGJK"
REPEATED = [("D", "G"), ("F", "I")]
ODD = ["B", "D", "F", "G", "I", "K"]
START, END = "B", "K"
MILES = 19
L2_COLS, L2_ROWS, L2_MILES = 3, 3, 14


def grid(cols: int, rows: int):
    """Stations named A, B, C... row by row; lines between neighbours (alphabetical pairs)."""
    names = {}
    for r in range(rows):
        for c in range(cols):
            names[(c, r)] = ascii_uppercase[r * cols + c]
    edges = []
    for (c, r), n in names.items():
        if c + 1 < cols:
            edges.append(tuple(sorted((n, names[(c + 1, r)]))))
        if r + 1 < rows:
            edges.append(tuple(sorted((n, names[(c, r + 1)]))))
    return names, sorted(edges)


POS, LINES = grid(COLS, ROWS)               # POS: (column, row) -> station letter
STATION = {v: k for k, v in POS.items()}    # letter -> (column, row)


def odd_stations(edges) -> list[str]:
    deg: dict[str, int] = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    return sorted(s for s, d in deg.items() if d % 2)


def connected(edges, nodes) -> bool:
    seen, stack = set(), [next(iter(nodes))]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack += [b if a == n else a for a, b in edges if n in (a, b)]
    return seen >= set(nodes)


def shortest_walk(edges) -> int:
    """Fewest lines travelled to cover every line once at least: lines + fewest repeats such that the
    doubled graph has at most two odd stations (then an Euler walk exists, the graph being connected)."""
    nodes = {s for e in edges for s in e}
    for k in range(len(edges) + 1):
        for extra in combinations(edges, k):
            if len(odd_stations(list(edges) + list(extra))) <= 2:
                return len(edges) + k
    raise AssertionError


def main() -> None:
    assert len(POS) == 12 and len(LINES) == 17
    edges = set(LINES)
    assert connected(LINES, {s for e in LINES for s in e})

    # Dudeney's route
    steps = [tuple(sorted(p)) for p in zip(ROUTE, ROUTE[1:])]
    assert set(steps) == edges, "route must use real lines and cover all of them"
    assert len(steps) == MILES
    twice = sorted(e for e in edges if steps.count(e) == 2)
    assert twice == sorted(tuple(sorted(e)) for e in REPEATED)
    assert all(steps.count(e) in (1, 2) for e in edges)
    assert ROUTE[0] == START and ROUTE[-1] == END

    # Odd stations, and the pairing trick
    assert odd_stations(LINES) == ODD
    assert odd_stations(LINES + [tuple(sorted(e)) for e in REPEATED]) == [START, END]
    for a, b in REPEATED:                      # each repeated line joins two neighbouring odd stations
        assert a in ODD and b in ODD and tuple(sorted((a, b))) in edges

    # Lower bound by brute force
    assert shortest_walk(LINES) == MILES

    # Level 2
    _, lines2 = grid(L2_COLS, L2_ROWS)
    assert len(lines2) == 12 and len(odd_stations(lines2)) == 4
    assert shortest_walk(lines2) == L2_MILES

    print(f"OK  {len(LINES)} lines, odd {ODD}, shortest walk {MILES} miles; level2 3x3 grid: {L2_MILES}")


if __name__ == "__main__":
    main()
