"""Verify Short 0003: Inspecting a Mine (Dudeney, Amusements in Mathematics, no. 247).

Checks, in code, every claim the video makes:
  * the mine is a 5 x 4 grid of junctions A-T with 31 passages
  * exactly 10 junctions have 3 passages, and all the others have 2 or 4
  * the two naive tries shown before the countdown walk every passage, in 43 and 41 miles
  * the trap walk shown on screen really uses all 3 passages at C and leaves no way out
  * one repeated passage changes the parity of exactly 2 junctions, so 10 stuck spots need 5 repeats
  * 5 repeats is the true minimum from A, finishing anywhere: no set of 4 or fewer repeats works
  * Dudeney's route is legal, walks every passage, and repeats exactly the 5 passages shown: 36 miles
  * Level 2: finishing back at A needs 7 repeats, no fewer, so 38 miles, and such a route exists

A set of repeated passages works when the mine plus those copies has an Euler trail with the right
ends, which depends only on junction parity plus connectedness. The mine is connected, so we search
the sets directly rather than trust a matching argument.

The scene imports the junctions, passages, route and numbers below.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations

COLS, ROWS = 5, 4
LETTERS = "ABCDEFGHIJKLMNOPQRST"
START, FINISH = "A", "Q"

# Dudeney's route, from the book's solution.
ROUTE = list("ABGHCDIHMNIJONSRMLGFKLQRSTOJEDCBAFKPQ")
REPEATS = ["AB", "CD", "FK", "JO", "RS"]     # the order the scene shows them
TRAP_WALK = list("BCHIDC")                   # in, out, around, in: C has no passage left
MILES, L2_MILES = 36, 38
NAIVE_TRIES = [list("ABGFKPQRSNOTSNIJEDCHIDCBAFGLQLMNMHGLKLMRMNOJ"),   # clumsy but complete: 43 miles
               list("AFKLMRSTONMHIDEJINSRQLGHCDCBGFABAFKPQLMNOJ")]     # a little better: 41 miles


def pos(letter: str) -> tuple[int, int]:
    """Column and row of a junction, with A at (0, 0) and rows counted downward."""
    i = LETTERS.index(letter)
    return i % COLS, i // COLS


def edge(a: str, b: str) -> str:
    return "".join(sorted((a, b)))


def passages() -> list[str]:
    out = []
    for i, a in enumerate(LETTERS):
        c, r = pos(a)
        if c < COLS - 1:
            out.append(edge(a, LETTERS[i + 1]))
        if r < ROWS - 1:
            out.append(edge(a, LETTERS[i + COLS]))
    return out


EDGES = passages()


def degree(letter: str) -> int:
    return sum(letter in e for e in EDGES)


ODD = [v for v in LETTERS if degree(v) % 2]   # the junctions with 3 passages


def mask(*letters: str) -> int:
    m = 0
    for v in letters:
        m ^= 1 << LETTERS.index(v)
    return m


def fewest_repeats(start: str, finish: str | None, limit: int) -> tuple[int, list[tuple[str, ...]]]:
    """Fewest repeated passages for a walk from `start` that covers everything.

    finish=None means any finish. Returns the count and every set of that size. A passage repeated
    twice has the same parity as not repeating it, so distinct passages are enough."""
    want = {mask(*ODD) ^ mask(start, finish)} if finish else {
        mask(*ODD) ^ mask(start, f) for f in LETTERS}
    flips = {e: mask(*e) for e in EDGES}
    for n in range(limit + 1):
        hits = []
        for combo in combinations(EDGES, n):
            m = 0
            for e in combo:
                m ^= flips[e]
            if m in want:
                hits.append(combo)
        if hits:
            return n, hits
    raise AssertionError(f"nothing within {limit} repeats")


def euler_route(extra: tuple[str, ...], start: str) -> list[str]:
    """Hierholzer's walk over the mine plus `extra` copies, from `start`."""
    left = Counter(EDGES) + Counter(extra)
    stack, out = [start], []
    while stack:
        v = stack[-1]
        e = next((k for k, n in left.items() if n and v in k), None)
        if e is None:
            out.append(stack.pop())
        else:
            left[e] -= 1
            stack.append(e[0] if e[1] == v else e[1])
    return out[::-1]


def check_walk(route: list[str], start: str, finish: str, length: int, repeats: set[str]) -> None:
    assert route[0] == start and route[-1] == finish, (route[0], route[-1])
    steps = [edge(a, b) for a, b in zip(route, route[1:])]
    assert len(steps) == length, len(steps)
    assert set(steps) <= set(EDGES), "stepped along something that is not a passage"
    assert set(steps) == set(EDGES), "missed a passage"
    assert {e for e, n in Counter(steps).items() if n > 1} == repeats


def main() -> None:
    assert len(EDGES) == len(set(EDGES)) == 31
    assert all(e in EDGES for e in ("AB", "BC", "CH", "HI")), "the passages the book names"
    assert sorted(degree(v) for v in LETTERS) == [2] * 4 + [3] * 10 + [4] * 6
    assert ODD == list("BCDFJKOQRS"), ODD
    assert degree(START) == 2 and degree(FINISH) == 3

    # The naive tries on screen: legal, complete, and neither gives away an answer.
    for attempt, miles in zip(NAIVE_TRIES, (43, 41)):
        steps = [edge(a, b) for a, b in zip(attempt, attempt[1:])]
        assert attempt[0] == START and attempt[-1] != START
        assert len(steps) == miles and set(steps) == set(EDGES)
        assert miles not in (MILES, L2_MILES)

    # The trap on screen: every step is a passage, no repeats, and all 3 at C are used up.
    trap = [edge(a, b) for a, b in zip(TRAP_WALK, TRAP_WALK[1:])]
    assert len(set(trap)) == len(trap) and set(trap) <= set(EDGES)
    assert TRAP_WALK[-1] == "C" and {e for e in EDGES if "C" in e} <= set(trap)

    # 10 stuck spots on screen: the 10 three-way junctions, plus A, minus the finish.
    stuck = (set(ODD) | {START}) - {FINISH}
    assert len(ODD) == 10 and len(stuck) == 10
    assert sorted("".join(REPEATS)) == sorted(stuck), "each repeat clears exactly 2 stuck spots"
    assert all(e in EDGES for e in REPEATS)

    n, sets = fewest_repeats(START, None, 5)
    assert n == 5 and tuple(sorted(REPEATS)) in {tuple(sorted(s)) for s in sets}
    assert 31 + n == MILES

    assert ROUTE[0] == START and ROUTE[-1] == FINISH
    check_walk(ROUTE, START, FINISH, MILES, set(REPEATS))

    # Level 2: back at A.
    closed, closed_sets = fewest_repeats(START, START, 7)
    assert closed == 7 and 31 + closed == L2_MILES
    check_walk(euler_route(closed_sets[0], START), START, START, L2_MILES, set(closed_sets[0]))

    print(f"OK  31 passages, 10 three-way junctions, {n} repeats minimum, route is {MILES} miles; "
          f"level2 {closed} repeats, {L2_MILES} miles")


if __name__ == "__main__":
    main()
