"""`ms tick`: the orchestrator for the script and video loops (#28, #29, docs/pipeline-design.md).

Run every few minutes (scripts/tick.sh). Each tick, under a lock:

1. Reads each Short's Discord thread. Only your account counts:
   - a cross on any version              -> abandoned (its review videos are deleted)
   - a reply                             -> a revise job, with your words as its brief
     (a reply wins over a check mark left at the same time; the bot says so)
   - a check mark on the newest script   -> animating
   - a check mark on the newest video    -> scheduled: that exact file (by sha256) is uploaded private
     with `publishAt` at the next open slot (config/pipeline.yaml `release:`), and YouTube releases
     it. If the upload fails or is paused, it's retried each tick and the slot is worked out again.
   - a stop sign on the scheduled notice -> back to video_review; the upload is private, unscheduled
   - a check mark on an older version    -> nothing; the bot says which version is current
2. For scheduled Shorts past their release time, checks YouTube and records them as published.
3. Runs revise jobs, then animate and video revise jobs. A video version is rendered and posted in
   the thread as an attachment (#48), re-encoded to `review.max_mb` if it's over Discord's limit;
   nothing goes to YouTube until your check mark. If YouTube says the channel's daily upload limit
   is hit, uploads stop for 8 hours (a pause file in out/) with one notice in the thread.
4. With --draft, starts one script job if the queue has room, and posts the script.

A job's own claims are not trusted: tick runs verify.py, `ms check` and the final render itself,
in the sandbox (mathshorts/sandbox.py), before anything is posted. No model decides an approval:
reactions are read as data. Every change is committed, one Short per commit, and logged to the
Short's events.jsonl.

No spoilers (#46): a thread opens with the puzzle alone, and everything about the solution (job
the script's beats, summaries, errors, videos) goes inside Discord spoiler tags, so you can try it first.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from . import jobs, paths, release, sandbox, youtube, yamlio
from .discord import ACCEPT, CROSS, FILE_LIMIT, STOP
from .discord import LIMIT as DISCORD_LIMIT
from .shorts import SCRIPT_LOOP, VIDEO_LOOP, Short, all_shorts

ATTEMPTS = 2
LATE = dt.timedelta(hours=1)          # a release this late gets flagged
UPLOAD_PAUSE = dt.timedelta(hours=8)  # after YouTube's uploadLimitExceeded (#47)


def spoiler(text: str) -> str:
    """Hide text behind Discord spoiler tags. A `||` or code fence inside would end the spoiler early."""
    text = (text or "").strip().replace("||", "| |").replace("```", "'''")
    return f"||{text}||" if text else ""


_BEAT = re.compile(r"^\s*(\d+[a-z]?)\.\s*(\([^)]*\))?\s*(.*)$")
_QUOTE = re.compile(r"[\"“]([^\"”]+)[\"”]")


def script_beats(text: str) -> list[str] | None:
    """SCRIPT.md's `## Beats` as one line each, captions only (#51): `6. (14-19 s) Pause and try it.`
    A beat with no quoted caption keeps its whole text. None if there's no Beats section."""
    m = re.search(r"^##\s+Beats\s*$(.*?)(?=^##\s|\Z)", text or "", re.M | re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).splitlines():
        b = _BEAT.match(line)
        if not b:
            continue
        num, when, rest = b.groups()
        caps = _QUOTE.findall(rest)
        caption = " ".join(c.strip() for c in caps) if caps else rest.strip()
        out.append(" ".join(x for x in (f"{num}.", when, caption) if x))
    return out or None


def chunk_lines(lines: list[str], limit: int) -> list[str]:
    """Join lines into as few blocks as fit `limit` characters each (a too-long line is cut)."""
    blocks, cur = [], ""
    for line in lines:
        line = line[:limit]
        if cur and len(cur) + 1 + len(line) > limit:
            blocks.append(cur)
            cur = line
        else:
            cur = f"{cur}\n{line}" if cur else line
    return blocks + [cur] if cur else blocks


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


def pause_file() -> Path:
    return paths.out() / "youtube-upload-pause.json"


