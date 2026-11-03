# Issues

The software backlog. Add items freely; one line is enough. Work them with `/work-issue` in Claude Code (see OPERATING.md).

- **status:** `open` · `doing` · `blocked` · `done`
- **priority:** `P1` now · `P2` soon · `P3` someday
- **type:** `bug` · `feature` · `content` · `chore`

Next id: **37**

## Open

### #33 · `ms check` misses mid-animation faults
status: open · P3 · feature
It samples the screen at the end of each `play()` and `wait()`, so something that slides off-screen and back, or overlaps only mid-move, isn't caught. Sampling a few points inside each animation (Manim's `interpolate`) would close it.

### #34 · Should `ms approve` require `ms check` to pass?
status: open · P2 · feature
Today `ms check` is advisory in `/draft-short`. Making errors block approval (with `--force`) would make it a real gate before the pipeline's video review. A product decision; published 0002, 0003, 0005 would all fail it.

### #36 · A question in Discord shouldn't force a revision
status: open · P3 · feature
Every reply to a script starts a revise job. On 0006 the reply was half question ("Is that the book's solution?"), and the job answered it but also rewrote the solution. Let a reply that starts with `?` get an answer in the thread (a cheap read-only job) with no new version.

### #35 · verify.py exposes few plain numbers
status: open · P3 · chore
`ms check`'s number match reads verify.py's module-level values, but most Shorts keep their numbers inside functions, so the check leans on short.yaml. A convention such as an `ANSWERS` dict in each verify.py would make it stronger.

### #31 · Put the Google OAuth app in Production before Phase 3
status: blocked · P2 · chore
The app is in Testing, so its refresh tokens expire after 7 days, which would stop unattended uploads every week. Publishing it needs the consent screen's app information filled in (Google Auth Platform → Audience → Publish app). Use the channel's identity, not a personal one.
**Blocked (2026-11-02):** console-only, needs the human signed in to the Google Cloud project. Steps:
1. Google Auth Platform → Branding: app name "Master Math USA", support and developer contact = the channel's Google account email; no logo (a logo triggers brand verification). Leave homepage/privacy links empty unless asked.
2. Audience → Publish app → Confirm. The `youtube` scope is sensitive, so Google offers verification; skip it. A single-user app works unverified: sign-in shows "Google hasn't verified this app" → Advanced → Go to (unsafe). The 100-user cap doesn't matter.
3. The current `~/.config/mathshorts-youtube-token.json` was issued in Testing and still dies 7 days after issue. Delete it and sign in again as the channel, without uploading anything: `python -c "import sys; sys.path.insert(0, 'scripts'); import youtube_test; youtube_test.credentials()"`.
4. Done when Audience shows "In production" and a new token still refreshes after 8 days.

