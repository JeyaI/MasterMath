# Script: 0008 The Six Frogs

## Puzzle
`dudeney-amusements-214`, The Six Frogs (Dudeney, *Amusements in Mathematics*, public domain).
Why: the catalog's first counters puzzle for us. It has a single clean idea (every pair must swap, and only a leap swaps a pair), a number the code can check by brute-force search, and a Level 2 that is the same count with 8 frogs. The top of `ms suggest` is all dissections, which we have just done in 0001, 0002 and 0006.
Runner-up: `dudeney-amusements-245`, The Fly on the Octahedron (1,488 routes). It is harder to check on screen and the count can't be shown in 40 s.

## Hook
Pop in the row of six numbered frogs on seven squares, one empty square on the left. Text: **"Reverse the frogs. What is the fewest number of moves?"** Squares and frogs appear first, then the question.

## Retelling
Six frogs numbered 1 to 6 sit on a row of seven squares, in order, with the empty square at the left end. A frog can slide into the next square if it is empty, or leap over one frog into an empty square just beyond. Frogs may go either way. Get them into the order 6 5 4 3 2 1, with the empty square still on the left. What is the fewest number of moves?

## Insight
One idea: **count the pairs that must swap.** Frogs 1 and 2 start in order and must end reversed; so must every pair. A slide never changes the order of two frogs, but a leap swaps exactly one pair. Six frogs make 15 pairs, so 15 leaps at the very least. The remaining moves are a slide for each frog: 6. Total 15 + 6 = 21, which matches Dudeney's answer and our breadth-first search in `verify.py`.

Animation: a small frog-row on top plays Dudeney's order (2 4 6 5 3 1, three times, then 2 4 6) with arcs for leaps. Each leap draws a line between the two frogs it swapped, in a triangle-of-pairs grid underneath: all 15 cells (one per pair) start empty/grey and light up one by one, each at the moment of its leap. Slides do not light a cell, only a small slide counter increments. By the end the grid is full and a counter reads 15 leaps + 6 slides.

Recent Shorts checked (docstrings of `scene.py`): 0007 Seven Pigs (fences splitting a square, region counting), 0006 St George's Banner (bars lighting up and peeled-off overlap in an equation), 0005 Potato Puzzle (cuts adding pieces, 1+2+...+6). Also 0001, 0002 dissections. None uses moving pieces, a board position changing over time, or a pair-grid; this one is the first to animate a sequence of moves.

## Beats
1. "6 frogs, 1 empty square": the row builds in, numbers on the frogs, hook question. (3 s)
2. "Slide or leap one frog": one demo slide, one demo leap with an arc. (4 s)
3. "Reverse the order": target row 6 5 4 3 2 1 ghosted beneath. (3 s)
4. "Pause and try it": 5 s countdown. (5 s)
5. "Every pair must swap": a pair, 1 and 2, highlighted, before and after. (3 s)
6. "Only a leap swaps a pair": slide vs leap side by side. (4 s)
7. "6 frogs: 15 pairs": the triangle grid of 15 cells builds. (3 s)
8. "So 15 leaps": Dudeney's sequence runs fast; each leap lights its cell. (7 s)
9. "Plus 6 slides": the slides tally as a second counter. (2 s)
10. "15 + 6 = 21 moves ✓": payoff. (3 s)
11. Level 2 card: 8 frogs on 9 squares, not solved. (3 s)
12. "Comment just the number ↓", held about 12 s.

Total: 3+4+3+5+3+4+3+7+2+3+3+12 = 52 s with the hold; about 40 s before the Level 2 card. If the preview runs long, shorten beat 2 or 8.

## Level 2
Question: the same puzzle with 8 frogs on 9 squares. What is the fewest number of moves?
Answer: **36** (accept: 36, "thirty-six", "36 moves").
Why: 8 frogs make 8 × 7 ÷ 2 = 28 pairs, so 28 leaps, plus 8 slides (one per frog): 28 + 8 = 36. This needs no calculator. Verified: search over the 8-frog board finds 36 and the recipe plays it.

## Music
`bwv846` (Bach, Prelude in C): steady and unhurried, suits counting moves. It is the least recently used key in `ms music` (last used by 0002); the last two used were `gymnopedie-1` (0006) and `k545` (0007).

## Risks
- The original figure is not in the text. We assume the empty square is on the left with frogs 1 to 6 in the next six squares. `verify.py` shows this is the only layout in which Dudeney's own first move (frog 2 leaps frog 1) is legal, and the search then gives his 21.
- The minimal-move claim for 6 frogs is checked by exhaustive search. The "15 leaps is a lower bound" argument is a lower bound only: that exactly 6 slides suffice comes from the search and the recipe, not from the pair argument. The video should say "plus 6 slides" after showing Dudeney's sequence rather than claim to derive it.
- The 8-frog recipe is in `verify.py`; Level 2 is not solved on screen.
- Frogs must stay distinguishable by number in a 1080-wide frame: seven squares need to be large enough for numerals, so the row is about 6.5 units wide with the pair grid below it.
