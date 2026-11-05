# 0010: A Juvenile Puzzle

**Revision (reviewer: the format is paper, the audience is on a screen).** Moved the puzzle onto a screen. Dudeney's own second form is "draw it on a slate and rub it out in three rubs", so we use that: the figure sits on a touchscreen and you wipe it off with swipes. The loophole is now two fingers on the glass at once instead of folding paper. The maths, the figure and the Level 2 answer are unchanged.

## Puzzle
`dudeney-amusements-239`, "A Juvenile Puzzle" (the rub-out form in Dudeney's text). Chosen because the statement is one sentence, the check is exact (parity plus an exhaustive search in `verify.py`), the payoff is a real "oh!" (the rules allow a move nobody thinks of), and Level 2 is a clean one-step extension with a number answer. Runner-up: `dudeney-amusements-245`, "The Fly On The Octahedron". I passed over 242 and 246 because they are the odd-point-and-repeat idea 0003 already used.

## Hook
The figure pops onto a phone screen: a box, a bar across the middle, two uprights above the bar, one below. Then, in plain words: "Can you wipe this off in three swipes?" No teaser, no slogan.

## Retelling
Here is a figure on a touchscreen: a rectangle, a bar across the middle, two upright lines above the bar and one below. Wipe it clean in three swipes. A swipe never lifts off the glass and never goes back over a line it has already wiped. It looks as if you need four.

## Insight
**Every swipe has only two ends, and every point where an odd number of lines meet must be an end.** The figure has 8 such points (shown as glowing dots), so ordinary swipes give 4, and three is impossible. The way out is a loophole: nothing says a swipe must use one finger. The two upright lines above the bar are parallel and the same length, so put two fingers on them and wipe both at once. That is one swipe. The 8 odd points shrink to 4 once those two lines are gone, and two swipes finish the rest: 1 + 2 = 3.

Animation: the odd points light up one at a time with a counter (8 dots, pairs joined by arcs to show "4 swipes"). Then two fingertip dots land on the two uprights and slide down together, wiping both lines in a single swipe. The remaining two swipes are traced by one fingertip dot in two different colours, wiping the lines as it goes.

Checked against the recent Shorts: I read the `scene.py` docstring of 0003 (Inspecting a Mine) and the `SCRIPT.md` files of 0006 to 0009. 0003 is also a route problem, but it is solved by repeating passages and walking a dot along a long route; here no line is repeated and the visual idea is two fingers moving as one. 0006 is overlapping bars, 0007 fences, 0008 moving frogs, 0009 a pinwheel of triangles. None of them wipes a screen with two touches at once.

## Beats
1. The figure pops onto a screen. "Wipe it off in three swipes" (3 s)
2. The rule: a fingertip traces one swipe, then a lifted finger and a repeated line each get a red cross. "Finger stays down. No repeats" (3 s)
3. "Pause and try it" with a 5 s countdown (5 s)
4. The 8 odd points glow, one by one, with a count. "Odd points are swipe ends" (5 s)
5. Pairs joined: 8 points, 2 ends per swipe. "Eight odd points: four swipes" (4 s)
6. Two fingertips land on the two uprights. "Use two fingers" (5 s)
7. Both slide down together and both lines vanish in one swipe. "Two lines, one swipe" (5 s)
8. Two more swipes in two colours, the screen clear, a tick. "Three swipes ✓" (5 s)
9. Level 2 card: a 3 by 5 grid, one finger only. "One finger: how many swipes?" (4 s)
10. "Comment just the number ↓" held (12 s)

Total about 51 s including the 12 s end card.

## Level 2
A grid of 3 by 5 squares on the screen, one finger only. What is the fewest number of swipes to wipe it clean? Answer: 6. Why: the points on the edge that are not corners each have three lines, there are 2 x 4 + 2 x 2 = 12 of them, every swipe has two ends, so 12 / 2 = 6. The interior points have four lines and the corners two, so they need no ends. `verify.py` finds six swipes that do it. No calculator needed.

## Music
`pachelbel-canon` (unchanged).

## Risks
- The book's figure is only ASCII art. I recreated a figure with the same shape that has the same property. The credit says "after" Dudeney.
- The answer is a quibble (two fingers), and some viewers will call it cheating. Dudeney says the plain puzzle is impossible and that the trick is the catch in the wording; the Short should say that out loud in the payoff and not claim the plain version is solvable.
- Two fingers only work because the two uprights are parallel and equal; the scene must show that clearly.
- The Level 2 card must say "one finger", otherwise a commenter can answer 3 or 1.
- `scene.py` still draws the fold version and will need rewriting for the screen version in the video loop.
