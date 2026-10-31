# Operating Master Math USA

This is the playbook for running the channel: what you do, when, and with which command. For how the code works, see CLAUDE.md. For what's broken or planned, see ISSUES.md.

## The system in one picture

```
 sources ──▶ catalog ──▶ suggest ──▶ draft (Claude Code) ──▶ approve ──▶ nightly batch ──▶ ready ──▶ you upload
 (rarely)    (puzzles)    (you pick)   (you direct)          (you)       (automatic)       (you watch)  (manual for now)
```

You're the editor: you pick puzzles, direct the animation, approve, watch the finished video, upload it and read the numbers. The software does the scraping, ranking, rendering and mixing.

## Where a Short is, and what it needs from you

| Status | Meaning | Your move |
|---|---|---|
| `drafting` | Being made in Claude Code | Give feedback until it's right, then say "approve" |
| `approved` | Waiting for tonight's render | Nothing |
| `ready` | Finished MP4, thumbnail and upload kit in `out/ready/` | Watch it on your phone, then upload or reject |
| `failed` | Tonight's render broke | Open it in Claude Code: `/draft-short <n>` |
| `published` | Live on YouTube | Comments, if you like |

`ms status` shows every Short by status. `ms inbox` shows only what needs you.

---

## One-time setup

1. **WSL + repo.** Keep the repo inside the WSL filesystem (`~/mathshorts`), not under `/mnt/c`. Renders write many files, and the Windows drive is slow for that.
2. **Install, either way:**
   - **Native (simplest):** needs Python 3.11 or later. Ubuntu 22.04 ships 3.10, and its `python3.11` package is only a release candidate, so use uv to get a current Python without touching the system one.
     1. `sudo apt install ffmpeg texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science dvisvgm fonts-inter libcairo2-dev libpango1.0-dev pkg-config`
     2. `curl -LsSf https://astral.sh/uv/install.sh | sh`, then open a new terminal.
     3. `uv python install 3.13`, then `uv venv --seed --python 3.13 ~/.venvs/mathshorts`
     4. `source ~/.venvs/mathshorts/bin/activate`, then `pip install -e ".[dev]"` from the repo.

     Run `source ~/.venvs/mathshorts/bin/activate` in every new terminal before using `ms`.
   - **Docker:** `docker build -t mathshorts .` (about 7 minutes uncached), then set `MS_USE_DOCKER=1` for the nightly script. The image has Inter 4.1, while Ubuntu 22.04's `fonts-inter` is 3.19, so type looks very slightly different between native previews and Docker renders. Layout and timing match.
   - Check: `ms status` shows `0001-greek-cross`, and `python -m pytest -q` passes.
3. **Claude Code** in WSL: `curl -fsSL https://claude.ai/install.sh | bash`, then `cd ~/mathshorts && claude`. It reads CLAUDE.md automatically, and the skills `/draft-short` and `/work-issue` are in `.claude/skills/`.
4. **Anonymity.** The repo is already set to commit as `mathshorts`. Keep it that way (`git config user.name` should print `mathshorts`). Use the channel's own Google account and a separate GitHub account if you push anywhere.
5. **Schedule the nightly batch**, for example at 2:00 AM:
   - **Windows Task Scheduler (recommended):** a daily task with action `wsl.exe` and arguments `-d Ubuntu -- bash -lc "~/mathshorts/scripts/nightly.sh"`. Tick "Wake the computer to run this task" if you want it to run while the laptop sleeps.
   - Or cron inside WSL (needs systemd enabled): `0 2 * * * bash -lc ~/mathshorts/scripts/nightly.sh`
   - If the laptop was off, nothing breaks: run `ms batch` in the morning instead.
6. **YouTube channel:** upload `brand/out/avatar.png` and `brand/out/banner.png` (generate them with `python brand/logo.py`). Check the handle is free.
7. **Catalog:** `catalog/dudeney-amusements.jsonl` is already in the repo (430 puzzles). To add another book, see "Rarely" below.

---

## Rarely: adding a source (~15 min)

1. Make sure it's licensed: public domain, or a license that allows commercial use. If unsure, don't add it.
2. If it isn't registered yet, ask Claude Code: "add <book> as a source" (`/work-issue`). It adds an entry to `catalog/sources.yaml` and a parser if needed.
3. `ms sources add <source>`. It downloads (cached in `~/.cache/mathshorts`), parses into `catalog/<source>.jsonl`, and gives new puzzles a heuristic score in `catalog/annotations.yaml`.
   - If the download is blocked, download the `.txt` in a browser and run `ms sources add <source> --file path/to/book.txt`.
4. Run `ms suggest -n 15` and skim. For any score that looks wrong, edit `catalog/annotations.yaml`: change `visual_potential`, add `tags`, set `skip: true` for puzzles you'll never make, and set `scored_by: human`. Re-scraping never overwrites these.
5. Commit: `git add catalog && git commit -m "catalog: add <source>"`.

---

## Weekly: the drafting session (one 2–4 hour block, 4–5 Shorts)

For each Short:

