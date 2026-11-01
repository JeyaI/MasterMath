"""Verify Short 0004: Bishops In Convocation (Dudeney, Amusements in Mathematics, no. 299).

Checks, in code, every claim the video makes:
  * 14 is the most non-attacking bishops an 8 x 8 board holds, and 256 placements reach it
  * every bishop in every one of those placements stands on the edge
  * bouncing a diagonal off the edges closes into a track: 6 rectangular loops and 2 corner diagonals
  * neighbouring corners of a loop attack each other, opposite corners do not
  * the tracks use every edge square once, and every diagonal is part of exactly one track
  * so each track's 2 settings are free, and those 2^8 choices are exactly the brute-force placements
  * the three placements shown before the countdown are legal and different
  * Level 2: on 10 x 10 the maximum is 18, in 2^10 = 1024 ways, from 10 tracks

Squares are (column, row) from the bottom left, so a1 is (0, 0). The brute force works one colour
at a time, because bishops on opposite colours never attack. The scene imports everything below.
"""
from __future__ import annotations

from itertools import combinations, product

Square = tuple[int, int]

N, MAX_BISHOPS, WAYS = 8, 14, 256
L2_N, L2_BISHOPS, L2_WAYS = 10, 18, 1024


def attack(a: Square, b: Square) -> bool:
    return a != b and abs(a[0] - b[0]) == abs(a[1] - b[1])


def bounce(n: int, start: Square, heading: Square) -> list[Square]:
    """Run a diagonal from `start`, reflecting off the walls until it comes home. Returns the corners."""
    corners = [start]
    (c, r), (dc, dr) = start, heading
    while True:
        k = min(n - 1 - c if dc > 0 else c, n - 1 - r if dr > 0 else r)
        c, r = c + dc * k, r + dr * k
        if c in (0, n - 1):
            dc = -dc
        if r in (0, n - 1):
            dr = -dr
        if (c, r) == start:
            return corners
        corners.append((c, r))


def tracks(n: int) -> list[list[Square]]:
    """Every track on an even board, dark-square loops first, then light, then the two long diagonals."""
    dark = [bounce(n, (0, k), (1, -1)) for k in range(2, n, 2)]
    light = [bounce(n, (0, k), (1, 1)) for k in range(n - 3, 0, -2)]
    return dark + light + [bounce(n, (0, 0), (1, 1)), bounce(n, (0, n - 1), (1, -1))]


def seats(track: list[Square], setting: int) -> list[Square]:
    """Where a track's bishops stand: opposite corners of a loop, or one end of a long diagonal."""
    return [track[setting]] if len(track) == 2 else [track[setting], track[setting + 2]]


def placement(ts: list[list[Square]], settings: tuple[int, ...]) -> frozenset[Square]:
    return frozenset(s for t, k in zip(ts, settings) for s in seats(t, k))


def brute(n: int) -> tuple[int, set[frozenset[Square]]]:
    """Largest non-attacking bishop sets, by exhaustive search on each colour."""
    total, sets = 0, []
    for colour in (0, 1):
        squares = [(c, r) for c in range(n) for r in range(n) if (c + r) % 2 == colour]
        best: list = [0, []]

        def go(i: int, chosen: list[Square], sums: frozenset, diffs: frozenset) -> None:
            if len(chosen) + len(squares) - i < best[0]:
                return
            if i == len(squares):
                if len(chosen) > best[0]:
                    best[:] = [len(chosen), []]
                best[1].append(frozenset(chosen))
                return
            c, r = squares[i]
            if c + r not in sums and c - r not in diffs:
                go(i + 1, chosen + [(c, r)], sums | {c + r}, diffs | {c - r})
            go(i + 1, chosen, sums, diffs)

        go(0, [], frozenset(), frozenset())
        total += best[0]
        sets.append(best[1])
    return total, {a | b for a in sets[0] for b in sets[1]}


def diagonal(a: Square, b: Square) -> tuple[str, int]:
    """Name the diagonal line through two squares."""
    return ("/", a[0] - a[1]) if (a[0] - b[0]) == (a[1] - b[1]) else ("\\", a[0] + a[1])


