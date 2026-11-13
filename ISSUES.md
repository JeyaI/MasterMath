# Issues

The software backlog. Add items freely; one line is enough. Work them with `/work-issue` in Claude Code (see OPERATING.md).

- **status:** `open` · `doing` · `blocked` · `done`
- **priority:** `P1` now · `P2` soon · `P3` someday
- **type:** `bug` · `feature` · `content` · `chore`

Next id: **52**

## Open

### #43 · Find the best time to release
status: open · P3 · feature
Releases used to go out at a fixed 5:00 PM New York (`release:` in `config/pipeline.yaml`). Since #44, they follow the ✅ (about an hour later), so release times vary by themselves; record each Short's release hour when comparing. Find out whether another time, or two different slots on a 2-Short day, does better: start from the YouTube Analytics API (when viewers are on, views in the first hours per Short, ties in with #12), or a simple A/B over a few weeks. Then change `release.time`, or give `release.py` a list of times.

### #38 · A crash between upload and saving the video id leaves a stray upload
status: open · P3 · bug
Happened on 0006's first live run (2026-11-03): a Discord SSL timeout while adding reactions crashed the tick after the upload, and the next tick uploaded again (stray: `2OiU6RuGGpg`). Fixed the likely cases the same day: the id is saved to `video.pending` right after `videos.insert` returns, and Discord network errors are retried. Left: a crash *during* `videos.insert` can still leave a copy; matching on title and upload time on the next tick would catch it.

### #39 · Wire `filecheck.check_upload` into the video loop
status: open · P2 · feature
Once #27's checks exist, run `check_upload` on the upload made at ✅ (title, description, tags, duration against the file; since #48 that is the only upload) before scheduling it. `video.versions[n].sha256` already records the file.

### #40 · ❌ is only read once a video is up for review
status: open · P3 · bug
A cross on the script message while the Short is `animating` or `revise_video` is ignored, and the job runs anyway (its video then arrives and can be crossed). Read crosses in every loop state before starting a job.

### #42 · Tick runs long while a video job works
status: open · P3 · chore
An animate job plus render and upload takes 10–20 minutes, and the tick lock makes the 5-minute ticks skip meanwhile, so replies on other threads wait. Fine at today's volume; if it bites, read threads in a separate quick tick and run jobs in another. **2026-11-03:** a `--draft` tick now waits up to 45 minutes for the lock instead of skipping, so a busy tick no longer costs the night's script.

### #33 · `ms check` misses mid-animation faults
status: open · P3 · feature
It samples the screen at the end of each `play()` and `wait()`, so something that slides off-screen and back, or overlaps only mid-move, isn't caught. Sampling a few points inside each animation (Manim's `interpolate`) would close it.

### #34 · Should `ms approve` require `ms check` to pass?
status: open · P2 · feature
Today `ms check` is advisory in `/draft-short`. Making errors block approval (with `--force`) would make it a real gate before the pipeline's video review. A product decision; published 0002, 0003, 0005 would all fail it.

### #37 · Run the script loop for a week
status: open · P2 · chore
#28's original bar. Schedule `scripts/tick.sh` in cron (every 5 min, plus `--draft` nightly; OPERATING.md setup step 7), then let it run for a week of real scripts. Check `out/logs/jobs.jsonl` for time and estimated cost per job, and `out/logs/tick.log` for failures. Do this before #29 builds on it.

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

### #29 · Phase 3: video loop
status: doing · P2 · feature
Animate and revise jobs in containers, private uploads, approval by check mark. The human still releases by hand. Rule 4 now allows it (reworded 2026-11-03); still needs #31 and the real #27 file checks. Absorbs #9. Done when five Shorts are approved without a terminal.
**2026-11-03: built**, with two changes the human asked for: review uploads are **unlisted**, and a ✅ also **schedules the release** (next 5:00 PM New York slot, 1 a day, ≥2 h lead, `release:` in `config/pipeline.yaml`), with 🛑 to pull it and a release check that records `published`. That pulls #30's scheduling, stop sign and release check in. #31 and #27 were not waited for: a lapsed token pauses video jobs and the bot says so; `filecheck` stays a stub. Jobs and every check of job-written code run in `mathshorts-job` (`Dockerfile.job`, `mathshorts/sandbox.py`). `ms animate <n> [--as-is]` hands a `drafting` Short over. Remaining: a live run, then the five-Short bar.

