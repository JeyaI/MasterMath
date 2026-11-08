"""Verify Short 0014: Mrs. Perkins's Quilt (Dudeney, Amusements in Mathematics, no. 173).

Checks, in code, every claim the video makes:
  * the 13 x 13 quilt (169 unit pieces) can be tiled by 11 squares (the tiling drawn below is exact:
    squares inside the quilt, no overlaps, areas sum to 169)
  * no tiling with 10 or fewer squares exists (exhaustive skyline search, which finds the minimum)
  * the minimum for the 13 x 13 quilt is therefore 11, and the sizes are 7, 6, 6, 4, 3, 3, 2, 2, 2, 1, 1
  * the three biggest squares (7, 6, 6) fit along two sides: 7 + 6 = 13
  * Level 2: a 5 x 5 quilt needs at least 8 squares (search), and the drawn tiling 3,2,2,1,1,1,1,1 works

Squares are (x, y, size) with (0, 0) the bottom left corner. The scene imports everything below.
"""
from __future__ import annotations

from functools import lru_cache

N = 13
MIN_SQUARES = 11
SIZES = (7, 6, 6, 4, 3, 3, 2, 2, 2, 1, 1)
L2_N = 5
L2_ANSWER = 8

Square = tuple[int, int, int]


def search(n: int, limit: int) -> list[Square] | None:
    """A tiling of the n x n square by at most `limit` squares, or None. Fills the lowest gap first."""

    @lru_cache(maxsize=None)
    def go(heights: tuple[int, ...], left: int) -> tuple[Square, ...] | None:
        if min(heights) == n:
            return ()
        if left == 0:
            return None
        low = min(heights)
        x = heights.index(low)
        run = 1
        while x + run < n and heights[x + run] == low:
            run += 1
        for s in range(min(run, n - low, n - 1), 0, -1):    # the whole quilt as one piece doesn't count
            nxt = heights[:x] + (low + s,) * s + heights[x + s:]
            rest = go(nxt, left - 1)
            if rest is not None:
                return ((x, low, s),) + rest
        return None

    res = go((0,) * n, limit)
    return None if res is None else list(res)


def minimum(n: int) -> int:
    for k in range(1, n * n + 1):
        if search(n, k) is not None:
            return k
    raise AssertionError


def is_tiling(n: int, squares: list[Square]) -> bool:
    cells = set()
    for x, y, s in squares:
        if x < 0 or y < 0 or x + s > n or y + s > n:
            return False
        for i in range(s):
            for j in range(s):
                if (x + i, y + j) in cells:
                    return False
                cells.add((x + i, y + j))
    return len(cells) == n * n


# The tilings the video draws.
QUILT: list[Square] = sorted(search(N, MIN_SQUARES) or [], key=lambda q: (-q[2], q[1], q[0]))
L2_QUILT: list[Square] = sorted(search(L2_N, L2_ANSWER) or [], key=lambda q: (-q[2], q[1], q[0]))


def main() -> None:
    assert QUILT and is_tiling(N, QUILT) and len(QUILT) == MIN_SQUARES
    assert tuple(sorted((s for _, _, s in QUILT), reverse=True)) == SIZES, [s for _, _, s in QUILT]
    assert sum(s * s for s in SIZES) == N * N == 169
    assert search(N, MIN_SQUARES - 1) is None              # nothing smaller exists
    assert minimum(N) == MIN_SQUARES
    assert SIZES[0] + SIZES[1] == N                        # 7 + 6 fills one side
    assert L2_QUILT and is_tiling(L2_N, L2_QUILT) and len(L2_QUILT) == L2_ANSWER
    assert search(L2_N, L2_ANSWER - 1) is None
    assert minimum(L2_N) == L2_ANSWER
    print(f"OK  {N}x{N}: {MIN_SQUARES} squares {SIZES}; {L2_N}x{L2_N}: {L2_ANSWER}")
    print("quilt", QUILT)
    print("level2", L2_QUILT)


if __name__ == "__main__":
    main()
