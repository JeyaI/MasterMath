# 0017 The Twickenham Puzzle: script

## Puzzle
`dudeney-amusements-217`, The Twickenham Puzzle (Dudeney, public domain). Chosen because the wording is fully self-contained (every letter's disc is given, so no figure is needed beyond a ring we draw ourselves), the answer is checkable by exhaustive search, and the first Dudeney "moving counters" puzzle we have not done. Runner-up: `dudeney-amusements-234`, The Exchange Puzzle (needs the starting figure, which the text does not give).

## Hook
A ring of 11 discs pops in with the ten lettered counters. Text: **"What is the fewest number of moves that spells TWICKENHAM?"** (about 4 s)

## Retelling
Eleven discs sit in a ring, the bottom one empty. Five white counters and five black counters carry the letters of TWICKENHAM, scrambled. Black counters only travel clockwise and white ones only anticlockwise. On a move, a counter either steps into the empty disc beside it, or jumps over one counter of the other colour into the empty disc. Rearrange them so that, reading clockwise from the disc after the empty one, they spell TWICKENHAM, with the empty disc back at the bottom. What is the fewest number of moves?

Start, clockwise from the empty bottom disc: C E H M I N A T W K. White (black letters): I M H E C. Black (white letters): N A T W K.

## Insight
**The moves come in waves of one colour.** Dudeney's 26 moves split into runs of the same colour: black 1 (K), white 2 (C E), black 3 (K W T), white 4 (C E H M), black 5 (K W T A N), white 5 (C E H M I), black 1 (K), white 4 (C E H M), black 1 (T). That is 1, 2, 3, 4, 5, 5, 1, 4, 1 = 26.

Animation: the ring is drawn large; the empty disc is a dashed outline. Each wave plays as a quick run of hops (steps slide along the ring, jumps arc over the neighbour) and the counters of the moving colour glow while the other colour stays dim. A bar strip beside the ring grows one block per wave, the block's length equal to the wave's size and its colour the wave's colour (so the strip reads 1, 2, 3, 4, 5, 5, 1, 4, 1), with a move counter ticking up to 26 beneath it. At the end the letters sit on TWICKENHAM and "26" lands. `verify.py` replays Dudeney's moves legally, confirms the waves, and runs a breadth-first search over all positions to show 26 is the fewest.

Checked against: `SCRIPT.md` of 0013, 0014, 0015, 0016 (counting ladder, square packing, odd-degree tags, calculus), and 0008 (six frogs), the nearest in subject: that one plays a line of frogs with a move counter and a "slide / leap" tag, with no structure drawn. Here the ring, the colour waves and the growing bar strip of wave sizes are the picture. I did not re-read the scene docstrings of 0001-0012 beyond 0008, 0011 and 0012 (almonds, a jump-chain count), none of which shows alternating colour runs.

## Beats
1. Hook: ring pops in with counters; "What is the fewest number of moves that spells TWICKENHAM?" (4 s)
2. "Ten counters sit on a ring of eleven discs." Discs and counters build in, the empty bottom disc dashed. (4 s)
3. "Black counters move clockwise, white ones move anticlockwise." Arrows around the ring in each colour. (4 s)
4. "A counter can step into the empty disc." One demo step (K). (3 s)
5. "Or it can jump over a counter of the other colour." One demo jump (C over K), then reset. (4 s)
6. "Spell TWICKENHAM clockwise, with the empty disc back at the bottom." The target word appears around the ring as ghost letters. (4 s)
7. "Try to find the shortest way." / "Pause and try it" with a 5 s countdown. (5 s)
8. "Watch how the moves come in waves of one colour." Strip appears. (3 s)
9. "First one black counter moves, then two white ones." Waves 1 and 2. (4 s)
10. "Then three black counters, then four white ones." Waves 3 and 4. (4 s)
11. "Then a wave of five black counters, and one of five white." Waves 5 and 5. (4 s)
12. "Three short waves finish the word: one, four, and one." Waves 1, 4, 1. (4 s)
13. "TWICKENHAM, in 26 moves ✓" Counter at 26, strip sum 1+2+3+4+5+5+1+4+1. (3 s)
14. "26 is the fewest possible." Short note, search checked in code. (2 s)
15. "Level 2: 4 white and 4 black counters on 9 discs must swap sides." The 9-disc ring builds. (4 s)
16. "How many moves does it take?" (2 s)
17. "Comment just the number ↓" held about 12 s.

Seconds are rough and tighten when animated: beats 2-6 overlap the building animation (about 14 s together), the wave beats 9-12 take about 12 s, so the content is about 45 s, plus the 5 s countdown (beat 7) and the 12 s hold (beat 17), about 60 s in all. If it runs long, merge beats 4 and 5 into one demo.

## Level 2
**Same rules on a ring of 9 discs, the bottom one empty. 4 white counters sit on one side and 4 black ones on the other. Swap the two colours' places, with the empty disc staying at the bottom. What is the fewest number of moves?** Answer: **24**. Why: every white counter must get past every black one, one jump each: 4 x 4 = 16; each of the 8 counters also needs one plain step: 8 more; 16 + 8 = 24. (The waves are 1, 2, 3, 4, 4, 4, 3, 2, 1.) Checked by search in `verify.py`, and the pattern k(k+2) holds for k = 1..5. No calculator needed.

## Music
`minuet-g` (Petzold, Minuet in G, BWV Anh. 114; light, dancing): the least recently used key in `ms music`; the last few used were bwv846 (0014), fur-elise (0015) and pachelbel-canon (0016).

## Risks
- **Where the word starts.** The text says "spell Twickenham in a clockwise direction, leaving the vacant disc in the original position". We read it as starting at the disc just after the empty one (T right after the gap), which is Dudeney's 26-move answer. The word starting one disc earlier (split across the gap) can be done in 25, but it does not spell the word in one run; the statement says "read clockwise from the disc after the empty one" to remove the doubt. `verify.py` notes this.
- **Figure.** We must recreate the ring and the letter positions. We read the circled single parentheses `( )` as white counters and double `(( ))` as black from the text figure; the moves in Dudeney's solution replay legally only with this reading, which `verify.py` checks.
- **Level 2 and the insight.** The Level 2 answer follows from the "every white passes every black" count more directly than from the wave sizes; the video does not solve it, and the `why` gives both.
