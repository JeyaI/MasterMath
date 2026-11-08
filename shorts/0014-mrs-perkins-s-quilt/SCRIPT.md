# 0014 Mrs. Perkins's Quilt

## Puzzle
`dudeney-amusements-173`, Mrs. Perkins's Quilt (Dudeney, *Amusements in Mathematics*, public domain). Chosen because it has one clear picture (big squares first, then fill the gap), a statement that retells in three sentences, no artwork needed (a 13 x 13 grid), and an answer that `verify.py` proves by exhaustive search, including that fewer is impossible. Level 2 is a natural smaller quilt. Runner-up: `dudeney-amusements-245`, The Fly on the Octahedron (1,488 routes), which is a fine puzzle but needs a long count that is hard to show in 45 s.

## Hook
A 13 x 13 grid of small patches pops in. Text, as one sentence: "What is the fewest square pieces a 13 by 13 quilt can be cut into?"

## Retelling
A square quilt is sewn from 169 small square patches, 13 by 13. You may cut only along the stitches, every piece must be a square, and one piece can't be the whole quilt. What is the fewest number of square pieces the quilt can be cut into?

## Insight
**Biggest squares first, and sides that add up to 13.** Start from the "obvious" answer, 169 single patches (a counter reads 169), then merge. A 7 square goes in the bottom-left corner, a 6 square beside it (7 + 6 = 13, the whole bottom edge) and a second 6 square above the 7 (7 + 6 = 13 again, the whole left side). The three squares leave a gap of 169 - 121 = 48 patches, highlighted. The same rule fills it, biggest square that fits each time (4, 3, 3, 2, 2, 2, 1, 1), and a counter ticks up 1 to 11. The tiling drawn is the one `verify.py` found by search, and it matches Dudeney's up to reflection. The last caption notes that a full search shows 10 squares are not enough.

Checked against: the `SCRIPT.md` files of 0009, 0011, 0012 and 0013, and the 0013 retelling of its Insight (shrinking choices, 8, 7, 6, ...). 0011 (sheep pens) is about sharing walls between equal pens, 0012 (almonds) is about counting jumps and chains, 0009 (easy square) is area and a slanted side, 0013 is a counting ladder. None packs squares of different sizes into a square, and none uses a "sides add to the total" fit. I did not read 0010's Insight line in full, nor the earlier scene docstrings of 0001 (Greek cross) and 0006 (banner), which are cut-and-rearrange dissections; here nothing is moved after cutting, the picture is built up square by square.

## Beats
1. Hook: the 13 x 13 grid pops in, "What is the fewest square pieces a 13 by 13 quilt can be cut into?" (4 s)
2. "This quilt is sewn from 169 small square patches." the patches shimmer, counter reads 169 (3 s)
3. "You may cut only along the stitches." a cut line runs along a grid line (2.5 s)
4. "Every piece must be a square, but not the whole quilt." the whole-quilt square flashes red and crosses out (3 s)
5. "How few squares can you cut it into?" (2 s)
6. "Pause and try it" with 5 s countdown (6 s)
7. "Using all 169 single patches works, but it's far too many." counter 169, then patches merge away (3.5 s)
8. "Let's use the biggest squares we can instead." (2.5 s)
9. "A 7 square and a 6 square together fill one whole side." 7 and 6 pop in, "7 + 6 = 13" (4 s)
10. "A second 6 square fills the other side." (3 s)
11. "That leaves an awkward gap of 48 patches." gap tinted, "169 - 121 = 48" (3 s)
12. "We fill the gap the same way: the biggest square that fits each time." eight squares pop in, largest first, counter ticking (6 s)
13. "In the end, we have used 11 squares." (2.5 s)
14. "A full search shows that 10 squares are not enough." (3 s)
15. "The fewest is 11 squares ✓" payoff (2.5 s)
16. Level 2 card: a 5 x 5 grid, "Same rules on a 5 by 5 quilt. Fewest squares?" and "Comment just the number ↓", held 12 s

Total about 50 s to the payoff-ish end of Level 1 (about 46 s of Level 1 content), plus the 12 s Level 2 hold.

## Level 2
Question: the same rules on a 5 by 5 quilt; what is the fewest number of squares? Answer: **8**. Why: a 3 square in the corner, then three 2 squares, then four single patches (area 9 + 12 + 4 = 25); `verify.py` proves 7 is impossible. `accept`: 8, "8 squares", "eight", "8 pieces". Solvable by hand with the same biggest-first trick.

## Music
`bwv846` (Bach, Prelude in C), the first key listed by `ms music` (last used on 0008). Steady and unhurried suits a build-up puzzle.

## Risks
- Dudeney's text has "smallest possible number of square portions" and relies on the picture to say that the quilt itself isn't one piece; the video says so explicitly ("but not the whole quilt"), and `verify.py` excludes that tiling.
- Dudeney's own figure is not needed: the grid is a 13 x 13 recreation. The tiling shown is a reflection of Dudeney's (same sizes, 7/6/6 then the group of eight).
- Viewers may reasonably wonder whether tilings with the same count but different arrangement exist. Dudeney says the three largest squares are forced and the group of eight may be reflected; the video claims only the count.
- The exhaustive search claim ("10 are not enough") is checked in `verify.py`; the video does not show why, just says a full search shows it.
- "Patches" and "pieces" are used consistently: patches are the 169 unit cells, pieces are the squares we cut.
