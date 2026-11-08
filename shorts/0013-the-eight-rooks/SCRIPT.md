# 0013 The Eight Rooks

## Puzzle
`dudeney-amusements-295`, The Eight Rooks (Dudeney, *Amusements in Mathematics*, public domain). Chosen because it is a clean counting puzzle with one visual idea (rooks fill rows, columns run out), a statement that retells in three captions, and an answer checked by brute force. It is not a dissection, which the recent Shorts and the top of `ms suggest` are full of. Runner-up: `dudeney-amusements-173`, Mrs. Perkins's Quilt (13 x 13 into 11 squares), which would be a fourth patchwork-style dissection in a row.

## Hook
A chessboard pops in with 8 rooks on one row. Text: "8 rooks. Every square covered." then "No rook attacks another. How many ways?"

## Retelling
A rook attacks every square along its row and column. Put 8 rooks on a chessboard so that every square is either occupied or attacked, and no rook attacks another. How many different arrangements are there? Mirror images and turns count as different.

## Insight
Two rooks in one row would attack each other, so there is exactly one rook per row; the same for columns. Then build a placement row by row. A tall ladder of 8 labelled rungs sits beside the board. Row 1: all 8 columns glow as options, the rook lands, and its column dims. Row 2: 7 columns glow; the rook lands, another column dims. This repeats with a counter ladder 8, 7, 6, ... 1 while the dimmed columns grow into a striped wall. The ladder numbers then fly together into 8 × 7 × ... × 1 = 40,320.

Checked against: the `SCRIPT.md` files and scene docstrings of 0001-0012. The nearest idea is 0004 (Bishops), which multiplies independent 2-way choices around closed diagonal loops. Here the choices shrink (8, 7, 6, ...) as columns are used up, and the picture is the disappearing columns, not loops. 0005 (Potato) and 0007 (Pigs) add increasing counts of cuts or fences, again a different picture.

## Beats
1. Hook: board with 8 rooks in a row, "8 rooks. Every square covered." (3 s)
2. "Rooks attack along lines": rays shoot out of one rook along row and column (2 s)
3. "Cover every square": the row of rooks lights the whole board (2 s)
4. "No rook attacks another": Dudeney's diagonal, rays touch no rook (2 s)
5. "Another way": the other diagonal, then an irregular placement (3 s)
6. "How many ways in all?" (2 s)
7. "Pause and try it" with 5 s countdown (6 s)
8. "Two in a row would attack": two rooks in a row flash red (2 s)
9. "One rook per row": rows light up one by one (2 s)
10. "And one per column": columns light up (1 s)
11. "Row 1: 8 columns free": top rook lands, ladder shows 8 (2 s)
12. "Row 2: only 7": its column dims (2 s)
13. "Then 6, 5, 4 ...": the rest fill quickly with the ladder counting down (3 s)
14. "Last row: 1 choice" (1 s)
15. "Choices multiply" / "8 × 7 × 6 × ... × 1": ladder numbers join into the product (3 s)
16. "40,320 ways ✓": payoff (2 s)
17. Level 2 card: 6 × 6 board with 6 rooks, "how many ways?" and "Comment just the number ↓", held 12 s

Total about 50 s: roughly 38 s up to the payoff plus the 12 s Level 2 hold.

## Level 2
Question: the same rules on a 6 by 6 board with 6 rooks; how many ways? Answer: **720**, because it is 6 × 5 × 4 × 3 × 2 × 1. No calculator is needed. `accept` includes "6!" and spelled-out forms.

## Music
`k545` (Mozart, Piano Sonata in C, K. 545). It is the least recently used key in `ms music` (last on 0007); the recent Shorts used gymnopedie-1, minuet-g and pachelbel-canon. Bright and quick suits a counting puzzle.

## Risks
- Dudeney's wording is "every square occupied or attacked and no rook ever guarded by another". "Guarded" means attacked by another rook of the same colour. The video says "no rook attacks another" and shows rays, to avoid the odd word.
- Reflections and turns count as different. This is said on screen so that a commenter does not answer with a smaller number.
- Some viewers may think rooks block each other's lines. With one rook per row and column this never matters, but a viewer may raise it. `verify.py` brute-forces 4x4, 5x5 and 6x6 boards to show that the count is n!, and also checks all 40,320 permutations at 8x8.
- The figures (board, rooks, rays) are simple to recreate; no artwork from the book is needed.
