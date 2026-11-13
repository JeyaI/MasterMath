"""Check every claim the video makes, in code. `ms approve` refuses until this passes.

Model: n pennies in a circle at positions 1..n, one each. A move lifts a single penny,
passes over exactly two pennies (two singles, or one pair; either direction; empty
places are skipped) and lands on the next place, which must hold a single penny. Every move therefore turns two
single pennies into one pair, whatever happens elsewhere.
"""
from functools import lru_cache

N = 12
# Dudeney's six moves (from -> to), as the video plays them.
SOLUTION = [(12, 3), (7, 4), (10, 6), (8, 1), (9, 5), (11, 2)]
TARGETS = {1, 2, 3, 4, 5, 6}

# Level 2: the same game on a bigger circle.
N2 = 20
LEVEL2_ANSWER = N2 // 2


def landing_spots(counts: tuple[int, ...], p: int) -> list[int]:
    """Positions (0-based) a lone penny at p can land on, going either way round."""
    n = len(counts)
    out = []
    for step in (1, -1):
        seen = 0  # pennies passed over; a pair counts as two
        q = p
        for _ in range(n - 1):
            q = (q + step) % n
            if counts[q] == 0:
                continue  # empty places are not jumped over
            if seen == 2:
                if counts[q] == 1:
                    out.append(q)
                break
            seen += counts[q]
            if seen > 2:
                break
    return out


def moves(counts: tuple[int, ...]):
    for p, c in enumerate(counts):
        if c != 1:
            continue
        lifted = counts[:p] + (0,) + counts[p + 1:]
        for q in landing_spots(lifted, p):
            new = list(lifted)
            new[q] += 1
            yield p, q, tuple(new)


def play(n: int, seq: list[tuple[int, int]]) -> tuple[int, ...]:
    counts = (1,) * n
    for a, b in seq:
        for p, q, new in moves(counts):
            if (p + 1, q + 1) == (a, b):
                counts = new
                break
        else:
            raise AssertionError(f"illegal move {a} to {b}")
    return counts


def solve(n: int):
    """Depth-first search for any all-pairs finish; returns the move list."""
    start = (1,) * n

    @lru_cache(maxsize=None)
    def go(counts):
        if all(c in (0, 2) for c in counts):
            return ()
        for p, q, new in moves(counts):
            rest = go(new)
            if rest is not None:
                return ((p + 1, q + 1),) + rest
        return None

    return go(start)


def main() -> None:
    # 1. Dudeney's six moves are legal and end with pairs exactly on 1..6.
    final = play(N, SOLUTION)
    assert len(SOLUTION) == 6
    assert {i + 1 for i, c in enumerate(final) if c == 2} == TARGETS, final
    assert all(c in (0, 2) for c in final)

    # 2. Six is the fewest: each move lowers the number of occupied places by exactly one,
    #    and 12 places must become 6.
    for _, _, new in moves((1,) * N):
        assert sum(1 for c in new if c) == N - 1
    assert N // 2 == 6

    # 3. Each coin of the second half lands three places away in the shrinking circle:
    #    the landing spot is the third occupied place along.
    assert {a for a, _ in SOLUTION} == {7, 8, 9, 10, 11, 12}

    # 4. Level 2: 20 pennies, same rule. Ten pairs are reachable, and ten moves is the
    #    least, by the same count (20 occupied places down to 10, one per move).
    sol = solve(N2)
    assert sol is not None and len(sol) == LEVEL2_ANSWER, sol
    end = play(N2, list(sol))
    assert all(c in (0, 2) for c in end) and sum(1 for c in end if c) == N2 // 2

    print("ok: 12 pennies in 6 moves; 20 pennies in", len(sol))


if __name__ == "__main__":
    main()
