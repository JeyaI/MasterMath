# 0009: An Easy Square Puzzle

## Puzzle
`dudeney-amusements-147`, "An Easy Square Puzzle". Chosen because it has one clean idea (a square with a hole, and a hole the size of one piece), a short statement, an exact answer checked in code, and a natural Level 2. Runner-up: `dudeney-amusements-150`, "Dissecting A Mitre" (five pieces, but the cut points need a compass construction, so it is harder to retell in 45 seconds).

## Hook
Five identical right triangles pop in, in a row, the first labelled "short side 1, long side 2". Then the question in plain words: "Make a square from 5 triangles?" (Captions in `short.yaml` are kept in step.)

Revision note (reviewer comment): beat 2 now shows a sample cut on the fifth triangle, with the two cut pieces wiggling apart to prove they can be separated; the old rectangle-cut beat is gone (the 1 and 2 labels in beat 1 carry the "twice as long as broad" shape). Captions are rewritten in natural English.

## Retelling
Take a 2 by 1 rectangle and cut it along its diagonal. You get a right triangle with short side 1 and long side 2. You have five identical ones. Make a perfect square using all five. You may cut one triangle in two pieces; the other four must stay whole.

## Insight
Area first: each triangle is worth 1, so the square is worth 5 and its side is the square root of 5, which is exactly the triangle's long slanted edge. So the slanted edges form the outside of the square.

Four whole triangles, slanted edge outward, make a tilted square with a 1 by 1 hole in the middle (long leg 2 minus short leg 1). The fifth triangle also has area 1. One vertical cut from the middle of its long leg to its slanted edge gives a trapezoid and a small triangle. The trapezoid slides up into the hole's lower-left; the small triangle turns half a turn and drops into the leftover corner. The hole is filled with no gap.

Animation: the four triangles fly in one by one and rotate into a pinwheel, the unit hole glows. The fifth triangle sits beside it, a cut line draws, the two parts separate, slide and rotate (half turn) into the hole, and the whole square outline lights up with "area 5".

Compared with the recent Shorts: I read the `scene.py` docstrings of 0001 to 0008. 0001 (Greek cross) also ends on a sqrt(5) square, but it slides four cross pieces cut along slopes; this one builds a pinwheel of whole triangles round a hole and fills it with a trapezoid and triangle, a different picture and motion. 0005 and 0007 are cut and fence counts; 0006 colours bars in place; 0002 is circles; 0003, 0004, 0008 are routes, boards and counters.

## Beats
1. Five triangles pop in, the first labelled 1 and 2. "Make a square from 5 triangles?" (3 s)
2. The rule, shown on the fifth triangle: a sample cut line draws across it (not the solution cut), the two pieces wiggle apart to show they separate, then slide back together; the other four stay whole. "You may cut one, once" (4 s)
3. "Pause and try it" with a 5 s countdown (5 s)
4. Area 5, so the side is the slanted edge. "Slanted edges form the outside" (3 s)
5. Four triangles swing into a pinwheel round a hole. "Four around a hole" (5 s)
6. The hole measures 1 by 1 and glows. "The hole is 1 by 1" (3 s)
7. Fifth triangle: cut line, split, slide and half-turn into the hole. "Cut the fifth triangle" (6 s)
8. Square lights up with area 5. "It fits exactly ✓" (3 s)
9. Level 2 card: legs 3 and 6, area of the square? "Short side 3, long side 6" (4 s)
10. "Comment just the number ↓" held (12 s)

Total 48 s, of which the last 12 s is the held end card.

## Level 2
Triangles with short side 3 and long side 6 (same shape, scaled by 3). Five make a square the same way. What is the area of that square? Answer: 45. Why: each triangle is 3 x 6 / 2 = 9, and 5 x 9 = 45. No calculator needed.

## Music
`fur-elise` (least recently used, listed first; the tense, mysterious mood suits a puzzle where the trick is hidden). Not one of the recent pieces (bwv846 was used by 0008, 0002 and 0001).

## Risks
- The book's figure is only given as ASCII art in the catalog; the solution here is my own reconstruction (same idea: four triangles and a cut fifth), verified in `verify.py` with shapely. The cut at the midpoint of the long leg is one valid way to cut; Dudeney's drawing may cut differently, so the credit says "after".
- "Twice as long as broad" must be made visible: show the 2 by 1 rectangle before the diagonal cut.
- The half turn of the small triangle must read clearly; give it a distinct colour.
- Level 2 sidesteps the hypotenuse check by asking for area, which is the same on any size scaling.
