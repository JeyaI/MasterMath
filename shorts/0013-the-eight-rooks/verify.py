"""Verify Short 0013: The Eight Rooks (Dudeney, Amusements in Mathematics, no. 295).

Checks, in code, every claim the video makes:
  * a placement of n rooks leaves no rook attacked and no square unattacked exactly when it has one rook
    in every row and every column (brute force on 4 x 4, 5 x 5 and 6 x 6 boards, all subsets of n squares)
  * the number of such placements is n!: 24, 120, 720 (brute force), and 8! = 40320 for the real board
  * the row-by-row choice counts 8, 7, 6, ..., 1 multiply to 8! (the video's ladder)
  * the three placements shown before the countdown are legal and different
  * Level 2: a 10 x 10 board with ten rooks -> 10! = 3,628,800

Squares are (column, row) from the bottom left. The scene imports everything below.
"""
from __future__ import annotations

from itertools import combinations, permutations
from math import factorial, prod

Square = tuple[int, int]

N, WAYS = 8, 40320
L2_N, L2_WAYS = 10, 3628800
L2_COLS = (2, 7, 0, 5, 9, 3, 8, 1, 6, 4)            # the rooks drawn on the Level 2 card
LADDER = list(range(N, 0, -1))                     # 8, 7, 6, ... 1: free columns left for each row

# Placements the video shows: column of the rook in each row, top row first.
DIAGONAL = tuple(range(N))                          # Dudeney's Fig. 2
ANTI = tuple(reversed(range(N)))                    # the other diagonal (counts as different)
SCATTER = (3, 6, 1, 4, 7, 0, 2, 5)                  # a third, irregular one


def rooks(cols: tuple[int, ...]) -> list[Square]:
    """Rooks from a column per row, listed top row first (row 0 is the top of the picture)."""
    return [(c, r) for r, c in enumerate(cols)]


def attacks(a: Square, b: Square) -> bool:
    return a != b and (a[0] == b[0] or a[1] == b[1])


def legal(n: int, placed: list[Square]) -> bool:
    """n rooks, none attacked by another, every square occupied or attacked."""
    if len(placed) != n or any(attacks(a, b) for a, b in combinations(placed, 2)):
        return False
    cols, rows = {c for c, _ in placed}, {r for _, r in placed}
    return all(c in cols or r in rows for c in range(n) for r in range(n))


def brute(n: int) -> int:
    squares = [(c, r) for c in range(n) for r in range(n)]
    good = 0
    for placed in combinations(squares, n):
        if legal(n, list(placed)):
            good += 1
            assert len({c for c, _ in placed}) == n and len({r for _, r in placed}) == n
    return good


def main() -> None:
    for n in (4, 5, 6):
        assert brute(n) == factorial(n), n
    assert prod(LADDER) == factorial(N) == WAYS
    assert sum(1 for _ in permutations(range(N))) == WAYS
    assert all(legal(N, rooks(p)) for p in permutations(range(N)))   # every permutation is legal
    assert factorial(L2_N) == L2_WAYS == 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1
    assert sorted(L2_COLS) == list(range(L2_N)) and legal(L2_N, rooks(L2_COLS))

    shown = [DIAGONAL, ANTI, SCATTER]
    assert len(set(shown)) == 3 and all(sorted(p) == list(range(N)) for p in shown)
    assert all(legal(N, rooks(p)) for p in shown)

    # Dudeney's Fig. 1: eight rooks along one rank cover the board but guard each other.
    fig1 = [(c, 3) for c in range(N)]
    assert not legal(N, fig1) and all(any(attacks(a, b) for b in fig1) for a in fig1)

    print(f"OK  {N} rooks: {WAYS} ways (= {N}!), ladder {LADDER}; level2 {L2_N}x{L2_N}: {L2_WAYS}")


if __name__ == "__main__":
    main()
