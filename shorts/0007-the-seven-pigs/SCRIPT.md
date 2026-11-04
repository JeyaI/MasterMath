# 0007 The Seven Pigs

## Puzzle
`dudeney-amusements-165`, The Seven Pigs. Chosen because it is one clean picture (a pen, seven dots, three lines), the statement retells in a few captions, the answer is checkable in code (shapely), and the insight takes about 15 seconds. It is also the first Short on lines and sorting rather than cutting up a shape.
Runner-up: `dudeney-amusements-173`, Mrs. Perkins's Quilt (13 x 13 into 11 squares): good visual, but it is a pure dissection like 0001 and 0006, and the answer is a fiddly arrangement to animate.

## Hook
Pop in the square pen with seven pigs (dots). Text: **"Seven pigs, one pen."** then the question: **"Can 3 straight fences give every pig its own sty?"**

## Retelling
A square pen holds seven pigs, scattered so no row or pattern helps. You have three straight fences, each running wall to wall. No fence may touch a pig. Build them so every pig ends up alone in its own sty.

## Insight
The tempting plan is three parallel fences: they make only 4 sties, so the pigs crowd. The idea is to make the fences cross. Each new fence crosses all the earlier ones inside the pen, so it cuts through more sties: the 1st fence gives 2 sties, the 2nd adds 2 (4), the 3rd adds 3 (7). Three lines can never make more than 7, so 7 pigs fit only if the sties are exactly those 7. Three crossing fences leave a small triangle in the middle, three sties beside its sides and three in the corners, so one pig goes in the triangle and the rest get sorted around it.

Animation: the pen and pigs sit perfectly still, as in Dudeney (the pigs never move; only the fences do). Before the countdown, a failed example: 3 parallel fences slide in, the sties are tinted and the crowded ones pulse red, so viewers see what a fail looks like. The fences retract, then the countdown. After it, the crossing fences sweep in one at a time; after each, the newly split sties flash and a counter 2 / 4 / 7 ticks up. At the end each sty is tinted in a different colour, and each pig gets a colour pop and a tick. Fence positions, sties and pigs come from `verify.py`.

Differs from recent Shorts. I checked the docstrings of 0004 (bishop loops, multiplying choices), 0005 (the potato: grid vs every-cut-crosses-every-cut, counter 2, 4, 7, 11, 16, 22) and 0006 (flag cross area, algebra). 0005 is the nearest: it also counts regions from crossing cuts, and the 2, 4, 7 steps overlap with it. What is new here is the opposite direction: the regions are given by where the pigs are, so the picture is a placement and sorting problem (which side of each fence is each pig) in a square pen with a given point set, not a count on a blank disc. I kept the region-count caption to a single beat so that it does not retell the potato.

## Beats
1. "Seven pigs, one pen": pen and pigs pop in (3 s)
2. "3 straight fences": the three fence lines pass over the pen once (4 s)
3. "One pig per sty": the rule; touching a pig is out (4 s)
4. "Parallel fences: 4 sties": a failed try, shown before the countdown; fences slide in, pigs stay put (5 s)
5. "Pigs still share": crowded sties pulse red, then the fences slide out (3 s)
6. "Pause and try it": countdown 5 (6 s)
7. "So make fences cross": the fences slide in from the walls to the right places (3 s)
8. "First fence: 2 sties" (2 s)
9. "Second crosses it: 4" (3 s)
10. "Third crosses both: 7": counter ticks to 7 (4 s)
11. "A triangle in the middle": highlight the triangle and its neighbours (3 s)
12. "Sort the pigs": the pigs get their sties, colours in (3 s)
13. "7 sties, 7 pigs ✓": payoff (3 s)
14. Level 2 card then "Comment just the number ↓" (about 12 s for the hold)

Total about 58 s with the 12 s hold, about 46 s before it.

## Level 2
Four straight fences, every pair crossing inside the pen, no three meeting at a point. How many sties are shut in completely, touching no wall?
Answer: **3**. Why: with 3 fences only the middle triangle is shut in. The 4th fence crosses all three and closes 2 more sties in the middle, so 1 + 2 = 3. (The 4 fences make 11 sties in all, which the card does not ask.)

## Music
`k545` (Mozart, Piano Sonata in C, K. 545), the first of `ms music`'s list and still unused. The last used were `bwv846`, `fur-elise`, `pachelbel-canon`, `minuet-g` (0005), `gymnopedie-1` (0006), so it avoids them.

## Risks
- Dudeney's figure is a picture, so the pig positions are ours (seven scattered points); the puzzle is the same. The pigs are placed so that each of the 7 sties holds exactly one and no fence is within 0.25 of a pig. `verify.py` checks it.
- The book says to find the arrangement "by trial". Our solution is shown as a picture of fences going in, not a proof that these pig positions need exactly these fences. The claim made is only that this pen works and 7 is the most that 3 lines can make.
- The parallel try (4 sties) is our own illustration, not from the book.
- The Level 2 wording "shut in" needs to be clear on the card: sties that touch no wall. Counting 11 would be the nearest wrong answer.
- Overlap with 0005 on the counting step (see Insight).
