# 0016: How To Make Cisterns

## Puzzle
`dudeney-amusements-201`, Dudeney, *Amusements in Mathematics*, "How To Make Cisterns". Chosen because it has one clear visual (a flat sheet folding into a box while a volume reading rises and falls), a short statement, an answer that checks exactly in code (2/3 ft, i.e. 8 inches), and a natural Level 2. It is also the first optimisation puzzle in the series. Runner-up: `dudeney-amusements-180` (The Four Sons), whose figure is only described in words and would be risky to recreate.

## Hook
Pop in the flat sheet with its four corner squares, then the question:
"How big should the corner squares be to make the cistern hold the most water?"

## Retelling
A man has a flat sheet of zinc, 8 feet by 3 feet. He cuts a square of the same size out of each corner, folds up the four sides and solders the edges, making an open box to hold water. Small squares give a wide, shallow box; big squares give a tall, thin one. What size of square gives the biggest box?

## Insight
**Write the volume as a cubic and find where its slope is zero, using the quadratic formula** (revised after the reviewer's comments: solve analytically; nobody spots a factorisation by eye; keep everything in feet). With squares of side x feet, the box is x high, (8 − 2x) long and (3 − 2x) wide:

V(x) = x(8 − 2x)(3 − 2x) = 4x³ − 22x² + 24x.

The peak is where the slope is zero: V′(x) = 12x² − 44x + 24 = 0. Quadratic formula: x = (44 ± √(44² − 4·12·24)) / 24 = (44 ± √784) / 24 = (44 ± 28) / 24, so x = 3 or x = 2/3. A cut of 3 ft is impossible (x must be under 1.5 ft, half the short side), so 2/3 ft is the candidate. V′ is positive just before 2/3 and negative just after (equivalently V″(2/3) = −28 < 0), so it is a maximum: V(2/3) = 2/3 × 20/3 × 5/3 = 200/27 cubic feet. The answer is 2/3 of a foot, which is 8 inches (stated once at the end as a check; the working stays in feet). verify.py checks the expansion, the discriminant, both roots, the sign change and the value in code (and a fine grid of cuts).

Animation: on the left, the flat sheet with corner squares folding up into a simple isometric box with the height x drawn. On the right, the equations appear line by line (V, the expanded cubic, V′, the quadratic formula filled in), then the cubic's curve is drawn for x from 0 to 1.5 with a tangent line sliding along it; the tangent flattens at x = 2/3, where a dot settles and is labelled "2/3 ft". The root 3 is shown greyed out as off the sheet.

Checked against: the `SCRIPT.md` files of 0011 (sharing walls), 0012 (counting jumps), 0013 (shrinking choices ladder), 0014 (squares fit-up by edge sums) and 0015 (odd stations paired). None is an optimisation or a fold-up, and none draws a curve with a peak. I did not read the SCRIPT.md files of 0001–0010 in full.

## Beats
1. (4 s) Hook: "How big should the corner squares be to make the biggest cistern?" The flat sheet pops in first.
2. (3 s) "A man has a flat zinc sheet, eight feet by three feet."
3. (2 s) "He cuts a square out of each of the four corners."
4. (2 s) "Then he folds up the sides to make a cistern."
5. (5 s) "Pause and try it" with the 5 s countdown. The instructions stay on screen the whole time: the sheet (8 ft by 3 ft, square x cut from each corner) and the task text "Find x, in feet, for the biggest box."
6. (2 s) "Tiny squares make a wide cistern, but it is very shallow."
7. (2 s) "Big squares make a deep cistern, but it is tall and thin."
8. (3 s) "If the square has side x feet, the volume is x times the length times the width." (V = x(8 − 2x)(3 − 2x), expands to 4x³ − 22x² + 24x)
9. (2 s) "That is a cubic, so its peak is where the slope is zero."
10. (3 s) "The slope is twelve x squared minus 44 x plus 24, and we set it to zero."
11. (4 s) "The quadratic formula gives x equals 44 plus or minus 28, over 24." (√784 = 28)
12. (3 s) "So x is 3 or two thirds, but 3 feet is too big for the sheet."
13. (3 s) "The slope goes from positive to negative at two thirds, so that is the peak."
14. (2 s) "At two thirds of a foot, the volume is 200 over 27 cubic feet."
15. (3 s) "The squares should be two thirds of a foot, or eight inches ✓"
16. (3 s) Level 2 card: "Now try a square sheet, twelve feet on each side." The question stays on screen: "How many feet should each cut-out square be?"
17. (12 s) "Comment just the number ↓"

Total: 53 s with the 12 s end hold; trim beats 6–8 if it runs long.

## Level 2
"Same idea with a square zinc sheet 12 feet by 12 feet. How many feet long should the side of each cut-out square be for the biggest box?" Answer: **2**. Try whole feet: 1 ft gives 1 × 10 × 10 = 100, 2 ft gives 2 × 8 × 8 = 128, 3 ft gives 3 × 6 × 6 = 108, so 2 feet is best (it is a sixth of the side). No calculator needed.

## Music
`pachelbel-canon` (warm, building), the least recently used key; the last Shorts used `fur-elise`, `bwv846` and `k545`.

## Risks
- The original figure is only an illustration of a sheet with four corners cut away; we redraw it ourselves.
- Dudeney's text gives a formula but not the reason it works; we now derive the answer with calculus (cubic, derivative, quadratic formula), which is exact and needs no trust in a table. Level 2 stays solvable by trying whole feet (1, 2, 3 ft), no calculus needed.
- Units: everything stays in feet (8 ft by 3 ft, answer 2/3 ft); the 8 inches of Dudeney's answer appears only as a conversion at the end. The level 1 statement asks for the answer in feet.
- "Cistern" is an open-topped box; we say "open" in the retelling and draw no lid.
- Beat timing above runs long and needs trimming when the scene is built.
