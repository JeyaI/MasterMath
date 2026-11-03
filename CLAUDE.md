# Master Math USA: project brief for Claude Code

An anonymous YouTube Shorts channel of animated math-puzzle solutions (Manim, 3Blue1Brown-style), loosely modeled on "Master Catur Indonesia". The human runs it from **OPERATING.md**; the backlog is **ISSUES.md**. Brand: `lib/brand.py`. Logo: `python brand/logo.py`.

## Skills
- `/draft-short <catalog-id | pick | number>`: draft or revise a Short with the user; `pick` has Claude choose from `ms suggest` (`.claude/skills/draft-short`).
- `/work-issue [id]`: work the backlog (`.claude/skills/work-issue`).

## Non-negotiables
1. **Originality (YouTube "inauthentic content" policy).** Every Short gets a different puzzle and a custom solution animation. The shared template (hook, captions, countdown, Level 2 card) is fine; a new problem dropped into the same animation is not. At most 1–2 uploads a day.
2. **Licensed sources only.** Allowed: Dudeney (*Amusements in Mathematics*, *The Canterbury Puzzles*, public domain), famous named problems retold in our own words, our own problems, GSM8K (MIT). **Not allowed:** AMC/AIME (MAA), AoPS, Brilliant, the MATH dataset, Project Euler. Log assets in `LICENSES.csv`.
3. **Every answer is checked in code.** `verify.py` must pass before `ms approve` will run, and the scene imports its shapes and numbers from `verify.py`.
4. **The human approves and the human uploads.** Never approve a Short or change `status` without the user explicitly saying so; status changes only go through `ms` commands.
5. **Level 2 is solvable without a calculator**, with a single number or word as the answer (listed in `level2.accept`). The call to action promises nothing ("Comment just the number ↓"; no "answer tomorrow").
6. **Anonymity.** Commits are by `mathshorts`. No personal names or emails in the repo, descriptions or config. Secrets only in env vars.

## The format (every Short)
9:16, 1080×1920, 30 fps, aim for 40–50 s (a target, not a cap), no narration. Beats: hook (0–3 s), problem builds, "Pause and try it" with a 5 s countdown, animated insight and solution, ✓ payoff, Level 2 card (same trick, one step further, not solved), "Comment just the number ↓" held about 12 s. Captions are 2–6 words. Music is a public-domain composition synthesized by `lib/audio.py` (we own the recording), chosen by the `music.piece` key from its `PIECES` library, plus sound effects.

## Architecture: five modules, connected only through files
| Module | Code | Data | Run |
|---|---|---|---|
| Sources → catalog | `mathshorts/catalog.py`, `mathshorts/sources/` | `catalog/sources.yaml`, `catalog/<src>.jsonl` (regenerated), `catalog/annotations.yaml` (judgements; never overwritten) | rarely |
| Draft selector | `mathshorts/selector.py` (pure `rank()`) | `config/selector.yaml` | `ms suggest` |
| Drafting | `.claude/skills/draft-short`, `mathshorts/render.py` (preview, compare), `mathshorts/check.py` + `probe.py` (`ms check`) | `shorts/NNNN-slug/{short.yaml, verify.py, scene.py, NOTES.md}` | weekly, with the user |
| Nightly batch | `mathshorts/batch.py`, `scripts/nightly.sh` | `out/ready/<short>/`, `out/logs/` | nightly |
| Upload | manual for now (`upload.txt` in each kit) | `short.yaml` `youtube.*` | `ms published` |

Shared: `mathshorts/shorts.py` (Short folder + status machine), `mathshorts/yamlio.py` (round-trip YAML, atomic writes), `mathshorts/paths.py` (`MS_ROOT`, `MS_OUT`, `MS_CACHE`), `lib/` (Manim layout, components, audio, brand).

**Status machine** (`mathshorts/shorts.py: TRANSITIONS`): `drafting → approved → ready → published`; batch failure → `failed`; `reject` returns approved/ready/failed to `drafting`; `approve` also works from `failed`.

**Catalog ids** are `<source>-<number>` (e.g. `dudeney-amusements-087`). A Short records its `catalog_id`; "used" is derived from that, never stored in the catalog.

**Beats.** `lib.components.beat()` (called by every `Captions.show`) logs `{t, anim, name}`. A full `ms preview` writes `out/preview/<short>/beats.json`. `ms preview --at M:SS` renders only that beat (Manim `-n start,end`), and `ms note` tags notes with their beat.

## Layout
```
catalog/   sources.yaml · <src>.jsonl · annotations.yaml
config/    selector.yaml
docs/      pipeline-design.md (the overnight pipeline plan; phases are issues in ISSUES.md)
shorts/    NNNN-slug/ short.yaml · verify.py · scene.py (class Short) · NOTES.md
lib/       brand.py (no side effects) · layout.py (9:16 frame, safe zone) · components.py · audio.py
mathshorts/ the `ms` CLI and modules
brand/     logo.py → brand/out/ (gitignored)
scripts/   nightly.sh
tests/     pytest; fixtures/ has parser samples
out/       preview/ build/ ready/ logs/ media/ (gitignored)
```
Safe zone: the Shorts UI covers the bottom ~20% and a right-hand column. Keep content in x ∈ [-3.8, 3.2], y ∈ [-4.6, 7.0] (the frame is 9×16 units). Use `lib.components.CENTRE_X`.

## Conventions
- Run `python -m pytest -q` after code changes. Tests use a temp root via `MS_ROOT`, so they never touch real data.
- Changes to `lib/` affect every Short. Re-preview at least one existing Short and look at the frames.
- When the human workflow changes, update OPERATING.md in the same commit.
- New ideas or bugs go to ISSUES.md (next id at the top).
- Commit messages: `0007: approved`, `#12: <issue title>`, `catalog: add <source>`, `batch <date>`.

## Gotchas
- `LaggedStart(GrowFromCenter(c) for c in group)` adds children individually, so use `self.remove(*group)`.
- Manim's audio track ends at the last `add_sound`; `render.mix` pads it (`apad`) before mixing in music.
- `lib/layout.py` sets config on import (9:16). Brand colors for other frame shapes come from `lib/brand.py`.
- `--resolution` from the CLI wins; `layout.py` only forces 1080×1920 if nothing else set a portrait size.
- font_size values are about 2× Manim defaults because the frame is 16 units tall.
- Gutenberg #16713 has heading slips (`44--TITLE`, a misprinted `384.--`). `TYPOS` and `NO_PERIOD` in `sources/dudeney.py` handle them. One wrong number silently loses every puzzle up to it, so check the counts after any re-scrape (430 puzzles, 429 solutions; #163 has none in the book).
