"""Verify Short 0019: The Square of Veneer (Dudeney, Amusements in Mathematics, no. 159).

Checks, in code, every claim the video makes:
  * a 5 in. square board, marked in 25 square inches, has a nail at each of the 16 inner crossings
  * 13 x 13 small cells (each 5/13 in.): 13^2 = 12^2 + 5^2 (169 = 144 + 25)
  * the cut is made along the lines of that 13 x 13 grid; it gives 4 pieces: A (5 x 5 square, cut
    out whole), B, C and D
  * A is the 5 x 5 square; B, C and D slide (no turns, except D which is turned a quarter) into a
    12 x 12 square: exposed as MOVES; the two squares have no gap and no overlap
  * the sides are 5 x 5/13 = 25/13 in. and 12 x 5/13 = 60/13 in., and (25/13)^2 + (60/13)^2 = 25
  * none of the 16 nails touches any cut (every cut sits at a multiple of 5/13 in., never a whole inch)
  * a second construction that works: 17 x 17 grid, 289 = 225 + 64, six pieces, squares 40/17 and 75/17,
    no nail touched (check_second_construction)
  * Level 2: the same cut on a 26 cm square gives squares of 10 cm and 24 cm (26^2 = 10^2 + 24^2)

The scene imports everything below. Cells are (col, row), row 0 at the top, in 13 x 13 units.
"""
from __future__ import annotations

from fractions import Fraction

N = 13                       # 13 x 13 small cells
SIDE_IN = 5                  # the board is 5 in. square
CELL = Fraction(SIDE_IN, N)  # one small cell is 5/13 in.
BIG, SMALL = 12, 5           # the two squares, in cells
NAILS = [(i, j) for i in range(1, SIDE_IN) for j in range(1, SIDE_IN)]   # in inches, 16 of them


def block(c0, c1, r0, r1) -> set:
    """Cells with c0 <= col < c1 and r0 <= row < r1."""
    return {(c, r) for c in range(c0, c1) for r in range(r0, r1)}


# The four pieces (Dudeney's cut)
A = block(8, 13, 8, 13)                                  # the 5 x 5 square, cut out whole
C = block(12, 13, 0, 4) | block(10, 13, 4, 8)            # a two-step staircase, 16 cells
D = block(0, 8, 12, 13)                                  # a thin strip 8 x 1
B = block(0, 13, 0, 13) - A - C - D                      # the rest, a three-step staircase, 120 cells
PIECES = {"A": A, "B": B, "C": C, "D": D}

# How the pieces move to make the two squares. (dx, dy) in cells; D is turned a quarter first.
MOVES = {"A": ("slide", (0, 0)),          # the small square stays put
         "B": ("slide", (0, 0)),
         "C": ("slide", (-2, 4)),
         "D": ("turn and slide", None)}
# D after the quarter turn: a vertical strip, column 11, rows 4..11
D_MOVED = block(11, 12, 4, 12)
C_MOVED = {(c - 2, r + 4) for c, r in C}
BIG_SQUARE = block(0, BIG, 0, BIG)

# Level 2: the same cut on a 26 cm square (each small cell is 2 cm)
L2_SIDE, L2_BIG, L2_SMALL = 26, 24, 10


# Second construction that WORKS: a 17 x 17 grid (cells 5/17 in.), 289 = 225 + 64 = 15^2 + 8^2.
# Six pieces (not four): A is the 8 x 8 square cut out whole at the bottom-right; the rest of the
# board is B (stays put) plus four strips that are re-stacked into the 15 x 15 square.
N2 = 17
BIG2, SMALL2 = 15, 8
CELL2 = Fraction(SIDE_IN, N2)
A2 = block(9, 17, 9, 17)
P1, P2 = block(15, 17, 0, 6), block(15, 17, 6, 9)      # right strip, 2 x 6 and 2 x 3
Q1, Q2 = block(0, 6, 15, 17), block(6, 9, 15, 17)      # bottom strip, 6 x 2 and 3 x 2
B2 = block(0, N2, 0, N2) - A2 - P1 - P2 - Q1 - Q2
PIECES2 = {"A": A2, "B": B2, "P1": P1, "P2": P2, "Q1": Q1, "Q2": Q2}
# where the strips go inside the hole left by A in the 15 x 15 square (cols 9-14, rows 9-14)
P1_MOVED = block(9, 11, 9, 15)                          # slides down and left
Q1_MOVED = block(11, 13, 9, 15)                         # turned a quarter
P2_MOVED = block(13, 15, 9, 12)
Q2_MOVED = block(13, 15, 12, 15)                        # turned a quarter


