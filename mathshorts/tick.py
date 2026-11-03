"""`ms tick`: the orchestrator for the script loop (#28, docs/pipeline-design.md).

Run every few minutes (scripts/tick.sh). Each tick, under a lock:

1. Reads each script thread in Discord. Only your account counts:
   - a cross on any version            -> abandoned
   - a reply                           -> revise, with your words as the job's brief
     (a reply wins over a check mark left at the same time; the bot says so)
   - a check mark on the newest version -> drafting: you take it from there with /draft-short
   - a check mark on an older version  -> nothing; the bot says which version is current
2. Runs the revise job for each Short in `revise` (one try and one retry), then posts the new version.
3. With --draft, starts one script job if the queue has room, and posts the script.

A job's own claims are not trusted: tick runs verify.py itself before anything is posted.
No model decides an approval: reactions are read as data. Every change is committed, one Short per
commit, and logged to the Short's events.jsonl.
"""
from __future__ import annotations

import fcntl
import shutil
import subprocess
from contextlib import contextmanager
from typing import Callable

from . import jobs, paths, yamlio
from .discord import ACCEPT, CROSS
from .shorts import SCRIPT_LOOP, Short, all_shorts

ATTEMPTS = 2


def limits() -> dict:
    cfg = yamlio.load(paths.config() / "pipeline.yaml") if (paths.config() / "pipeline.yaml").exists() else {}
    return {"max_waiting": 4, "max_queued": 7, **(cfg or {})}


@contextmanager
def lock():
    p = paths.out() / ".tick.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    f = open(p, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        yield False
        return
    try:
        yield True
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