### #30 · Phase 4: auto release
status: open · P2 · feature
Scheduling (5:00 PM slot), release check, stop sign. Retire the nightly batch, ready kits and `ms published`. Done after two weeks with no action needed after any approval.
**2026-11-03:** scheduling, the stop sign and the release check were built in #29. Left: the soft rule that consecutive Shorts don't share a main tag, the low-schedule alert (under 3 days), and retiring the manual path once nobody uses it.

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
**Same-path rule (2026-11-03, #29):** if `ms tick` itself runs in a container, it starts job containers through the host's Docker socket, so `-v` paths are resolved on the host. Mount the repo and `MS_CACHE` at the same absolute path inside and out (e.g. `/srv/mathshorts`), or set `MS_HOST_MAP` (`mathshorts/sandbox.py`).

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

### #51 · Post the script to Discord as its beats, inline, instead of an attached SCRIPT.md
status: done · 2026-11-12 · P2 · feature
In script review, the only part of a script that matters is the beats. Right now `post_version` (`mathshorts/tick.py`) posts a spoilered summary and attaches the whole `SCRIPT.md` (0021's runs to about 1,000 words: puzzle choice, insight, Level 2, music, risks). Instead, post just the beats as an inline message, one line per beat with its time range and caption (e.g. `6. (14-19 s) Pause and try it.`), all inside a spoiler, and drop both the attachment and the summary. Keep the version line and the ✅/❌ prompt. `SCRIPT.md` stays on disk as it is, since the animate and revise jobs read its Insight, Level 2 and Music sections. Pull the beats from its `## Beats` section; if that section is missing, fall back to attaching the file as before. Watch Discord's 2,000-character limit: 0021's beats with their stage directions come to about 2,000, so show the captions only (no stage directions) and split into a second message if it's still too long. Do the same for revised versions (`revise` job), and update the script-review paragraph in OPERATING.md.
- **Resolution:** `post_version` posts `## Beats` captions inline in a spoiler (`script_beats`), split across messages under 2,000 characters with ✅/❌ on the last; no Beats section falls back to the attachment.

### #50 · Check the first custom thumbnail on a released Short
status: done · 2026-11-12 · P3 · chore
After #41, the first ✅ upload (0009 or 0010 tonight) calls `thumbnails.set`. Check the approval message for a "thumbnail wasn't set" note. If YouTube refused it because the channel isn't verified, verify the channel (YouTube Studio → Settings → Channel → Feature eligibility). Once it's live, see where the thumbnail actually shows for a Short: channel Shorts tab, search, subscriptions. If YouTube ignores it everywhere, there's no harm in keeping the call.
- **Resolution:** checked by hand; done.

### #49 · Check that Discord video attachments are good enough to judge a Short on the phone
status: done · 2026-11-12 · P2 · chore
Since #48, review videos arrive as MP4 attachments in the thread. On the first one (0009 v1, 5.4 MB, sent as it is), check on the phone app that it plays inline at full height, that the sound works, and that you can scrub to a timestamp. Also check a compressed copy (`vN-discord.mp4`, sent when a render is over 9.5 MB) for blur in text and thin lines. If attachments don't work, raise `review.max_mb` (needs a server boost) or bring back an unlisted YouTube link for review only.
- **Resolution:** checked by hand; done.

### #41 · Thumbnails for scheduled Shorts
status: done · 2026-11-05 · P3 · feature
The manual path makes `thumbnail.png`; the video loop sets none. Shorts mostly ignore custom thumbnails, and `thumbnails.set` needs a verified channel. Decide whether it matters.
- **Resolution:** it matters: without one YouTube picks its own frame, which can come from the solution. The sandbox render now keeps the kit's `thumbnail.png` (the frame just before "Pause and try it") as `out/review/<short>/vN.png`. It's attached in the thread with the video, and set with `thumbnails.set` right after the ✅ upload. That's best effort: a refusal (for example an unverified channel) is noted in the approval message and the release goes ahead. Backfilled by hand for 0009 v3 and 0010 v4, which were rendered before this. Follow-up: #50.

### #48 · Post review videos to Discord instead of uploading them to YouTube
status: done · 2026-11-05 · P2 · feature
Every review version is uploaded to YouTube as unlisted, which spends the channel's daily upload cap (#47), costs API quota, and leaves stray uploads when a tick crashes (#38). Review renders are small: 5.7–9.7 MB so far (`out/review/`, 0006–0008). Attaching the MP4 to the thread (`discord.post(files=…)`, `SPOILER_` name) would make the review loop YouTube-free, and only the ✅ version would be uploaded, at approval, as a fresh upload that is scheduled straight away (which also settles #45). To check: Discord's attachment limit is 10 MB without a server boost, and 0008 v10 was 9.65 MB, so longer Shorts may go over. Either re-encode review copies to a cap (for example a two-pass bitrate) or keep YouTube as a fallback above the limit. Also check that the phone app plays the attachment well enough to judge it. Approval would have to tie the ✅ to the attachment's sha256 (we already record it) instead of a video id. Moving the upload to approval also means an upload failure or #47 pause can delay a release, so `next_slot` must allow for that.
- **Resolution:** review versions are attached to the thread as `SPOILER_NNNN-video-vN.mp4` (a two-pass re-encode to `review.max_mb`, 9.5 MB, when the master is bigger; 0008 v4's 10.2 MB became 9.2 MB in 13 s), with no YouTube call. On ✅ tick checks the master's sha256, uploads it private, saves the id, and schedules it at a slot worked out then, retrying each tick on failure or a #47 pause. 🛑 sets it private and unscheduled, and a new ✅ reuses it. Pre-#48 versions with an unlisted upload are scheduled as before. Phone playback still to be confirmed on the first real post (#49).

### #45 · Check that unlisted → public gets the full new-upload treatment
status: done · 2026-11-05 · P3 · bug
Every release (slot or asap, #44) flips a review upload from unlisted to public via `publishAt`. Check on 0006 (public 2026-11-04) and the first asap release whether subscribers got a notification and it reached the Shorts feed (first-hour views in YouTube Studio). If not, upload a fresh copy at approval instead.
- **Resolution:** settled by #48. Releases are now fresh private uploads scheduled with `publishAt`, YouTube's normal scheduled-release path, not unlisted review copies made public. 0007 (scheduled before #48) is the last unlisted → public one.

### #47 · Stop uploads for 8 hours on `uploadLimitExceeded`
status: done · 2026-11-04 · P2 · bug
YouTube can refuse `videos.insert` with `uploadLimitExceeded` (the channel's daily upload cap, separate from API quota). Right now `make_video` treats it like any upload error and retries every tick, which keeps hitting the limit. Detect that reason in `mathshorts/youtube.py`, record a pause-until time (8 hours out) that persists across ticks, skip uploads until then (renders can still go ahead), and post one notice in the thread saying when uploads resume. Test with a fake YouTube that raises it once: no upload attempts for 8 hours, then a normal upload.
- **Resolution:** `youtube.upload` raises `UploadLimitError` on `uploadLimitExceeded`; tick writes `out/youtube-upload-pause.json` (8 h), skips uploads until then with one ⏸️ notice giving the resume time, and renders still go ahead. Tested with a fake YouTube.

### #46 · Don't spoil the puzzle in Discord
status: done · 2026-11-04 · P2 · feature
I want to try each puzzle before I see its answer. Right now the first script message (`post_version` in `mathshorts/tick.py`) shows the title and the job's `summary`, which can give away the trick or the answer. `SCRIPT.md` is attached openly, and the video post shows its summary too.
- **First message of a thread:** state the problem in full (the puzzle as the Short poses it, from `short.yaml`), with nothing about the solution, so I can work it out first.
- **Spoiler tags on everything about the solution:** wrap the summary, the answer, the insight and the Level 2 answer in Discord `||…||`. Name attachments `SPOILER_<name>` so Discord blurs them (the script file, any frames). This covers script versions, revisions, video posts, and job summaries/errors that quote the answer.
- Titles and video links can give it away too: check the title, and put the YouTube link (whose thumbnail shows the solution) inside a spoiler.
- Tell the jobs (`scripts/jobs/*.md`) to keep `summary` free of the answer, or to mark what is a spoiler, so tick can wrap it reliably.
- Test: a fake Discord in `tests/test_tick.py` asserts that the answer from `verify.py`/`level2.accept` never appears outside `||…||` in any bot post.
Resolved: threads open with `level1.statement` alone; summaries, errors, Level 2, `SCRIPT.md` (`SPOILER_`) and YouTube links go in spoilers; a title naming an answer becomes "a new puzzle"; jobs told to keep summaries and statements clean; tested in `test_tick.py`.

### #44 · Release about an hour after approval instead of at a fixed slot
status: done · 2026-11-03
`release.mode: asap` (now live in `config/pipeline.yaml`): a ✅ goes public on the first full hour at least `asap_minutes` (60) later, still through `publishAt` so 🛑 works; past the 2-a-day cap it takes the next day's 5:00 PM. `mode: slot` keeps the old rule. Follow-up: #45.

### #28 · Phase 2: script loop
status: done · 2026-11-03
`ms tick`, the Discord bot, script and revise jobs, and the new statuses are built (`mathshorts/tick.py`, `discord.py`, `jobs.py`), and one live run worked end to end: 0006 scripted, revised from a reply, and accepted by ✅ (about $0.85 + $0.66 estimated). Closed before the week of real scripts; that moved to #37.

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
