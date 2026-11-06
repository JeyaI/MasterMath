# 0011 The Six Sheep-Pens

## Puzzle
`dudeney-amusements-205`, The Six Sheep-Pens. Chosen because the whole solution is one clean picture (a hexagon with spokes), the statement retells in a few captions, and `verify.py` checks it exactly (12 equal matches, no loose ends, six equal pens). Runner-up: `dudeney-amusements-180` (The Four Sons), whose figure is harder to recreate and whose wording ("exactly similar in shape") is ambiguous.

## Revision (v2)
Reviewer asked for: (1) a second solution, two squares sharing a corner, each with 2 internal matches making 3 pens; (2) longer, self-explanatory captions (hook included); (3) a Level 2 caption that actually tells viewers the setup. Done below; `verify.py` now checks the two-square layout too (12 matches, no overlaps, no loose ends, 6 equal pens of area 1/3).

## Revision (v3)
Reviewer asked for: no sheep (never introduced in the video), and the opening matches laid out 2 tall by 6 wide, pointing up with a small random tilt so all 12 can be counted. Done: sheep removed from the pens; pile is a tidy 2 x 6 grid.

## Hook
"12 matches" pops in as a pile of twelve matchsticks, then the caption asks the question plainly: "Can you make 6 equally sized pens with 12 matches?"

## Retelling
A farmer has twelve hurdles, all the same length. Lay them flat, end to end, to fence six sheep-pens of exactly the same size. All twelve must be used, none may lie on top of another, and no end may dangle loose. (We drop Dudeney's 13-match starting figure; the puzzle stands without it.)

## Insight
**Walls can be shared, and pens needn't be squares.** Squares or rectangles waste matches: six equal pens in a 2 by 3 block take 17. Triangles are the cheapest: a hexagon of six matches, plus six spokes to the centre, makes six equal triangles, and every spoke serves as a wall for two pens. 6 + 6 = 12.

Animation: the twelve matches drop in one at a time. First try: a 2 by 3 block of squares grows and runs out of matches at six pens short (a counter shows matches left going to negative / "17 needed"), then fades. Then the six rim matches swing into a hexagon, the six spokes slide in from the centre one after another, and each triangle pen fills with a colour and a little sheep dot as it closes. A match counter ticks 12/12.

Second solution (after the hexagon payoff): the matches clear, then two squares of four matches each appear touching at one corner. Two internal matches slide into each square, parallel to a side and a third of the way across, cutting it into three equal pens. Each square: 4 + 2 = 6 matches, and 6 + 6 = 12. Pens fill with colour again, counter 12/12. Caption: "Another way: two squares sharing a corner".

Visual ideas checked: `SCRIPT.md` for 0006, 0008, 0009, 0010 (0007's insight I could only skim). Those use area counting, a cut-and-slide dissection, a state-search of moves, and a swipe/odd-point count. None builds a figure from sticks or compares a failed grid with a shared-wall layout, so this is different.

## Beats
1. Hook: twelve matches pop in, "Can you make 6 equally sized pens with 12 matches?" (4 s)
2. "Use every match: no overlaps, no loose ends" (3 s)
3. "Pause and try it", 5 s countdown (6 s); the opening question "Can you make 6 equally sized pens with 12 matches?" stays up with it
4. "A 2 by 3 block of squares needs 17 matches: too many" (4 s)
5. "Triangles share more walls, so try those" (3 s)
6. "Six matches make a hexagon" (3 s)
7. "Six spokes to the centre: each is a wall for two pens" (5 s)
8. "6 equal pens, 12 matches ✓" (3 s)
9. "Another way: two squares sharing a corner" (3 s)
10. "Two matches inside each square make 3 pens each" (4 s)
11. Level 2 card: "Level 2: a triangle with 3 matches on each side, cut into small triangles of 1 match per side" (4 s)
12. "How many matches in all?" (2 s)
13. "Comment just the number ↓" held (12 s)

About 56 s in total (a target, not a cap).

## Level 2
A big triangle has three matches along each side (the card draws it) and is cut by lines parallel to its sides into small triangular pens of one match per side. How many matches? Answer: 18. Matches run in three directions, and each direction has 3 + 2 + 1 = 6, so 3 x 6 = 18 (9 pens). Checked in `verify.py`.

## Music
`minuet-g` (light, dancing). It is the least recently used key (last used on 0005).

## Risks
- Dudeney's figure of 13 matches is not recreated; the Short starts from the 12-match version. A viewer may find other valid answers (the puzzle only requires six equal pens), and we say "one way" in the payoff.
- "Pens of the same size" could be read as the same shape; our answer satisfies both.
- Level 1 says "hurdles" in short.yaml for the farm flavour; the video should call them matches throughout.