class Tick:
    def __init__(self, discord, user_id: str, runner: Callable = jobs.run, echo=print, commit: bool = True):
        self.d, self.user, self.runner, self.echo, self.commit_on = discord, str(user_id), runner, echo, commit

    # --- entry point -----------------------------------------------------------------
    def run(self, draft: bool = False) -> dict:
        done = {"accepted": [], "abandoned": [], "revised": [], "scripted": [], "failed": [], "skipped": None}
        with lock() as got:
            if not got:
                done["skipped"] = "another tick is running"
                return done
            for s in [s for s in all_shorts() if s.status == "script_review"]:
                self.read_thread(s, done)
            for s in [s for s in all_shorts() if s.status == "revise"]:
                self.revise(s, done)
            if draft:
                why = self.no_room()
                if why:
                    done["skipped"] = why
                else:
                    self.script(done)
        return done

    def no_room(self) -> str | None:
        lim, shorts = limits(), all_shorts()
        waiting = sum(s.status in SCRIPT_LOOP for s in shorts)
        queued = sum(s.status in ("approved", "ready") for s in shorts)
        if waiting >= lim["max_waiting"]:
            return f"{waiting} scripts already waiting on you (max_waiting: {lim['max_waiting']})"
        if queued >= lim["max_queued"]:
            return f"{queued} Shorts already approved or ready (max_queued: {lim['max_queued']})"
        return None

    # --- 1. your reactions and replies ---------------------------------------------------
    def read_thread(self, s: Short, done: dict) -> None:
        rv = dict(s.data().get("review") or {})
        thread, current = rv["thread_id"], int(rv["version"])
        versions = {int(k): str(v) for k, v in (rv.get("messages") or {}).items()}
        mine = lambda mid, emoji: self.user in self.d.reactors(thread, mid, emoji)  # noqa: E731

        if any(mine(mid, CROSS) for mid in versions.values()):
            self.change(s, "abandon", f"{s.number}: abandoned", event={"version": current})
            self.d.post(thread, "❌ Abandoned. Its puzzle goes back in the pool.")
            done["abandoned"].append(s.name)
            return

        new = [m for m in self.d.messages_after(thread, rv.get("last_seen"))
               if m["author_id"] == self.user and not m["bot"]]
        comment = "\n\n".join(m["content"].strip() for m in new if m["content"].strip())
        if new:
            rv["last_seen"] = new[-1]["id"]
        accepted = mine(versions[current], ACCEPT)

        if comment:
            rv["comment"] = comment
            s.update(review=rv)
            self.change(s, "comment", f"{s.number}: revising script v{current}",
                        event={"version": current, "comment": comment})
            note = " Your ✅ was set aside, since a comment wins; react again on the new version." if accepted else ""
            self.d.post(thread, f"Revising v{current} with your comment.{note}")
            return
        if accepted:
            s.update(review=rv)
            self.change(s, "accept_script", f"{s.number}: script v{current} accepted", event={"version": current})
            self.d.post(thread, f"✅ v{current} accepted. Animate it in Claude Code: `/draft-short {s.number}`.")
            done["accepted"].append(s.name)
            return

        told = set(int(v) for v in rv.get("told_superseded") or [])
        for v, mid in versions.items():
            if v < current and v not in told and mine(mid, ACCEPT):
                self.d.post(thread, f"v{v} is superseded. React ✅ on v{current} to accept it.")
                told.add(v)
        if told != set(int(v) for v in rv.get("told_superseded") or []):
            rv["told_superseded"] = sorted(told)
        if rv != (s.data().get("review") or {}):
            s.update(review=rv)
            self.commit(s, f"{s.number}: review read")

    # --- 2. revise ---------------------------------------------------------------------
    def revise(self, s: Short, done: dict) -> None:
        rv = dict(s.data().get("review") or {})
        result, error = self.attempt("revise", s.name, rv.get("comment", ""))
        if result is None:
            self.fail(s, error, done, thread=rv.get("thread_id"))
            return
        version = int(rv["version"]) + 1
        mid = self.post_version(rv["thread_id"], s, version, result.summary)
        rv.update(version=version, comment=None)
        rv.setdefault("messages", {})[version] = mid
        s.update(review=rv)
        self.change(s, "revised", f"{s.number}: script v{version}", event={"version": version, "usage": result.usage})
        done["revised"].append(s.name)

    # --- 3. a new script -----------------------------------------------------------------
    def script(self, done: dict) -> None:
        result, error = self.attempt("script")
        if result is None:
            s = Short(paths.shorts() / error[0]) if error[0] and (paths.shorts() / error[0]).is_dir() else None
            if s and s.status == "scripting":
                self.fail(s, error[1], done)
            else:
                self.echo(f"  script job failed: {error[1]}")
                done["failed"].append(error[1])
            return
        s = Short(paths.shorts() / result.short)
        if s.status != "scripting":
            self.fail(s, f"the job left {s.name} in {s.status!r}, not 'scripting'", done)
            return
        title = f"{s.number} · {s.data().get('title') or s.name}"
        thread = self.d.open_thread(title)
        mid = self.post_version(thread, s, 1, result.summary)
        s.update(review={"thread_id": thread, "version": 1, "messages": {1: mid}, "last_seen": mid})
        self.change(s, "script_done", f"{s.number}: script v1", event={"version": 1, "usage": result.usage})
        done["scripted"].append(s.name)

    # --- helpers -----------------------------------------------------------------------
    def attempt(self, kind: str, short: str | None = None, comment: str | None = None):
        """Run a job up to ATTEMPTS times; a run only counts if verify.py passes here, in the main checkout.
        Returns (result, None) or (None, error); for script jobs the error is (folder name or None, text)."""
        error, name = "", short
        for n in range(ATTEMPTS):
            r = self.runner(kind, short, comment)
            name = r.short or name
            if r.ok:
                ok, out = Short(paths.shorts() / r.short).verify()
                if ok and (paths.shorts() / r.short / "SCRIPT.md").exists():
                    return r, None
                r.error = "verify.py fails" if not ok else "no SCRIPT.md"
                if not ok:
                    r.error += f": {out.splitlines()[-1] if out else ''}"
                if kind == "script" and n < ATTEMPTS - 1:
                    shutil.rmtree(paths.shorts() / r.short)    # uncommitted; the retry starts fresh
            error = r.error
            self.echo(f"  {kind} job: {error}")
        return None, ((name, error) if kind == "script" else error)

    def post_version(self, thread: str, s: Short, version: int, summary: str) -> str:
        head = (f"**Script v{version}** · {s.data().get('title') or s.name}\n{summary.strip()}\n\n"
                f"React {ACCEPT} to accept, {CROSS} to abandon, or reply to revise.")
        return self.d.post(thread, head, files={f"{s.number}-script-v{version}.md": s.folder / "SCRIPT.md"},
                           reactions=(ACCEPT, CROSS))

    def fail(self, s: Short, error: str, done: dict, thread: str | None = None) -> None:
        s.update(last_error=error[:200])
        self.change(s, "job_failed", f"{s.number}: needs attention", event={"error": error})
        if thread:
            self.d.post(thread, f"⚠️ The job failed twice: {error[:300]}\nIt needs you in Claude Code: "
                                f"`/draft-short {s.number}`, or ❌ to abandon.")
        done["failed"].append(s.name)

    def change(self, s: Short, action: str, message: str, event: dict | None = None) -> None:
        new = s.transition(action)
        s.log_event(action, status=new, **(event or {}))
        self.echo(f"  {s.name}: {new}")
        self.commit(s, message)

    def commit(self, s: Short, message: str) -> None:
        if not self.commit_on:
            return
        rel = s.folder.relative_to(paths.root()).as_posix()
        subprocess.run(["git", "add", "--", rel], cwd=paths.root(), capture_output=True)
        r = subprocess.run(["git", "commit", "-q", "-m", message, "--", rel], cwd=paths.root(),
                           capture_output=True, text=True)
        if r.returncode:
            self.echo(f"  not committed: {message}")
