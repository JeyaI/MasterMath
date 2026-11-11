# 0020 The Yorkshire Estates

## Puzzle
`dudeney-amusements-189`, Dudeney, *Amusements in Mathematics*, no. 189. Chosen because one picture solves it (a grid and a subtraction), the answer is an exact whole number, and the figure is easy to recreate. Runner-up: `dudeney-amusements-180` (The Four Sons), whose answer is a dissection that is hard to state as a single checkable number.

## Hook
"How many acres is the triangle between these three square estates?" The three squares and the triangle pop in first, then the question appears.

## Retelling
Three square estates touch corner to corner, and a small triangle of land is left in the gap between them. The estates cover 370, 116 and 74 acres. How many acres does the triangle in the middle cover?

## Insight
**Every square's area is a sum of two squares, so every side of the triangle is a whole number of grid steps across and down.** 370 = 17² + 9², 74 = 7² + 5², 116 = 10² + 4². The triangle's corners then land on grid points, even though its side lengths are not whole numbers. Draw the big right triangle (17 by 9) around it and subtract what is not the triangle: two small corner triangles and a rectangle. 76.5 − 17.5 − 20 − 28 = 11.

Animation: each square is shown with its side drawn as a staircase (across, then down), so the viewer sees the hypotenuse as a diagonal of a 17 by 9 box. The triangle then sits on the grid. The big triangle fills with a colour, and the pieces to remove (the two corner triangles and the rectangle) slide out one at a time with their areas shown as a running subtraction. The leftover glows as the answer.

Checked against recent Shorts: I read the `SCRIPT.md` Insight sections of 0015 (parity of odd stations), 0016 (calculus on a box volume), 0017 (waves of one colour), 0018 (four rotated pieces on a grid) and 0019 (13×13 grid dissection). None uses "build a box and subtract the pieces". 0019 also uses a grid, but as a dissection into pieces that slide, not as an area subtraction.

## Beats
1. (0–4 s) Squares and triangle pop in. Caption: "How many acres is the triangle between these three square estates?"
2. (4–9 s) "The three squares meet corner to corner and enclose a small triangle."
3. (9–14 s) Labels appear on the squares. "The estates cover 370, 116 and 74 acres."
4. (14–17 s) "How many acres does the triangle in the middle cover?"
5. (17–23 s) "Pause and try it." with the 5 s countdown.
6. (23–28 s) Squares tilt-reveal their sums. "Each square's area is a sum of two squares, so look for whole numbers."
7. (28–32 s) "370 is 17 squared plus 9 squared, so that side goes 17 across and 9 down."
8. (32–35 s) "74 is 7 squared plus 5 squared, and 116 is 10 squared plus 4 squared."
9. (35–37 s) "Now every corner of the triangle sits on a grid point."
10. (37–40 s) "Start with the big right triangle: half of 17 times 9 is 76 and a half."
11. (40–43 s) "Take away the two small corner triangles, 17 and a half and 20."
12. (43–45 s) "Take away the 7 by 4 rectangle, which is 28 acres."
13. (45–48 s) "What is left is the triangle: 76.5 minus 65.5 is 11 acres ✓"
14. (48–54 s) Level 2 card. "Level 2: squares of 26, 20 and 18 acres meet round a triangle." then "Same trick: how many acres is the triangle?"
15. (54–66 s) "Comment just the number ↓" held about 12 s.

About 48 s up to the payoff, and about 66 s with the Level 2 card and the 12 s hold. If it runs long, merge beats 11 and 12 and shorten beat 2.

## Level 2
Question: squares of 26, 20 and 18 acres meet round a triangle. How many acres is the triangle? Answer: **9**. Why: 26 = 1 + 25, 20 = 4 + 16, 18 = 9 + 9, so the corners are (0,0), (5,1), (2,4) on a grid. The 5 by 4 box (20) minus corner triangles of 2.5, 4.5 and 4 leaves 9. `verify.py` checks the corners, the unique two-square splits and the answer, including Dudeney's quarter-root formula as a second method.

## Music
`bwv846` (Bach, Prelude in C): steady and unhurried, first in the `ms music` list. The latest Shorts used k545, gymnopedie-1, minuet-g, pachelbel-canon and fur-elise.

## Risks
- Dudeney's figure shows the estates' arrangement; we must recreate it: A on AB (370), B on CB (116), C on AC (74). The book's labels are confusing (the triangle's corners are also called A, B, C), so the video should label the squares by area only.
- The grid trick only works because each area splits into two squares in one way, and the triangle's vertex positions must be drawn exactly (A (0,9), B (17,0), C (7,4)). The squares on the sides stand outward from the triangle.
- 370 can be written as a sum of two squares in two ways (17² + 9² and 19² + 3²); the video uses 17 and 9, the pair that makes the three sides close into a triangle, and `verify.py` checks that these legs fit all three sides at once. Say so lightly, if at all, or a viewer may try 19 and 3.
- The Level 2 numbers have unique two-square splits, so there is no ambiguity.
