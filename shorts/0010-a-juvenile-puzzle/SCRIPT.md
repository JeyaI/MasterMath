# 0010: A Juvenile Puzzle

## Puzzle
`dudeney-amusements-239`, "A Juvenile Puzzle". Chosen because the statement is one sentence, the check is exact (parity plus an exhaustive search in `verify.py`), the payoff is a real "oh!" (the rules allow a move nobody thinks of), and Level 2 is a clean one-step extension with a number answer. Runner-up: `dudeney-amusements-245`, "The Fly On The Octahedron" (answer 1,488 routes, but there is no picture that shows why in 45 seconds). I passed over 242 (Tube Inspector) and 246 (Icosahedron) because they are the odd-point-and-repeat idea 0003 already used.

## Hook
A rectangle figure draws itself in: a box, a bar across the middle, two uprights above the bar, one below. Then, in plain words: "Draw it in three strokes". No teaser, no slogan.

## Retelling
Here is a figure: a rectangle, a bar across the middle, two upright lines above the bar and one below. Draw it with three strokes of a pencil. Inside a stroke the pencil never leaves the paper and never goes over a line twice. It looks as if you need four.

## Insight
**Every stroke has only two ends, and every point where an odd number of lines meet must be an end.** The figure has 8 such points (shown as glowing dots), so ordinary strokes give 4, and three is impossible. The way out is a loophole: nothing forbids folding the paper. Fold it between the two upright lines above the bar and they lie on top of each other, so one pencil stroke draws both. The 8 odd points shrink to 4 once those two lines are drawn, and two strokes finish the rest: 1 + 2 = 3.

Animation: the odd points light up one at a time with a counter (8 dots, pairs joined by arcs to show "4 strokes"). Then the paper folds: the left upright slides sideways over the right one while a crease line draws, a single pencil dot runs down the stack, and the paper unfolds with both lines drawn. The remaining two strokes are traced by a coloured dot in two different colours.

Checked against the recent Shorts: I read the `scene.py` docstring of 0003 (Inspecting a Mine) and the `SCRIPT.md` files of 0006 to 0009. 0003 is also a route problem, but it is solved by repeating passages and walking a dot along a long route; here no line is repeated and the visual idea is the fold, two lines sliding together onto one. 0006 is overlapping bars, 0007 fences, 0008 moving frogs, 0009 a pinwheel of triangles. None of them folds or stacks anything.

## Beats
1. The figure draws in. "Draw it in three strokes" (3 s)
2. The rule: a dot traces one stroke, then a lifted pencil and a repeated line each get a red cross. "Pen stays down. No repeats" (3 s)
3. "Pause and try it" with a 5 s countdown (5 s)
4. The 8 odd points glow, one by one, with a count. "Odd points are stroke ends" (5 s)
5. Pairs joined: 8 points, 2 ends per stroke. "Eight odd points: four strokes" (4 s)
6. The paper folds, the two uprights stack. "Fold the paper" (5 s)
7. One pencil dot draws both at once, then it unfolds. "Two lines, one stroke" (5 s)
8. Two more strokes in two colours, the whole figure lit, a tick. "Three strokes ✓" (5 s)
9. Level 2 card: a 3 by 5 grid, no folding. "No folding: how many strokes?" (4 s)
10. "Comment just the number ↓" held (12 s)

Total about 51 s including the 12 s end card.

## Level 2
A grid of 3 by 5 squares, no folding allowed. What is the fewest number of strokes? Answer: 6. Why: the points on the edge that are not corners each have three lines, there are 2 x 4 + 2 x 2 = 12 of them, every stroke has two ends, so 12 / 2 = 6. The interior points have four lines and the corners two, so they need no ends. `verify.py` finds six strokes that do it. No calculator needed.

## Music
`pachelbel-canon` (listed first by `ms music`, least recently used; its warm, building feel suits the slow reveal of the trick). Recent pieces were bwv846, fur-elise and k545.

## Risks
- The book's figure is only ASCII art. I recreated a figure with the same shape (a rectangle, a middle bar, two uprights above, one below) that has the same property: it looks like four strokes. The credit says "after" Dudeney. The reviewer may want to compare with the book's HTML illustration.
- The answer is a quibble (folding), and some viewers will call it cheating. Dudeney himself says the plain puzzle is impossible and that folding "is not actually forbidden"; the Short should say that out loud in the payoff and not claim the plain version is solvable.
- The statement and Discord thread title do not give the fold away; the "it looks like four" line is from the book.
- The fold has to read clearly in 2D: use a crease line between the two uprights and slide one over the other, not a 3D flip.
- The Level 2 answer assumes no folding; the card must say so, otherwise a commenter can answer 3 or 1.
