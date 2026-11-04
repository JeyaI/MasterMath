"""Verify Short 0008: The Six Frogs (Dudeney, Amusements in Mathematics, no. 214).

Checks, in code, every claim the video makes:
  * layout: squares 0..n, the blank on the left (square 0), frog k on square k. This is the layout
    in which Dudeney's own opening move (frog 2 leaps frog 1) is legal
  * a move is a slide into the next square or a leap over one frog; frogs go either way
  * the goal is n .. 3 2 1 with the blank still on the left
  * Level 1 is 4 frogs: breadth-first search says 10 moves is the fewest, and Dudeney's recipe
    (2 4 3 1 twice, then 2 4) is a legal 10-move solution (6 leaps + 4 slides)
  * Level 2 is 6 frogs: the fewest is 21 (search), the recipe (2 4 6 5 3 1 three times, then 2 4 6)
    plays it, and 15 of the 21 moves are leaps (the answer asked for)
  * the general count: n even gives n(n+1)/2 moves, checked by search for n = 2, 4, 6

The scene imports everything below.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations
from math import comb

N = 4
RECIPE = [2, 4, 3, 1] * 2 + [2, 4]
MOVES = 10
L2_N = 6
L2_RECIPE = [2, 4, 6, 5, 3, 1] * 3 + [2, 4, 6]
L2_MOVES, L2_LEAPS, L2_SLIDES = 21, 15, 6      # Level 2 asks: how many of the 21 moves are leaps? 15

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
    assert start(N) == (0, 1, 2, 3, 4) and goal(N) == (0, 4, 3, 2, 1)

    # "Can you do it in 10 moves?" is also the true minimum, so we may say 10 is optimal
    assert shortest(N) == MOVES == 10
    assert shortest(N - 1) != MOVES            # sanity: the search is not a constant
    # Dudeney's recipe (2 4 3 1 twice, then 2 4) is legal and lands on the goal in 10 moves
    assert len(RECIPE) == MOVES and BOARDS[-1] == goal(N)
    assert N_LEAPS == comb(N, 2) == 6 and N_SLIDES == 4

    # Level 2: 6 frogs, 21 moves, optimal; 15 of them are leaps
    assert shortest(L2_N) == L2_MOVES == 21
    t6 = play(L2_RECIPE, L2_N)
    assert t6[-1][1] == goal(L2_N) and len(t6) == L2_MOVES
    assert sum(lp for _, _, lp in t6) == L2_LEAPS == comb(L2_N, 2) == 15
    assert L2_MOVES - L2_LEAPS == L2_SLIDES == L2_N
    # in the recipe a leap flips exactly one pair and a slide none, so its 15 leaps are the 15 pairs
    for k, (_, nb, lp) in enumerate(t6):
        prev = start(L2_N) if k == 0 else t6[k - 1][1]
        assert inversions(nb) - inversions(prev) == (1 if lp else 0)

    # general rule for even n, for the "it always works" line
    for n in (2, 4, 6):
        assert shortest(n) == n * (n + 1) // 2, n

    print(f"OK  4 frogs: {MOVES} moves = {N_LEAPS} leaps + {N_SLIDES} slides (BFS agrees, optimal); "
          f"level2 6 frogs: {L2_MOVES} moves, {L2_LEAPS} leaps")


if __name__ == "__main__":
    main()
