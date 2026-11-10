"""Verify Short 0017: The Twickenham Puzzle (Dudeney, Amusements in Mathematics, no. 217).

Checks, in code, every claim the video makes:
  * the start position (11 discs, 5 white counters, 5 black counters, bottom disc empty) and the rules:
    black moves clockwise, white anticlockwise, one step into the empty disc, or a jump over one counter
    of the OTHER colour into the empty disc
  * Dudeney's 26 moves replay legally from the start and end on TWICKENHAM read clockwise from the disc
    after the empty one, with the empty disc back at the bottom; each letter names exactly one legal move
  * breadth-first search over every position: 26 is the fewest moves, so "26" is optimal
  * the other readings of the word (the word starting at another disc, so that it would run across the
    empty disc) are not what the puzzle asks, and none is reached in 26 or fewer except the one asked for
    (rotation 1 is the word split by the gap; noted, not shown)
  * the solution splits into waves of one colour moving in a row: 1, 2, 3, 4, 5, 5, 1, 4, 1 (sums to 26)
  * Level 2: 4 white + 4 black counters on a ring of 9 discs, the two colours swap sides, empty disc stays:
    fewest moves = 24 (BFS), waves 1,2,3,4,4,4,3,2,1; the pattern k(k+2) holds for k = 1..5 (BFS)

Discs are numbered 0..n-1 clockwise, disc 0 is the bottom one. The scene imports everything below.
"""
from __future__ import annotations

from collections import deque

WORD = "TWICKENHAM"
START = (None, "C", "E", "H", "M", "I", "N", "A", "T", "W", "K")   # clockwise from the bottom disc
WHITE = frozenset("IMHEC")      # white counters, black letters: travel anticlockwise
BLACK = frozenset("NATWK")      # black counters, white letters: travel clockwise
GOAL = (None,) + tuple(WORD)
DUDENEY = "K C E K W T C E H M K W T A N C E H M I K C E H M T".split()
MOVES = 26
WAVES = [1, 2, 3, 4, 5, 5, 1, 4, 1]

L2_K = 4                        # counters per colour on the Level 2 ring (2k + 1 = 9 discs)
L2_START = (None,) + ("w",) * L2_K + ("B",) * L2_K
L2_GOAL = (None,) + ("B",) * L2_K + ("w",) * L2_K
L2_MOVES = 24
L2_WAVES = [1, 2, 3, 4, 4, 4, 3, 2, 1]


def colour(ch: str) -> str:
    return "W" if ch in WHITE else "B"


def l2_colour(ch: str) -> str:
    return "W" if ch.islower() else "B"


def moves(state: tuple, colour_of=colour):
    """Every legal move as (new_state, label, kind, src, dst). Black goes clockwise (+1), white anticlockwise (-1)."""
    n = len(state)
    hole = state.index(None)
    out = []
    for step in (1, 2):
        for direction in (1, -1):
            src = (hole - direction * step) % n
            ch = state[src]
            if ch is None or (colour_of(ch) == "B") != (direction == 1):
                continue
            if step == 2:
                mid = state[(hole - direction) % n]
                if mid is None or colour_of(mid) == colour_of(ch):
                    continue            # a jump needs a counter of the other colour to jump over
            new = list(state)
            new[hole], new[src] = ch, None
            out.append((tuple(new), ch, "step" if step == 1 else "jump", src, hole))
    return out


def solve(start: tuple, goal: tuple, colour_of=colour):
    """Shortest list of labels from start to goal (breadth-first), or None."""
    prev = {start: None}
    q = deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            path = []
            while prev[s]:
                s, ch = prev[s]
                path.append(ch)
            return path[::-1]
        for t, ch, *_ in moves(s, colour_of):
            if t not in prev:
                prev[t] = (s, ch)
                q.append(t)
    return None


def replay(start: tuple, labels: list[str], colour_of=colour):
    """Play labelled moves; each must name exactly one legal move. Returns [(state, label, kind, src, dst), ...]."""
    state, trace = start, []
    for ch in labels:
        options = [m for m in moves(state, colour_of) if m[1] == ch]
        assert len(options) == 1, (ch, state)
        state = options[0][0]
        trace.append(options[0])
    return trace


def waves(labels: list[str], colour_of=colour) -> list[int]:
    out: list[int] = []
    last = None
    for ch in labels:
        c = colour_of(ch)
        if c == last:
            out[-1] += 1
        else:
            out.append(1)
        last = c
    return out


# What the scene plays: Dudeney's moves with their kind and discs.
PLAY = replay(START, DUDENEY)


def main() -> None:
    assert len(START) == 11 and START[0] is None
    assert len(WHITE | BLACK) == 10 and not (WHITE & BLACK)
    assert sum(c in WHITE for c in START if c) == 5 and sum(c in BLACK for c in START if c) == 5
    assert len(set(WORD)) == 10 and sorted(WORD) == sorted(c for c in START if c)
    # the example in the puzzle text: K first, then C jumps over K, then K moves on, then W jumps over C
    first = replay(START, ["K", "C"])
    assert first[0][2] == "step" and first[1][2] == "jump" and first[1][0][10] == "C"

    assert len(DUDENEY) == MOVES and PLAY[-1][0] == GOAL
    assert PLAY[-1][0][0] is None                     # the empty disc is back at the bottom
    assert "".join(PLAY[-1][0][1:]) == WORD
    assert sum(m[2] == "jump" for m in PLAY) + sum(m[2] == "step" for m in PLAY) == MOVES

    best = solve(START, GOAL)
    assert best is not None and len(best) == MOVES, len(best or [])
    assert waves(DUDENEY) == WAVES and sum(WAVES) == MOVES

    # other starting points for the word are not the question, and none is shorter than 26 except the gap-split one
    for r in range(2, 10):
        p = solve(START, (None,) + tuple(WORD[r:] + WORD[:r]))
        assert p is None or len(p) > MOVES, r

    # Level 2
    p2 = solve(L2_START, L2_GOAL, l2_colour)
    assert p2 is not None and len(p2) == L2_MOVES == L2_K * (L2_K + 2)
    assert waves(p2, l2_colour) == L2_WAVES and sum(L2_WAVES) == L2_MOVES
    for k in range(1, 6):
        s = (None,) + ("w",) * k + ("B",) * k
        g = (None,) + ("B",) * k + ("w",) * k
        assert len(solve(s, g, l2_colour)) == k * (k + 2), k

    print(f"OK  Twickenham in {MOVES} moves (fewest possible), waves {WAVES}; "
          f"level2 ring of {2 * L2_K + 1}: {L2_MOVES} moves, waves {L2_WAVES}")


if __name__ == "__main__":
    main()
