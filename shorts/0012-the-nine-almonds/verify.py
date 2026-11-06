"""Verify Short 0012: The Nine Almonds (Dudeney, Amusements in Mathematics, no. 229).

Board: 5x5 squares, coordinates (x, y) with 0..4, the centre is (2, 2). Nine almonds fill the middle 3x3.
Rule: an almond jumps over a neighbouring almond (any of 8 directions, as Dudeney's own solution uses a
diagonal) onto the empty square beyond and removes the almond jumped. One MOVE is any number of jumps in
a row by the same almond.

Checks, in code:
  * the book solution (5 over 8, 9, 3, 1; 7 over 4; 6 over 2 and 7; 5 over 6) is legal, takes 4 moves
    and 8 jumps, and leaves one almond on the centre square
  * breadth-first search over every position: 4 moves is the fewest that leaves only the centre almond
    (3 moves is impossible)
  * Level 2: if each move may be only ONE jump, 8 moves are needed, since every jump removes exactly one
    almond and 8 must go (search agrees). The answer is 8.

The scene imports START, SOLUTION (the 4 moves as lists of squares) and the counts below.
"""
from __future__ import annotations

from collections import deque

SIZE = 5
CENTRE = (2, 2)
DIRS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
# numbering as in the book's figure: 1 2 3 across the top, 4 5 6, 7 8 9 (y grows upward)
NUMBERED = {1: (1, 3), 2: (2, 3), 3: (3, 3), 4: (1, 2), 5: (2, 2), 6: (3, 2), 7: (1, 1), 8: (2, 1), 9: (3, 1)}
START = frozenset(NUMBERED.values())

# Each move: (almond number, [squares it lands on, in order])
BOOK = [(5, [8, 9, 3, 1]), (7, [4]), (6, [2, 7]), (5, [6])]   # numbers jumped over


def on_board(p) -> bool:
    return 0 <= p[0] < SIZE and 0 <= p[1] < SIZE


def jumps_from(pos, board):
    """Single jumps for the almond at pos: [(jumped square, landing square)]."""
    out = []
    for dx, dy in DIRS:
        mid = (pos[0] + dx, pos[1] + dy)
        land = (pos[0] + 2 * dx, pos[1] + 2 * dy)
        if mid in board and on_board(land) and land not in board:
            out.append((mid, land))
    return out


def play_book():
    """Play the book solution, asserting every jump is legal.

    Returns (moves, final board). Each move is a dict: almond number, start square, the squares jumped
    over (`jumped`) and the squares landed on (`path`), in order."""
    board = set(START)
    pos_of = dict(NUMBERED)            # almond number -> current square
    moves = []
    for n, over in BOOK:
        cur = pos_of[n]
        mv = {"almond": n, "start": cur, "jumped": [], "path": []}
        for victim in over:
            vsq = pos_of.pop(victim)
            land = [l for m, l in jumps_from(cur, board) if m == vsq]
            assert len(land) == 1, f"almond {n} cannot jump {victim}"
            board -= {cur, vsq}
            board.add(land[0])
            mv["jumped"].append(vsq)
            mv["path"].append(land[0])
            cur = land[0]
        pos_of[n] = cur
        moves.append(mv)
    return moves, board


MOVES, FINAL = play_book()
N_MOVES = len(MOVES)
N_JUMPS = sum(len(m["path"]) for m in MOVES)


def chains(board):
    """All positions reachable by one full move (one or more jumps by one almond)."""
    results = set()

    def go(cur, b):
        for mid, land in jumps_from(cur, b):
            nb = frozenset((b - {cur, mid}) | {land})
            results.add(nb)
            go(land, nb)

    for p in board:
        go(p, board)
    return results


def single_jumps(board):
    out = set()
    for p in board:
        for mid, land in jumps_from(p, board):
            out.add(frozenset((board - {p, mid}) | {land}))
    return out


def shortest(step, goal=frozenset({CENTRE})):
    seen = {START: 0}
    q = deque([START])
    while q:
        b = q.popleft()
        if b == goal:
            return seen[b]
        for nb in step(b):
            if nb not in seen:
                seen[nb] = seen[b] + 1
                q.append(nb)
    raise AssertionError("goal unreachable")


def main() -> None:
    assert len(START) == 9 and CENTRE in START
    assert FINAL == {CENTRE}, FINAL
    assert N_MOVES == 4 and N_JUMPS == 8
    assert shortest(chains) == 4                  # 3 moves is impossible
    L2_ANSWER = shortest(single_jumps)
    assert L2_ANSWER == 8
    print(f"OK  book solution: {N_MOVES} moves, {N_JUMPS} jumps, ends on the centre; "
          f"BFS: fewest moves with chains = 4, with single jumps only = {L2_ANSWER}")


if __name__ == "__main__":
    main()
