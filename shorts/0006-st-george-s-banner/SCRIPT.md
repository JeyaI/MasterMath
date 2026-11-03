# 0006 · St. George's Banner: script

## Puzzle
- **Catalog id:** `dudeney-amusements-185` (Dudeney, *Amusements in Mathematics*, no. 185).
- **Why:** one picture solves it (slide the white corners together and the cross vanishes), the answer is a clean whole number checked exactly in `verify.py`, and it moves us off dissection, chess and counting, the tags of the last few Shorts.
- **Runner-up:** `dudeney-amusements-214` *The Six Frogs* (reverse six frogs in 21 moves). Good, but the move sequence is long to show in 45 s and the "fewest" claim needs a search to back it up.

## Hook (0–3 s)
The flag pops in: a red cross on white, with "4 ft" along the top and "3 ft" down the side. Then the hook text:

> **How wide must the cross be**
> **for equal red and white?**

## Retelling
A flag is 4 feet wide and 3 feet tall. A red cross runs across it: one bar the full width, one bar the full height, both the same width, crossing in the middle. The rest of the flag is white. How wide must the bars be so that the flag has exactly as much red as white?

## Insight
**Squeeze the cross out.** The white is four equal corner rectangles. Slide each one diagonally towards the centre, by half the arm width in each direction, and they meet with no gap and no overlap: one white rectangle, (4 − w) by (3 − w). The red has been squeezed out entirely, so this rectangle is all the white. It has to be half the flag, 6 square feet, and the only way to get 6 by trimming the same amount off 4 and 3 is 3 × 2. Each side lost 1 foot, so the arm is 1 foot. Check: red is 4 + 3 − 1 = 6 (two bars, minus the square where they overlap, counted twice).

**Animation.** The four white corners lift slightly (a shadow), then glide diagonally inward together while the red cross shrinks to a thin line and fades. The closed-up rectangle gets "3 ft" and "2 ft" labels, which morph out of "4 − w" and "3 − w". A dashed outline of the original 4 × 3 flag stays behind it, so the strip of 1 ft missing on each side is visible. Then everything slides back: the corners return, the cross reappears, and its two bars light up in turn (4, 3) with the centre square flashing as "− 1".

The thin-cross beat before the pause uses the same flag: the arm starts at ½ ft (red visibly much smaller) as a hint that the answer is "wider than it looks".

**Checked against recent Shorts (read each `scene.py` docstring):**
- 0001 Greek Cross: cut a cross into pieces and *rearrange* them into a square (a dissection; pieces rotate and reassemble). Here nothing is cut or turned: the white corners only translate inward, and the point is the area that *disappears* between them, not a new shape.
- 0002 Crescent: a quarter-turn and scale of a triangle, then algebra.
- 0003 Inspecting a Mine: odd junctions on a graph, a dot walking a route.
- 0004 Bishops: diagonals bouncing into loops on a chessboard.
- 0005 Potato: knife cuts counted piece by piece.

## Beats
| # | Caption (2–6 words) | What happens | ~s |
|---|---|---|---|
| 1 | *(hook)* How wide must the cross be / for equal red and white? | Flag pops in with dimension labels; hook text | 0–3 |
| 2 | 4 feet by 3 feet | Dimension arrows pulse | 3–5 |
| 3 | Red and white: equal amounts | Red and white areas flash in turn | 5–8 |
| 4 | How wide is the cross? | Width bracket "w = ?" appears on the vertical bar | 8–10 |
| 5 | Too thin: too much white | Arm at ½ ft, then eases back to an unlabelled width | 10–13 |
| 6 | Pause and try it | 5 s countdown | 13–18 |
| 7 | Slide the corners together | Four corners glide diagonally inward | 18–21 |
| 8 | The cross squeezes out | Cross shrinks to nothing; one white rectangle, labels "4 − w", "3 − w" | 21–24 |
| 9 | White must be half: 6 | "12 ÷ 2 = 6" next to the rectangle | 24–27 |
| 10 | 6 = 3 × 2 | Labels morph to "3 ft" and "2 ft" | 27–30 |
| 11 | Each side lost 1 foot | 1 ft gaps highlighted against the dashed 4 × 3 outline | 30–33 |
| 12 | Red: 4 + 3 − 1 = 6 | Corners slide back, cross returns; bars light up, centre square flashes | 33–37 |
| 13 | 1 foot ✓ | Badge, arm labelled "1 ft" | 37–39 |
| 14 | *(Level 2 card)* | 12 ft × 5 ft flag, "How wide?" (not solved) | 39–43 |
| 15 | Comment just the number ↓ | Held | 43–55 |

About 43 s to the call to action, 55 s with the 12 s hold on it.

## Level 2
- **Question:** Same flag design, now 12 feet by 5 feet. How many feet wide is the cross?
- **Answer:** **2**
- **Why:** slide the corners together: the white is (12 − w)(5 − w) and must be half of 60, which is 30. Trimming the same amount off 12 and 5 to get 30 gives 10 × 3, so w = 2. (Red check: 24 + 10 − 4 = 30.) No calculator: just try small trims of 12 × 5. Checked in `verify.py`, which also confirms 2 is the only width that fits on the flag.

## Music
`gymnopedie-1`: Erik Satie, Gymnopédie No. 1 (slow, sparse). It is first in `ms music` (unused), and it suits a calm, single-idea Short. It avoids `minuet-g` (0005), `pachelbel-canon` (0004) and `fur-elise` (0003). Description line: `Music: Erik Satie, Gymnopédie No. 1.`

## Risks
- **The cross's shape.** Dudeney's figure is a full-length upright cross (St George's cross: both bars reach the edges and have the same width). The retelling and the first frame must make clear that the bars run edge to edge and are equally wide, or "w" is ambiguous. We recreate the figure ourselves as a plain 4 × 3 rectangle with a centred cross. No illustration is reproduced.
- **A second root.** (4 − w)(3 − w) = 6 also has w = 6, which is wider than the flag. We don't mention it on screen; `verify.py` checks that 1 is the only width that fits.
- **Dudeney's own method** (a quarter of the perimeter minus half the diagonal: 3½ − 2½ = 1) is different from ours and isn't shown; `verify.py` checks that it agrees. If a commenter quotes it, it gives the same answer.
- **Flag symbolism.** The flag is drawn without naming England in captions; the title keeps Dudeney's "St. George's Banner" for credit only. Plain red (brand red, not a national-flag spec) on white.
- **Level 2 shape.** A 12 × 5 flag is unusually long; the card should draw it to scale so it reads as a banner, which fits in the safe-zone width at about 6.5 units × 2.7.
