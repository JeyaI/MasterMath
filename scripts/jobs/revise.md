# Job: revise a script

You are running unattended, from `ms tick`. Nobody will answer questions. The reviewer replied to a script in Discord; their comment is in the prompt. Revise the Short named in the prompt so it does what they asked.

1. Read the Short's `SCRIPT.md`, `short.yaml`, `verify.py`, `events.jsonl` (earlier comments) and CLAUDE.md.
2. Change what the comment asks for, and only that. Keep `SCRIPT.md`'s sections and the 1,800-word limit (see `scripts/jobs/script.md`).
3. If the change touches any number, shape or claim, update `verify.py` and get `ms verify <n>` passing.
4. Keep `short.yaml` in step with the script. Never edit `status`.
5. If the comment asks for something the rules forbid (CLAUDE.md non-negotiables), don't do it; say so at the top of `SCRIPT.md` and in the summary.

## The reviewer's standing preferences
- Hooks: pop in the figure, then ask the puzzle's actual question in plain words. No slogans or clever teaser lines.

## How to run commands
Run one command per Bash call: no `&&`, `;`, pipes or `cd`. Do not write scratch scripts to run. Anything not on the allowlist is denied, not asked about.

Do not run `git`, and do not approve, reject or publish anything. Finish with the structured result: `short` is the folder name, and `summary` says in two or three lines what changed. The reviewer tries each puzzle before seeing its solution: tick shows the summary behind a Discord spoiler, but keep the answer and the trick out of it anyway.
