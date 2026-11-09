# 0015 The Tube Inspector's Puzzle

## Puzzle
`dudeney-amusements-242`. Chosen because it has a single clean visual idea (count the lines at each station, then pair up the odd ones), a figure we can rebuild exactly as a 3 x 4 grid, an answer verified by brute force, and a natural Level 2. Runner-up: `dudeney-amusements-180` (The Four Sons), a nice dissection but hard to retell without the figure, and with a clumsy Level 2.

## Hook
On-screen text, after the network pops in: **"What is the fewest number of miles the inspector can travel to ride every line?"** (about 4 s)

## Retelling
A tube company has twelve stations laid out in a grid, three across and four down, with seventeen lines between neighbouring stations. Every line is one mile long. An inspector has to ride along every single line at least once, and he may start and finish at any station he likes. Riding each line once would be seventeen miles, but nobody seems to manage it. What is the fewest miles he must travel?

(The original gives distances in "if the stations are a mile apart" terms; we state it directly. Stations are lettered A to L row by row so the route can be shown in Dudeney's letters if wanted.)

## Insight
**Odd stations must be paired up.** Every time the inspector passes through a station he uses two of its lines (one in, one out), so a station with an odd number of lines always leaves one line unused-or-repeated. Only a start or an end can use up an odd line.

Animation: small dots sit on each station, one per line meeting there. Corners show 2 dots, the middle ones on the long sides show 3, the inner ones show 4. The six stations with an odd count (B, D, F, G, I, K) pulse red. Two of them (B and K) are marked START and END and turn green, because a walk may begin and end at an odd station. The other four, D, G and F, I, are joined in pairs: a glowing second line is drawn over the short line D-G and the short line F-I ("ride it twice"), and each pair's red turns green as the extra dot is added. All stations now show an even count except the start and end, and the route BADGDEFIFCBEHKLIHGJK is traced as a moving dot with a mile counter ticking 1 to 19.

Checked against: the `SCRIPT.md` files of 0008–0014, and the `short.yaml` insight for 0003 (Inspecting a Mine). 0008 (frogs), 0011 (sheep pens, matchsticks on a grid), 0012 (almonds), 0013 (rooks) and 0014 (quilt) use unrelated ideas. **0003 is the same underlying theory** (odd junctions, repeated passages), so the visual must differ: 0003 argues with "trapped" junctions (in, out, in) on a maze and counts needed repeats there. Here the picture is a dot-per-line parity tally at every station, red-to-green recolouring, and pairing neighbouring odd stations with a doubled line. The reviewer may still judge the overlap too close; this is the main risk.

## Beats
1. Hook: the 3 x 4 grid of stations pops in with all 17 lines, then the question. (4 s)
2. "Twelve stations are joined by seventeen lines, each a mile long." Line counter 17. (3.5 s)
3. "The inspector must ride along every single line." A dot rides one line and it glows. (3 s)
4. "He may start and finish wherever he likes." Start flag and end flag drop anywhere. (3 s)
5. "What is the fewest number of miles he can travel?" (2.5 s)
6. "Pause and try it" with a 5 s countdown. (6 s)
7. "Riding each line once would only be seventeen miles." (2.5 s)
8. "But every walk he tries ends up repeating some lines." A dot walks, gets stuck, repeated line flashes. (3 s)
9. "Let's count how many lines meet at each station." Dots appear at every station. (3 s)
10. "Six stations have an odd number of lines." The six pulse red. (2.5 s)
11. "He can only start or end a walk at an odd station." (2.5 s)
12. "Each time he passes through a station, he uses two of its lines." A dot passes through a 4-station: in and out lines light. (3 s)
13. "So two odd stations are the start and the end." B and K turn green. (2.5 s)
14. "The other four odd stations must be paired up." (2 s)
15. "Walking one short line twice fixes two stations at once." The D-G line doubles. (3 s)
16. "Two repeated lines fix all four, so the extra cost is two miles." F-I doubles. (3 s)
17. "That makes seventeen plus two, which is nineteen miles." Dot traces the route, counter to 19. (4 s)
18. "The shortest trip is 19 miles ✓" Caption added: a search shows nothing shorter. (2.5 s)
19. Level 2 card and "Comment just the number ↓", held about 12 s.

Total about 48 s with the Level 2 card.

## Level 2
Same rules on a 3 x 3 grid of 9 stations with 12 lines of 1 mile each. Fewest miles? **Answer: 14.** Why: the four middle-of-the-side stations are odd; two are the start and end, the other two are 2 miles apart, so repeating that route adds 2: 12 + 2 = 14. No calculator needed.

## Music
`fur-elise` (tense, mysterious; the least recently used key, and not used by 0010–0014's last few).

## Risks
- **Overlap with 0003** in the underlying parity idea (see Insight). The visual is different, but the reviewer should judge.
- The figure is not shown in the text; Dudeney's poster is a 3 x 4 grid, which we confirm from his own route (all 17 lines, with D-G and F-I the only lines used twice, are exactly the 3 x 4 grid; `verify.py` checks this). Station letters here run row by row; Dudeney's own labelling may differ, so the route letters in the video should be from our grid, or omitted.
- "Stations a mile apart" is retold as "each line is a mile long".
- The claim "fewer is impossible" is checked by brute force over all repeat sets, and depends on repeating a line more than once never helping (true for this graph; `verify.py` covers all single repeats).
