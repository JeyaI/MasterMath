# Master Math USA: Overnight Pipeline Design

Copied from the reviewed design doc on 2026-11-02. This file is the source of truth from here on; change it in the same commit as the work it describes.

## Summary

**Recommendation: build this model, with one structural change: render once at final quality, and publish the exact video you approved.** That change delivers "no human review after approval" by construction, because nothing is produced after your approval. The post-approval step only sets a release time.

The proposed model replaces the weekly drafting session with two asynchronous touchpoints a day:

1. Two scripts arrive each morning, and you send back a first review.
2. Finished private videos arrive as YouTube links, and you approve or comment.
3. Approved videos are scheduled and go public with no further action.

Three prerequisites decide whether it works: an automated format check, a shared scene base class, and a YouTube API project that can publish publicly. The first two are software work. The third depends on Google's audit, so it needs a fallback from day one.

## Feedback on the proposed model

The model is sound, and one change matters more than the rest: **drop the second render.** A final render takes about a minute today, so a cheap preview saves almost nothing and creates the risk you want to remove.

**What works well**

- **Script review first.** It is the cheapest point to change direction, and it replaces the pitch step in `/draft-short`.
- **Private YouTube links.** You watch on your phone in the real player, which replaces copying files over by hand.
- **The review loop.** A draft stays in the loop until you approve it, so feedback never needs a special path.

**What I would change**

| Proposed | Change | Why |
| --- | --- | --- |
| Render a preview, then rerender on approval | Upload the full-quality, mixed video as the preview. On approval, schedule that same video | You approve the exact file that goes public. A rerender could differ, and the Docker and native builds already do (SSIM 0.985) |
| Make the pipeline robust enough to need no review | Run every automated check before you see the video, then do nothing to it afterward | There is no post-approval work left to fail, except scheduling |
| Cron drives the pipeline | Cron only starts scripts. Your replies start the next step | Otherwise each revision waits a night, and the loop takes a week |
| Two drafts every night | Skip a night when the queue is full | Two a night is 14 a week, more than a 1-a-day schedule can use |
| Reply by any channel in free text | Approval is one explicit action tied to one video version | Publishing should never depend on a model's reading of a comment |
| Replies handled as they arrive | Poll for replies every few minutes | Messages wait in the channel while the laptop sleeps, so no always-on listener is needed at first |

**Two corrections to my earlier advice.** I said to skip cloud hosting, but overnight jobs make reliable uptime matter, so hosting is now a real choice (see Infrastructure). I also listed the upload audit as a requirement, which may no longer be true (see YouTube).

## Goals and non-goals

The goal is to turn your job from directing sessions into answering messages, without lowering the bar for what goes public.

**Goals**

- Two scripts ready for review each morning, without a live Claude Code session.
- Review from a phone, in the channel, with no terminal.
- No human action on a Short after approval.
- A steady schedule of public Shorts, within the 1–2 a day rule.

**Non-goals**

