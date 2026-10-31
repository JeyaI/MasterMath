---
name: work-issue
description: Work an item from ISSUES.md, the project's backlog. Use for /work-issue <id>, "next issue", "work the backlog", or when asked to fix or build something tracked there.
---

# Work an issue

1. **Pick.** Read ISSUES.md. Use the given id, or the highest-priority `open` issue (P1 before P2 before P3, then lowest id). Set its status to `doing`.
2. **Plan.** In 3–5 lines, say what you'll change and how you'll know it works. If it's more than about an hour of work, touches `lib/` (shared by every Short), or changes the human workflow, wait for the user's OK.
3. **Build.** Small, focused changes. Follow CLAUDE.md conventions.
4. **Check.**
   - `python -m pytest -q` passes; add a test when the change is testable.
   - If `lib/` changed: `ms preview` at least one existing Short and look at frames, since every Short shares lib.
   - If the human workflow changed: update OPERATING.md in the same change.
5. **Close.** Move the issue to **Done** with today's date and a one-line resolution. Add any follow-ups you discovered as new issues (next id at the top of the file).
6. **Commit:** `git commit -m "#<id>: <title>"`.

If you hit something you can't resolve (missing access, an unclear product decision), set the issue to `blocked`, write why in it, and tell the user.
