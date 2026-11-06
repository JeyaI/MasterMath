# 0011 The Six Sheep-Pens

## Puzzle
`dudeney-amusements-205`, The Six Sheep-Pens. Chosen because the whole solution is one clean picture (a hexagon with spokes), the statement retells in a few captions, and `verify.py` checks it exactly (12 equal matches, no loose ends, six equal pens). Runner-up: `dudeney-amusements-180` (The Four Sons), whose figure is harder to recreate and whose wording ("exactly similar in shape") is ambiguous.

## Hook
"12 matches" pops in as a pile of twelve matchsticks, then: "Can you fence six equal pens?"

## Retelling
A farmer has twelve hurdles, all the same length. Lay them flat, end to end, to fence six sheep-pens of exactly the same size. All twelve must be used, none may lie on top of another, and no end may dangle loose. (We drop Dudeney's 13-match starting figure; the puzzle stands without it.)

## Insight
**Walls can be shared, and pens needn't be squares.** Squares or rectangles waste matches: six equal pens in a 2 by 3 block take 17. Triangles are the cheapest: a hexagon of six matches, plus six spokes to the centre, makes six equal triangles, and every spoke serves as a wall for two pens. 6 + 6 = 12.

Animation: the twelve matches drop in one at a time. First try: a 2 by 3 block of squares grows and runs out of matches at six pens short (a counter shows matches left going to negative / "17 needed"), then fades. Then the six rim matches swing into a hexagon, the six spokes slide in from the centre one after another, and each triangle pen fills with a colour and a little sheep dot as it closes. A match counter ticks 12/12.

Visual ideas checked: `SCRIPT.md` for 0006, 0008, 0009, 0010 (0007's insight I could only skim). Those use area counting, a cut-and-slide dissection, a state-search of moves, and a swipe/odd-point count. None builds a figure from sticks or compares a failed grid with a shared-wall layout, so this is different.

## Beats
1. Hook: twelve matches pop in, "Six equal pens" (3 s)
2. "Only twelve matches" (2 s)
3. "No overlaps. No loose ends" (3 s)
4. "Pause and try it", 5 s countdown (6 s)
5. "Squares need too many": 2 by 3 block runs out (4 s)
6. "Try triangles" (2 s)
7. "A hexagon: six matches" (3 s)
8. "Spokes share the walls": six spokes, pens fill (5 s)
9. "Six pens, twelve matches ✓" (3 s)
10. Level 2 card: "Big triangle, side three" (3 s)
11. "How many matches?" (2 s)
12. "Comment just the number ↓" held (12 s)

About 48 s in total.

## Level 2
A big triangle has three matches along each side and is cut by lines parallel to its sides into small triangular pens of one match per side. How many matches? Answer: 18. Matches run in three directions, and each direction has 3 + 2 + 1 = 6, so 3 x 6 = 18 (9 pens). Checked in `verify.py`.

## Music
`minuet-g` (light, dancing). It is the least recently used key (last used on 0005).

## Risks
- Dudeney's figure of 13 matches is not recreated; the Short starts from the 12-match version. A viewer may find other valid answers (the puzzle only requires six equal pens), and we say "one way" in the payoff.
- "Pens of the same size" could be read as the same shape; our answer satisfies both.
- Level 1 says "hurdles" in short.yaml for the farm flavour; the video should call them matches throughout.
