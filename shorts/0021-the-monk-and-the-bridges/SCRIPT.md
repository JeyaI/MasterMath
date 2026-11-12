# 0021 The Monk and the Bridges

## Puzzle
`dudeney-amusements-261`, The Monk and the Bridges (Dudeney, public domain). Chosen because it is a clean counting puzzle with a figure that is easy to redraw (three places, five bridges), a single visual idea, and a natural Level 2. Runner-up: `dudeney-amusements-255`, The Level Puzzle (80 ways), rejected because its letter grid is hard to reconstruct from the text alone.

## Hook
The map pops in (monk bank, island, monastery bank, five bridges), then the text: **"Can you count the routes that cross all five bridges exactly once?"**

## Retelling
A monk is on one bank of a river and wants to walk home to his monastery on the other bank. There is an island in the middle. Two bridges join his bank to the island, two join the island to the monastery's bank, and one bridge crosses the river directly. On the way home he will cross every bridge exactly once. How many different routes could he choose?

## Insight
**Twin bridges: count the shapes, then the names.** Two bridges in each pair are interchangeable as far as the walk goes. Look only at the places he visits (M, I, Y) and there are just four shapes of walk: M-I-M-Y-I-Y, M-I-Y-I-M-Y, M-I-Y-M-I-Y and M-Y-I-M-I-Y. Each shape can then be named in 2 x 2 ways (which twin is a or b, which is c or d), so 4 x 4 = 16. `verify.py` brute-forces all orderings, matches Dudeney's printed list of 16, and checks that swapping twins always gives another route with the same places visited.

Animation: the monk's dot walks each shape along the map with an unlabelled thick trail, and the four shapes stack as small thumbnails down the side. Then the first shape is picked up, and the twin pair a/b flips its labels (two versions side by side), then c/d flips (four versions in a 2 x 2 grid). The grid fills each thumbnail in turn and a counter climbs 4, 8, 12, 16.

Different from the recent Shorts: I read the `SCRIPT.md` of 0020 (grid area by subtracting triangles) and the Insight headings of 0018 and 0019 (a picture split into four rotated pieces; a veneer dissection). This one is graph counting with a symmetry / multiplication idea, not a dissection or area argument.

## Beats
1. (0-4 s) Hook: "Can you count the routes that cross all five bridges exactly once?"
2. (4-6 s) "A monk wants to walk home to the monastery." The monk walks onto his bank.
3. (6-10 s) "Two bridges lead to the island, two lead off it, and one crosses the river." The bridges draw in pair by pair.
4. (10-12 s) "He must cross every bridge once, and only once."
5. (12-14 s) "How many different routes could he take?"
6. (14-19 s) "Pause and try it." 5 s countdown.
7. (19-22 s) "Every route has to start at the monk and end at the monastery."
8. (22-24 s) "Let's call the bridges a, b, c, d and e." Labels appear.
9. (24-27 s) "The two bridges in each pair are twins, so ignore their names for now." Labels fade; twins tinted alike.
9b. (about 2 s) "Let's redraw it as a simple map: three places, joined by five bridges." The river picture (bank, river, island, monastery, five real bridges, used from the hook on) turns into the M / I / Y graph. Added after the reviewer asked for real bridges before the graph.
10. (27-31 s) "Looking only at the places he visits, there are just four different shapes." The four shapes are traced.
11. (31-33 s) "In every shape, the first pair of twins can be named in two ways."
12. (33-35 s) "The second pair of twins can be named in two ways too."
13. (35-37 s) "So each shape gives 2 times 2, which is 4 routes."
14. (37-40 s) "Four shapes times four names makes 16 routes ✓"
15. (40-44 s) "Level 2: the same river, but with six bridges and a walk back to the start."
16. (44-46 s) "Same trick: how many routes are there now?"
17. (46-58 s) "Comment just the number ↓" held about 12 s.

The puzzle and solution (beats 1-14) take about 40 s; with the Level 2 card and the hold the Short is about 58 s. If the preview runs long, merge beats 11-13 into one.

## Level 2
A monk starts on his bank, M. Two bridges join M to an island, two join the island to the far bank, and two more join M directly to the far bank. He crosses all six bridges exactly once and finishes back at M. How many routes? **Answer: 64.** Ignoring which twin is which there are 8 shapes of walk, and each of the three twin pairs can be named in 2 ways, giving 8 x 8 = 64 (computed in `verify.py`). No calculator needed: 8 x 8.

## Music
`fur-elise`: least recently used, and its mildly tense mood suits a wandering puzzle. Last used in 0015, 0009 and 0003. Credit: L. van Beethoven, Für Elise, WoO 59.

## Risks
- Dudeney's original figure is a sketch of a river, island and bridges; we redraw it as a clean map, which is fine because it is just three places and five lines.
- "Routes" counts the order of bridges, so a route is a sequence of the five bridges; reversing a route is not allowed since the walk must go from the monk to the monastery. The retelling says so by stating start and end.
- Level 2 asks the viewer to find 8 shapes, which is more work than 4; a viewer who simply multiplies by 8 without counting shapes will need to find all 8. If the reviewer thinks that is too hard, drop to a variant with only two twin pairs and a start-and-return walk (1 shape, 4 routes), which is too easy, so this is the middle option.
- The first-bridge split (6 + 6 + 4) is verified in code and could be shown as an alternative way to count.
