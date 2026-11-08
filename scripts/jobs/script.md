# Job: script

You are running unattended, from `ms tick --draft`. Nobody will answer questions, so do not stop to ask for an OK. Your job ends at a written, verified script. Do not write `scene.py` or render anything.

Follow CLAUDE.md, and steps 1, 3 and 4 of `.claude/skills/draft-short/SKILL.md`, with these changes:

1. Choose the puzzle yourself, as in the skill's `pick` path. Then run `ms new <id> --scripting` (the flag matters: it puts the Short in the script loop). Run it once only.
2. Write `verify.py` and get `ms verify <n>` passing before anything else in the Short.
3. Fill `short.yaml`. Never edit `status`. The Discord thread opens with `title` and `level1.statement` in plain view, so neither may give away the answer or the trick; `level1.statement` is the full puzzle as the Short poses it.
4. Write `SCRIPT.md` in the Short's folder, under 1,800 words, with these sections:
   - **Puzzle**: catalog id, one line on why you chose it, and the runner-up.
   - **Hook**: the opening on-screen text (about 3–4 s): the puzzle's question.
   - **Retelling**: the puzzle in our own words.
   - **Insight**: the one visual idea that solves it, and how it is animated. It must differ from the recent Shorts' visual ideas: read their `SCRIPT.md` or `scene.py` docstring and say which you checked.
   - **Beats**: a numbered list with the caption for each (see the caption preference below) and rough seconds, totalling about 40–50.
   - **Level 2**: the question, its answer and why. No calculator; a single number or word.
   - **Music**: a key from `ms music`, preferring the ones it lists first and avoiding the last few used.
   - **Risks**: anything ambiguous in the original wording, or a figure we must recreate.

## The reviewer's standing preferences
- Hooks: pop in the figure, then ask the puzzle's actual question as one full, natural sentence (e.g. "Can you place 8 rooks so that none of them attack each other?"). No slogans, clever teaser lines or fragments.
- Captions: write each one the way a native speaker would say it out loud: a natural phrase or sentence with its articles and verbs, one idea per caption. No headline-style fragments ("8 rooks. Every square covered."). Readable on a phone means roughly 14 words at most, not as few as possible.

## How to run commands
Run one command per Bash call: no `&&`, `;`, pipes or `cd`. Do not write scratch scripts to run; put checks in `verify.py`. Anything not on the allowlist is denied, not asked about.

Do not run `git`, and do not approve, reject or publish anything. Finish with the structured result: `short` is the folder name (e.g. `0006-the-six-frogs`), and `summary` is two or three lines for the reviewer. The reviewer tries each puzzle before seeing its solution: tick shows the summary behind a Discord spoiler, but keep the answer and the trick out of it anyway.
