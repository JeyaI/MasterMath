"""Verify Short 0010: A Juvenile Puzzle (Dudeney, Amusements in Mathematics, no. 239).

The book's figure is only given as a sketch, so we draw our own figure with the same property
(it looks like it needs four strokes): a rectangle, a bar across the middle, two upright lines
above the bar (C-D, E-F) and one below it (G-H).

Checks, in code, every claim the video makes:
  * the figure is connected and has exactly 8 odd points, so (parity) it needs at least 4 strokes
  * exhaustive search: 4 strokes work and 3 do not (without folding)
  * with two fingers, one swipe wipes C-D and E-F together (parallel, equal); the rest needs
    2 more swipes: 3 in all
  * the explicit strokes below cover every line exactly once, each a legal pencil path
  * Level 2: a 3 x 5 grid of squares has 12 odd points, so it needs 6 strokes (and 6 are found)

The scene imports everything below.
"""
from __future__ import annotations

from functools import lru_cache

# Points of the figure (x right, y up); the rectangle is 6 wide and 4 tall
PTS = {
    "TL": (0, 4), "C": (2, 4), "E": (4, 4), "TR": (6, 4),
    "A": (0, 2), "D": (2, 2), "G": (3, 2), "F": (4, 2), "B": (6, 2),
    "BL": (0, 0), "H": (3, 0), "BR": (6, 0),
}
# Lines (each joins two points)
FOLD_PAIR = [("C", "D"), ("E", "F")]            # the two lines drawn together by the fold
REST = [
    ("TL", "C"), ("C", "E"), ("E", "TR"), ("TR", "B"), ("B", "BR"), ("BR", "H"),
    ("H", "BL"), ("BL", "A"), ("A", "TL"),
    ("A", "D"), ("D", "G"), ("G", "F"), ("F", "B"),
    ("G", "H"),
]
EDGES = FOLD_PAIR + REST

# The folded solution: stroke 1 is the fold (both uprights at once), then two ordinary strokes
# (filled in below from the search, so the scene draws exactly what was checked)
STROKES: list = []

# Level 2: a 3 x 5 grid of squares (4 rows by 6 columns of points)
GRID_ROWS, GRID_COLS = 3, 5
L2_ANSWER = 6


def key(e):
    return frozenset(e)


def odd_points(edges):
    deg: dict = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    return sorted(n for n, d in deg.items() if d % 2)


def connected(edges) -> bool:
    adj: dict = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    start = next(iter(adj))
    seen, todo = {start}, [start]
    while todo:
        for m in adj[todo.pop()]:
            if m not in seen:
                seen.add(m)
                todo.append(m)
    return len(seen) == len(adj)


def cover(edges, k):
    """Exhaustive search: cover all edges with at most k trails (no line twice in one stroke)."""
    @lru_cache(maxsize=None)
    def go(rem: frozenset, k: int):
        if not rem:
            return ()
        if k == 0 or (len(odd_points([tuple(e) for e in rem])) + 1) // 2 > k:
            return None
        nodes = {n for e in rem for n in e}
        for s in sorted(nodes):
            found = walk(s, [s], rem, rem, k)
            if found is not None:
                return found
        return None

    def walk(start, path, left, rem, k):
        # try ending the stroke here (needs at least one edge), then continue extending
        if len(path) > 1:
            r = go(left, k - 1)
            if r is not None:
                return (tuple(path),) + r
        here = path[-1]
        for e in sorted(tuple(sorted(x)) for x in left):
            if here in e:
                nxt = e[0] if e[1] == here else e[1]
                r = walk(start, path + [nxt], left - {frozenset(e)}, rem, k)
                if r is not None:
                    return r
        return None

    return go(frozenset(key(e) for e in edges), k)


def check_trails(trails, edges):
    """Each trail is a legal pencil path; together they use every edge exactly once."""
    want = sorted(tuple(sorted(e)) for e in edges)
    used = []
    for t in trails:
        for a, b in zip(t, t[1:]):
            used.append(tuple(sorted((a, b))))
    assert sorted(used) == want, (sorted(used), want)


