---
name: draft-short
description: Draft or revise a Master Math USA Short. Use for /draft-short <catalog-id> (start a new Short from a catalog puzzle), /draft-short pick (choose the puzzle yourself from `ms suggest`), /draft-short <number> (resume one, e.g. after `ms reject` or with open notes), or when the user gives feedback on a preview.
---

# Draft a Short

You are the animator; the user is the director. They decide what's good. You never approve a Short on your own.

Read CLAUDE.md first if you haven't this session (rules, format, layout).

## 1. Get oriented
- **Catalog id** (e.g. `dudeney-amusements-087`): `ms show <id>` to read the puzzle and the book's solution, then `ms new <id>`. If the puzzle has a figure, the HTML edition linked in the output has it; recreate the figure yourself in Manim.
- **`pick`, no argument, or "you choose"**: choose the puzzle yourself.
  1. Run `ms suggest -n 10`. Ties are listed in id order, so if the ten are bunched in one or two sections, run `ms suggest -n 30` to see past them.
  2. `ms show` your 3–4 favourites and choose the one with a single visual insight that fits 40–50 seconds, a statement that retells clearly in a few natural sentences, an answer you can check in code, and a natural Level 2. Avoid the tags of the latest Shorts. The score is a coarse first pass (a keyword heuristic); use your judgement over it.
  3. Go to step 2. Add the puzzle's id, one line on why you chose it, and a runner-up to the top of the pitch. Run `ms new <id>` only after the user OKs the pitch, so a rejected pick leaves no folder behind.
- **Short number** (e.g. `7`): read `shorts/0007-*/short.yaml`, `NOTES.md` (open items are your to-do list) and the latest `out/preview/0007-*/beats.json`. If it has a `SCRIPT.md` (a script the user accepted in Discord), that is the agreed pitch: skip step 2, keep `verify.py` passing, and build the scene from its beats.

## 2. Pitch before animating (new Shorts only)
Before writing any scene code, run `ms music`, then give the user a 5-line pitch and wait for an OK:
- **Hook** (the opening on-screen text, about 3–4 s: the puzzle's question as one full, natural sentence)
- **Insight** (the one visual idea that solves it)
- **Level 2** (same trick, one step further; a single number or word; solvable without a calculator)
- **Risk** (anything ambiguous in the original wording, or a figure we must recreate)
- **Music** (a library key that fits the Short's mood; prefer the pieces `ms music` lists first and avoid the last few used)

## 3. Verify first
Write `verify.py`: check every claim the video makes, in code (geometry with shapely, numbers with fractions or sympy). Expose the exact shapes and numbers the scene will draw, so the video shows what was checked. Run `ms verify <n>` until it passes.

## 4. Fill short.yaml
`title`, `level1`, `level2` (with `accept`: every reasonable way a commenter writes the answer, and a one-line `why`), `captions`, `music.piece` (the agreed library key), `youtube` (title under 100 chars, description crediting the source and, word for word, `Music: <credit>` from `ms music`; `ms approve` refuses otherwise), `source.credit`. Change `status` only through `ms` commands.

## 5. Build the scene
`scene.py`, class `Short`, built from `lib/components.py`: `hook`, `Captions` (every `show` marks a beat), `pause_and_try`, `badge`, `footer`, plus `beat(self, "name")` for beats without a caption. The format, in order: hook, problem builds, "Pause and try it" with a 5-second countdown, animated insight and solution, ✓ payoff, Level 2 card, "Comment just the number ↓" held about 12 seconds. Aim for 40–50 seconds. Keep everything inside the safe zone in `lib/layout.py`.

The pause is one call: `pause_and_try(self, cap, "How many routes could the monk take?", tick_sound=SFX["tick"])`. It shows "Pause and try it", keeps the question (two lines at most) on screen above it, and runs the 5-second countdown in whichever slot of `PAUSE_SLOTS` (`top`, `top-right`, `top-left`, `low`, `middle`, `right`, `left`) covers the least of what is on screen. The puzzle must stay fully in view during the pause, so don't hide or dim it. Pass `slot="..."` to choose the slot yourself, or `extra=[...]` to clear things away first (the slot is picked after they're gone). Use plain `countdown` only in older Shorts.

## 6. Preview, check it yourself, then show it
- `ms check <n>` and fix every error (safe zone, text overlaps, beat order, a countdown ring covering the puzzle or no question shown during it, captions and numbers that differ from `short.yaml` or `verify.py`). Warnings are targets: mention them to the user rather than forcing a fix. It checks the end of each animation only, so frames still matter.
- `ms preview <n>`. Before showing the user, pull 6–10 frames (`ffmpeg -ss T -i … -frames:v 1 …png`) and look at them yourself: overlaps, text off-screen, leftover objects, unreadable sizes. Fix what you find first.
- Then `ms preview <n> --open` and give the user a short beat list with timestamps (from beats.json).

## 7. Feedback loop
For each piece of feedback, in chat or from NOTES.md:
1. Record it if it isn't there yet: `ms note <n> "0:12 slide too fast"`.
2. Fix it in `scene.py` (or `verify.py` / `short.yaml`).
3. Re-render just that beat: `ms preview <n> --at 0:12`, then `ms compare <n> --open` so the user sees before and after.
4. Tick it in NOTES.md (`- [x]`) once the user is happy with that fix.

After several beat fixes, do one full `ms preview <n>` so timing is checked end to end.

If a requested change belongs in `lib/` (fonts, colors, a component every Short uses), don't hack it into this scene. Add it to ISSUES.md and tell the user.

## 8. Approval (only when the user says so)
Only when the user explicitly says "approve" (or equivalent):
1. All notes ticked? If not, ask.
2. `ms approve <n>`. It runs verify and refuses with open notes. Don't use `--force` unless the user asks.
3. Commit: `git add shorts/<folder> && git commit -m "<number>: approved"`.
4. Tell them it renders in tonight's batch, or now with `ms batch <n>`.

Alternatively, if the user says to send it to Discord instead (the video loop, #29): `ms animate <n> --as-is`. The next `ms tick` renders it and posts the video in its Discord thread, and the user approves it there with ✅ (only then is it uploaded). Don't run both.

## Don'ts
- Don't edit `status` by hand or approve without the user's explicit OK.
- Don't use AMC/AIME/AoPS/Brilliant problems or any unlicensed material.
- Don't put real people's photos or clips in a Short.
- Don't make Level 2 answers that need a calculator.
