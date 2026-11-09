# 0016: How To Make Cisterns

## Puzzle
`dudeney-amusements-201`, Dudeney, *Amusements in Mathematics*, "How To Make Cisterns". Chosen because it has one clear visual (a flat sheet folding into a box while a volume reading rises and falls), a short statement, an answer that checks exactly in code (8 inches), and a natural Level 2. It is also the first optimisation puzzle in the series. Runner-up: `dudeney-amusements-180` (The Four Sons), whose figure is only described in words and would be risky to recreate.

## Hook
Pop in the flat sheet with its four corner squares, then the question:
"How big should the corner squares be to make the cistern hold the most water?"

## Retelling
A man has a flat sheet of zinc, 8 feet by 3 feet. He cuts a square of the same size out of each corner, folds up the four sides and solders the edges, making an open box to hold water. Small squares give a wide, shallow box; big squares give a tall, thin one. What size of square gives the biggest box?

## Insight
**Write the volume as a cubic and find where its slope is zero** (revised after the reviewer's comment: solve analytically, not by tabulating). With squares of side x inches, the box is x high, (96 − 2x) long and (36 − 2x) wide:

V(x) = x(96 − 2x)(36 − 2x) = 4x³ − 264x² + 3456x.

The peak is where the slope is zero: V′(x) = 12x² − 528x + 3456 = 12(x − 8)(x − 36). The roots are x = 8 and x = 36. A cut of 36 is impossible (x must be under 18, half the short side, and there the box has no width), so 8 is the candidate. V′ is positive just before 8 and negative just after (equivalently V″(8) = −336 < 0), so it is a maximum: V(8) = 8 × 80 × 20 = 12,800 cubic inches. verify.py checks the expansion, the factorisation, the sign change and the value in code (and still checks a fine grid of cuts).

Animation: on the left, the flat sheet with corner squares folding up into a simple isometric box with the height x drawn. On the right, the equations appear line by line (V, the expanded cubic, V′, the factored V′), then the cubic's curve is drawn for x from 0 to 18 with a tangent line sliding along it; the tangent flattens at x = 8, where a dot settles and is labelled "8 in, 12,800". The root 36 is shown greyed out as off the sheet.

Checked against: the `SCRIPT.md` files of 0011 (sharing walls), 0012 (counting jumps), 0013 (shrinking choices ladder), 0014 (squares fit-up by edge sums) and 0015 (odd stations paired). None is an optimisation or a fold-up, and none draws a curve with a peak. I did not read the SCRIPT.md files of 0001–0010 in full.

## Beats
1. (4 s) Hook: "How big should the corner squares be to make the biggest cistern?" The flat sheet pops in first.
2. (3 s) "A man has a flat zinc sheet, eight feet by three feet."
3. (2 s) "He cuts a square out of each of the four corners."
4. (2 s) "Then he folds up the sides to make a cistern."
5. (5 s) "Pause and try it" with the 5 s countdown.
6. (2 s) "Tiny squares make a wide cistern, but it is very shallow."
7. (2 s) "Big squares make a deep cistern, but it is tall and thin."
8. (3 s) "If the square has side x, the volume is x times the length times the width." (V = x(96 − 2x)(36 − 2x), expands to 4x³ − 264x² + 3456x)
9. (2 s) "That is a cubic, so its peak is where the slope is zero."
10. (3 s) "The slope is twelve x squared minus 528 x plus 3456."
11. (3 s) "That factors as twelve times (x minus 8) times (x minus 36)."
12. (3 s) "The slope is zero at 8 and 36, but 36 is too big for the sheet."
13. (3 s) "The slope goes from positive to negative at 8, so that is the peak."
14. (2 s) "At eight inches the volume is twelve thousand eight hundred."
15. (3 s) "The squares should be eight inches on each side ✓"
16. (3 s) Level 2 card: "Now try a square sheet, twelve feet on each side."
17. (12 s) "Comment just the number ↓"

Total: 53 s with the 12 s end hold; trim beats 6–8 if it runs long.

## Level 2
"Same idea with a square zinc sheet 12 feet by 12 feet. How many feet long should the side of each cut-out square be for the biggest box?" Answer: **2**. Try whole feet: 1 ft gives 1 × 10 × 10 = 100, 2 ft gives 2 × 8 × 8 = 128, 3 ft gives 3 × 6 × 6 = 108, so 2 feet is best (it is a sixth of the side). No calculator needed.

## Music
`pachelbel-canon` (warm, building), the least recently used key; the last Shorts used `fur-elise`, `bwv846` and `k545`.

## Risks
- The original figure is only an illustration of a sheet with four corners cut away; we redraw it ourselves.
- Dudeney's text gives a formula but not the reason it works; we now derive the answer with calculus (cubic, derivative, factorisation), which is exact and needs no trust in a table. Level 2 stays solvable by trying whole feet (1, 2, 3 ft), no calculus needed.
- Units: the sheet is in feet but the answer is 8 inches, so the video converts early (96 in by 36 in) and the statement asks for inches.
- "Cistern" is an open-topped box; we say "open" in the retelling and draw no lid.
- Beat timing above runs long and needs trimming when the scene is built.