def check_second_construction() -> None:
    assert N2 * N2 == BIG2 ** 2 + SMALL2 ** 2 == 289
    whole = block(0, N2, 0, N2)
    assert set().union(*PIECES2.values()) == whole
    assert sum(len(p) for p in PIECES2.values()) == N2 * N2           # no overlap
    # every piece is one connected piece
    for k, p in PIECES2.items():
        left = set(p)
        stack = [left.pop()]
        while stack:
            c, r = stack.pop()
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in left:
                    left.discard(n)
                    stack.append(n)
        assert not left, k
    # turned strips have the right shape (2 x 6 and 2 x 3 after a quarter turn of 6 x 2 and 3 x 2)
    assert (len(Q1), len(Q2)) == (len(Q1_MOVED), len(Q2_MOVED)) == (12, 6)
    assert max(c for c, r in Q1) - min(c for c, r in Q1) == max(r for c, r in Q1_MOVED) - min(r for c, r in Q1_MOVED) == 5
    assert max(c for c, r in Q2) - min(c for c, r in Q2) == max(r for c, r in Q2_MOVED) - min(r for c, r in Q2_MOVED) == 2
    # the moved pieces + B tile the 15 x 15 square exactly
    moved = [B2, P1_MOVED, Q1_MOVED, P2_MOVED, Q2_MOVED]
    assert sum(len(p) for p in moved) == BIG2 ** 2
    assert set().union(*moved) == block(0, BIG2, 0, BIG2)
    # sides
    s, b = SMALL2 * CELL2, BIG2 * CELL2
    assert (s, b) == (Fraction(40, 17), Fraction(75, 17)) and s ** 2 + b ** 2 == SIDE_IN ** 2
    # no nail touches any cut (cut edges are between pieces, or piece and outside)
    owner = {cell: k for k, p in PIECES2.items() for cell in p}
    for (c, r), k in owner.items():
        for dc, dr, a, e in ((1, 0, (c + 1, r), (c + 1, r + 1)), (0, 1, (c, r + 1), (c + 1, r + 1))):
            o = owner.get((c + dc, r + dr))
            if o is not None and o != k:
                (x0, y0), (x1, y1) = (a[0] * CELL2, a[1] * CELL2), (e[0] * CELL2, e[1] * CELL2)
                for nx, ny in NAILS:
                    assert not (x0 == x1 == nx and y0 <= ny <= y1 or y0 == y1 == ny and x0 <= nx <= x1)
    assert all((SIDE_IN * k) % N2 != 0 for k in range(1, N2))      # no cut is on a whole inch


def main() -> None:
    assert N * N == BIG * BIG + SMALL * SMALL == 169
    assert len(NAILS) == 16

    # the four pieces tile the 13 x 13 board
    whole = block(0, N, 0, N)
    assert set().union(*PIECES.values()) == whole
    assert sum(len(p) for p in PIECES.values()) == N * N        # no overlap
    assert [len(PIECES[k]) for k in "ABCD"] == [25, 120, 16, 8]
    assert A == block(8, 13, 8, 13) and len(A) == SMALL * SMALL

    # moved pieces tile the 12 x 12 square
    # D turned a quarter is an 8-tall strip, the same cells as D with columns and rows swapped
    assert {(c - 11, r - 4) for c, r in D_MOVED} == {(r - 12, c) for c, r in D}
    moved = [B, C_MOVED, D_MOVED]
    assert sum(len(p) for p in moved) == BIG * BIG
    assert set().union(*moved) == BIG_SQUARE

    # connectedness of every piece (so each really is one piece)
    for k, p in PIECES.items():
        left = set(p)
        stack = [left.pop()]
        while stack:
            c, r = stack.pop()
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in left:
                    left.discard(n)
                    stack.append(n)
        assert not left, k

    # real sizes
    small_in, big_in = SMALL * CELL, BIG * CELL
    assert small_in == Fraction(25, 13) and big_in == Fraction(60, 13)
    assert small_in ** 2 + big_in ** 2 == SIDE_IN ** 2 == 25

    # no nail on any cut: collect every cell edge that separates two pieces or a piece from outside
    owner = {cell: k for k, p in PIECES.items() for cell in p}
    segs = []            # ((x0, y0), (x1, y1)) in inches
    for (c, r), k in owner.items():
        for (dc, dr, a, b) in ((1, 0, (c + 1, r), (c + 1, r + 1)), (0, 1, (c, r + 1), (c + 1, r + 1))):
            other = owner.get((c + dc, r + dr))
            if other is not None and other != k:
                segs.append(((a[0] * CELL, a[1] * CELL), (b[0] * CELL, b[1] * CELL)))
    assert segs
    for (x0, y0), (x1, y1) in segs:
        for nx, ny in NAILS:
            on = x0 == x1 == nx and y0 <= ny <= y1 or y0 == y1 == ny and x0 <= nx <= x1
            assert not on, ((x0, y0), (x1, y1), (nx, ny))
    # why: a cut at x = 5k/13 is a whole number only when 13 divides k
    assert all((SIDE_IN * k) % N != 0 for k in range(1, N))

    # Not unique: area alone allows many pairs of sides (Dudeney: "an infinite number of ways").
    # We only claim 25/13 and 60/13 is one valid answer; the second construction gives 40/17, 75/17.
    assert (Fraction(40, 17), Fraction(75, 17)) != (small_in, big_in)
    check_second_construction()

    # Level 2
    assert L2_BIG ** 2 + L2_SMALL ** 2 == L2_SIDE ** 2
    # ...and it is the only way to write 26^2 as two squares of whole centimetres
    assert [(a, b) for a in range(1, L2_SIDE) for b in range(a, L2_SIDE) if a * a + b * b == L2_SIDE ** 2] \
        == [(L2_SMALL, L2_BIG)]
    assert L2_SIDE % N == 0 and L2_BIG == BIG * (L2_SIDE // N) and L2_SMALL == SMALL * (L2_SIDE // N)

    print("OK  13x13 cells; 4 pieces", {k: len(p) for k, p in PIECES.items()},
          f"-> squares {small_in} and {big_in} in.; {len(segs)} cut segments, no nail touched;",
          f"level2 {L2_SIDE} -> {L2_SMALL} and {L2_BIG}")


if __name__ == "__main__":
    main()
