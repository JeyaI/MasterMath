# 0022 The Twelve Pennies

## Puzzle
`dudeney-amusements-230`, The Twelve Pennies (Dudeney, public domain). Difficulty: `ms suggest` scored it 2/5; I agree (2/5): the moves are easy to try, and a viewer can nearly get it in the pause. Chosen because the figure is just a numbered circle of coins (no unseen illustration to guess at), the rules fit one clear sentence, the answer is checkable by search, and the "every jump makes one pair" idea gives a clean Level 2. Runner-up: `dudeney-amusements-334`, St. George and the Dragon (a knight's tour on 7x7 ending at the centre); it needs a long path with no single insight to teach. I passed over the top-ranked `dudeney-amusements-222` (A Railway Puzzle) because its figure is a diagram of circles and lines that the text does not describe.

## Hook
The circle of twelve numbered pennies pops in, then the text: **"Can you jump twelve pennies into six pairs in just six moves?"**

## Retelling
Twelve pennies sit in a circle, numbered 1 to 12. In one move you lift a single penny, jump it over exactly two other pennies (a pair counts as two), going either way round, and drop it on the penny just beyond. Empty places are skipped. After six moves the pennies must be in six pairs, on places 1 to 6.

## Insight
**Count what a jump does, then use the gaps.** Every jump turns two single pennies into one pair, so twelve singles need exactly six jumps. The work is the order: pennies 7 to 12 each leave their place and land on one of pennies 1 to 6. As pennies leave, the places they vacate are skipped, so later jumps reach across the gaps: 10 jumps over 9 and 8 to land on 6, and 9 jumps over the pair on 6 to land on 5. The verified solution is 12 to 3, 7 to 4, 10 to 6, 8 to 1, 9 to 5, 11 to 2. `verify.py` plays it move by move under the stated rules, checks that pairs end exactly on 1 to 6, and that each move lowers the number of occupied places by exactly one.

Animation: a ring of twelve coins with numbers. A counter beside it reads "singles: 12". Each jump is an arc over the two jumped coins (they flash), the mover lands on its target to make a stacked pair, and the counter drops by two. Vacated places show as faint empty outlines, so the viewer sees later arcs cross them. At the end a bracket marks places 1 to 6 with a ✓. For Level 2 the ring grows to 20 coins and the counter reads "singles: 20".

Different from the recent Shorts: I read `SCRIPT.md` of 0017 (waves of one colour in a letter swap), 0018, 0019, 0020 (grid area by subtracting triangles) and 0021 (twin bridges, shapes times names). Those are a swap order, a picture split into rotated pieces, a veneer dissection, area subtraction and a counting by symmetry. This one is a conserved count (each move removes one single pair's worth) plus a shrinking circle, a different idea from all five, although 0017 is also a moving-counter puzzle.

## Beats
1. (0-4 s) Hook: "Can you jump twelve pennies into six pairs in just six moves?"
2. (4-6 s) "Twelve pennies sit in a circle, numbered one to twelve."
3. (6-10 s) "In one move, you lift a single penny and jump it over two others." A demo arc.
4. (10-12 s) "It lands on the next penny, which makes a pair."
5. (12-15 s) "A pair counts as two pennies, and you can jump either way round."
6. (15-17 s) "The goal is six pairs, on places one to six." Places 1 to 6 are highlighted.
7. (17-22 s) "Pause and try it." 5 s countdown; the circle and rules stay in view.
8. (22-25 s) "Every jump turns two single pennies into one pair." Counter 12 to 10.
9. (25-28 s) "So twelve pennies need exactly six jumps, no more."
10. (28-30 s) "Pennies 7 to 12 will each jump onto one of the pennies 1 to 6."
11. (30-32 s) "Penny 12 jumps over 1 and 2, and lands on 3."
12. (32-34 s) "Penny 7 jumps back over 6 and 5, and lands on 4."
13. (34-37 s) "Empty places don't count, so penny 10 jumps over 9 and 8 to land on 6."
14. (37-39 s) "Pennies 8, 9 and 11 finish the job the same way."
15. (39-41 s) "Six jumps, six pairs, on places one to six ✓"
16. (41-44 s) "Level 2: now there are twenty pennies in the circle."
17. (44-46 s) "Same trick: what is the fewest number of moves to make pairs?"
18. (46-58 s) "Comment just the number ↓" held about 12 s.

Puzzle and solution take about 41 s; with Level 2 and the hold, about 58 s.

## Level 2
Twenty pennies in a circle, same kind of move. What is the fewest number of moves that turns all 20 into pairs? **Answer: 10.** Each move turns two singles into one pair, so 20 singles need 20 / 2 = 10 moves; `verify.py` also finds an actual 10-move solution by search, so it is achievable. No calculator needed.

## Music
`pachelbel-canon`: the least recently used piece (last used in 0016, 0010, 0004), warm and building, which suits the steady growth of pairs. Credit: Johann Pachelbel, Canon in D.

## Risks
- Dudeney's text says "passing it over two pennies" and the solution (9 to 5 jumps over the pair on 6) only works if a pair counts as two pennies; the retelling states this and `verify.py` encodes it. The jumped-over places may also be empty ones skipped; this is also encoded and stated on screen.
- The original figure is a numbered circle; I assume the numbers run clockwise from the top, matching the solution list, and only the adjacency matters.
- A move onto a pair, or lifting a penny from a pair, is not used; the retelling says "lift a single penny" and lands "on the next penny" (a single).
- The solution is one of several; the answer to Level 1 is "yes, and here is one way". The pause may show people other valid routes.
- Level 2's "fewest" rests on the count argument and a search that confirms 10 is reachable.
