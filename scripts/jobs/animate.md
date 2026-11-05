# Job: animate

You are running unattended, from `ms tick`. Nobody will answer questions, so do not stop to ask for an OK. The reviewer accepted this Short's script in Discord. Your job ends at a scene that passes `ms check`, with a full preview you have looked at. `ms tick` then renders the final video and sends it for review.

Follow CLAUDE.md, and steps 5 and 6 of `.claude/skills/draft-short/SKILL.md`, with these changes:

1. Read the Short's `SCRIPT.md` (the accepted script: build from its beats and captions), `short.yaml`, `verify.py`, and `events.jsonl` (the reviewer's earlier comments).
2. Write `scene.py`, class `Short`, importing its shapes and numbers from `verify.py`. The solution animation must be custom to this puzzle; only the frame (hook, captions, countdown, Level 2 card) is shared.
3. Run `ms preview <n>`, pull 6–10 frames with `ffmpeg -ss T -i <video> -frames:v 1 <png>` and look at them: overlaps, text off-screen, leftover objects, unreadable sizes, empty stretches. Fix what you find and render again. Fill the frame: a sparse layout is the most common fault.
4. Run `ms check <n>` and fix every error. Warnings are targets; aim for 40–50 s.
5. Keep `short.yaml`'s `captions` in step with the scene, and `ms verify <n>` passing. Never edit `status`.
6. Finish with a full `ms preview <n>` after your last change.

## The reviewer's standing preferences
- Hooks: pop in the figure, then ask the puzzle's actual question in plain words. No slogans or clever teaser lines.

## How to run commands
Run one command per Bash call: no `&&`, `;`, pipes or `cd`. Do not write scratch scripts to run. Anything not on the allowlist is denied, not asked about. Do not use `--open`.

Do not run `git`, and do not approve, reject or publish anything. Finish with the structured result: `short` is the folder name, and `summary` is two or three lines for the reviewer (length, and anything you were unsure about). The reviewer tries each puzzle before seeing its solution: tick shows the summary behind a Discord spoiler, but keep the answer and the trick out of it anyway.
