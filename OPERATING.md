# Operating Master Math USA

This is the playbook for running the channel: what you do, when, and with which command. For how the code works, see CLAUDE.md. For what's broken or planned, see ISSUES.md.

## The system in one picture

```
 script job ──▶ script in Discord ──▶ ✅ ──▶ animate job ──▶ video in Discord ──▶ ✅ ──▶ scheduled ──▶ public ~1 h later
 (nightly)      (react or reply)            (automatic)      (unlisted link;      (that exact upload;    (YouTube releases it;
                                                              react or reply)       🛑 pulls it)           tick records it)

 The manual path still works: draft (Claude Code) ──▶ approve ──▶ nightly batch ──▶ ready ──▶ you upload
```

You're the editor: you accept scripts, watch each video on your phone and approve it, all in Discord. The software picks, writes, animates, checks, renders, uploads and releases. Nothing goes public without your ✅ on that exact version.

## Where a Short is, and what it needs from you

| Status | Meaning | Your move |
|---|---|---|
| `scripting` | The nightly script job is writing it | Nothing |
| `script_review` | A verified script is waiting in its Discord thread | ✅ to accept, ❌ to abandon, or reply to revise |
| `revise` | A job is revising the script from your reply | Nothing; the new version arrives in the thread |
| `animating` | The animate job is writing the scene; tick then checks, renders and uploads it | Nothing |
| `video_review` | An unlisted video is waiting in its Discord thread | Watch it; ✅ to approve, ❌ to abandon, or reply to revise |
| `revise_video` | A job is revising the video from your reply | Nothing; the new version arrives in the thread |
| `scheduled` | Approved; YouTube makes it public at the time the bot posted | Nothing, or 🛑 to stop it |
| `needs_attention` | A job failed twice | `/draft-short <n>` in Claude Code, or ❌ in Discord |
| `abandoned` | You crossed it out; its puzzle is free again | Nothing |
| `drafting` | Being made in Claude Code | Give feedback until it's right, then say "approve" |
| `approved` | Waiting for tonight's render | Nothing |
| `ready` | Finished MP4, thumbnail and upload kit in `out/ready/` | Watch it on your phone, then upload or reject |
| `failed` | Tonight's render broke | Open it in Claude Code: `/draft-short <n>` |
| `published` | Live on YouTube | Comments, if you like |

`drafting`, `approved`, `ready` and `failed` are the manual path (Claude Code and the nightly batch).

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
7. **Discord, for the script loop.** A private server with a drafts channel and a bot.
   1. Developer Portal → New Application → Bot: turn **Public Bot off** and **Message Content Intent on** (leave the other intents off). Copy the token from **Reset Token**.
   2. OAuth2 → URL Generator: scope `bot` only, no permissions; open the URL and add it to your server. Then on the drafts channel only (Edit Channel → Permissions → add the bot), allow: View Channel, Send Messages, Create Public Threads, Send Messages in Threads, Read Message History, Add Reactions, Attach Files, Embed Links.
   3. Put the token, your user ID and the channel ID in `~/.config/mathshorts.env` (template: `config/mathshorts.env.example`; `chmod 600`). For the IDs, turn on Settings → Advanced → Developer Mode and use "Copy ID".
   4. `set -a; . ~/.config/mathshorts.env; set +a; ms discord hello`. It checks each setting and permission and posts a test thread.
   5. Schedule `scripts/tick.sh` like the nightly batch: every 5 minutes (`*/5 * * * *  ~/mathshorts/scripts/tick.sh`) and twice a day with `--draft` (`0 1 * * *  ~/mathshorts/scripts/tick.sh --draft` and `0 20 * * *  ~/mathshorts/scripts/tick.sh --draft`). Each `--draft` run writes at most one script, only if the queue has room, and waits up to 45 minutes for a busy tick rather than skipping. Its log is `out/logs/tick.log`.
8. **YouTube and the job sandbox, for the video loop.**
   1. Sign in as the channel: `ms youtube login`, open the link it prints, and choose the channel's account. `ms youtube hello` checks it. While the Google app is in Testing (#31), the sign-in lasts 7 days; when it lapses, the bot says so in the thread and video jobs wait until you sign in again.
   2. Build the sandbox image that jobs run in: `docker build -t mathshorts . && docker build -t mathshorts-job -f Dockerfile.job .` Jobs, and every check of the code they write, run in it with no access to `~/.config`. Rebuild it when you update Claude Code (`CLAUDE_CODE_VERSION` in `Dockerfile.job`).
   3. Release time and the daily cap are in `config/pipeline.yaml` (`release:`; `mode: asap` = on the hour about an hour after your ✅, 2 a day, a full day's extra goes out at the next day's 5:00 PM New York; `mode: slot` = the next 5:00 PM, tomorrow at the soonest).
