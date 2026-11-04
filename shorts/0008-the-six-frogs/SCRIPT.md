# Script: 0008 The Six Frogs

Revised after the reviewer's comment (v1 → v2): the angle is now "can you do it in N moves?", with no proof on screen. Level 1 starts at 4 frogs (10 moves); Level 2 is the 6-frog original (21 moves). The "count the pairs" insight beat is gone; the payoff is watching the optimal solution play.

Video revision (v1 → v2): the pieces are now side-view cartoon frogs on lily pads (blink, hop, jump for joy), the top bar reads "Reverse the frogs!" / "Can you do it in 10 moves?", and the rules ("Frogs can move 1 or 2 squares to the empty square") stay on screen from the demo through the "Pause and try it" countdown (the likely thumbnail). Demo captions: "Slide: move 1 square", "Leap: over 1 frog".

## Puzzle
`dudeney-amusements-214`, The Six Frogs (Dudeney, *Amusements in Mathematics*, public domain). Dudeney himself says to start easy and add frogs, so 4 frogs first and the full 6 as Level 2 follows his own text.
Why: the catalog's first counters puzzle for us, with a count the code checks by brute-force search. The top of `ms suggest` is all dissections, which we have just done in 0001, 0002 and 0006.
Runner-up: `dudeney-amusements-245`, The Fly on the Octahedron (1,488 routes). Harder to show in 40 s.

## Hook
Pop in the row of four numbered frogs on five squares, one empty square on the left. Then the question in plain words: **"Can you reverse the frogs in 10 moves?"** Squares and frogs appear first, then the question.

## Retelling
Four frogs numbered 1 to 4 sit on a row of five squares, in order, with the empty square at the left end. A frog can slide into the next square if it is empty, or leap over one frog into an empty square just beyond. Frogs may go either way. Get them into the order 4 3 2 1, with the empty square still on the left. Can you do it in 10 moves? (10 is the fewest possible.)

## Insight
There is no proof beat. The Short asks "can you do it in 10?", gives a pause to try, then shows the solution, and says it is optimal (checked by exhaustive search in `verify.py`, so the claim is safe to make).

Animation: one frog-row, large. Dudeney's order (2 4 3 1, then 2 4 3 1, then 2 4) plays move by move, a slide as a hop along the row and a leap as an arc over the neighbour. A move counter ticks 1 to 10 in the corner. The counter and the row are the payoff: the viewer sees the frogs trade places in a rhythm (the evens go up the row, the odds come back) and ends on 4 3 2 1 with the counter at 10. A small tag marks each move as slide or leap but no totals are derived. Final text: "10 moves. The fewest possible ✓".

Recent Shorts checked (docstrings of `scene.py`): 0007 Seven Pigs (fences splitting a square, region counting), 0006 St George's Banner (bars lighting up and peeled-off overlap in an equation), 0005 Potato Puzzle (cuts adding pieces, 1+2+...+6). Also 0001, 0002 dissections. None uses moving pieces or a board position changing over time; this one is the first to animate a sequence of moves.

## Beats
1. "4 frogs, 1 empty square": the row builds in, numbers on the frogs. (3 s)
2. "Reverse them in 10 moves?": hook question, target row 4 3 2 1 ghosted beneath. (3 s)
3. "Slide or leap one frog": one demo slide, one demo leap with an arc. (4 s)
4. "Pause and try it": 5 s countdown. (5 s)
5. "Here is one way": the solution starts, counter at 1. (2 s)
6. "Evens go up, odds come back": moves 1 to 8 play, first pass 2 4 3 1 then again, counter ticking. (12 s)
7. "Last two: 2, then 4": moves 9 and 10 finish on 4 3 2 1. (3 s)
8. "10 moves. Fewest possible ✓": payoff. (3 s)
9. Level 2 card: 6 frogs on 7 squares, 21 moves, "How many of the 21 moves are leaps?", not solved. (4 s)
10. "Comment just the number ↓", held about 12 s.

Total: 3+3+4+5+2+12+3+3+4+12 = 51 s with the hold; about 39 s before the Level 2 card. If the preview runs long, shorten beat 6 (play moves faster).

## Level 2
Question: the full puzzle with 6 frogs on 7 squares, solved in 21 moves (optimal). How many of those 21 moves are leaps?
Answer: **15** (accept: 15, "fifteen", "15 leaps").
Why: no calculator needed. Only a leap changes which of two frogs is ahead, and every pair of the 6 frogs must trade places once: 6 × 5 ÷ 2 = 15 pairs, so 15 leaps, and the other 6 moves are slides. Verified in `verify.py`: the 21-move recipe plays legally and has 15 leaps, 6 slides. (Same trick as Level 1, one step further: the viewer can count leaps in the 4-frog solution, 6, and extend it.) This is not solved on screen, and the call to action promises nothing.
Note: the Level 1 answer on screen is a yes/no ("can you?"), so only Level 2 collects a number.

## Music
`bwv846` (Bach, Prelude in C): steady and unhurried, suits watching moves tick by. It is the least recently used key in `ms music` (last used by 0002); the last two used were `gymnopedie-1` (0006) and `k545` (0007).

## Risks
- The original figure is not in the text. We assume the empty square is on the left with frogs 1 to n in the next n squares. `verify.py` uses the layout in which Dudeney's own first move (frog 2 leaps frog 1) is legal; search then gives his counts (10 for 4 frogs, 21 for 6).
- "10 is the fewest possible" and "21 is the fewest" are both checked by exhaustive search, not by an argument on screen.
- Changing the Level 1 to 4 frogs means it's easier than Dudeney's six; the 10-move solution is short enough to try during the 5 s pause only partly, which is fine since the Short shows the answer next.
- The Level 2 question asks for the leap count rather than the move count, because the move count (21) is already stated. The viewer who has only watched the 4-frog solution has to reason or work out the 6-frog one; 15 is reachable by counting pairs, with no calculator.
- Frogs must stay distinguishable by number in a 1080-wide frame: five squares are comfortably big for numerals; the Level 2 card's seven squares are smaller but not played.