def sides(track: list[Square]) -> list[tuple[Square, Square]]:
    return [(track[0], track[1])] if len(track) == 2 else list(zip(track, track[1:] + track[:1]))


TRACKS = tracks(N)
L2_TRACKS = tracks(L2_N)
LOOP = TRACKS[0]                                   # a3, c1, h6, f8: the loop the video traces

# Dudeney's picture: a full top row and the bottom row without its corners.
DUDENEY = frozenset({(c, N - 1) for c in range(N)} | {(c, 0) for c in range(1, N - 1)})
START = next(s for s in product((0, 1), repeat=len(TRACKS)) if placement(TRACKS, s) == DUDENEY)
OTHERS = [tuple(1 - k if i % 2 else k for i, k in enumerate(START)),   # the "another way" boards
          tuple(1 - k if i % 3 == 0 else k for i, k in enumerate(START))]
RAY_FROM = (2, 7)                                  # the bishop whose diagonals the video draws
L2_START = frozenset({(c, L2_N - 1) for c in range(L2_N)} | {(c, 0) for c in range(1, L2_N - 1)})


def edge(n: int, s: Square) -> bool:
    return s[0] in (0, n - 1) or s[1] in (0, n - 1)


def check_board(n: int, ts: list[list[Square]], bishops: int, ways: int) -> None:
    total, sets = brute(n)
    assert total == bishops, total
    assert len(sets) == ways == 2 ** n, len(sets)
    assert all(edge(n, s) for p in sets for s in p), "a bishop off the edge"

    assert len(ts) == n and sum(len(t) == 4 for t in ts) == n - 2 and sum(len(t) == 2 for t in ts) == 2
    on_tracks = [s for t in ts for s in t]
    assert len(on_tracks) == len(set(on_tracks)) == 4 * (n - 1), "edge squares are shared"
    assert set(on_tracks) == {(c, r) for c in range(n) for r in range(n) if edge(n, (c, r))}

    for t in ts:
        assert all(attack(a, b) for a, b in sides(t)), "a track side is not a diagonal"
        if len(t) == 4:
            assert not attack(t[0], t[2]) and not attack(t[1], t[3]), "opposite corners attack"

    # Every diagonal of two or more squares is a side of exactly one track, so tracks can't interfere.
    lines = [diagonal(a, b) for t in ts for a, b in sides(t)]
    assert len(lines) == len(set(lines)) == 2 * (2 * n - 3)
    from_settings = {placement(ts, s) for s in product((0, 1), repeat=n)}
    assert from_settings == sets, "the tracks do not give exactly the true placements"


def main() -> None:
    check_board(N, TRACKS, MAX_BISHOPS, WAYS)
    check_board(L2_N, L2_TRACKS, L2_BISHOPS, L2_WAYS)
    assert (2 * N - 2, 2 * L2_N - 2) == (MAX_BISHOPS, L2_BISHOPS)

    assert LOOP == [(0, 2), (2, 0), (7, 5), (5, 7)], LOOP
    assert TRACKS[-2] == [(0, 0), (7, 7)] and TRACKS[-1] == [(0, 7), (7, 0)]
    colours = [{(c + r) % 2 for c, r in t} for t in TRACKS]
    assert all(len(k) == 1 for k in colours), "a track changes colour"
    assert [k for k, in colours] == [0, 0, 0, 1, 1, 1, 0, 1], colours

    shown = [DUDENEY, *(placement(TRACKS, s) for s in OTHERS)]
    assert len(set(shown)) == 3 and all(len(p) == MAX_BISHOPS for p in shown)
    assert not any(attack(a, b) for p in shown for a, b in combinations(p, 2))
    assert RAY_FROM in DUDENEY and L2_START in brute(L2_N)[1]

    print(f"OK  {MAX_BISHOPS} bishops, {WAYS} ways from {len(TRACKS)} tracks, all on the edge; "
          f"level2 {L2_N}x{L2_N}: {L2_BISHOPS} bishops, {L2_WAYS} ways")


if __name__ == "__main__":
    main()
