# 0018 The Grand Lama's Problem

## Puzzle
`dudeney-amusements-291`, Dudeney, *Amusements in Mathematics* no. 291 (public domain). Chosen because the answer is a single picture (four identical hooks), the figure is a simple 8 x 8 board, the cut is checkable in code, and it is a different kind of dissection from the recent Shorts (no rearranging, and no counting ladder). Runner-up: `dudeney-amusements-159`, The Square of Veneer (two squares from one, with nails to avoid): needs a fractional-side argument that is heavy for 40 s.

## Hook
The 8 x 8 golden board pops in with four gems on the diagonal, then the question:
"Can you cut this board into four identical parts, one gem in each?"

## Retelling
A Grand Lama owns a golden chessboard with four gems set in the squares of its diagonal, the first four from one corner. He orders four priests to cut the board, along the lines between squares, into four parts of exactly the same size and shape, so that every part holds exactly one gem. (The old story is trimmed: no tournament, no beheadings.)

## Insight
**One hook, turned a quarter turn at a time.** Because the gems are crowded together, the "obvious" cuts fail: four quarters put two gems in one quarter, and four strips do too. The animation tries those two first, each flashing red where two gems share a part. Then one long hook is drawn from the first gem: down the edge, along the bottom, and a small curl. A ghost copy of this hook turns a quarter turn, slides across, and lands exactly on the second shape, which is filled in. The ghost does it twice more, so the board fills up with four hooks, a quarter turn apart. Each piece gets its own colour and the piece's squares counter reads 16.

`verify.py` takes Dudeney's picture, finds the four pieces, checks that each has 16 squares and one gem, and that the maps from piece 1 to pieces 1 to 4 are: same, turn 90, turn 180, turn 270.

Checked against: the `SCRIPT.md` of 0014 (quilt: squares built up one by one), 0015, 0016, 0017 (waves of one colour on a ring), and the recent retellings of 0013 (rooks, a counting ladder). Also the cut-and-move shapes of 0001 (Greek cross) and 0006 (banner): there pieces are cut then rearranged into a different figure. Here nothing is rearranged into a new figure; the only motion is a ghost copy turning to prove the pieces are identical. I did not re-read the scene docstrings of 0002 to 0005.

## Beats
1. Hook: board and gems pop in; "Can you cut this board into four identical parts, one gem in each?" (4 s)
2. "A Grand Lama has a golden chessboard with four gems." gems sparkle (3 s)
3. "The gems sit in a row along the diagonal." a line runs through them (2 s)
4. "Cut along the lines into four parts of the same size and shape." sample cut lines sketch, fade (3 s)
5. "Every part must hold exactly one gem." (2 s)
6. "Pause and try it." with the 5 s countdown (5 s)
7. "Cutting it into four quarters puts two gems together." quarters, two gems flash red (3 s)
8. "Straight strips fail too, so the parts must bend." strips, flash red (3 s)
9. "Start with a long hook that wraps around the first gem." the first hook fills in (4 s)
10. "Turn the hook a quarter turn, and it fits around the next gem." ghost copy turns and lands on piece 2 (4 s)
11. "Turn it again and again, until the board is full." pieces 3 and 4 (4 s)
12. "Four identical hooks of 16 squares, one gem each ✓" payoff (3 s)
13. "Level 2: a 10 by 10 board is cut into 5 equal parts." (3 s)
14. "How many squares does each part hold?" (2 s)
15. "Comment just the number ↓" held about 12 s

The beats before the final hold add up to 4+3+2+3+2+5+3+3+4+4+4+3+3+2 = 45 s, then the 12 s hold.

## Level 2
"The Grand Lama's next board is 10 by 10, and he wants it cut into 5 parts of exactly the same size and shape. How many squares does each part hold?" Answer: **20**. Why: 100 squares shared equally by 5 parts. Yes, such a cut exists (`verify.py` builds and checks one: 5 identical pieces tiling the 10 x 10 board), so the question is well posed. (Reviewer asked whether Level 2 is possible; it is, and the answer is checked in code.) (Same idea as the main puzzle, equal parts must share the squares equally, one step further; no cutting needed.)

## Music
`gymnopedie-1`, the least recently used key (0012, 0006), slow and sparse for a quiet puzzle.

## Risks
- The figure: Dudeney's picture is ASCII in our source; I transcribed the shading into `verify.py` and the code confirmed it is a valid answer. The gems in the original are drawn on the diagonal in the first four squares; the scene must recreate that.
- "Same shape" includes turning, which is how Dudeney's pieces relate here; none needs a mirror flip. Say "turn", never "flip".
- Rotation is about each piece, not the board centre: the ghost turns and then slides. Do not show it spinning around the board centre.
- The solution is not claimed to be unique, and the video does not say so.
- Level 2 is plain division and may feel easy for a 10 x 10 board; if the reviewer wants more bite, try "12 by 12 into 9 parts" (16).