9. **Catalog:** `catalog/dudeney-amusements.jsonl` is already in the repo (430 puzzles). To add another book, see "Rarely" below.

---

## Rarely: adding a source (~15 min)

1. Make sure it's licensed: public domain, or a license that allows commercial use. If unsure, don't add it.
2. If it isn't registered yet, ask Claude Code: "add <book> as a source" (`/work-issue`). It adds an entry to `catalog/sources.yaml` and a parser if needed.
3. `ms sources add <source>`. It downloads (cached in `~/.cache/mathshorts`), parses into `catalog/<source>.jsonl`, and gives new puzzles a heuristic score in `catalog/annotations.yaml`.
   - If the download is blocked, download the `.txt` in a browser and run `ms sources add <source> --file path/to/book.txt`.
4. Run `ms suggest -n 15` and skim. For any score that looks wrong, edit `catalog/annotations.yaml`: change `visual_potential`, add `tags`, set `skip: true` for puzzles you'll never make, and set `scored_by: human`. Re-scraping never overwrites these.
5. Commit: `git add catalog && git commit -m "catalog: add <source>"`.

---

## Daily: scripts and videos in Discord (~2 min a script, ~3 min a video)

At 8 PM and 1 AM, `ms tick --draft` writes one new script if fewer than 4 drafts are in the loops (`config/pipeline.yaml`). A Claude job picks the puzzle, proves the answer in `verify.py`, and writes `SCRIPT.md`; tick runs `verify.py` again itself before posting. It arrives as its own thread in the drafts channel. The first post is the puzzle alone, so you can try it first; everything about the solution (the summary, the attached `SCRIPT.md`, Level 2, the video links, errors) is behind Discord spoilers: tap to reveal. If the title would name the answer, the thread is called "a new puzzle" instead.

- **✅ on the newest version:** accepted. The animate job starts on the next tick.
- **Reply in the thread:** a revise job rewrites the script from your words, and v2 arrives in the same thread within a few minutes. Several replies before the next tick count as one comment.
- **❌ on any version:** abandoned, and its puzzle goes back in the pool.

About 10–15 minutes later the video arrives in the same thread as an unlisted YouTube link. Before it's posted, tick has run `verify.py` and `ms check` itself and rendered the final 1080×1920 video; that file is what was uploaded. Watch it on your phone.