def euler_split(edges, nodes_odd):
    """Pair up odd points with spare links, take an Euler circuit, cut at the spare links."""
    spare = [("~%d" % i, nodes_odd[2 * i], nodes_odd[2 * i + 1]) for i in range(len(nodes_odd) // 2)]
    adj: dict = {}
    for i, (a, b) in enumerate(edges):
        adj.setdefault(a, []).append((b, ("r", i)))
        adj.setdefault(b, []).append((a, ("r", i)))
    for name, a, b in spare:
        adj.setdefault(a, []).append((b, ("s", name)))
        adj.setdefault(b, []).append((a, ("s", name)))
    used, stack, circuit = set(), [(next(iter(adj)), None)], []
    while stack:
        v, via = stack[-1]
        while adj[v] and adj[v][-1][1] in used:
            adj[v].pop()
        if adj[v]:
            w, eid = adj[v].pop()
            used.add(eid)
            stack.append((w, eid))
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    trails, cur = [], [circuit[0][0]]
    for v, eid in circuit[1:]:
        if eid[0] == "s":
            if len(cur) > 1:
                trails.append(cur)
            cur = [v]
        else:
            cur.append(v)
    if len(cur) > 1:
        trails.append(cur)
    # the circuit may have started mid-way: if it did not begin and end on a spare link,
    # the last piece and the first piece are really one stroke
    first_is_cut = circuit[1][1][0] == "s"
    last_is_cut = circuit[-1][1][0] == "s"
    if len(trails) > 1 and not first_is_cut and not last_is_cut:
        trails[0] = trails.pop() + trails[0][1:]
    return trails


def grid_edges(rows, cols):
    es = []
    for r in range(rows + 1):
        for c in range(cols + 1):
            if c < cols:
                es.append(((r, c), (r, c + 1)))
            if r < rows:
                es.append(((r, c), (r + 1, c)))
    return es


STROKES[:] = [list(t) for t in (cover(REST, 2) or ())]


def main() -> None:
    # --- Level 1: the figure without folding
    assert connected(EDGES)
    odd = odd_points(EDGES)
    assert odd == sorted(["C", "E", "D", "F", "A", "B", "G", "H"]), odd
    assert len(odd) == 8                          # 8 odd points -> at least 4 strokes
    assert cover(EDGES, 3) is None                # three ordinary strokes are impossible
    four = cover(EDGES, 4)
    assert four is not None and len(four) == 4
    check_trails(four, EDGES)

    # --- with the fold: C-D and E-F in one stroke, the rest in two
    assert odd_points(REST) == sorted(["A", "B", "G", "H"])
    two = cover(REST, 2)
    assert two is not None and len(two) == 2
    check_trails(two, REST)
    assert cover(REST, 1) is None                 # the rest needs both
    total = 1 + len(two)
    assert total == 3
    # the folded lines are parallel and the same length, so folded between them they coincide
    (c, d), (e, f) = FOLD_PAIR
    assert PTS[c][1] == PTS[e][1] and PTS[d][1] == PTS[f][1] and PTS[c][0] != PTS[e][0]
    fold_x = (PTS[c][0] + PTS[e][0]) / 2
    assert fold_x == PTS["G"][0]                  # the crease falls on the line G-H

    assert [list(t) for t in two] == STROKES

    # --- Level 2: 3 x 5 grid of squares
    g = grid_edges(GRID_ROWS, GRID_COLS)
    assert len(g) == 3 * 6 + 4 * 5 == 38
    assert connected(g)
    go = odd_points(g)
    assert len(go) == 2 * (GRID_COLS - 1) + 2 * (GRID_ROWS - 1) == 12   # edge points, not corners
    assert (len(go) // 2) == L2_ANSWER == 6
    trails = euler_split(g, go)
    assert len(trails) == L2_ANSWER
    check_trails(trails, g)

    print("OK  figure has 8 odd points: 4 strokes (3 impossible); with the fold 1 + 2 = 3 strokes; "
          "level2 3x5 grid has 12 odd points -> 6 strokes")


if __name__ == "__main__":
    main()