- Publishing anything you have not approved. Human approval stays mandatory.
- Changing the Short format or the content rules.
- Automated comment replies (#10) and analytics (#12). Both can follow later.

**Proposed targets, to confirm after the first month**

| Measure | Target |
| --- | --- |
| Your time per Short | Under 10 minutes across both reviews |
| Drafts reaching you that fail a check | 0 |
| Approved Shorts needing action after approval | 0 |
| Approved Shorts released outside their slot | 0 |
| Scripts accepted with at most one round of comments | Most of them; measure first |

## Flow and states

A Short passes through two review loops, and each comment produces a new version in the same loop. A video can reach `scheduled` only through your check mark, and it can reach `published` only from there.

```
scripting -> script_review <-> revise
                  | check mark
              animating -> video_review <-> revise
                               | check mark on this exact version
                           scheduled -> published
Any stage -> needs_attention (a job failed twice) or abandoned (cross reaction)
Stop sign on a scheduled Short removes its release time
```

This replaces the current status machine in `mathshorts/shorts.py`:

| Today | New |
| --- | --- |
| `drafting` | `scripting`, `script_review`, `animating`, `video_review` |
| `approved`, `ready` | `scheduled`, since rendering now happens before approval |
| `failed` | `needs_attention` |
| `published` | `published`, now confirmed from YouTube |
| None | `abandoned` |

A comment on a video can also change the script. The Revise job handles that case and reruns the affected checks, so it needs no separate state.

**Each version has a number.** A version covers the script, scene, verify result, metadata, video hash and YouTube ID. That record is what your check mark approves.

## Unattended drafting

Split `/draft-short` into three separate jobs, each starting fresh from the Short's files. The repo holds the memory, so a crashed job can simply run again.

| Job | Starts when | Produces | Stops at |
| --- | --- | --- | --- |
| Script | Nightly cron, if the queue has room | `SCRIPT.md`, `short.yaml`, passing `verify.py` | `script_review` |
| Animate | You accept a script | `scene.py`, final video, passing `ms check` | `video_review` |
| Revise | You comment on a script or video | Updated files, same checks as its stage | The same review, as a new version |

**The script job must prove the math first.** `verify.py` runs before the script is sent, so you never review a solution that is wrong. Each script contains the hook, puzzle retelling, insight, beat list with captions, Level 2 and answer, music, risks, and a runner-up puzzle.

**Queue limits.** Cron skips drafting when either limit is reached. Both are proposals, set in config:

- At least 7 Shorts are already scheduled.
- At least 4 drafts are waiting on you.

**How jobs run.** Each job is a [`claude -p`](https://code.claude.com/docs/en/headless) run. These settings keep it predictable:

| Setting | Purpose |
| --- | --- |
| `--bare` | Not used. It ignores subscription logins and setup tokens, so these jobs cannot pass it. It is due to become the `-p` default in a future release, so check each Claude Code update |
| `--append-system-prompt-file` | Adds each job's instructions on top of `CLAUDE.md`, which loads normally |
| `ANTHROPIC_API_KEY` | Left unset, because it would override the Pro token. It is the fallback if Pro limits are too tight. Jobs authenticate with `CLAUDE_CODE_OAUTH_TOKEN`, a one-year token from `claude setup-token` |
| `--permission-prompts none` with `--allowedTools` | Denies anything unlisted instead of waiting for a person |
| `--max-budget-usd` | Stops a runaway job. It caps an estimate and does not track Pro limits |
| `--output-format json` with `--json-schema` | Returns a checkable result and `total_cost_usd`, an estimate to log for each job |

**One job at a time, each in its own git worktree.** Running jobs in sequence avoids two drafts claiming the same Short number or catalog puzzle. The orchestrator assigns the number before the job starts, and overnight speed is not a constraint.

**Job limits.** Jobs never hold YouTube or Discord credentials, and they cannot change status. Only the orchestrator does those things, which keeps rule 4 enforced by design and not by prompt wording.

**Pro usage, measured in Phase 0 (2026-11-02).** Jobs run on your Pro plan and share its limits with your interactive Claude use. One script job and one animate job ran through `scripts/trial_job.sh` on the setup token, in a worktree, on Opus 5.5 (the default):

| Job | Session (5-hour) limit | Time | Turns | `total_cost_usd` estimate |
| --- | --- | --- | --- | --- |
| Script | about 5% | 3 min | 21 | $0.90 |
| Animate | about 9% | 6 min | 52 | $1.45 |

Readings came from `/usage` in an interactive session, which also counted that session's own turns, so the jobs used slightly less. One Short is about 14% of a session limit, before revisions. Two a night fit comfortably in a session you are asleep for. The weekly limit was not measured; log `/usage` across the first week of Phase 2. If Pro is too tight, the fallback is a pay-per-use API key.

**What the trial showed about the jobs.** The script job produced a sound, verified script (0006 The Six Frogs) with no help. The animate job produced a 48.5 s preview that followed the format and had correct math, but its layout was sparse, about where an interactive first preview starts. You watched it and judged it good. **Decided: continue on Pro.** Three commands per job were denied: compound shell commands and scratch scripts do not match a prefix allowlist, so widen it or tell the job to run commands one at a time. A job in a worktree also does not load your auto-memory, because memory is keyed by project path, so job prompts must carry those preferences (the hook rule, for example).

**Pro is allowed for this, within limits.** Anthropic's Consumer Terms bar scripted access unless Anthropic explicitly permits it. Its docs do describe setup tokens for scripts, and its help center says claude -p uses subscription limits. Its legal page adds that plan limits assume ordinary, individual use, so keep volume modest.

## The messaging channel

Use a private Discord server with one bot, one thread per Short, and only your account allowed to act. Replies wait in the channel, so the system can read them whenever it next runs.

| Option | Replies are easy to read | Anonymity | Verdict |
| --- | --- | --- | --- |
| Discord | Yes: threads and reactions | Your account is fine in a private server | **Use this** |
| Telegram | Yes: bot messages and reactions | Tied to a phone number | Workable second choice |
| Email | No: quoted text and signatures are messy to parse | Needs the channel's Gmail, not yours | Avoid |

**What you do**

| Your action | Where | Meaning |
| --- | --- | --- |
| React with a check mark | Script message | Accept the script and start animating |
| Reply with text | Any message in the thread | Comment, which starts a revision |
| React with a check mark | Video message | Approve this exact version |
| React with a cross | Any message in the thread | Abandon the draft |
| React with a stop sign | Scheduled confirmation | Pull the video before it goes public |

**Why reactions, not words.** A reaction sits on one specific message, so it identifies the version without any interpretation. A model reads your comments, but no model decides whether something is approved. This keeps rule 4 deterministic.

**Rules the orchestrator enforces**

- It acts only on your Discord user ID and ignores everyone else.
- A check mark on a superseded version does nothing, and the bot says why.
- If a version has both a check mark and a new comment, the comment wins and the bot asks you to confirm.
- It records the last message processed, so a restart never repeats an action.
- It confirms every action in the thread, including the scheduled release time.

**Polling.** A job reads the threads every few minutes with Discord's [Get Channel Messages and Get Reactions](https://docs.discord.com/developers/resources/message) endpoints. The bot needs the Message Content intent enabled, otherwise comment text arrives empty.

## YouTube

Upload each version as a private video, then schedule that same video on approval. YouTube makes it public at the set time, so the pipeline does not need to be running at release.

**The flow**

1. Upload with `videos.insert` as private, with title, description and tags.
2. Poll `videos.list` until processing succeeds, and only then send you the link.
3. On approval, call `videos.update` with `privacyStatus: private` and `publishAt`. The [API requires](https://developers.google.com/youtube/v3/docs/videos) both, and only allows this on a video that has never been published.
4. Delete superseded versions with `videos.delete`, so private drafts do not pile up.
5. After the release time, check the video is public and record it. This replaces `ms published`.

**Set these on every upload**

- `selfDeclaredMadeForKids: false`, subject to your confirmation. [Made-for-kids videos lose comments](https://support.google.com/youtube/answer/9527654), which would break the "Comment just the number" format.
- `privacyStatus: private`, always explicit. The [API default is public](https://developers.google.com/youtube/v3/docs/videos), so a missing field could publish an unapproved draft.

**Quota is not a constraint**

| Limit ([source](https://developers.google.com/youtube/v3/determine_quota_cost)) | Amount | Our use |
| --- | --- | --- |
| `videos.insert` | 100 calls a day, in its own bucket | About 2–6 a day |
| Other calls | 10,000 units a day | 50 per update or delete, 1 per list |

Older guides quote about 1,600 units per upload. Google [cut it in December 2025 and moved uploads to their own bucket in June 2026](https://developers.google.com/youtube/v3/revision_history).

**The audit question: tested, not locked (2026-11-02).** `#9` said uploads stay locked private until a compliance audit, and Google's own pages disagreed. `scripts/youtube_test.py` settled it from a new, unverified API project (OAuth app in Testing status), uploading two blank cards:

| Upload as | After processing | Set to private with `publishAt` a week out |
| --- | --- | --- |
| Unlisted | Stayed unlisted | Accepted |
| Private | Stayed private | Accepted |

Both cards were deleted before their release times, so nothing went public. **Approval can be fully automatic, as designed**, and the hand-upload fallback is not needed. Limits of the test: no video has yet actually gone public by `publishAt` (the first real release in Phase 4 proves that); each card existed only a few minutes, so a later lock is not ruled out; and the app was in Testing, not Production. After `videos.update`, `publishAt` took up to about 30 seconds to appear in `videos.list`, so code that confirms a schedule must re-read rather than check once.

**Private or unlisted previews.** The API allows unlisted uploads, and they are easier to watch because any signed-in phone can open the link. The test showed an unlisted video can still be scheduled, so unlisted previews are an option. Private remains the default until you choose; decide before Phase 3.

**Two easy mistakes**

- **OAuth:** keep the Google app in Production status. In Testing, [refresh tokens expire after 7 days](https://developers.google.com/identity/protocols/oauth2), which would silently stop uploads each week. A token also dies after six months unused, or if access is revoked.
- **Viewing:** [private videos are visible only to you and people you invite](https://support.google.com/youtube/answer/157177), and invites use email. Sign the YouTube app into the channel account on your phone instead, which keeps personal email out of it.

## Safe to publish unseen

A Short can go public without another look because every check runs before you see it, and nothing is produced after you approve it. Your review covers the exact bytes and metadata that go live.

| Gate | Runs | Catches | On failure |
| --- | --- | --- | --- |
| `verify.py` | Before the script is sent, and before each video | A wrong answer or claim | Job retries, then flags you |
| Source and license check | Script job | Banned sources, a missing credit | Job picks another puzzle |
| `ms check` format rules | Before upload | Duration, safe zone, overlaps, beat order, caption length, music credit | Job fixes it, then flags you |
| On-screen match | Before upload | Captions or numbers that differ from `verify.py` and `short.yaml` | Job fixes it, then flags you |
| File and upload match | After upload | A wrong or corrupted file, wrong metadata | Stop and flag you |
| Version match | At approval | Approval of an old version, or of one with changed files | Refuse and say why |
| Schedule rules | At approval | A slot over the daily cap | Pick the next valid slot |
| Release check | After release time | A video that did not go public | Flag you |

**Approval freezes the Short.** The orchestrator commits the approved state and tags it, then records the video's hash and YouTube ID. Later changes to `lib/` cannot affect a scheduled Short, because it never renders again.

**`ms check` needs to inspect the scene, not just pixels.** It can examine Manim objects at each animation for exact bounds and overlaps. Pixel checks and a Claude review of sampled frames can then cover what geometry cannot, such as whether something reads clearly.

**What this does not cover.** The gates check rules and math. They cannot judge whether a Short is good, which is what your two reviews are for. YouTube can also act on a video after release, such as a copyright claim on our recording, so that remains a monitoring task and not a pre-publish guarantee.

## Publish scheduling

Assign each approved Short the next open daily slot, and set its release time immediately. A simple rule is enough until analytics can show a better one.

**Hard rules**

- At most 1 public Short a day by default. Rule 1 caps it at 2.
- At least 2 hours between approval and release, leaving time to pull a Short.
- No two consecutive Shorts share a main tag, unless that is the only way to fill a slot.

**Soft preferences, in order**

1. Fill the earliest open slot.
2. Prefer the longest-approved Short.

**Settings in `config/schedule.yaml`**

| Setting | Proposed value |
| --- | --- |
| Daily slot | 5:00 PM |
| Time zone | `America/New_York`, so the slot holds through daylight saving |
| Maximum per day | 1 |
| Alert below | 3 days of scheduled Shorts, matching OPERATING.md |

**Changes to the schedule.** Scheduled Shorts keep their slots. If you pull one, its slot goes to the next Short you approve, and the rest stay put. Stable release times are easier to trust.

**What this replaces.** The rule stops a day like 2026-11-01, when three Shorts were recorded as published. That date only shows when `ms published` ran, so they may have released on different days. The system would now enforce the limit either way.

## Infrastructure, secrets and policy

Decided: run on this laptop under WSL for now, and move to a small always-on server only if missed runs become a problem. YouTube handles releases and Discord holds your replies, so a sleeping laptop causes delays, not lost work.

|  | Laptop (WSL) | Small server |
| --- | --- | --- |
| Scheduling | Windows Task Scheduler with wake enabled | Cron |
| When it misses | Sleep, power loss, or being away | Rarely |
| Effect of a miss | Scripts arrive late | None |
| Added work | Move the repo off `/mnt/c`, fix `#17` | Hosting, backups, and the Docker image from `#13`, with at least 2 GB of RAM |
| Use when | Phases 0–4 | Missed runs start to matter |

**Components**

- **Orchestrator:** a new `ms tick`, run every few minutes under a lock. It reads replies, advances states and starts the next job. It holds the YouTube and Discord credentials.
- **Job runner:** runs `claude -p` in a container with only its worktree mounted. Keeping credentials out of a job needs this boundary, because a job with shell access can read files owned by the same user.
- **State:** stays in the existing files, with `short.yaml` for status and an append-only event log per Short. This keeps the "connected only through files" architecture, and no database is needed.
- **Commits:** the orchestrator commits one Short's folder at a time, replacing the broad `git add shorts`.

**Secrets** are `CLAUDE_CODE_OAUTH_TOKEN`, `DISCORD_BOT_TOKEN` and the YouTube OAuth token. All stay in env vars or files outside the repo, and only the Claude token enters a job container. Your Discord user ID also stays out of the repo, in line with rule 6.

**Anonymity.** The Google Cloud project and any hosting should use the channel's identity, not yours. Your own Discord account is fine, because the server is private and nothing there is public. A leaked bot token also cannot react as you, so it cannot approve a Short. Payment accounts may still link to you privately, so check each one before signing up.

**Policy changes**

| Where | Today | Proposed |
| --- | --- | --- |
| CLAUDE.md rule 4 | "The human approves and the human uploads" | "The human approves every Short, and the system uploads only what was approved. Never approve a Short or change status without the user explicitly saying so; status changes only go through ms commands" |
| CLAUDE.md status machine | `drafting` to `published` | The new states in the flow section |
| OPERATING.md | Weekly session, morning upload | Daily reviews in Discord |
| `/draft-short` | Interactive, pitch step | Stays for manual work; job prompts share its rules |

**YouTube policy needs the most care.** The [inauthentic content policy](https://support.google.com/youtube/answer/1311392) does not ban automation or templates, but says the result must show your creative vision. It flags content that "looks like it's made with a template", and it allows identical intros and outros when the main content differs.

That puts a limit on the scene base class: it may own the frame, never the solution animation. Three safeguards apply:

- Your script review stays mandatory, and that is the creative direction.
- Each script names a visual idea not used by a recent Short, and you can reject it.
- The 1–2 a day limit stays, however many drafts the system can produce.

## Failure modes

Every failure either retries safely or stops and tells you. None can make a Short public, because only a version-matched approval sets a release time.

| Failure | Effect | Response |
| --- | --- | --- |
| Job crashes or hits its budget | No new version | Retry once, then flag you in the thread |
| Job hits a Pro limit | Draft arrives late, and interactive Claude use may be blocked too | Retry after the limit resets |
| Job fails the same check twice | Draft cannot advance | Move to `needs_attention`; you can resume with `/draft-short <n>` |
| Upload or processing fails | No link sent | Retry, then flag you |
| Crash between upload and saving the video ID | A duplicate private video | Find it by file hash and delete it on the next run |
| YouTube token stops working | Uploads pause | Alert you and pause video jobs; script jobs continue |
| Discord is unavailable | Messages wait | Hold outgoing messages and retry; nothing changes state |
| Two runs overlap | Possible double action | Lock file, plus the record of processed messages |
| Accidental approval | Short is scheduled | Stop sign removes the release time, up until release |
| Comment is misread | Wrong revision | You see a new version before anything can publish |
| Laptop off at release time | Release still happens | YouTube publishes; the release check runs later |
| You stop replying | Drafts wait | Reminder after 3 days; queue limits pause new drafts |
| Schedule runs low | Gap ahead | Alert below 3 days of scheduled Shorts |
| Problem found after release | Public video has a fault | You decide. Nothing is automated here, as with today's process |

## Rollout

Build in five phases and keep today's process working until Phase 4 passes. The order matters: the format checks come before unattended jobs, because they are what make those jobs safe to trust.

| Phase | Work | Gate before the next phase |
| --- | --- | --- |
| 0 Foundations | Fix #17 and the publish commit; move off `/mnt/c`; raise bitrate; run the YouTube test and trial Pro jobs | Audit and Pro usage known; tests pass on a clean run |
| 1 Quality gates | Build `ms check`, on-screen match and file checks; build the scene base class for the frame only | `ms check` catches 0003; one Short on the base class |
| 2 Script loop | Build the Discord bot, `ms tick` and new statuses; run the script job, with you still animating interactively | One week of scripts; usage per job logged |
| 3 Video loop | Run animate and revise jobs in containers; upload private versions; approve by check mark; you still release by hand | Five Shorts approved without a terminal |
| 4 Auto release | Add scheduling, the release check and the stop sign; retire nightly batch, ready kits and `ms published` | Two weeks with no action after any approval |

I have not estimated durations, because the job costs and the audit result are still unknown.

**Migration**

- **0001 to 0005** are all `published`, and need no change.
- **Existing commands** keep working through Phase 3, so you can fall back to a manual Short at any point.
- **Documentation** changes with each phase: CLAUDE.md, OPERATING.md and ISSUES.md, as the repo already requires. `#9`, `#13` and `#17` are absorbed into this plan, and `#11` is largely replaced by Discord.

## Open decisions

None are open: the rule 4 rewording was made on 2026-11-03, ahead of Phase 3.

- [x] **Accept "render once, publish the approved file"?** Recommended. Everything after the Summary assumes it.
- [x] **Reword rule 4 so the system uploads? Done (2026-11-03)**, with the wording in the policy table.
- [x] **Discord as the channel?** Recommended, with reactions as the only way to approve.
- [x] **Which daily release time? Decided: 5:00 PM.** It can change later, once there is audience data.
- [x] **Mark Shorts as not made for kids?** Recommended, because the format depends on comments. Puzzles aimed at general audiences fit this, but the legal declaration is yours to make.

Phase 0 measured the two unknowns: uploads are not locked private, and one Short takes about 14% of a Pro session limit (see YouTube and Unattended drafting). Still open: the weekly Pro limit, and private or unlisted previews.

## Sources

Checked on 2026-11-01:

- [YouTube: `videos.insert`](https://developers.google.com/youtube/v3/docs/videos/insert), [video resource](https://developers.google.com/youtube/v3/docs/videos), [quota costs](https://developers.google.com/youtube/v3/determine_quota_cost), [audits](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits), [revision history](https://developers.google.com/youtube/v3/revision_history)
- [YouTube Help: monetization policies](https://support.google.com/youtube/answer/1311392), [made for kids](https://support.google.com/youtube/answer/9527654), [privacy settings](https://support.google.com/youtube/answer/157177)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2), [Discord messages API](https://docs.discord.com/developers/resources/message), [Claude Code headless mode](https://code.claude.com/docs/en/headless)