1. **Pick.** `ms suggest`. Read the promising ones with `ms show <id>`. Choose one.
2. **Start.** In Claude Code: `/draft-short <id>`. It replies with a 4-line pitch (hook, insight, Level 2, risks). Push back now; it's the cheapest moment to change direction.
3. **First preview.** It writes `verify.py` (the answers, checked in code), then the scene, renders a preview and opens it, listing the beats with timestamps.
4. **Direct.** Reply in plain language, with a timestamp first when you can:
   - "0:12 the slide is too fast"
   - "0:31 the Level 2 question wraps badly"
   - "the hook should say 'in 4 pieces' bigger"

   Each note is logged in the Short's `NOTES.md`. Only the affected beat is re-rendered (a few seconds), and you get a before/after side by side.
5. **Approve.** When you're happy, say **"approve"**. It runs the answer check, refuses if any notes are still open, marks the Short `approved` and commits. It never approves without you saying so.
6. Start a fresh Claude Code session for the next Short (`/clear`), so each one starts focused.

**Batch the picking.** If you know your next few puzzles, write them down before you start.

---

## Nightly (automatic)

`scripts/nightly.sh` runs `ms batch`: every `approved` Short is rendered at 1080×1920, mixed with the music bed, normalized for loudness, and put in `out/ready/<short>/` with its `thumbnail.png` and `upload.txt`. Status changes are committed.

If one Short fails, it's marked `failed` with a log in `out/logs/` and the others still build. The batch's own log is `out/logs/nightly.log`. If it ends with `ERROR: status changes not committed`, the videos are fine: run the git command it prints.

---

## Mornings (~5 min, plus ~3 min per upload)

1. `ms inbox`.
2. **Watch each `ready` video on your phone**, not the laptop. Pacing and caption size only show up on the real screen. (Copy them over, or open `out/ready/` from Windows: `explorer.exe out/ready`.)
3. Not happy? `ms reject <n> "0:20 captions overlap the square"`. It goes back to `drafting` with your note, and next session you run `/draft-short <n>`.
4. **Upload by hand**, one per publishing day:
   1. YouTube Studio → Create → Upload, choose `out/ready/<short>/<short>.mp4`.
   2. Paste the title, description and tags from `upload.txt`.
   3. If Studio offers a custom thumbnail, use `out/ready/<short>/thumbnail.png`.
   4. Schedule it for your fixed daily slot (same time every day; don't change it for a few weeks).
   5. `ms published <n> <the video URL>`.
5. Keep about a week of `ready` Shorts as a buffer. If it drops below 3, plan an extra drafting session.

## Evenings (optional, ~5 min)

Read comments. Nothing is promised in the videos, so pin or reply only if you want to. A good move after about a day: reply under the first correct answer with the one-line `why` from the Short's `short.yaml`.

## Weekly review (~15 min)

1. In YouTube Studio, for each Short published that week, note **viewed vs. swiped away** and **average percentage viewed**.
2. Look for patterns by tag (dissections vs. routes vs. counting…).
3. Adjust `config/selector.yaml`: raise `tag_weights` for what holds viewers and lower it for what doesn't. Commit.
4. Add anything that annoyed you this week to ISSUES.md.

---

## Improving the software

The backlog is **ISSUES.md**. Add an item whenever something is slow, broken or missing (one line is fine). To work it:

- `/work-issue` in Claude Code picks the top open issue, plans it, waits for your OK on anything big, builds it, runs the tests and moves it to Done.
- `/work-issue 7` works a specific one.

Keep software sessions separate from drafting sessions.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| A Short is `failed` | `ms inbox` shows the error. Open `/draft-short <n>`; Claude Code reads the log in `out/logs/`. Fix it, then say "approve" again. |
| "another batch is already running" | One is in progress (maybe the nightly). Wait. If none is running, delete `out/.batch.lock`. |
| `ms suggest` says nothing qualifies | Lower `min_visual` in `config/selector.yaml`, un-`skip` some puzzles, or add a source. |
| `ms approve` refuses | It says why: `verify.py` failing, or open notes in `NOTES.md`. Resolve those. `--force` only if you really mean it. |
| Want to change a `ready` Short | `ms reject <n> "what to change"`, then `/draft-short <n>`. |
| Want to change a published Short | You can't edit a YouTube video. Make an improved Short later if it's worth it. |
| Preview won't open from WSL | Open it manually: `explorer.exe "$(wslpath -w out/preview/<short>)"`. |
| Render is slow or crashes on the cloud box | Use a machine with at least 2 GB of RAM (LaTeX). See ISSUES.md for the Phase 2 plan. |

## Command reference

| When | Command | Does |
|---|---|---|
| Rarely | `ms sources list` | Sources and puzzle counts |
| | `ms sources add <src> [--file F]` | Scrape a source into the catalog |
| Drafting | `ms suggest [-n 5]` | Ranked shortlist with reasons |
| | `ms show <catalog-id>` | Read a puzzle and its solution |
| | `ms new <catalog-id>` / `--blank "Title"` | Create a Short (Claude Code usually does this) |
| | `ms verify <n>` | Run the answer checks |
| | `ms preview <n> [--at 0:12] [--open]` | Full preview, or one beat |
| | `ms compare <n> [--open]` | Before/after side by side |
| | `ms note <n> "0:12 text"` | Log a review note |
| | `ms approve <n>` | Your sign-off |
| Nightly | `ms batch [<n>]` | Render and mix approved Shorts |
| Mornings | `ms inbox` | What needs you |
| | `ms reject <n> "note"` | Back to drafting |
| | `ms published <n> <url>` | Record an upload |
| Anytime | `ms status` | Everything by status |

`<n>` is the Short number: `7`, `0007` or `0007-slug` all work.
