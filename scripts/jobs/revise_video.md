# Job: revise a video

You are running unattended, from `ms tick`. Nobody will answer questions. The reviewer watched this Short's video and replied in Discord; their comment is in the prompt. Revise the Short so it does what they asked. `ms tick` then renders the final video and sends the new version for review.

1. Read the Short's `SCRIPT.md`, `short.yaml`, `verify.py`, `scene.py`, `events.jsonl` (earlier comments) and CLAUDE.md. Timestamps in the comment refer to the reviewed video; `ms preview <n>` writes `beats.json` next to the preview, which maps them to beats.
2. Change what the comment asks for, and only that. A comment may change the script itself: then update `SCRIPT.md` too.
3. If the change touches any number, shape or claim, update `verify.py` and get `ms verify <n>` passing.
4. Run a full `ms preview <n>`, pull frames around what you changed with `ffmpeg -ss T -i <video> -frames:v 1 <png>`, and look at them. Then `ms check <n>` must have no errors.
5. Keep `short.yaml` in step. Never edit `status`.
6. If the comment asks for something the rules forbid (CLAUDE.md non-negotiables), don't do it; say so in the summary.

## The reviewer's standing preferences
- Hooks: pop in the figure, then ask the puzzle's actual question in plain words. No slogans or clever teaser lines.

## How to run commands
Run one command per Bash call: no `&&`, `;`, pipes or `cd`. Do not write scratch scripts to run. Anything not on the allowlist is denied, not asked about. Do not use `--open`.

Do not run `git`, and do not approve, reject or publish anything. Finish with the structured result: `short` is the folder name, and `summary` says in two or three lines what changed.
