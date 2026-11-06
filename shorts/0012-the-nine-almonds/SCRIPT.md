# 0012 The Nine Almonds

## Puzzle
`dudeney-amusements-229`, The Nine Almonds (Dudeney, *Amusements in Mathematics*, public domain). Chosen because the rules fit one sentence, the answer (4 moves) is checked by exhaustive search in `verify.py`, and the visual hook is a single almond sweeping the board. Runner-up: `dudeney-amusements-235` Torpedo Practice (the fleet layout is only in the book's figure and the "different direction" wording is ambiguous).

## Hook
First 3 seconds: the 5 by 5 board pops in with nine almonds in the middle 3 by 3. Text: "Remove 8 almonds in 4 moves?"

## Retelling
Nine almonds fill the middle of a 5 by 5 board. An almond can jump over a neighbour, in any direction including diagonals, into the empty square beyond, and the one jumped is taken off. Several jumps in a row by the same almond count as one move. Leave only the centre almond, in 4 moves.

## Insight
**Chain jumps: count jumps, not moves.** Eight almonds must go and each jump removes exactly one, so 8 jumps are needed. With 4 moves, the jumps must come in chains averaging two per move. The solution gives one almond the long chain (four jumps) and spends the other almonds on short ones.

Animation: the board with a small "jumps 0 / moves 0" counter pair. Move 1: the centre almond leaps out in an arc, over its neighbours, one jump after another; each jumped almond fades, the path is drawn as a glowing trail and the counters tick. Moves 2 and 3 show the shorter chains with fresh trail colours; move 4 brings the centre almond home along the last jump. The trail map at the end (four coloured paths) is the payoff. Counters finish at 4 moves, 8 jumps.

Checked against recent Shorts: read `SCRIPT.md` of 0008 (frogs: moves in a row with a move counter), 0009 (pinwheel), 0010 (two fingers wiping lines) and 0011 (matchstick pens), plus the 0003 docstring. 0008 is the nearest relative (a sequence of moves with a counter) but its idea is slides versus leaps along a line; here the idea is chained jumps leaving a trail across a 2D board while pieces are removed, with a jumps counter set against a moves counter.

## Beats
1. Hook: board pops in, nine almonds, "Remove 8 almonds in 4 moves?" (3 s)
2. "Jump over one, take it off": one demo jump, the jumped almond fades; a second jump in a row is "still one move" (6 s)
3. "Leave just the centre" (2 s)
4. "Pause and try it": 5 s countdown (5 s)
5. "Move 1: one almond, four jumps": centre almond sweeps 8, 9, 3, 1 (6 s)
6. "Move 2: 7 over 4" (2 s)
7. "Move 3: 6 over 2 and 7" (3 s)
8. "Move 4: 5 over 6": the centre almond is alone (2 s)
9. "4 moves. Fewest possible ✓": trail map, 8 jumps (3 s)
10. Level 2 card: no chains, how few moves? (3 s)
11. "Comment just the number ↓" held (12 s)

Total: 3 + 6 + 2 + 5 + 6 + 2 + 3 + 2 + 3 + 3 + 12 = 47 s.

## Level 2
Same board, but each move may be only ONE jump (no chains). Fewest moves to leave one almond? Answer: **8**. Every jump removes exactly one almond and eight must go, so at least 8 jumps, and search confirms 8 single-jump moves can do it (exact: `verify.py`).

## Music
`gymnopedie-1` (Erik Satie, Gymnopédie No. 1): least recently used, last on 0006. Slow and sparse suits the quiet board.

## Risks
- Diagonals: the book's wording ("any direction, and not diagonally only") and its own solution (6 over 2) use diagonal jumps. The Short must say "diagonals too" on screen.
- Numbering: the book figure numbers the almonds 1 2 3 / 4 5 6 / 7 8 9 (inferred; the book solution checks out in code under this numbering). Captions use these numbers; the scene must draw them on the almonds.
- The figure is a plain 5 by 5 grid with a 3 by 3 block of almonds, so it is easy to recreate. The board edge matters: the jump landings reach the outer ring.
- The book's chain move "5 over 8, 9, 3, 1" leaves the board's outer squares: the landing squares are on the outer ring, so draw the full 5 by 5.