def uploads_paused_until(now: dt.datetime) -> dt.datetime | None:
    """When uploads may resume after YouTube's daily upload limit, or None if they may go ahead."""
    try:
        until = dt.datetime.fromisoformat(json.loads(pause_file().read_text())["until"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return until if until > now else None


def pause_uploads(now: dt.datetime, reason: str) -> dt.datetime:
    until = now + UPLOAD_PAUSE
    pause_file().parent.mkdir(parents=True, exist_ok=True)
    pause_file().write_text(json.dumps({"until": until.isoformat(), "reason": reason[:300]}) + "\n")
    return until


def review_video(s: Short, version: int) -> Path:
    return paths.out() / "review" / s.name / f"v{version}.mp4"


def review_cap() -> int:
    """Bytes a review attachment may have (`review.max_mb`); under Discord's 10 MiB with room for the form."""
    cfg = yamlio.load(paths.config() / "pipeline.yaml") if (paths.config() / "pipeline.yaml").exists() else {}
    mb = float(((cfg or {}).get("review") or {}).get("max_mb", 9.5))
    return min(int(mb * 1_000_000), FILE_LIMIT - 200_000)


def review_copy(master: Path, cap: int | None = None) -> Path:
    """What goes in the Discord thread: the master itself if it fits, else a two-pass re-encode to the cap.

    The master is never changed: it is what gets uploaded on your check mark, and its sha256 is what
    you approved. The copy sits next to it as vN-discord.mp4 and is reused if it already fits.
    """
    cap = cap or review_cap()
    if master.stat().st_size <= cap:
        return master
    copy = master.with_name(f"{master.stem}-discord.mp4")
    if copy.exists() and copy.stat().st_size <= cap and copy.stat().st_mtime >= master.stat().st_mtime:
        return copy
    seconds = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "csv=p=0", str(master)], capture_output=True, text=True, check=True).stdout)
    audio = 96_000
    for squeeze in (0.92, 0.8, 0.65):                    # two-pass lands close to the target, but not exactly
        video = max(int(cap * 8 * squeeze / seconds) - audio, 100_000)
        with tempfile.TemporaryDirectory() as tmp:
            log = str(Path(tmp) / "pass")
            common = ["ffmpeg", "-y", "-v", "error", "-i", str(master), "-c:v", "libx264", "-preset", "medium",
                      "-b:v", str(video), "-pix_fmt", "yuv420p", "-passlogfile", log]
            subprocess.run([*common, "-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
            subprocess.run([*common, "-pass", "2", "-c:a", "aac", "-b:a", str(audio), "-movflags", "+faststart",
                            str(copy)], check=True)
        if copy.stat().st_size <= cap:
            return copy
    raise RuntimeError(f"couldn't fit {master.name} under {cap} bytes")


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
            step = {"script_review": self.read_thread, "video_review": self.read_video,
                    "scheduled": self.watch_scheduled}
            for s, st in self.shorts():
                if st in step:
                    self.safely(step[st], s, done)
            for s, _ in self.shorts("revise"):
                self.safely(self.revise, s, done)
            for s, _ in self.shorts("animating", "revise_video"):
                self.safely(self.make_video, s, done)   # review videos go to Discord: no YouTube needed (#48)
            if draft:
                why = self.no_room()
                if why:
                    done["skipped"] = why
                else:
                    self.script(done)
        return done

    def shorts(self, *statuses: str) -> list[tuple[Short, str]]:
        """(Short, status) for every Short whose short.yaml loads, optionally only those statuses.
        One unreadable short.yaml is logged and skipped, so it can't stop the other Shorts."""
        out = []
        for s in all_shorts():
            try:
                st = s.status
            except Exception as e:  # noqa: BLE001
                self.echo(f"  {s.name}: skipped, short.yaml doesn't load: {' '.join(str(e).split())[:200]}")
                continue
            if not statuses or st in statuses:
                out.append((s, st))
        return out

    def safely(self, fn: Callable, s: Short, done: dict) -> None:
        """One Short's step; an error in it is logged and the tick carries on with the others."""
        try:
            fn(s, done)
        except Exception as e:  # noqa: BLE001
            self.echo(f"  {s.name}: {fn.__name__} crashed: {type(e).__name__}: {' '.join(str(e).split())[:300]}")
            done["failed"].append(s.name)

    def no_room(self) -> str | None:
        lim, shorts = limits(), [st for _, st in self.shorts()]
        waiting = sum(st in (*SCRIPT_LOOP, *VIDEO_LOOP) for st in shorts)
        queued = sum(st in ("approved", "ready", "scheduled") for st in shorts)
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
            self.d.post(thread, "❌ Abandoned. Any upload is deleted, and its puzzle goes back in the pool.")
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
        """Your check mark on video v{n}: upload exactly that file (private) and schedule it (#48).

        Your check mark stays on the message, so anything that fails here is simply retried next tick,
        and the slot is worked out afresh each time: a delayed upload goes out later, never in the past.
        The video id is saved the moment the upload returns, so a crash after it can't upload twice (#38).
        Versions from before #48 were already uploaded unlisted for review; those are scheduled as they are.
        """
        yt = self.yt()
        video_id = ver.get("video_id")
        try:
            if not yt:
                raise youtube.YouTubeError(self.yt_error or "no client")
            if not video_id:
                master = Path(ver.get("file") or review_video(s, n))
                if not master.exists() or sha256(master) != ver.get("sha256"):
                    self.warn_once(s, v, thread, f"⚠️ v{n}'s file is missing or changed since it was posted, so "
                                                 f"I won't upload it. Reply to have it rendered again, or ❌.")
                    return
                if until := uploads_paused_until(self.now()):
                    self.warn_once(s, v, thread, self.limit_notice(n, until))
                    return
                try:
                    video_id = yt.upload(master, youtube.metadata(s.data()), "private")
                except youtube.UploadLimitError as e:
                    self.warn_once(s, v, thread, self.limit_notice(n, pause_uploads(self.now(), str(e))))
                    return
                ver["video_id"] = video_id
                v["versions"] = {**{int(k): dict(x) for k, x in (v.get("versions") or {}).items()}, n: ver}
                s.update(video=v)                 # saved before anything else can fail
                self.commit(s, f"{s.number}: video v{n} uploaded")
                st = yt.wait_processed(video_id)
                if st.get("processingStatus") != "succeeded":
                    self.delete_videos([ver])
                    ver.pop("video_id")
                    s.update(video=v)
                    raise youtube.YouTubeError(f"processing {st.get('processingStatus') or 'timed out'}")
            slot = self.slot()
            yt.schedule(video_id, slot)
        except youtube.YouTubeError as e:
            self.warn_once(s, v, thread, f"⚠️ Couldn't upload or schedule v{n}: {spoiler(str(e)[:300])}\n"
                                         f"I'll retry on the next tick.")
            return
        thumb = self.thumbnail(yt, video_id, s, n, ver)
        when = slot.strftime("%a %d %b, %I:%M %p %Z").replace(" 0", " ")
        mid = self.d.post(thread, f"✅ v{n} approved. It goes public **{when}**. React {STOP} here to stop it "
                                  f"before then.{thumb}", reactions=(STOP,))
        v.update(approved={"version": n, "video_id": ver["video_id"], "sha256": ver.get("sha256"), "message": mid},
                 warned=None)
        s.update(video=v, **{"youtube.video_id": ver["video_id"], "youtube.url": youtube.url(ver["video_id"]),
                             "youtube.publish_at": slot.isoformat()})
        self.change(s, "approve_video", f"{s.number}: video v{n} approved, release {slot.isoformat()}",
                    event={"version": n, "video_id": ver["video_id"], "publish_at": slot.isoformat()})
        done["approved"].append(s.name)

    def thumbnail(self, yt, video_id: str, s: Short, n: int, ver: dict) -> str:
        """Set the posed-problem frame as the thumbnail (#41), so YouTube can't pick a frame that gives the
        answer away. Best effort: a refusal (an unverified channel, say) never holds up the release.
        Returns a note for the approval message ("" when it worked)."""
        path = Path(ver.get("file") or review_video(s, n)).with_suffix(".png")
        if not path.exists():
            return "\n⚠️ No thumbnail for this version, so YouTube picks a frame. Check it in YouTube Studio."
        try:
            yt.set_thumbnail(video_id, path)
        except (youtube.YouTubeError, OSError) as e:
            return (f"\n⚠️ The thumbnail wasn't set, so YouTube picks a frame: {spoiler(str(e)[:200])}\n"
                    f"Set it in YouTube Studio from `{path}`.")
        return ""

    def slot(self) -> dt.datetime:
        """When a Short approved now goes public, given the days already taken."""
        cfg = release.settings()
        taken = [d for x, _ in self.shorts("scheduled", "published")
                 if (d := release.local_date((x.data().get("youtube") or {}).get("publish_at")
                                             or (x.data().get("youtube") or {}).get("published_at"), cfg))]
        return release.next_slot(self.now(), taken, cfg)

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
            yt.unschedule(ap["video_id"])             # private, publishAt cleared; a new ✅ reuses it
        except youtube.YouTubeError as e:
            self.warn_once(s, v, thread, f"⚠️ Couldn't stop it: {str(e)[:300]}\nRetrying next tick. If the "
                                         f"release is close, set it to private in YouTube Studio.")
            return
        n = int(ap["version"])
        # The old check mark stays on the old message, so post this version afresh for a new decision.
        versions = {int(k): dict(x) for k, x in (v.get("versions") or {}).items()}
        versions[n]["message"] = self.post_video(thread, s, n, versions[n],
                                                 "Stopped: the upload is private again, and a new ✅ schedules it.")
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
        """Animate (or revise), render and check in the sandbox, then post the file in the thread (#48)."""
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
        ver = {"file": pending["file"], "sha256": pending["sha256"]}
        if pending.get("video_id"):               # uploaded for review by a tick from before #48
            ver["video_id"] = pending["video_id"]
        ver["message"] = self.post_video(thread, s, version, ver, pending.get("summary", ""))
        versions = {int(k): dict(x) for k, x in (v.get("versions") or {}).items()}
        self.delete_videos(versions.values())                  # old review uploads (before #48) don't pile up
        versions = {k: {**x, "video_id": None} for k, x in versions.items()}
        versions[version] = ver
        v.update(version=version, versions=versions, pending=None, comment=None, warned=None, as_is=None)
        s.update(video=v)
        self.change(s, "animated" if kind == "animate" else "revised_video", f"{s.number}: video v{version}",
                    event={"version": version, "sha256": pending["sha256"], "usage": pending.get("usage")})
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
        """The script's beats inline, behind a spoiler (#51); the reactions go on the last message,
        whose id is returned. Without a Beats section, the summary and SCRIPT.md attached, as before."""
        top = f"**Script v{version}** · {title(s)}"
        prompt = f"React {ACCEPT} to accept, {CROSS} to abandon, or reply to revise."
        path = s.folder / "SCRIPT.md"
        beats = script_beats(path.read_text()) if path.exists() else None
        if not beats:
            return self.d.post(thread, f"{top}\n{spoiler(summary)}\n\n{prompt}",
                               files={f"SPOILER_{s.number}-script-v{version}.md": path},
                               reactions=(ACCEPT, CROSS))
        room = DISCORD_LIMIT - len(top) - len(prompt) - 8       # newlines and the two `||`
        blocks = [spoiler(b) for b in chunk_lines(beats, room)]
        blocks[0] = f"{top}\n{blocks[0]}"
        blocks[-1] = f"{blocks[-1]}\n\n{prompt}"
        for b in blocks[:-1]:
            self.d.post(thread, b)
        return self.d.post(thread, blocks[-1], reactions=(ACCEPT, CROSS))

    def post_video(self, thread: str, s: Short, version: int, ver: dict, summary: str) -> str:
        """The video itself as a spoilered attachment (a compressed copy if the master is over the cap)."""
        master, files, extra = Path(ver.get("file") or review_video(s, version)), {}, ""
        thumb = master.with_suffix(".png")                     # what YouTube will show (#41)
        try:
            copy = review_copy(master, review_cap() - (thumb.stat().st_size if thumb.exists() else 0))
            files = {f"SPOILER_{s.number}-video-v{version}.mp4": copy}
            if thumb.exists():
                files[f"SPOILER_{s.number}-thumbnail-v{version}.png"] = thumb
            if copy != master:
                extra = "\n(Compressed to fit Discord. Your ✅ uploads the full-quality file.)"
        except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as e:
            if ver.get("video_id"):
                extra = f"\n{spoiler(youtube.url(ver['video_id']))}"
            else:
                extra = f"\n⚠️ Couldn't attach the video: {spoiler(str(e)[:200])}"
        head = (f"**Video v{version}** · {title(s)}\n{spoiler(summary)}{extra}\n\nReact {ACCEPT} to approve: "
                f"this exact file is uploaded and goes public {release.describe(release.settings())}. "
                f"{CROSS} abandons; a reply revises.")
        return self.d.post(thread, head, files=files, reactions=(ACCEPT, CROSS))

    def delete_videos(self, versions) -> list[str]:
        """Delete uploads that won't be released; best effort, since a leftover private draft is harmless."""
        ids, gone = [x.get("video_id") for x in versions if x.get("video_id")], []
        yt = self.yt() if ids else None             # no client (or network) when there's nothing to delete
        for vid in ids:
            if not yt:
                break
            try:
                yt.delete(vid)
                gone.append(vid)
            except youtube.YouTubeError as e:
                self.echo(f"  couldn't delete {vid}: {e}")
        return gone

    @staticmethod
    def limit_notice(version: int, until: dt.datetime) -> str:
        tz = release.ZoneInfo(release.settings()["timezone"])
        when = until.astimezone(tz).strftime("%a %d %b, %I:%M %p %Z").replace(" 0", " ")
        return (f"⏸️ v{version} is approved, but YouTube's daily upload limit was hit. "
                f"Uploads resume after {when}; I'll upload and schedule it then.")

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