### #27 · Phase 1: file checks and scene base class
status: open · P2 · feature
File and upload match checks, plus a base class that owns the frame only, never the solution animation (YouTube's inauthentic content policy). Done when one existing Short runs on it and has been re-previewed.
**2026-11-02:** stubbed `mathshorts/filecheck.py` (`check_kit`, `check_upload`). They raise `NotImplementedError` and nothing calls them yet. Needed before Phase 3 (#29), when the system uploads. The base class is in doubt: the frame is already in `lib/components.py`, `ms check` catches frame faults, and all five Shorts are published, so moving one onto it changes code behind a live video. Build it only if Phase 2 jobs keep getting the frame wrong, or start with 0006.

### #28 · Phase 2: script loop
status: doing · P2 · feature
New statuses, `ms tick`, Discord bot, script job. Needs from the human: a Discord server and bot. The human still animates interactively. Done after one week of real scripts, with usage per job logged.
**2026-11-02:** built and tested against a fake Discord and job runner (`mathshorts/tick.py`, `discord.py`, `jobs.py`, `scripts/jobs/`, `scripts/tick.sh`, `config/pipeline.yaml`; OPERATING.md has the setup and daily steps). **2026-11-03:** first live run worked end to end: `ms discord hello` passed; script job 0006 (126 s, 29 turns, ~$0.85 est.), a reply, revise job to v2 (108 s, ~$0.66 est.), then ✅ moved it to `drafting`. No commands denied. Left: schedule `tick.sh` in cron, then a week of real scripts.

### #29 · Phase 3: video loop
status: open · P2 · feature
Animate and revise jobs in containers, private uploads, approval by check mark. The human still releases by hand. Rule 4 now allows it (reworded 2026-11-03); still needs #31 and the real #27 file checks. Absorbs #9. Done when five Shorts are approved without a terminal.

### #30 · Phase 4: auto release
status: open · P2 · feature
Scheduling (5:00 PM slot), release check, stop sign. Retire the nightly batch, ready kits and `ms published`. Done after two weeks with no action needed after any approval.

### #21 · Thumbnail can catch a fade in progress
status: open · P2 · bug
`render.thumbnail` takes the frame `THUMB_LEAD` (0.1 s) before the "Pause and try it" beat. If a scene is still fading something out then, it lands in the thumbnail: 0003's has a ghost "41 miles" and the "Can you beat that?" caption. The frame also isn't always the best one once a Short has beats before the pause. Let a Short choose its frame (say a `thumbnail_at` key or a named beat), or warn when the frame is mid-animation.

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
YouTube Data API `videos.insert` with a scheduled publish time, after `ms batch`. Tested in #25: uploads from our unverified project are not locked private, and `publishAt` scheduling works, so no audit is needed. Absorbed into Phases 3–4 of `docs/pipeline-design.md`.

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

### #18 · Final mix measures -16 LUFS, not the -14 target
status: open · P3 · bug
`render.mix` asks loudnorm for -14 LUFS, but ebur128 measures -16.0 on 0001's final, both native and in Docker. Likely single-pass loudnorm on a quiet track. Try two-pass, or confirm that -16 is acceptable and change the target.

## Done

### #32 · Job allowlist and prompts for unattended runs
status: done · 2026-11-02
Script and revise jobs (`mathshorts/jobs.py`) get a per-command `ms` allowlist plus Read/Write/Edit, deny git and every status-changing command, and their prompts (`scripts/jobs/`) say one command per call, no scratch scripts, and carry the plain-question hook rule. The animate job gets its own in #29.

### #26 · Phase 1: `ms check` and on-screen match
status: done · 2026-11-02
`ms check <n>` dry-runs the scene in seconds (`mathshorts/probe.py`, no lib change) and checks safe zone, text overlaps, beat order, comment hold, captions and numbers against short.yaml and verify.py, and the music credit. Duration and caption length are warnings, since 40–50 s is a target; it flags 0003's 57.8 s.

### #25 · Phase 0: trial Pro jobs and the YouTube test
status: done · 2026-11-02
Uploads aren't locked private and `publishAt` works (`scripts/youtube_test.py`); one Short takes about 14% of a Pro session limit (`scripts/trial_job.sh`) and the trial Short was good, so we continue on Pro. Results in `docs/pipeline-design.md`.

### #24 · Move the repo off /mnt/c
status: done · 2026-11-02
The working copy is now `~/mathshorts`, on WSL's own filesystem, as OPERATING.md always asked. The venv's editable install points there too.

### #23 · Raise the final video bitrate
status: done · 2026-11-02
Final renders now use `crf=14`, `preset=slow` instead of Manim's crf 23. On 0005 the raw video went from 0.90 to 1.55 Mbps, with no meaningful change in render time. Previews are unchanged.

### #22 · `ms published` doesn't commit
status: done · 2026-11-02
It now commits that Short's folder and nothing else, as `<number>: published`, so a later batch can't sweep it up. If git fails, it prints the command to run.

### #17 · Native batch can't find manim when run via `MS_BIN`
status: done · 2026-11-02
`render.manim` runs the `manim` beside `sys.executable`, then falls back to PATH. `nightly.sh` falls back to `~/.venvs/mathshorts/bin/ms`, so the scheduler lines work without activating the venv. All tests pass with the venv off PATH.

### #16 · Visual scores are bunched at the top
status: done · 2026-11-01
The figure and keyword bonuses now give one point together, not one each, and dissection sections start at 4 like the other visual sections. 5/5 drops from 175 to 67 of 430, across five tags, and the puzzles behind 0002 and 0003 still clear `min_visual`. Added `ms sources add <src> --rescore`, which updates `scored_by: heuristic` entries only, and applied it. Scores are whole numbers, so the top band still ties; #7 is the way to split it further.

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
