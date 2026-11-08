# 0006 · St. George's Banner: script

> **Revision 2 (reviewer's comment).** No, the slide-the-corners method was not the book's. Dudeney's own solution is a one-line rule with no explanation: a quarter of the perimeter minus half the diagonal (3½ − 2½ = 1 ft). As suggested, the insight is now the direct count of the red: 4x + 3x − x² = 6, so x = 1. Hook, problem beats and the pause are unchanged; Level 2 keeps its numbers and now uses the same red count.

## Puzzle
- **Catalog id:** `dudeney-amusements-185` (Dudeney, *Amusements in Mathematics*, no. 185).
- **Why:** one picture solves it (the two bars overlap in a square that gets counted twice), the answer is a clean whole number checked exactly in `verify.py`, and it moves us off dissection, chess and counting, the tags of the last few Shorts.
- **Runner-up:** `dudeney-amusements-214` *The Six Frogs* (reverse six frogs in 21 moves). Good, but the move sequence is long to show in 45 s and the "fewest" claim needs a search to back it up.

## Hook (0–3 s)
The flag pops in: a red cross on white, with "4 ft" along the top and "3 ft" down the side. Then the hook text:

> **How wide must the cross be**
> **for equal red and white?**

## Retelling
A flag is 4 feet wide and 3 feet tall. A red cross runs across it: one bar the full width, one bar the full height, both the same width, crossing in the middle. The rest of the flag is white. How wide must the bars be so that the flag has exactly as much red as white?

## Insight
**Count the red, and don't count the middle twice.** Call the arm width x. The red is two bars: the long one is 4 by x, so 4x; the upright is 3 by x, so 3x. But they cross in an x-by-x square in the middle, and adding the two bars counts that square twice. So the red is 4x + 3x − x², and it must be half the flag, 6 square feet: 7x − x² = 6. Try x = 1: 7 − 1 = 6. The cross is 1 foot wide. Check with the white: four corners, each 1½ by 1, make 6.

**Animation.** The long bar lifts off the flag (a shadow) and lights up, labelled "4 × x". Then the upright lifts and lights, "3 × x". Where they cross, the centre square glows twice as bright with a double outline and a "×2" tag, then one copy peels away labelled "− x²". The three labels slide down into one line, "4x + 3x − x² = 6", which tidies to "7x − x² = 6". A "x = 1" chip drops in and the line evaluates to "7 − 1 = 6 ✓". The bars settle back into the flag, the arm gets its "1 ft" label, and the four white corners flash in turn, each "1½ × 1", totalling 6.

The thin-cross beat before the pause uses the same flag: the arm starts at ½ ft (red visibly much smaller) as a hint that the answer is "wider than it looks".

**Checked against recent Shorts (read each `scene.py` docstring):**
- 0001 Greek Cross: cut a cross into pieces and *rearrange* them into a square (a dissection; pieces rotate and reassemble). Here nothing is cut or moved to a new place: the bars only lift and light up in place, and the idea is the overlap counted twice.
- 0002 Crescent: a quarter-turn and scale of a triangle, then algebra. Ours also ends in a line of algebra, but the visual idea is different: overlapping strips and a double-counted square, no turning or scaling.
- 0003 Inspecting a Mine: odd junctions on a graph, a dot walking a route.
- 0004 Bishops: diagonals bouncing into loops on a chessboard.
- 0005 Potato: knife cuts counted piece by piece.

## Beats
| # | Caption | What happens | ~s |
|---|---|---|---|
| 1 | *(hook)* How wide must the cross be / for equal red and white? | Flag pops in with dimension labels; hook text | 0–3 |
| 2 | 4 feet by 3 feet | Dimension arrows pulse | 3–5 |
| 3 | Red and white: equal amounts | Red and white areas flash in turn | 5–8 |
| 4 | How wide is the cross? | Width bracket "x = ?" appears on the vertical bar | 8–10 |
| 5 | Too thin: too much white | Arm at ½ ft, then eases back to an unlabelled width | 10–13 |
| 6 | Pause and try it | 5 s countdown | 13–18 |
| 7 | Red must be half: 6 | "12 ÷ 2 = 6" beside the flag | 18–20 |
| 8 | Long bar: 4 × x | Long bar lifts and lights, label "4x" | 20–23 |
| 9 | Upright bar: 3 × x | Upright lifts and lights, label "3x" | 23–26 |
| 10 | Middle counted twice: − x² | Centre square glows double, one copy peels off as "− x²" | 26–29 |
| 11 | 4x + 3x − x² = 6 | Labels slide into one line, tidy to "7x − x² = 6" | 29–32 |
| 12 | Try x = 1: 7 − 1 = 6 | "x = 1" chip drops in; line evaluates, ✓ | 32–35 |
| 13 | White check: 4 × 1½ = 6 | Bars settle back; four corners flash, each "1½ × 1" | 35–37 |
| 14 | 1 foot ✓ | Badge, arm labelled "1 ft" | 37–39 |
| 15 | *(Level 2 card)* | 12 ft × 5 ft flag, "How wide?" (not solved) | 39–43 |
| 16 | Comment just the number ↓ | Held | 43–55 |

About 43 s to the call to action, 55 s with the 12 s hold on it.

## Level 2
- **Question:** Same flag design, now 12 feet by 5 feet. How many feet wide is the cross?
- **Answer:** **2**
- **Why:** count the red the same way: 12x + 5x − x² must be half of 60, which is 30, so 17x − x² = 30. Try x = 1: 16, too small. Try x = 2: 34 − 4 = 30. (White check: four 5 × 1½ corners, 30.) No calculator: just try small widths. Checked in `verify.py`, which also confirms 2 is the only width that fits on the flag (the other root, 15, is wider than the flag).

## Music
`gymnopedie-1`: Erik Satie, Gymnopédie No. 1 (slow, sparse). It is first in `ms music` (unused), and it suits a calm, single-idea Short. It avoids `minuet-g` (0005), `pachelbel-canon` (0004) and `fur-elise` (0003). Description line: `Music: Erik Satie, Gymnopédie No. 1.`

## Risks
- **The cross's shape.** Dudeney's figure is a full-length upright cross (St George's cross: both bars reach the edges and have the same width). The retelling and the first frame must make clear that the bars run edge to edge and are equally wide, or "x" is ambiguous. We recreate the figure ourselves as a plain 4 × 3 rectangle with a centred cross. No illustration is reproduced.
- **A second root.** 7x − x² = 6 also has x = 6, which is wider than the flag. We don't mention it on screen; `verify.py` checks that 1 is the only width that fits.
- **"Try x = 1" is a guess.** It is the honest way to solve this without the quadratic formula, and the check (7 − 1 = 6) makes it convincing. If it feels too lucky, beat 12 could show "x² − 7x + 6 = (x − 1)(x − 6)" instead, at the cost of a busier frame.
- **Dudeney's own method** (a quarter of the perimeter minus half the diagonal: 3½ − 2½ = 1) is different from ours and isn't shown; `verify.py` checks that it agrees. If a commenter quotes it, it gives the same answer.
- **Flag symbolism.** The flag is drawn without naming England in captions; the title keeps Dudeney's "St. George's Banner" for credit only. Plain red (brand red, not a national-flag spec) on white.
- **Level 2 shape.** A 12 × 5 flag is unusually long; the card should draw it to scale so it reads as a banner, which fits in the safe-zone width at about 6.5 units × 2.7.
