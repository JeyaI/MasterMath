"""Verify Short 0008: The Six Frogs (Dudeney, Amusements in Mathematics, no. 214).

Checks, in code, every claim the video makes:
  * layout: squares 0..6, the blank on the left (square 0), frog k on square k. This is the layout
    in which Dudeney's own opening move (frog 2 leaps frog 1) is legal
  * a move is a slide into the next square or a leap over one frog; frogs go either way
  * the goal is 6 5 4 3 2 1 with the blank still on the left
  * breadth-first search: the fewest moves is 21 (and no 20-move solution exists)
  * Dudeney's recipe (2 4 6 5 3 1, three times over, then 2 4 6) is a legal 21-move solution
  * the insight: a slide never changes the order of two frogs, a leap changes exactly one pair,
    and the goal flips all C(6,2)=15 pairs, so at least 15 leaps; the solution has 15 leaps + 6 slides
  * the general count: n even gives n(n+1)/2 moves, checked by search for n = 2, 4, 6, 8
  * Level 2: 8 frogs need 28 leaps + 8 slides = 36 moves

The scene imports everything below.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations
from math import comb

N = 6
RECIPE = [2, 4, 6, 5, 3, 1] * 3 + [2, 4, 6]
L2_N = 8
L2_MOVES, L2_LEAPS, L2_SLIDES = 36, 28, 8

Board = tuple[int, ...]            # board[i] = frog on square i, 0 for the blank


def start(n: int) -> Board:
    return tuple(range(n + 1))      # blank, 1, 2, ..., n


def goal(n: int) -> Board:
    return (0, *range(n, 0, -1))    # blank, n, ..., 1


def moves(b: Board) -> list[tuple[int, Board, bool]]:
    """Every legal move from b as (frog, new board, is_leap)."""
    blank = b.index(0)
    out = []
    for d in (-1, 1):
        for step in (1, 2):
            src = blank + d * step
            if not 0 <= src < len(b):
                continue
            if step == 2 and b[blank + d] == 0:
                continue
            nb = list(b)
            nb[blank], nb[src] = b[src], 0
            out.append((b[src], tuple(nb), step == 2))
    return out


def shortest(n: int) -> int:
    seen = {start(n): 0}
    q = deque([start(n)])
    while q:
        b = q.popleft()
        if b == goal(n):
            return seen[b]
        for _, nb, _ in moves(b):
            if nb not in seen:
                seen[nb] = seen[b] + 1
                q.append(nb)
    raise AssertionError("goal unreachable")


def play(order: list[int], n: int = N) -> list[tuple[int, Board, bool]]:
    """Play the frogs in the given order. Returns [(frog, board after, is_leap)]; asserts each move is legal."""
    b, trace = start(n), []
    for f in order:
        options = [(fr, nb, lp) for fr, nb, lp in moves(b) if fr == f]
        assert len(options) == 1, f"frog {f} has no single legal move from {b}"
        b = options[0][1]
        trace.append(options[0])
    return trace


def inversions(b: Board) -> int:
    frogs = [x for x in b if x]
    return sum(1 for i, j in combinations(range(len(frogs)), 2) if frogs[i] > frogs[j])


TRACE = play(RECIPE)
BOARDS: list[Board] = [start(N)] + [t[1] for t in TRACE]     # BOARDS[k] = position after k moves
LEAPS = [lp for _, _, lp in TRACE]
N_LEAPS, N_SLIDES = sum(LEAPS), len(LEAPS) - sum(LEAPS)


def main() -> None:
    assert start(N) == (0, 1, 2, 3, 4, 5, 6) and goal(N) == (0, 6, 5, 4, 3, 2, 1)

    # shortest by search
    assert shortest(N) == 21
    # Dudeney's recipe is legal and lands on the goal in 21 moves
    assert len(RECIPE) == 21 and BOARDS[-1] == goal(N)

    # the pair-crossing argument
    for k, (_, nb, lp) in enumerate(TRACE):
        d = inversions(nb) - inversions(BOARDS[k])
        assert d == (1 if lp else 0), "a leap must flip exactly one pair, a slide none"
    assert inversions(goal(N)) == comb(N, 2) == 15
    assert N_LEAPS == 15 and N_SLIDES == 6 and N_LEAPS + N_SLIDES == 21

    # general rule for even n (and the 7-frog extension the puzzle asks for)
    for n in (2, 4, 6, 8):
        assert shortest(n) == n * (n + 1) // 2, n
    assert shortest(7) == (49 + 21) // 2 - 4

    # Level 2: 8 frogs
    order8 = ([2, 4, 6, 8, 7, 5, 3, 1]) * 4 + [2, 4, 6, 8]
    t8 = play(order8, L2_N)
    assert t8[-1][1] == goal(L2_N) and len(t8) == L2_MOVES == shortest(L2_N)
    assert sum(lp for _, _, lp in t8) == L2_LEAPS == comb(L2_N, 2)
    assert L2_MOVES - L2_LEAPS == L2_SLIDES == L2_N

    print(f"OK  6 frogs: {len(RECIPE)} moves = {N_LEAPS} leaps + {N_SLIDES} slides (BFS agrees); "
          f"level2 8 frogs: {L2_MOVES} moves")


if __name__ == "__main__":
    main()
