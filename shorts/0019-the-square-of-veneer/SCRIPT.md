# 0019 The Square of Veneer

## Puzzle
`dudeney-amusements-159`, *Amusements in Mathematics* no. 159 (public domain). Chosen because the whole solution is one clean picture (a 13 by 13 grid, 169 = 144 + 25, then cut-and-slide), every piece sits on whole grid cells so `verify.py` can check it exactly, and the nails add a little twist at the end. It also has a natural Level 2 (the same 5-12-13 trick, doubled). Runner-up: `dudeney-amusements-156` (The Dissected Triangle), whose cuts would need a numerical search to recreate.

## Hook
A 5 inch square board with a grid of 16 nails pops in, then the question: **"Can you cut this square into four pieces that make two squares?"**

## Retelling
A square board is 5 inches on a side and marked in a one-inch grid. At each of the 16 inner crossings a nail has been driven in, and the saw must not touch any of them. Cut the board into four pieces that fit together to make two squares of different sizes. What are the exact sides of the two squares?

(Dudeney asks for the fewest pieces; we state four and do not claim that fewer is impossible.)

## Insight
**Re-grid the board as 13 by 13, because 169 = 12² + 5².** The board is redrawn with a 13 by 13 grid of small squares (each 5/13 inch) fading over the nails. A counter shows 169, then splits into 144 + 25. The 5 by 5 block in the bottom-right corner lifts out whole. The L-shape that is left is cut along grid lines into a three-step staircase (B), a two-step staircase (C) and a thin strip (D). C slides down and left into the gap, D turns upright and slides in beside it, and the 12 by 12 square closes with no gap. Finally the nails fade back in over the cuts: the cut lines are at multiples of 5/13 inch, which are never whole inches, so none touches a nail. Sides: 5 × 5/13 = 25/13 and 12 × 5/13 = 60/13.

Checked against: the `SCRIPT.md` files of 0014 to 0018, and the `scene.py` docstrings of 0001 (Greek cross), 0002 (crescent) and 0006 (banner). 0014 (quilt) packs squares of different sizes into one square and 0018 (Grand Lama) uses rotated copies of one hook; 0001, 0002 and 0006 are cut-and-rearrange dissections of one figure, but none of them uses a "sum of two squares" counting step to choose the cut, none moves pieces by slides on a lattice, and none has the obstacle of nails. The risk of overlap with the earlier Greek cross dissection is the "cut and rearrange" motion; the numbers-first idea (169 = 144 + 25) is new.

## Beats
1. Hook: the board and nails pop in, "Can you cut this square into four pieces that make two squares?" (4 s)
2. "This 5 inch board has 16 nails, and the saw must not touch any." The nails highlight one by one. (3.5 s)
3. "The four pieces must fit together into two perfect squares." A ghost of two squares of different size appears beside the board. (3 s)
4. "What are the exact sides of the two squares?" (2.5 s)
5. "Pause and try it." with a 5 s countdown. (6 s)
6. "Slice the board into a 13 by 13 grid of small squares." The grid draws in. (2.5 s)
7. "Notice that 169 is 144 plus 25, which is 12 squared plus 5 squared." The counter splits. (3.5 s)
8. "So cut a 5 by 5 square out whole; the rest must become 12 by 12." The corner square lifts out, leaving an L. (3 s)
9. "Cut the L into two staircases and one thin strip." The cuts glow along grid lines, three colours. (3 s)
10. "Slide the staircase down, stand the strip upright, and it all fits." Pieces move into a 12 by 12 square. (3.5 s)
11. "The grid lines are 5/13 inch apart, so no cut ever meets a nail." The nails return, all clear of the cuts. (3 s)
12. "Each small square is 5/13 inch: the sides are 25/13 and 60/13 ✓" (3.5 s)
13. "Level 2: a 26 cm square is cut the same way." (2.5 s)
14. "It makes two squares with whole number sides. How long is the larger side, in cm?" (3 s)
15. "Comment just the number ↓" held (12 s)

Total: the beats before the hold add up to about 46 s (hook 3.5 s included), and the 12 s hold brings the Short to about 58 s. This is over the 40 to 50 s target, so if the preview runs long, shorten beats 9 and 11 first.

## Level 2
"A 26 cm square board is cut the same way into two squares whose sides are whole numbers of centimetres. What is the side, in cm, of the larger square?" Answer: **24**. Why: 26 is twice 13, so the 5-12-13 cut doubles to 10 and 24 (100 + 576 = 676 = 26²). It is the only way to write 26² as two whole squares, which `verify.py` checks. Not solved in the video. No calculator needed.

## Music
`k545`, Mozart's Piano Sonata in C. It is the least recently used key (last used by 0013 and 0007), and its bright, quick feel suits a tidy cut-and-slide.

## Risks
- Dudeney's puzzle asks for the fewest pieces; we say "four" and do not claim a proof of minimality (he does not prove it either).
- The figure is not in the text. We recreate Dudeney's cuts by reading his ASCII solution diagram; `verify.py` confirms that the transcribed pieces tile the 13 by 13 board, that three of them (with one slide-and-turn each) tile a 12 by 12 square, and that no nail touches a cut. The slide for C and the turn for D are ours, not read from the book.
- The nails are drawn on the one-inch grid of the 5 inch board; when the 13 by 13 grid overlays it the nails fade so the picture is not cluttered.
- Level 2 assumes the same cut scaled; the video keeps it unsolved.
