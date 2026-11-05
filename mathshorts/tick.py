"""`ms tick`: the orchestrator for the script and video loops (#28, #29, docs/pipeline-design.md).

Run every few minutes (scripts/tick.sh). Each tick, under a lock:

1. Reads each Short's Discord thread. Only your account counts:
   - a cross on any version              -> abandoned (its review videos are deleted)
   - a reply                             -> a revise job, with your words as its brief
     (a reply wins over a check mark left at the same time; the bot says so)
   - a check mark on the newest script   -> animating
   - a check mark on the newest video    -> scheduled: that exact upload is set to go public at the
     next open slot (config/pipeline.yaml `release:`), and YouTube releases it
   - a stop sign on the scheduled notice -> back to video_review, unlisted again
   - a check mark on an older version    -> nothing; the bot says which version is current
2. For scheduled Shorts past their release time, checks YouTube and records them as published.
3. Runs revise jobs, then animate and video revise jobs. A video version is rendered, uploaded
   unlisted and posted. If YouTube is down, the render waits and the upload is retried next tick.
4. With --draft, starts one script job if the queue has room, and posts the script.

A job's own claims are not trusted: tick runs verify.py, `ms check` and the final render itself,
in the sandbox (mathshorts/sandbox.py), before anything is posted. No model decides an approval:
reactions are read as data. Every change is committed, one Short per commit, and logged to the
Short's events.jsonl.

No spoilers (#46): a thread opens with the puzzle alone, and everything about the solution (job
summaries, errors, SCRIPT.md, video links) goes inside Discord spoiler tags, so you can try it first.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import re
import shutil
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from . import jobs, paths, release, sandbox, youtube, yamlio
from .discord import ACCEPT, CROSS, STOP
from .shorts import SCRIPT_LOOP, VIDEO_LOOP, Short, all_shorts

ATTEMPTS = 2
LATE = dt.timedelta(hours=1)          # a release this late gets flagged


def spoiler(text: str) -> str:
    """Hide text behind Discord spoiler tags. A `||` or code fence inside would end the spoiler early."""
    text = (text or "").strip().replace("||", "| |").replace("```", "'''")
    return f"||{text}||" if text else ""


def answers(d: dict) -> list[str]:
    """What would give the puzzle away: both levels' answers and Level 2's accepted forms."""
    l1, l2 = d.get("level1") or {}, d.get("level2") or {}
    out = [l1.get("answer"), l2.get("answer"), *(l2.get("accept") or [])]
    return [str(a).strip() for a in out if a is not None and str(a).strip() and str(a).strip() != "TODO"]


def title(s: Short) -> str:
    """The thread and post title, unless it names an answer (a thread title can't hold a spoiler)."""
    d = s.data()
    name = str(d.get("title") or s.name)
    if any(re.search(rf"(?<!\w){re.escape(a)}(?!\w)", name, re.I) for a in answers(d)):
        return f"{s.number} · a new puzzle"
    return f"{s.number} · {name}"


def limits() -> dict:
    cfg = yamlio.load(paths.config() / "pipeline.yaml") if (paths.config() / "pipeline.yaml").exists() else {}
    return {"max_waiting": 4, "max_queued": 7, **(cfg or {})}


DRAFT_WAIT = 45 * 60                  # a --draft tick waits this long for a busy tick (a video job)


@contextmanager
def lock(wait: float = 0):
    """Yields False if another tick holds it after `wait` seconds."""
    p = paths.out() / ".tick.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    f = open(p, "w")
    deadline = time.monotonic() + wait
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                f.close()
                yield False
                return
            time.sleep(min(15, max(deadline - time.monotonic(), 0.1)))
    try:
        yield True
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def review_video(s: Short, version: int) -> Path:
    return paths.out() / "review" / s.name / f"v{version}.mp4"


class Tick:
    def __init__(self, discord, user_id: str, runner: Callable = jobs.run, echo=print, commit: bool = True,
                 youtube_client=None, checks=None, now: Callable[[], dt.datetime] | None = None):
        self.d, self.user, self.runner, self.echo, self.commit_on = discord, str(user_id), runner, echo, commit
        self._yt, self.yt_error = youtube_client, None
        self.checks = checks or sandbox.Checks()
        self.now = now or (lambda: dt.datetime.now(dt.timezone.utc))

    def yt(self):
        """The YouTube client, made on first use. None (with yt_error set) if it can't be had."""
        if self._yt is None:
            try:
                self._yt = youtube.Client()
            except Exception as e:  # noqa: BLE001 - a missing token or library must not stop the script loop
                self._yt, self.yt_error = False, str(e)[:300]
        return self._yt or None

    # --- entry point -----------------------------------------------------------------
    def run(self, draft: bool = False) -> dict:
        done = {"accepted": [], "abandoned": [], "revised": [], "scripted": [], "videos": [], "approved": [],
                "stopped": [], "released": [], "failed": [], "skipped": None, "paused": None}
        with lock(wait=DRAFT_WAIT if draft else 0) as got:     # the nightly script must not be lost
            if not got:
                done["skipped"] = "another tick is running"
                return done
            for s in all_shorts():
                if s.status == "script_review":
                    self.read_thread(s, done)
                elif s.status == "video_review":
                    self.read_video(s, done)
                elif s.status == "scheduled":
                    self.watch_scheduled(s, done)
            for s in [s for s in all_shorts() if s.status == "revise"]:
                self.revise(s, done)
            video = [s for s in all_shorts() if s.status in ("animating", "revise_video")]
            if video and not self.yt():
                done["paused"] = f"video jobs paused, YouTube unavailable: {self.yt_error}"
                self.echo(f"  {done['paused']}")
            else:
                for s in video:
                    self.make_video(s, done)
            if draft:
                why = self.no_room()
                if why:
                    done["skipped"] = why
                else:
                    self.script(done)
        return done

    def no_room(self) -> str | None:
        lim, shorts = limits(), all_shorts()
        waiting = sum(s.status in (*SCRIPT_LOOP, *VIDEO_LOOP) for s in shorts)
        queued = sum(s.status in ("approved", "ready", "scheduled") for s in shorts)
        if waiting >= lim["max_waiting"]:
            return f"{waiting} drafts already in the loops (max_waiting: {lim['max_waiting']})"
        if queued >= lim["max_queued"]:
            return f"{queued} Shorts already approved or scheduled (max_queued: {lim['max_queued']})"
        return None

    def mine(self, thread: str, message: str, emoji: str) -> bool:
        return self.user in self.d.reactors(thread, message, emoji)

    def my_replies(self, thread: str, rv: dict) -> str:
        """Your new messages in the thread, joined; advances rv['last_seen']."""
        new = [m for m in self.d.messages_after(thread, rv.get("last_seen"))
               if m["author_id"] == self.user and not m["bot"]]
        if new:
            rv["last_seen"] = new[-1]["id"]
        return "\n\n".join(m["content"].strip() for m in new if m["content"].strip())

    # --- 1a. scripts: your reactions and replies ---------------------------------------------
    def read_thread(self, s: Short, done: dict) -> None:
        rv = dict(s.data().get("review") or {})
        thread, current = rv["thread_id"], int(rv["version"])
        versions = {int(k): str(v) for k, v in (rv.get("messages") or {}).items()}

        if any(self.mine(thread, mid, CROSS) for mid in versions.values()):
            self.change(s, "abandon", f"{s.number}: abandoned", event={"version": current})
            self.d.post(thread, "❌ Abandoned. Its puzzle goes back in the pool.")
            done["abandoned"].append(s.name)
            return

        comment = self.my_replies(thread, rv)
        accepted = self.mine(thread, versions[current], ACCEPT)

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
            self.d.post(thread, f"✅ v{current} accepted. Animating it now; the video comes back here for review.")
            done["accepted"].append(s.name)
            return

        told = self.superseded(thread, versions, current, rv.get("told_superseded"))
        if told is not None:
            rv["told_superseded"] = told
        if rv != (s.data().get("review") or {}):
            s.update(review=rv)
            self.commit(s, f"{s.number}: review read")

    def superseded(self, thread: str, versions: dict[int, str], current: int, told_) -> list[int] | None:
        """Tell you once about a check mark on an old version. Returns the new told list, if it grew."""
        told = set(int(v) for v in told_ or [])
        before = set(told)
        for v, mid in versions.items():
            if v < current and v not in told and self.mine(thread, mid, ACCEPT):
                self.d.post(thread, f"v{v} is superseded. React ✅ on v{current} to approve it.")
                told.add(v)
        return sorted(told) if told != before else None

    # --- 1b. videos: your reactions and replies ---------------------------------------------
    def read_video(self, s: Short, done: dict) -> None:
        rv, v = dict(s.data().get("review") or {}), dict(s.data().get("video") or {})
        thread, current = rv["thread_id"], int(v["version"])
        versions = {int(k): dict(x) for k, x in (v.get("versions") or {}).items()}

        if any(self.mine(thread, str(x["message"]), CROSS) for x in versions.values()):
            gone = self.delete_videos(versions.values())
            self.change(s, "abandon", f"{s.number}: abandoned", event={"version": current, "deleted": gone})
            self.d.post(thread, "❌ Abandoned. Its review videos are deleted, and its puzzle goes back in the pool.")
            done["abandoned"].append(s.name)
            return

        comment = self.my_replies(thread, rv)
        accepted = self.mine(thread, str(versions[current]["message"]), ACCEPT)
        if comment:
            v["comment"] = comment
            s.update(review=rv, video=v)
            self.change(s, "comment_video", f"{s.number}: revising video v{current}",
                        event={"version": current, "comment": comment})
            note = " Your ✅ was set aside, since a comment wins; react again on the new version." if accepted else ""
            self.d.post(thread, f"Revising video v{current} with your comment.{note}")
            return
        if accepted:
            s.update(review=rv)
            self.approve(s, v, versions[current], current, thread, done)
            return

        told = self.superseded(thread, {k: str(x["message"]) for k, x in versions.items()}, current,
                               v.get("told_superseded"))
        if told is not None:
            v["told_superseded"] = told
        if rv != (s.data().get("review") or {}) or v != (s.data().get("video") or {}):
            s.update(review=rv, video=v)
            self.commit(s, f"{s.number}: review read")

    def approve(self, s: Short, v: dict, ver: dict, n: int, thread: str, done: dict) -> None:
        """Your check mark on video v{n}: schedule exactly that upload. Retried next tick if YouTube fails."""
        yt = self.yt()
        cfg = release.settings()
        taken = [d for x in all_shorts() if x.status in ("scheduled", "published")
                 if (d := release.local_date((x.data().get("youtube") or {}).get("publish_at")
                                             or (x.data().get("youtube") or {}).get("published_at"), cfg))]
        slot = release.next_slot(self.now(), taken, cfg)
        try:
            if not yt:
                raise youtube.YouTubeError(self.yt_error or "no client")
            yt.schedule(ver["video_id"], slot)
        except youtube.YouTubeError as e:
            self.warn_once(s, v, thread, f"⚠️ Couldn't schedule v{n}: {str(e)[:300]}\nI'll retry on the next tick.")
            return
        when = slot.strftime("%a %d %b, %I:%M %p %Z").replace(" 0", " ")
        mid = self.d.post(thread, f"✅ v{n} approved. It goes public **{when}**. React {STOP} here to stop it "
                                  f"before then.", reactions=(STOP,))
        v.update(approved={"version": n, "video_id": ver["video_id"], "sha256": ver.get("sha256"), "message": mid},
                 warned=None)
        s.update(video=v, **{"youtube.video_id": ver["video_id"], "youtube.url": youtube.url(ver["video_id"]),
                             "youtube.publish_at": slot.isoformat()})
        self.change(s, "approve_video", f"{s.number}: video v{n} approved, release {slot.isoformat()}",
                    event={"version": n, "video_id": ver["video_id"], "publish_at": slot.isoformat()})
        done["approved"].append(s.name)

    # --- 2. scheduled: the stop sign and the release check -----------------------------------
    def watch_scheduled(self, s: Short, done: dict) -> None:
        d = s.data()
        rv, v, yt_ = dict(d.get("review") or {}), dict(d.get("video") or {}), dict(d.get("youtube") or {})
        thread, ap = rv["thread_id"], dict(v.get("approved") or {})
        if ap.get("message") and self.mine(thread, str(ap["message"]), STOP):
            self.stop(s, rv, v, ap, thread, done)
            return
        if self.my_replies(thread, rv):
            self.d.post(thread, f"It's scheduled, so replies don't change it. React {STOP} on the scheduled "
                                f"message first, then reply.")
            s.update(review=rv)
            self.commit(s, f"{s.number}: review read")
        publish_at = dt.datetime.fromisoformat(str(yt_["publish_at"]))
        if self.now() < publish_at:
            return
        yt = self.yt()
        if not yt:
            return
        try:
            st = yt.status(ap["video_id"])
        except youtube.YouTubeError as e:
            self.echo(f"  {s.name}: release check failed: {e}")
            return
        if st.get("privacyStatus") == "public":
            s.update(video=v, **{"youtube.published_at": release.local_date(yt_["publish_at"]).isoformat()})
            self.change(s, "released", f"{s.number}: published", event={"video_id": ap["video_id"]})
            self.d.post(thread, f"🎉 Live: {spoiler(youtube.url(ap['video_id']))}")
            done["released"].append(s.name)
        elif self.now() > publish_at + LATE:
            self.warn_once(s, v, thread, f"⚠️ It was due to go public at {publish_at.isoformat()}, but YouTube "
                                         f"says {st.get('privacyStatus') or 'the video is gone'}. Check YouTube "
                                         f"Studio.")

    def stop(self, s: Short, rv: dict, v: dict, ap: dict, thread: str, done: dict) -> None:
        yt = self.yt()
        try:
            if not yt:
                raise youtube.YouTubeError(self.yt_error or "no client")
            yt.unschedule(ap["video_id"])
        except youtube.YouTubeError as e:
            self.warn_once(s, v, thread, f"⚠️ Couldn't stop it: {str(e)[:300]}\nRetrying next tick. If the "
                                         f"release is close, set it to private in YouTube Studio.")
            return
        n = int(ap["version"])
        # The old check mark stays on the old message, so post this version afresh for a new decision.
        versions = {int(k): dict(x) for k, x in (v.get("versions") or {}).items()}
        versions[n]["message"] = self.post_video(thread, s, n, ap["video_id"], f"Stopped and unlisted again.")
        v.update(versions=versions, approved=None, warned=None)
        s.update(review=rv, video=v, **{"youtube.publish_at": None, "youtube.video_id": None, "youtube.url": None})
        self.change(s, "stop", f"{s.number}: release stopped", event={"version": n})
        done["stopped"].append(s.name)

    # --- 3. jobs ------------------------------------------------------------------------
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

    def make_video(self, s: Short, done: dict) -> None:
        """Animate (or revise), render and check in the sandbox, then upload unlisted and post."""
        kind = "animate" if s.status == "animating" else "revise_video"
        v = dict(s.data().get("video") or {})
        version = int(v.get("version") or 0) + 1
        pending = dict(v.get("pending") or {})
        v["pending"] = pending or None
        if int(pending.get("version") or 0) != version or not Path(pending.get("file", "")).exists():
            dest = review_video(s, version)
            if v.get("as_is") and kind == "animate":       # `ms animate --as-is`: your scene, no job
                problem = self.problem(kind, s.name, dest)
                result, error = (jobs.JobResult(True, s.name, "Your scene, as it is."), None) if not problem \
                    else (None, problem)
            else:
                result, error = self.attempt(kind, s.name, v.get("comment") if kind == "revise_video" else None,
                                             video=dest)
            if result is None:
                self.fail(s, error, done, thread=(s.data().get("review") or {}).get("thread_id"))
                return
            pending = {"version": version, "file": str(dest), "sha256": sha256(dest),
                       "summary": result.summary, "usage": result.usage}
            v["pending"] = pending
            s.update(video=v)
            self.commit(s, f"{s.number}: video v{version} rendered")
        thread = self.thread(s)
        yt = self.yt()
        video_id = pending.get("video_id")       # uploaded by a tick that stopped before posting (#38)
        try:
            if not video_id:
                video_id = yt.upload(Path(pending["file"]), youtube.metadata(s.data()), "unlisted")
                pending["video_id"] = v["pending"]["video_id"] = video_id
                s.update(video=v)                 # saved before anything else can fail
                self.commit(s, f"{s.number}: video v{version} uploaded")
            st = yt.wait_processed(video_id)
            if st.get("processingStatus") != "succeeded":
                raise youtube.YouTubeError(f"processing {st.get('processingStatus') or 'timed out'}")
        except youtube.YouTubeError as e:
            if video_id:
                self.delete_videos([{"video_id": video_id}])
                v["pending"].pop("video_id", None)
                s.update(video=v)
            self.warn_once(s, v, thread, f"⚠️ Video v{version} is rendered, but the upload failed: "
                                         f"{spoiler(str(e)[:300])}\nI'll retry on the next tick.")
            return
        mid = self.post_video(thread, s, version, video_id, pending.get("summary", ""))
        versions = {int(k): dict(x) for k, x in (v.get("versions") or {}).items()}
        self.delete_videos(versions.values())                  # superseded drafts don't pile up
        versions[version] = {"message": mid, "video_id": video_id, "sha256": pending["sha256"]}
        v.update(version=version, versions=versions, pending=None, comment=None, warned=None, as_is=None)
        s.update(video=v)
        self.change(s, "animated" if kind == "animate" else "revised_video", f"{s.number}: video v{version}",
                    event={"version": version, "video_id": video_id, "sha256": pending["sha256"],
                           "usage": pending.get("usage")})
        done["videos"].append(s.name)

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
        thread = self.d.open_thread(title(s))
        self.post_problem(thread, s)
        mid = self.post_version(thread, s, 1, result.summary)
        s.update(review={"thread_id": thread, "version": 1, "messages": {1: mid}, "last_seen": mid})
        self.change(s, "script_done", f"{s.number}: script v1", event={"version": 1, "usage": result.usage})
        done["scripted"].append(s.name)

    # --- helpers -----------------------------------------------------------------------
    def attempt(self, kind: str, short: str | None = None, comment: str | None = None, video: Path | None = None):
        """Run a job up to ATTEMPTS times; a run only counts if its checks pass here, in the sandbox.
        Returns (result, None) or (None, error); for script jobs the error is (folder name or None, text)."""
        error, name = "", short
        for n in range(ATTEMPTS):
            r = self.runner(kind, short, comment)
            name = r.short or name
            if r.ok:
                problem = self.problem(kind, r.short, video)
                if not problem:
                    return r, None
                r.error = problem
                if kind == "script" and n < ATTEMPTS - 1:
                    shutil.rmtree(paths.shorts() / r.short)    # uncommitted; the retry starts fresh
            error = r.error
            self.echo(f"  {kind} job: {error}")
        return None, ((name, error) if kind == "script" else error)

    def problem(self, kind: str, name: str, video: Path | None) -> str | None:
        s = Short(paths.shorts() / name)
        ok, out = self.checks.verify(s)
        if not ok:
            return f"verify.py fails: {out.splitlines()[-1] if out else ''}"
        if kind in ("script", "revise"):
            return None if (s.folder / "SCRIPT.md").exists() else "no SCRIPT.md"
        if not (s.folder / "scene.py").exists():
            return "no scene.py"
        ok, out = self.checks.check(s)
        if not ok:
            errors = [l.strip() for l in out.splitlines() if "error" in l.lower()][:3]
            return "ms check: " + "; ".join(errors or out.splitlines()[-1:])
        ok, out = self.checks.render(s, video)
        if not ok:
            return f"final render failed: {' '.join(out.splitlines()[-3:])[:300]}"
        return None

    def thread(self, s: Short) -> str:
        """The Short's thread; a Short handed over with `ms animate` may not have one yet."""
        rv = dict(s.data().get("review") or {})
        if not rv.get("thread_id"):
            rv["thread_id"] = self.d.open_thread(title(s))
            self.post_problem(rv["thread_id"], s)
            s.update(review=rv)
        return rv["thread_id"]

    def post_problem(self, thread: str, s: Short) -> str:
        """The thread's first post: the puzzle as the Short poses it, and nothing about the solution."""
        d = s.data()
        text = str((d.get("level1") or {}).get("statement") or "").strip()
        if not text or text.startswith("TODO"):
            text = str((d.get("puzzle") or {}).get("text") or "").strip()
        head = f"**The puzzle.** Try it before you open anything hidden below.\n\n{text}"
        l2 = str((d.get("level2") or {}).get("statement") or "").strip()
        if l2 and not l2.startswith("TODO"):
            head += f"\n\n**Level 2** (it may hint at the trick): {spoiler(l2)}"
        return self.d.post(thread, head)

    def post_version(self, thread: str, s: Short, version: int, summary: str) -> str:
        head = (f"**Script v{version}** · {title(s)}\n{spoiler(summary)}\n\n"
                f"React {ACCEPT} to accept, {CROSS} to abandon, or reply to revise.")
        return self.d.post(thread, head,
                           files={f"SPOILER_{s.number}-script-v{version}.md": s.folder / "SCRIPT.md"},
                           reactions=(ACCEPT, CROSS))

    def post_video(self, thread: str, s: Short, version: int, video_id: str, summary: str) -> str:
        cfg = release.settings()
        head = (f"**Video v{version}** · {title(s)}\n{spoiler(youtube.url(video_id))}\n"
                f"{spoiler(summary)}\n\nReact {ACCEPT} to approve: this exact upload goes public "
                f"{release.describe(cfg)}. {CROSS} abandons; a reply revises.")
        return self.d.post(thread, head, reactions=(ACCEPT, CROSS))

    def delete_videos(self, versions) -> list[str]:
        """Delete review uploads; best effort, since a leftover unlisted draft is harmless."""
        yt, gone = self.yt(), []
        for x in versions:
            vid = x.get("video_id")
            if not vid or not yt:
                continue
            try:
                yt.delete(vid)
                gone.append(vid)
            except youtube.YouTubeError as e:
                self.echo(f"  couldn't delete {vid}: {e}")
        return gone

    def warn_once(self, s: Short, v: dict, thread: str, text: str) -> None:
        """Post a warning unless the same one is already up; it's cleared when things move on."""
        if v.get("warned") != text[:120]:
            self.d.post(thread, text)
            v["warned"] = text[:120]
            s.update(video=v)
            self.commit(s, f"{s.number}: warned")
        self.echo(f"  {s.name}: {text.splitlines()[0]}")

    def fail(self, s: Short, error: str, done: dict, thread: str | None = None) -> None:
        s.update(last_error=error[:200])
        self.change(s, "job_failed", f"{s.number}: needs attention", event={"error": error})
        if thread:
            self.d.post(thread, f"⚠️ The job failed twice: {spoiler(error[:300])}\nIt needs you in Claude Code: "
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
