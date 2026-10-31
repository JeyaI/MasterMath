# Issues

The software backlog. Add items freely; one line is enough. Work them with `/work-issue` in Claude Code (see OPERATING.md).

- **status:** `open` · `doing` · `blocked` · `done`
- **priority:** `P1` now · `P2` soon · `P3` someday
- **type:** `bug` · `feature` · `content` · `chore`

Next id: **16**

## Open

### #1 · Check the Dudeney parser against the real Gutenberg file
status: open · P1 · chore
`ms sources add dudeney-amusements` was built against a fixture: the workspace it was written in couldn't reach Gutenberg. Run it on the real file and check: about 430 puzzles, solutions attached to the right numbers, sections look right (e.g. "Greek Cross Puzzles"), figure flags make sense. The puzzle heading format (`1.--A POST-OFFICE PERPLEXITY.`) is confirmed; the SOLUTIONS layout is not. Fix the parser if needed and add a short real excerpt to `tests/fixtures/`.

### #2 · 0001's Level 2 needs a calculator
status: open · P1 · content
θ = arctan(1/2) ≈ 26.57° can't be worked out from what the video teaches. Change Level 2 to "What's the slope of the yellow cut?" (answer 1/2; accept 1/2, 0.5, .5), add the check to `verify.py`, update `short.yaml`, re-render. 0001 is `ready`, so start with `ms reject 1 "Level 2: switch to slope"`.

### #3 · Link 0001 to its catalog puzzle
status: open · P2 · content
After #1, find the Greek-cross-to-square puzzle in the catalog and set `catalog_id` in `shorts/0001-greek-cross/short.yaml`, so the selector never suggests it again. Update `source.credit` with the puzzle number.

### #4 · Confirm the Docker image builds and renders on WSL
status: open · P2 · chore
`docker build -t mathshorts .`, then `MS_USE_DOCKER=1 scripts/nightly.sh` on an approved test Short. Check file ownership in `out/`, and that the output matches the native render.

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
`ms show <id> --figure` fetches the matching illustration from the HTML edition into `out/figures/`, so Claude Code can look at it when recreating the figure.

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

## Done

### #0 · Split the pipeline into modules
status: done · 2026-10-31
Catalog (sources, annotations), selector (`ms suggest`), drafting (`/draft-short`, notes, beat previews, compare), nightly batch with failure isolation and upload kits, morning commands, OPERATING.md and this file.
