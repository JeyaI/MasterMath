# 0016: How To Make Cisterns

## Puzzle
`dudeney-amusements-201`, Dudeney, *Amusements in Mathematics*, "How To Make Cisterns". Chosen because it has one clear visual (a flat sheet folding into a box while a volume reading rises and falls), a short statement, an answer that checks exactly in code (8 inches), and a natural Level 2. It is also the first optimisation puzzle in the series. Runner-up: `dudeney-amusements-180` (The Four Sons), whose figure is only described in words and would be risky to recreate.

## Hook
Pop in the flat sheet with its four corner squares, then the question:
"How big should the corner squares be to make the cistern hold the most water?"

## Retelling
A man has a flat sheet of zinc, 8 feet by 3 feet. He cuts a square of the same size out of each corner, folds up the four sides and solders the edges, making an open box to hold water. Small squares give a wide, shallow box; big squares give a tall, thin one. What size of square gives the biggest box?

## Insight
**Try every size and watch the volume rise and fall.** The box volume is base × height, and the cut size trades one against the other. Working in whole inches, the volumes are 12,096 (6 in), 12,628 (7 in), 12,800 (8 in), 12,636 (9 in) and 12,160 (10 in). The peak is at 8 inches, and an exact check (verify.py) confirms nothing between the inches beats it.

Animation: on the left, the flat sheet with corner squares; a slider lets the squares grow and shrink and the sides fold up into a 3D-looking box (a simple isometric box with the height drawn). On the right, a bar for each whole inch grows to its volume in turn, 6 to 10 in, with a highlight on the tallest bar; a dot then traces the smooth curve through the tops and settles on the peak at 8 inches, which is labelled "8 in, 12,800".

Checked against: the `SCRIPT.md` files of 0011 (sharing walls), 0012 (counting jumps), 0013 (shrinking choices ladder), 0014 (squares fit-up by edge sums) and 0015 (odd stations paired). None is an optimisation or a fold-up, and none draws a curve with a peak. I did not read the SCRIPT.md files of 0001–0010 in full.

## Beats
1. (4 s) Hook: "How big should the corner squares be to make the biggest cistern?" The flat sheet pops in first.
2. (3 s) "A man has a flat zinc sheet, eight feet by three feet."
3. (2 s) "He cuts a square out of each of the four corners."
4. (2 s) "Then he folds up the sides to make a cistern."
5. (5 s) "Pause and try it" with the 5 s countdown.
6. (2 s) "Tiny squares make a wide cistern, but it is very shallow."
7. (2 s) "Big squares make a deep cistern, but it is tall and thin."
8. (2 s) "So let's try every whole inch and measure the volume."
9. (2 s) "Cutting six inches holds about twelve thousand cubic inches."
10. (2 s) "Seven inches holds a little more."
11. (3 s) "Eight inches holds the most: twelve thousand eight hundred."
12. (2 s) "Nine inches holds less again, and ten inches even less."
13. (2 s) "The volume rises, peaks at eight inches, then falls."
14. (2 s) "An exact check confirms eight inches really is the peak."
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
- Dudeney's text gives a formula but not the reason it works; we show the answer by tabulating volumes and an exact check, not by deriving the formula. The viewer must trust the table past the whole inches; the caption says it was checked exactly.
- Units: the sheet is in feet but the answer is 8 inches, so the video converts early (96 in by 36 in) and the statement asks for inches.
- "Cistern" is an open-topped box; we say "open" in the retelling and draw no lid.
- Beat timing above runs long and needs trimming when the scene is built.