- **✅ on the newest video:** approved. That exact upload is set to go public on the hour about an hour later (a ✅ at 7:23 PM → 9:00 PM; if 2 already go out that day, the next day's 5:00 PM), and the bot posts the time. You have until then to 🛑. YouTube releases it, and the next tick after that records it as `published` and posts the link.
- **🛑 on the "approved" message:** stops the release. The video goes back to unlisted and is posted again for a fresh ✅ or a reply.
- **Reply in the thread:** a video revise job changes it, and v2 arrives as a new upload; v1's upload is deleted. Start with a timestamp when you can ("0:12 slow down the slide"). A reply can change the script too.
- **❌ on any version:** abandoned; its uploads are deleted.

Only your account counts. A reply beats a ✅ left at the same time (the bot tells you), and a ✅ on an old version does nothing. Jobs never see the Discord or YouTube tokens, and only tick changes status, from your reactions. Each job's time and estimated cost go to `out/logs/jobs.jsonl`, and every step is in the Short's `events.jsonl`.

**Sending your own scene for review.** A Short you animated in Claude Code can skip `ms approve` and the batch: `ms animate <n> --as-is` renders it, uploads it and posts it in Discord like any other video. `ms animate <n>` without the flag hands a `drafting` Short with a `SCRIPT.md` to the animate job instead.

---

## Weekly: the drafting session (one 2–4 hour block, 4–5 Shorts)

For each Short:

1. **Pick.** `ms suggest`. Read the promising ones with `ms show <id>`. Choose one. Or skip this and let Claude Code choose with `/draft-short pick`.
2. **Start.** Scripts you accept in Discord are animated by a job, so this session is for Shorts you want to direct yourself. To take one over (say from `needs_attention`): `/draft-short <n>`; its `SCRIPT.md` is the agreed pitch, so it goes straight to the scene. Otherwise, in Claude Code: `/draft-short <id>` (or `pick`, whose pitch also names the puzzle, why, and a runner-up). It replies with a 5-line pitch (hook, insight, Level 2, risks, music). To hear a piece first, run `ms music <key> --open`. Push back now; it's the cheapest moment to change direction.
3. **First preview.** It writes `verify.py` (the answers, checked in code), then the scene, renders a preview, runs `ms check` (format rules, and on-screen text against `short.yaml` and `verify.py`), and opens the preview, listing the beats with timestamps and any check warnings.
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

`scripts/nightly.sh` runs `ms batch`: every `approved` Short is rendered at 1080×1920, mixed with the piece named in its `music.piece`, normalized for loudness, and put in `out/ready/<short>/` with its `thumbnail.png` and `upload.txt`. Status changes are committed.

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
| A Short is `needs_attention` | A job failed twice; `last_error` in `short.yaml` and `out/logs/job-*.jsonl` say why. Take it over with `/draft-short <n>`, then `ms reject <n> "taking over"` moves it to `drafting`; when it's right, `ms animate <n> --as-is` sends it back to Discord. Or ❌ it in Discord. |
| The bot says an upload failed, or `tick.log` says video jobs are paused | `ms youtube hello`. If the token lapsed, `ms youtube login`. The rendered video waits, and the next tick uploads it without redoing the job. |
| A job fails at once with a Docker error | Is Docker running, and does `docker images` list `mathshorts-job`? Build it (setup step 8). |
| No new script arrived | `out/logs/tick.log`: the queue may be full (`config/pipeline.yaml`), or the job failed. |
| `ms tick` says "not set" or HTTP 401 | Check `~/.config/mathshorts.env` and run `ms discord hello`. The bot token is the one from Bot → Reset Token, not the OAuth2 client secret. |
| Render is slow or crashes on the cloud box | Use a machine with at least 2 GB of RAM (LaTeX). See ISSUES.md for the Phase 2 plan. |

## Command reference

| When | Command | Does |
|---|---|---|
| Rarely | `ms sources list` | Sources and puzzle counts |
| | `ms sources add <src> [--file F]` | Scrape a source into the catalog |
| | `ms sources add <src> --rescore` | Same, and re-run the heuristic on `scored_by: heuristic` entries (after changing it) |
| Drafting | `ms suggest [-n 5]` | Ranked shortlist with reasons |
| | `ms show <catalog-id>` | Read a puzzle and its solution |
| | `ms new <catalog-id>` / `--blank "Title"` | Create a Short (Claude Code usually does this) |
| | `ms verify <n>` | Run the answer checks |
| | `ms preview <n> [--at 0:12] [--open]` | Full preview, or one beat |
| | `ms compare <n> [--open]` | Before/after side by side |
| | `ms check <n>` | Format rules and on-screen match, in seconds, without rendering. Errors exit non-zero; warnings (duration outside 40–50 s, caption length) are targets |
| | `ms note <n> "0:12 text"` | Log a review note |
| | `ms music [<key>] [--open]` | List the music library, least recently used first; a key writes a 46 s WAV to `out/music/` |
| | `ms approve <n>` | Your sign-off; refuses if the description doesn't credit the Short's piece |
| Nightly | `ms batch [<n>]` | Render and mix approved Shorts |
| Mornings | `ms inbox` | What needs you |
| | `ms reject <n> "note"` | Back to drafting |
| | `ms published <n> <url>` | Record an upload and commit it |
| Script and video loops | `ms tick [--draft]` | Read your Discord reactions and replies, run jobs, upload review videos, schedule what you approve and record releases; `--draft` also writes one new script (run by `scripts/tick.sh`) |
| | `ms animate <n> [--as-is]` | Hand a `drafting` Short to the video loop: the animate job, or `--as-is` for your own scene |
| | `ms youtube login` / `hello` | Sign in as the channel / check the token |
| | `ms discord hello` | Check the bot's token, channel, your user ID and every permission |
| Anytime | `ms status` | Everything by status |

`<n>` is the Short number: `7`, `0007` or `0007-slug` all work.
