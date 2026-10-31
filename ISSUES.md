# Issues

The software backlog. Add items freely; one line is enough. Work them with `/work-issue` in Claude Code (see OPERATING.md).

- **status:** `open` · `doing` · `blocked` · `done`
- **priority:** `P1` now · `P2` soon · `P3` someday
- **type:** `bug` · `feature` · `content` · `chore`

Next id: **21**

## Open

### #3 · Link 0001 to its catalog puzzle
status: open · P2 · content
The Greek-cross-to-square dissection has no number of its own: Dudeney gives it in the unnumbered article before #142 (his Fig. 39), and the parser drops those articles. The closest entry is `dudeney-amusements-142` (The Silk Patchwork), which cites it and asks the reverse. Decide whether that is the right link, then set `catalog_id` in `shorts/0001-greek-cross/short.yaml`, so the selector never suggests it again. Update `source.credit` and the `LICENSES.csv` note.

### #5 · Scrape The Canterbury Puzzles
status: open · P2 · feature
`dudeney-canterbury` is registered but untested. Its headings may be mixed case and grouped by story section; check the parser and the section-to-tag rules in `mathshorts/catalog.py`.

### #6 · Sam Loyd's Cyclopedia of Puzzles as a source
status: open · P3 · feature
Very visual, believed public domain (1914). Not on Gutenberg as clean text; find a usable transcription and confirm its status before adding.

### #7 · AI scoring of visual potential
status: open · P3 · feature
Replace the keyword heuristic with an Anthropic API call per puzzle (key from env). It writes `scored_by: ai` and never overwrites `human`. Run on demand: `ms sources score <src>`.

### #8 · Show a puzzle's original figure while drafting
status: open · P3 · feature
`ms show <id> --figure` fetches the matching illustration from the HTML edition into `out/figures/`, so Claude Code can look at it when recreating the figure. In the text edition a figure can sit above its heading (e.g. #71), so 63 puzzles end in a placeholder that may belong to the next puzzle. Match by position in the HTML, not by the text placeholder.

### #9 · Automate uploads
status: open · P3 · feature
YouTube Data API `videos.insert` with a scheduled publish time, after `ms batch`. API projects created after July 2020 upload locked-private until they pass Google's audit, so apply for the audit first. Until then, upload manually.

### #10 · `ms answers`: find the first correct comment
status: open · P3 · feature
For published Shorts, read comments via the API (`commentThreads.list`), find the earliest one containing a value in `level2.accept`, and print its link plus a drafted reply. Pinning stays manual.

### #11 · Local GUI
status: open · P3 · feature
A `ms gui` local web app: inbox with video player and "note at current time" button, a pipeline board, copy buttons for the upload kit. Deferred; the CLI comes first.

### #12 · Track per-Short performance
status: open · P3 · feature
Record viewed-vs-swiped-away and average % viewed per Short (entered by hand, or via the YouTube Analytics API later), and use them to suggest `tag_weights` changes.

### #13 · Phase 2: nightly batch in the cloud
status: open · P3 · chore
Run the same Docker image on a schedule (GitHub Actions, or a t3.small; t3.micro's 1 GB is tight for LaTeX). Put `out/ready/` behind a small storage interface so it can be object storage. Note: AWS's free tier for new accounts is credit-based, about 6 months.

### #14 · Grow the component library
status: open · P3 · feature
Add to `lib/components.py` as Shorts need them: dot grid, area model, number line, probability tree, angle marker, a "yesterday's answer" banner (optional).

### #15 · Beat previews start cold
status: open · P3 · chore
`ms preview --at` renders from the start of the beat. Consider including the last second of the previous beat for context.

### #16 · Visual scores are bunched at the top
status: open · P3 · chore
On the real catalog the heuristic gives 175 of 430 puzzles 5/5, because the has-figure and keyword bonuses stack on high section scores, so `ms suggest` barely separates them. Rebalance the bonuses (or let #7 replace them).

### #17 · Native batch can't find manim when run via `MS_BIN`
status: open · P2 · bug
With `MS_BIN=~/.venvs/mathshorts/bin/ms` and the venv not on PATH (as under a scheduler), `render.manim` looks `manim` up on PATH and every Short fails with `[Errno 13] Permission denied: 'manim'`. Run the `manim` next to `sys.executable`, and fix the scheduler lines in OPERATING.md if needed: `bash -lc` doesn't activate the venv either.

### #18 · Final mix measures -16 LUFS, not the -14 target
status: open · P3 · bug
`render.mix` asks loudnorm for -14 LUFS, but ebur128 measures -16.0 on 0001's final, both native and in Docker. Likely single-pass loudnorm on a quiet track. Try two-pass, or confirm that -16 is acceptable and change the target.

## Done

### #20 · More classical music, chosen per Short
status: done · 2026-10-31
`lib/audio.py` now has a six-piece `PIECES` library, and `music.piece` selects from it, defaulting to an unchanged BWV 846. Batch fails early on an unknown key, `ms approve` requires the exact `Music: <credit>` line, `ms music` lists use and writes WAVs, and `/draft-short` pitches a piece. Notes were checked against Mutopia scores; checked end to end in a throwaway batch.

### #19 · Thumbnail PNG in the upload kit
status: done · 2026-10-31
`ms batch` now writes `thumbnail.png` to the kit, the frame 0.1 s before the "Pause and try it" beat, using beats recorded during the final render, not `out/preview`. A Short with no such beat is marked `failed`. `upload.txt` and OPERATING.md mention it; checked on 0001 and 0002 in a throwaway batch.

### #2 · 0001's Level 2 needs a calculator
status: done · 2026-10-31
Level 2 is now "What's the slope of the yellow cut?" (answer 1/2; accept 1/2, 0.5, .5), checked in `verify.py`; `short.yaml` updated and re-rendered.

### #4 · Confirm the Docker image builds and renders on WSL
status: done · 2026-10-31
No-cache build works (about 7 min, 3 GB); `nightly.sh` rendered 0001 to `ready` in throwaway clones on `/mnt/c` and on WSL's own filesystem, identical streams on both, `out/` owned by the host user. Against native: same format, duration and layout, but not bit-identical (Inter 4.1 vs 3.19, SSIM 0.985). Fixed `nightly.sh` silently skipping its commit when the working directory went stale on `/mnt/c`; it now retries and exits non-zero on failure.

### #1 · Check the Dudeney parser against the real Gutenberg file
status: done · 2026-10-31
Ran on the real #16713: now 430 puzzles and 429 solutions (#163 has none in the book), up from 326; fixed misprinted and period-less headings, the index leaking into #430, figure flags and section tags, and added `tests/fixtures/dudeney_excerpt.txt`.

### #0 · Split the pipeline into modules
status: done · 2026-10-31
Catalog (sources, annotations), selector (`ms suggest`), drafting (`/draft-short`, notes, beat previews, compare), nightly batch with failure isolation and upload kits, morning commands, OPERATING.md and this file.
