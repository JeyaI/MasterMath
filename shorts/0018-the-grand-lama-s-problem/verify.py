"""Verify Short 0018: The Grand Lama's Problem (Dudeney, Amusements in Mathematics, no. 291).

Checks, in code, every claim the video makes:
  * the board is 8 x 8 with four gems on the long diagonal, squares (0,0), (1,1), (2,2), (3,3)
    (row, column; row 0 at the top)
  * the cut transcribed from Dudeney's diagram (shaded squares = '#') splits the board into exactly four
    connected pieces of 16 squares each, with exactly one gem in each piece
  * all four pieces are the same shape: each is a rotation and/or reflection of piece 1
    (the rotation or reflection that carries piece 1 onto each of the others is exposed as MAPS)
  * the obvious cuts fail: four 4 x 4 quarters (two gems share a quarter), four 2-row strips and
    four 2-column strips (two gems share a strip)
  * the gems are stuck close together, so the pieces cannot be simple blocks: every piece is a long thin
    hook (its bounding box is at least 7 squares in one direction)
  * Level 2: a 10 x 10 board cut into 5 equal pieces gives 100 / 5 = 20 squares each

The scene imports everything below. Cells are (row, column), row 0 at the top.
"""
from __future__ import annotations

N = 8
GEMS = [(0, 0), (1, 1), (2, 2), (3, 3)]

# Dudeney's picture: '#' = shaded squares (two pieces), '.' = white squares (the other two)
SHADING = [
    "#.......",
    "#.######",
    "#.#....#",
    "#.#.##.#",
    "#.##.#.#",
    "#....#.#",
    "######.#",
    ".......#",
]

L2_SIZE = 10
L2_PIECES = 5
L2_EACH = 20
# The Level 2 construction shown in the video: 5 identical 2 x 10 strips (row 0 at the top)
_K = L2_SIZE // L2_PIECES
L2_PIECES_CELLS = [{(r, c) for r in range(_K * i, _K * i + _K) for c in range(L2_SIZE)}
                   for i in range(L2_PIECES)]


def components(cells: set) -> list[set]:
    """Connected components (edge-adjacent) of a set of cells."""
    left, out = set(cells), []
    while left:
        stack = [left.pop()]
        comp = set(stack)
        while stack:
            r, c = stack.pop()
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (r + d[0], c + d[1])
                if n in left:
                    left.discard(n)
                    comp.add(n)
                    stack.append(n)
        out.append(comp)
    return out


def _by_gem(pieces: list[set]) -> list[set]:
    return sorted(pieces, key=lambda p: min(GEMS.index(g) for g in GEMS if g in p))


_shaded = {(r, c) for r in range(N) for c in range(N) if SHADING[r][c] == "#"}
_white = {(r, c) for r in range(N) for c in range(N) if SHADING[r][c] == "."}
PIECES = _by_gem(components(_shaded) + components(_white))     # piece i holds gem i

# the eight symmetries of the square grid, as (name, function on (r, c) in a k x k box)
TRANSFORMS = {
    "same": lambda r, c: (r, c),
    "turn 90": lambda r, c: (c, -r),
    "turn 180": lambda r, c: (-r, -c),
    "turn 270": lambda r, c: (-c, r),
    "flip left-right": lambda r, c: (r, -c),
    "flip top-bottom": lambda r, c: (-r, c),
    "flip diagonal": lambda r, c: (c, r),
    "flip anti-diagonal": lambda r, c: (-c, -r),
}


def normal(cells) -> frozenset:
    r0 = min(r for r, _ in cells)
    c0 = min(c for _, c in cells)
    return frozenset((r - r0, c - c0) for r, c in cells)


def match(a: set, b: set):
    """Name of a symmetry that carries shape a onto shape b (after sliding), or None."""
    target = normal(b)
    for name, f in TRANSFORMS.items():
        if normal([f(r, c) for r, c in a]) == target:
            return name
    return None


# How piece 1 is moved (turn or flip, then slide) to land on each other piece
MAPS = [match(PIECES[0], p) for p in PIECES]


def partition_ok(pieces: list[set], size: int = 16) -> bool:
    """True if the pieces tile the board, each has `size` squares, and each holds exactly one gem."""
    if len(pieces) != 4 or any(len(p) != size for p in pieces):
        return False
    if set().union(*pieces) != {(r, c) for r in range(N) for c in range(N)}:
        return False
    return all(sum(g in p for g in GEMS) == 1 for p in pieces)


def main() -> None:
    assert len(SHADING) == N and all(len(row) == N for row in SHADING)
    assert len(_shaded) == len(_white) == 32
    assert len(set(GEMS)) == 4 and all(0 <= r < N and 0 <= c < N for r, c in GEMS)

    assert len(components(_shaded)) == 2 and len(components(_white)) == 2   # two shaded + two white pieces
    assert partition_ok(PIECES)
    for i, p in enumerate(PIECES):
        assert len(components(p)) == 1, i
        assert GEMS[i] in p, i
    assert all(m is not None for m in MAPS), MAPS      # all four are the same shape

    # the obvious cuts do not work
    quarters = [{(r, c) for r in range(N) for c in range(N) if (r // 4, c // 4) == (i, j)}
                for i in range(2) for j in range(2)]
    rows = [{(r, c) for r in range(2 * i, 2 * i + 2) for c in range(N)} for i in range(4)]
    cols = [{(r, c) for c in range(2 * i, 2 * i + 2) for r in range(N)} for i in range(4)]
    for name, cut in (("quarters", quarters), ("row strips", rows), ("column strips", cols)):
        assert all(len(p) == 16 for p in cut), name
        assert not partition_ok(cut), name
        assert max(sum(g in p for g in GEMS) for p in cut) >= 2, name

    # every piece is a long thin hook
    for p in PIECES:
        h = max(r for r, _ in p) - min(r for r, _ in p) + 1
        w = max(c for _, c in p) - min(c for _, c in p) + 1
        assert max(h, w) >= 7, (h, w)

    # Level 2
    assert L2_SIZE * L2_SIZE // L2_PIECES == L2_EACH and L2_SIZE * L2_SIZE % L2_PIECES == 0
    # ...and such a cut really exists: a witness of 5 identical pieces tiling the 10 x 10 board
    witness = L2_PIECES_CELLS
    assert set().union(*witness) == {(r, c) for r in range(L2_SIZE) for c in range(L2_SIZE)}
    assert all(len(p) == L2_EACH for p in witness)
    assert all(normal(p) == normal(witness[0]) for p in witness)

    print("OK  4 pieces of 16 squares, one gem each, all the same shape; maps from piece 1:", MAPS,
          f"; level2 {L2_SIZE}x{L2_SIZE} in {L2_PIECES} -> {L2_EACH} each")


if __name__ == "__main__":
    main()
