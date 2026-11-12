"""The script and video loops: `ms tick` against a fake Discord, YouTube, job runner and sandbox."""
import datetime as dt
import re
import shutil
import subprocess

import pytest

from mathshorts import cli, jobs, release, sandbox, tick
from mathshorts.discord import ACCEPT, CROSS, STOP
from mathshorts.jobs import JobResult, _env
from mathshorts.youtube import UploadLimitError, YouTubeError
from mathshorts.shorts import all_shorts, find, used_catalog_ids

ME, OTHER, BOT = "100", "200", "999"


class FakeDiscord:
    def __init__(self):
        self.threads, self.reacts, self.n = {}, {}, 1000

    def _id(self):
        self.n += 1
        return str(self.n)

    def open_thread(self, title):
        t = self._id()
        self.threads[t] = []
        return t

    def post(self, thread, content, files=None, reactions=()):
        m = self._id()
        self.threads[thread].append({"id": m, "author_id": BOT, "bot": True, "content": content,
                                     "files": dict(files or {})})
        for e in reactions:
            self.reacts.setdefault((m, e), set()).add(BOT)
        return m

    def say(self, thread, user, text):                  # a person replies in the thread
        m = self._id()
        self.threads[thread].append({"id": m, "author_id": user, "bot": False, "content": text})

    def tap(self, message, emoji, user=ME):
        self.reacts.setdefault((message, emoji), set()).add(user)

    def reactors(self, thread, message, emoji):
        return set(self.reacts.get((message, emoji), set()))

    def messages_after(self, thread, after):
        return [m for m in self.threads[thread] if int(m["id"]) > int(after or 0)]

    def bot_said(self, thread):
        return [m["content"] for m in self.threads[thread] if m["bot"]]


class FakeRunner:
    """Writes a Short like a job would: script jobs create it via `ms new --scripting`."""

    def __init__(self, verify_ok=True, fail_first=False):
        self.calls, self.verify_ok, self.fail_first = [], verify_ok, fail_first

    def __call__(self, kind, short=None, comment=None):
        self.calls.append((kind, short, comment))
        if self.fail_first and len(self.calls) == 1:
            return JobResult(False, error="exit 1, error_max_budget_usd")
        if kind == getattr(self, "fail_kind", None):
            return JobResult(False, short, error="verify.py fails: expected 24")
        if kind == "script":
            cli.main(["new", "--blank", "Six Frogs", "--scripting"])
            short = all_shorts()[-1].name
            find(short.split("-")[0]).update(**{
                "level1.statement": "Six frogs sit in a row. Can they swap sides?",
                "level1.answer": "Fifteen jumps",
                "level2.statement": "Now eight frogs. How many jumps?", "level2.answer": 24,
                "level2.accept": [24, "twenty-four"]})
        folder = find(short.split("-")[0]).folder
        (folder / "verify.py").write_text("print('ok')\n" if self.verify_ok else "raise SystemExit('wrong')\n")
        if kind in ("animate", "revise_video"):
            (folder / "scene.py").write_text(f"# scene\n# {comment or 'first cut'}\n")
        else:
            (folder / "SCRIPT.md").write_text(getattr(self, "script_md", None)
                                              or f"# Script\n{comment or 'first draft'}\n")
        return JobResult(True, short, summary="Frogs swap places. Answer: fifteen jumps; Level 2 is 24.", usage={"total_cost_usd": 1.5})


class FakeYouTube:
    def __init__(self, fail_uploads=0, limit_uploads=0, fail_schedule=0, refuse_thumbnails=False):
        self.videos, self.deleted, self.n, self.fail_uploads = {}, [], 0, fail_uploads
        self.refuse_thumbnails, self.thumbnails = refuse_thumbnails, {}
        self.limit_uploads, self.attempts, self.fail_schedule = limit_uploads, 0, fail_schedule

    def upload(self, path, meta, privacy):
        self.attempts += 1
        if self.limit_uploads:
            self.limit_uploads -= 1
            raise UploadLimitError("upload: uploadLimitExceeded")
        if self.fail_uploads:
            self.fail_uploads -= 1
            raise YouTubeError("HTTP 503")
        assert privacy == "private"                       # #48: only the approved file is uploaded
        self.n += 1
        vid = f"vid{self.n}"
        self.videos[vid] = {"privacyStatus": privacy, "title": meta["title"], "bytes": path.read_bytes()}
        return vid

    def wait_processed(self, vid):
        return {"processingStatus": "succeeded"}

    def schedule(self, vid, when):
        if self.fail_schedule:
            self.fail_schedule -= 1
            raise YouTubeError("HTTP 500")
        self.videos[vid].update(privacyStatus="private", publishAt=when)

    def unschedule(self, vid):
        self.videos[vid].update(privacyStatus="private", publishAt=None)

    def status(self, vid):
        return dict(self.videos.get(vid, {}))

    def set_thumbnail(self, vid, path):
        if self.refuse_thumbnails:
            raise YouTubeError("HTTP 403 forbidden: the channel isn't verified")
        self.thumbnails[vid] = path.read_bytes()

    def delete(self, vid):
        self.videos.pop(vid)
        self.deleted.append(vid)

    def release_due(self):                               # what YouTube does at publishAt
        for v in self.videos.values():
            if v.get("publishAt"):
                v["privacyStatus"] = "public"


class FakeChecks:
    """The sandbox's checks, on the host: verify.py runs for real; `ms check` and the render are faked."""

    def __init__(self, check_ok=True):
        self.check_ok, self.renders = check_ok, []

    def verify(self, s):
        return s.verify()

    def check(self, s):
        return self.check_ok, "" if self.check_ok else "error  safe zone: caption off-screen"

    def render(self, s, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(f"video of {s.name} {len(self.renders)}".encode())
        dest.with_suffix(".png").write_bytes(b"posed problem")      # the kit's thumbnail.png, as sandbox moves it
        self.renders.append(dest)
        return True, ""


def make(root, runner=None, yt=None, checks=None, now=None):
    d = FakeDiscord()
    return d, tick.Tick(d, ME, runner or FakeRunner(), echo=lambda *a: None, commit=False,
                        youtube_client=yt if yt is not None else FakeYouTube(), checks=checks or FakeChecks(),
                        now=now)


def scripted(root):
    d, t = make(root)
    r = t.run(draft=True)
    s = all_shorts()[0]
    return d, t, s, s.data()["review"]["thread_id"]


def current_message(s):
    rv = s.data()["review"]
    return str(rv["messages"][rv["version"]])


def test_draft_posts_a_verified_script_for_review(root):
    d, t, s, thread = scripted(root)
    assert s.status == "script_review"
    problem, first = d.threads[thread][:2]
    assert problem["content"].startswith("**The puzzle.**") and "Six frogs sit in a row" in problem["content"]
    assert "Script v1" in first["content"] and "||Frogs swap places." in first["content"]
    assert list(first["files"]) == [f"SPOILER_{s.number}-script-v1.md"]
    assert d.reactors(thread, first["id"], ACCEPT) == {BOT}         # pre-added for you to tap
    assert [e["event"] for e in s.events()] == ["script_done"]
    assert s.events()[0]["usage"] == {"total_cost_usd": 1.5}


BEATS_MD = """# Script

## Beats
1. (0-4 s) Hook: "Can six frogs swap sides?" Frogs pop in.
2. (4-9 s) "Pause and try it." 5 s countdown.
2b. (about 2 s) The board slides left.
3. (9-12 s) “It takes fifteen jumps ✓”

## Level 2
Eight frogs: 24.
"""


def test_script_posts_its_beats_inline_and_spoilered(root):
    runner = FakeRunner()
    runner.script_md = BEATS_MD
    d, t = make(root, runner)
    t.run(draft=True)
    s = all_shorts()[0]
    thread = s.data()["review"]["thread_id"]
    post = d.threads[thread][1]
    assert post["files"] == {}                                       # no SCRIPT.md attached (#51)
    assert post["content"] == (
        f"**Script v1** · {tick.title(s)}\n"
        "||1. (0-4 s) Can six frogs swap sides?\n2. (4-9 s) Pause and try it.\n"
        "2b. (about 2 s) The board slides left.\n3. (9-12 s) It takes fifteen jumps ✓||\n\n"
        f"React {ACCEPT} to accept, {CROSS} to abandon, or reply to revise.")
    assert "Level 2" not in post["content"] and "Frogs swap places" not in post["content"]
    assert current_message(s) == post["id"] and d.reactors(thread, post["id"], ACCEPT) == {BOT}


def test_long_beats_split_and_reactions_go_on_the_last_message(root):
    runner = FakeRunner()
    lines = "\n".join(f'{i}. ({i}-{i + 1} s) "{"word " * 20}number {i}."' for i in range(1, 40))
    runner.script_md = f"## Beats\n{lines}\n"
    d, t = make(root, runner)
    t.run(draft=True)
    s = all_shorts()[0]
    thread = s.data()["review"]["thread_id"]
    posts = d.threads[thread][1:]
    assert len(posts) == 3 and all(len(p["content"]) <= 2000 for p in posts)
    assert all(p["content"].count("||") == 2 for p in posts)
    assert posts[0]["content"].startswith("**Script v1**") and "React" in posts[-1]["content"]
    assert current_message(s) == posts[-1]["id"]
    assert d.reactors(thread, posts[0]["id"], ACCEPT) == set()
    body = "".join(p["content"] for p in posts)
    assert all(f"number {i}." in body for i in range(1, 40))


def test_script_beats_parsing():
    assert tick.script_beats("# Script\nno beats here\n") is None
    assert tick.script_beats("## Beats\n\n## Level 2\n") is None
    assert tick.chunk_lines(["aaa", "bb", "c"], 6) == ["aaa\nbb", "c"]


def test_check_mark_from_me_accepts_and_others_are_ignored(root):
    d, t, s, thread = scripted(root)
    d.tap(current_message(s), ACCEPT, user=OTHER)
    d.say(thread, OTHER, "change everything")
    t.run()
    assert s.status == "script_review"
    d.tap(current_message(s), ACCEPT)
    t.run()
    assert s.status == "video_review"                     # accepted, then animated in the same tick
    assert any("v1 accepted. Animating it now" in c for c in d.bot_said(thread))


def test_reply_revises_and_posts_v2(root):
    runner = FakeRunner()
    d, t = make(root, runner)
    t.run(draft=True)
    s = all_shorts()[0]
    thread = s.data()["review"]["thread_id"]
    v1 = current_message(s)
    d.say(thread, ME, "Make the hook shorter")
    t.run()
    assert s.status == "script_review"
    assert runner.calls[-1] == ("revise", s.name, "Make the hook shorter")
    assert s.data()["review"]["version"] == 2
    assert "Make the hook shorter" in (s.folder / "SCRIPT.md").read_text()
    d.tap(v1, ACCEPT)                                     # a check mark on the old version does nothing
    t.run()
    t.run()
    assert s.status == "script_review"
    assert sum("v1 is superseded" in c for c in d.bot_said(thread)) == 1   # said once, not every tick
    d.tap(current_message(s), ACCEPT)
    t.run()
    assert s.status == "video_review"
    assert [e["event"] for e in s.events()] == ["script_done", "comment", "revised", "accept_script", "animated"]


def test_a_reply_wins_over_a_check_mark(root):
    d, t, s, thread = scripted(root)
    d.tap(current_message(s), ACCEPT)
    d.say(thread, ME, "Actually, use the runner-up")
    t.run()
    assert s.status == "script_review" and s.data()["review"]["version"] == 2
    assert any("comment wins" in c for c in d.bot_said(thread))


def test_cross_abandons_and_frees_the_puzzle(root):
    d, t, s, thread = scripted(root)
    s.update(catalog_id="dudeney-amusements-001")
    assert used_catalog_ids() == {"dudeney-amusements-001"}
    d.tap(current_message(s), CROSS)
    t.run()
    assert s.status == "abandoned"
    assert used_catalog_ids() == set()


def test_failing_verify_twice_needs_attention(root):
    d, t = make(root, FakeRunner(verify_ok=False))
    r = t.run(draft=True)
    s = all_shorts()
    assert len(s) == 1 and s[0].status == "needs_attention"     # the first try's folder was cleared
    assert "verify.py fails" in s[0].data()["last_error"]
    assert r["failed"] == [s[0].name]


def test_one_retry_recovers(root):
    runner = FakeRunner(fail_first=True)
    d, t = make(root, runner)
    t.run(draft=True)
    assert len(runner.calls) == 2 and all_shorts()[0].status == "script_review"


def test_queue_limit_stops_new_scripts(root):
    (root / "config" / "pipeline.yaml").write_text("max_waiting: 1\nmax_queued: 7\n")
    d, t, s, thread = scripted(root)
    r = t.run(draft=True)
    assert len(all_shorts()) == 1 and "already in the loops" in r["skipped"]


def test_tick_never_reads_drafting_or_published_shorts(root):
    cli.main(["new", "--blank", "Old"])
    d, t = make(root)
    t.run()
    assert all_shorts()[0].status == "drafting" and d.threads == {}


def test_jobs_get_no_discord_secrets_or_api_key(monkeypatch, tmp_path):
    for k, v in {"DISCORD_BOT_TOKEN": "x", "MS_DISCORD_USER_ID": "1", "ANTHROPIC_API_KEY": "k",
                 "CLAUDE_CODE_OAUTH_TOKEN": "t", "CLAUDE_CODE_ENTRYPOINT": "cli", "CLAUDECODE": "1"}.items():
        monkeypatch.setenv(k, v)
    env = _env(tmp_path)
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "t" and env["MS_ROOT"] == str(tmp_path)
    for k in ("DISCORD_BOT_TOKEN", "MS_DISCORD_USER_ID", "ANTHROPIC_API_KEY", "CLAUDE_CODE_ENTRYPOINT", "CLAUDECODE"):
        assert k not in env


# --- the video loop (#29) ---------------------------------------------------------------------
NOON = dt.datetime(2026, 11, 4, 17, 0, tzinfo=dt.timezone.utc)          # 12:00 PM in New York


class Clock:
    def __init__(self, t=NOON):
        self.t = t

    def __call__(self):
        return self.t


def video(s):
    v = s.data()["video"]
    return v, v["versions"][v["version"]]


def in_review(root, yt=None, checks=None, clock=None, runner=None):
    """A Short whose script was accepted and whose first video is up for review."""
    yt = yt or FakeYouTube()
    d, t = make(root, runner, yt=yt, checks=checks, now=clock or Clock())
    t.run(draft=True)
    s = all_shorts()[0]
    thread = s.data()["review"]["thread_id"]
    d.tap(current_message(s), ACCEPT)
    t.run()
    return d, t, yt, s, thread


def master(root, s, n=1):
    return root / "out" / "review" / s.name / f"v{n}.mp4"


def approve(d, t, s):
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()


def test_accepted_script_is_animated_and_posted_as_a_file_not_uploaded(root):
    d, t, yt, s, thread = in_review(root)
    assert s.status == "video_review"
    v, ver = video(s)
    assert v["version"] == 1 and yt.attempts == 0 and not ver.get("video_id")       # #48: no YouTube yet
    post = d.threads[thread][-1]
    assert "Video v1" in post["content"] and "youtube.com" not in post["content"]
    assert post["files"] == {f"SPOILER_{s.number}-video-v1.mp4": master(root, s),
                             f"SPOILER_{s.number}-thumbnail-v1.png": master(root, s).with_suffix(".png")}
    assert post["id"] == ver["message"] and d.reactors(thread, post["id"], ACCEPT) == {BOT}
    assert ver["sha256"] == tick.sha256(master(root, s))


def test_reply_on_a_video_revises_it(root):
    runner = FakeRunner()
    d, t, yt, s, thread = in_review(root, runner=runner)
    d.say(thread, ME, "0:12 slow down the slide")
    t.run()
    assert runner.calls[-1] == ("revise_video", s.name, "0:12 slow down the slide")
    v, ver = video(s)
    assert s.status == "video_review" and v["version"] == 2 and yt.attempts == 0
    assert d.threads[thread][-1]["files"][f"SPOILER_{s.number}-video-v2.mp4"] == master(root, s, 2)


def test_check_mark_uploads_that_exact_file_and_schedules_it(root):
    d, t, yt, s, thread = in_review(root)
    approve(d, t, s)
    assert s.status == "scheduled" and yt.n == 1
    when = dt.datetime.fromisoformat(s.data()["youtube"]["publish_at"])
    assert when.isoformat() == "2026-11-04T13:00:00-05:00"          # asap: the first full hour 60+ min out
    vid = s.data()["youtube"]["video_id"]
    assert yt.videos[vid] == {**yt.videos[vid], "privacyStatus": "private", "publishAt": when}
    assert yt.videos[vid]["bytes"] == master(root, s).read_bytes()
    assert s.data()["video"]["approved"]["video_id"] == vid == video(s)[1]["video_id"]
    assert d.reactors(thread, d.threads[thread][-1]["id"], STOP) == {BOT}
    assert yt.thumbnails[vid] == b"posed problem" and "thumbnail" not in d.bot_said(thread)[-1]   # #41


def test_a_refused_thumbnail_never_holds_up_the_release(root):
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(refuse_thumbnails=True))
    approve(d, t, s)
    assert s.status == "scheduled" and yt.thumbnails == {}
    said = d.bot_said(thread)[-1]
    assert "thumbnail wasn't set" in said and "isn't verified" in said and str(master(root, s).with_suffix(".png")) in said


def test_a_version_without_a_thumbnail_still_goes_out(root):
    d, t, yt, s, thread = in_review(root)
    master(root, s).with_suffix(".png").unlink()           # rendered before #41
    approve(d, t, s)
    assert s.status == "scheduled" and yt.thumbnails == {} and "No thumbnail" in d.bot_said(thread)[-1]


def test_check_mark_wont_upload_a_file_that_changed(root):
    d, t, yt, s, thread = in_review(root)
    master(root, s).write_bytes(b"something else")
    approve(d, t, s)
    t.run()
    assert s.status == "video_review" and yt.attempts == 0
    assert sum("missing or changed" in c for c in d.bot_said(thread)) == 1


def test_a_review_upload_from_before_48_is_scheduled_as_it_is(root):
    d, t, yt, s, thread = in_review(root)
    v = s.data()["video"]
    v["versions"][1]["video_id"] = "old1"
    s.update(video=dict(v))
    yt.videos["old1"] = {"privacyStatus": "unlisted"}
    approve(d, t, s)
    assert s.status == "scheduled" and s.data()["youtube"]["video_id"] == "old1" and yt.attempts == 0
    assert yt.videos["old1"]["privacyStatus"] == "private" and yt.videos["old1"]["publishAt"]


def test_a_reply_after_a_failed_schedule_deletes_that_upload(root):
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(fail_schedule=1))
    approve(d, t, s)
    assert s.status == "video_review" and video(s)[1]["video_id"] == "vid1"
    d.say(thread, ME, "bigger numbers")
    t.run()
    assert s.status == "video_review" and yt.deleted == ["vid1"] and yt.videos == {}


def test_a_check_mark_on_an_old_video_does_nothing(root):
    d, t, yt, s, thread = in_review(root)
    v1 = video(s)[1]["message"]
    d.say(thread, ME, "bigger numbers")
    t.run()
    d.tap(v1, ACCEPT)
    t.run()
    assert s.status == "video_review"
    assert any("v1 is superseded" in c for c in d.bot_said(thread))


def test_stop_sign_pulls_it_and_needs_a_fresh_check_mark(root):
    d, t, yt, s, thread = in_review(root)
    approve(d, t, s)
    vid = s.data()["youtube"]["video_id"]
    d.tap(s.data()["video"]["approved"]["message"], STOP)
    t.run()
    assert s.status == "video_review" and yt.videos[vid]["privacyStatus"] == "private"
    assert not yt.videos[vid]["publishAt"] and not s.data()["youtube"]["publish_at"]
    assert d.threads[thread][-1]["files"]                     # posted again, with the file
    t.run()                                    # the old check mark is on the old message: no re-approval
    assert s.status == "video_review"
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    assert s.status == "scheduled" and yt.n == 1             # the same upload, rescheduled


def test_release_check_records_it_as_published(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, clock=clock)
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    t.run()
    assert s.status == "scheduled"                      # not due yet
    clock.t = NOON + dt.timedelta(days=1, hours=6)
    yt.release_due()
    t.run()
    assert s.status == "published" and s.data()["youtube"]["published_at"] == "2026-11-04"
    assert d.bot_said(thread)[-1].startswith("🎉 Live")


def outside_spoilers(text):
    return re.sub(r"\|\|.*?\|\|", "", text, flags=re.S)


def test_no_bot_post_gives_the_answer_away(root):
    """#46: the answer and Level 2's accepted forms only ever appear inside ||spoiler|| tags."""
    clock = Clock()
    runner = FakeRunner()
    d, t, yt, s, thread = in_review(root, runner=runner, clock=clock)
    d.say(thread, ME, "0:12 slow down the slide")
    t.run()
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    d.tap(s.data()["video"]["approved"]["message"], STOP)
    t.run()
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    clock.t = NOON + dt.timedelta(days=1, hours=6)
    yt.release_due()
    t.run()
    assert s.status == "published"
    runner.fail_kind = "revise"                 # a second Short whose revise job fails, quoting the answer
    t.run(draft=True)
    s2 = all_shorts()[-1]
    d.say(s2.data()["review"]["thread_id"], ME, "shorter hook")
    t.run()
    assert s2.status == "needs_attention"

    words = tick.answers(s.data())
    assert {"Fifteen jumps", "24", "twenty-four"} <= set(words)
    posts = [m for ms in d.threads.values() for m in ms if m["bot"]]
    assert len(posts) > 8
    for m in posts:
        visible = outside_spoilers(m["content"])
        assert not any(re.search(rf"\b{re.escape(w)}\b", visible, re.I) for w in words), m["content"]
        assert "youtube.com" not in visible, m["content"]
        assert all(name.startswith("SPOILER_") for name in m["files"])


def test_spoiler_tags_cant_be_closed_early_and_titles_hide_answers(root):
    assert tick.spoiler("a || b ```x```") == "||a | | b '''x'''||"
    assert tick.spoiler("  ") == ""
    d, t, s, thread = scripted(root)
    assert tick.title(s) == f"{s.number} · Six Frogs"
    s.update(title="Twenty-four frogs")
    assert tick.title(s) == f"{s.number} · a new puzzle"


def test_a_late_release_is_flagged_once(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, clock=clock)
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    clock.t = NOON + dt.timedelta(days=1, hours=8)       # YouTube never released it
    t.run()
    t.run()
    assert s.status == "scheduled"
    assert sum("was due to go public" in c for c in d.bot_said(thread)) == 1


def test_failed_upload_warns_once_and_retries_with_a_fresh_slot(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(fail_uploads=2), clock=clock)
    approve(d, t, s)
    t.run()
    assert s.status == "video_review" and yt.attempts == 2
    assert sum("Couldn't upload or schedule v1" in c for c in d.bot_said(thread)) == 1
    clock.t = NOON + dt.timedelta(hours=3)                # 3 PM in New York
    t.run()
    assert s.status == "scheduled" and s.data()["youtube"]["publish_at"] == "2026-11-04T16:00:00-05:00"


def test_upload_limit_pauses_uploads_for_8_hours(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(limit_uploads=1), clock=clock)
    approve(d, t, s)
    assert s.status == "video_review" and yt.attempts == 1
    assert tick.uploads_paused_until(clock()) == NOON + dt.timedelta(hours=8)
    for hours in (1, 4, 7.9):                             # paused: no attempts, no repeat notices
        clock.t = NOON + dt.timedelta(hours=hours)
        t.run()
    assert yt.attempts == 1 and s.status == "video_review"
    notices = [c for c in d.bot_said(thread) if "daily upload limit" in c]
    assert len(notices) == 1 and "Uploads resume after Wed 4 Nov, 8:00 PM EST" in notices[0]
    clock.t = NOON + dt.timedelta(hours=8, minutes=5)
    t.run()
    assert yt.attempts == 2 and s.status == "scheduled"
    assert s.data()["youtube"]["publish_at"] == "2026-11-04T22:00:00-05:00"   # slot from when it went up


def test_video_jobs_need_no_youtube_only_approval_does(root):
    d, t = make(root, yt=False)
    t.yt = lambda: None                                   # noqa: E731 - as if the token expired
    t.yt_error = "token expired"
    t.run(draft=True)
    s = all_shorts()[0]
    thread = s.data()["review"]["thread_id"]
    d.tap(current_message(s), ACCEPT)
    t.run()
    assert s.status == "video_review"
    approve(d, t, s)
    assert s.status == "video_review" and any("token expired" in c for c in d.bot_said(thread))


def test_post_says_when_the_attachment_is_a_compressed_copy(root, monkeypatch):
    monkeypatch.setattr(tick, "review_copy", lambda m, cap=None: m.with_name("v1-discord.mp4"))
    d, t, yt, s, thread = in_review(root)
    post = d.threads[thread][-1]
    assert post["files"][f"SPOILER_{s.number}-video-v1.mp4"] == master(root, s).with_name("v1-discord.mp4")
    assert "Compressed to fit Discord" in post["content"]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_review_copy_fits_the_cap_and_leaves_the_master_alone(tmp_path):
    src = tmp_path / "v1.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=540x960:rate=30:duration=4",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-c:v", "libx264", "-b:v", "6M",
                    "-c:a", "aac", "-shortest", str(src)], check=True)
    before, size = tick.sha256(src), src.stat().st_size
    assert tick.review_copy(src, cap=size + 1) == src
    copy = tick.review_copy(src, cap=size // 3)
    assert copy == tmp_path / "v1-discord.mp4" and copy.stat().st_size <= size // 3
    assert tick.sha256(src) == before
    mtime = copy.stat().st_mtime_ns
    assert tick.review_copy(src, cap=size // 3) == copy and copy.stat().st_mtime_ns == mtime   # reused


def test_failing_ms_check_twice_needs_attention(root):
    d, t, yt, s, thread = in_review(root, checks=FakeChecks(check_ok=False))
    assert s.status == "needs_attention" and "ms check" in s.data()["last_error"]
    assert yt.videos == {}


def test_cross_on_a_video_abandons_and_deletes_uploads(root):
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(fail_schedule=1))
    approve(d, t, s)                                       # uploaded, but not scheduled
    assert yt.videos
    d.tap(video(s)[1]["message"], CROSS)
    t.run()
    assert s.status == "abandoned" and yt.videos == {}


def test_ms_animate_as_is_sends_your_scene_without_a_job(root):
    cli.main(["new", "--blank", "Mine"])
    s = all_shorts()[0]
    (s.folder / "verify.py").write_text("print('ok')\n")
    cli.main(["animate", s.number, "--as-is"])
    runner = FakeRunner()
    d, t = make(root, runner)
    t.run()
    assert s.status == "video_review" and runner.calls == []
    assert s.data()["review"]["thread_id"] in d.threads


# --- release slots -----------------------------------------------------------------------------
NY = {"time": "17:00", "timezone": "America/New_York", "per_day": 1, "lead_hours": 2}


@pytest.mark.parametrize("now,taken,expected", [
    ("2026-11-04T12:00:00-05:00", [], "2026-11-04T17:00:00-05:00"),                 # today
    ("2026-11-04T15:30:00-05:00", [], "2026-11-05T17:00:00-05:00"),                 # under 2 h: tomorrow
    ("2026-11-04T12:00:00-05:00", ["2026-11-04", "2026-11-05"], "2026-11-06T17:00:00-05:00"),
    ("2026-03-07T20:00:00-05:00", [], "2026-03-08T17:00:00-04:00"),                 # across the DST change
])
def test_next_slot(now, taken, expected):
    got = release.next_slot(dt.datetime.fromisoformat(now), [dt.date.fromisoformat(d) for d in taken], NY)
    assert got.isoformat() == expected


def test_days_ahead_skips_today():
    now = dt.datetime.fromisoformat("2026-11-04T09:00:00-05:00")
    assert release.next_slot(now, [], {**NY, "days_ahead": 1}).isoformat() == "2026-11-05T17:00:00-05:00"


def test_two_a_day_at_most():
    now = dt.datetime.fromisoformat("2026-11-04T12:00:00-05:00")
    day = [dt.date(2026, 11, 4)]
    assert release.next_slot(now, day, {**NY, "per_day": 2}).date() == dt.date(2026, 11, 4)
    assert release.next_slot(now, day * 2, {**NY, "per_day": 2}).date() == dt.date(2026, 11, 5)


ASAP = {**NY, "mode": "asap", "asap_minutes": 60, "per_day": 2, "days_ahead": 1}


@pytest.mark.parametrize("now, taken, expected", [
    ("2026-11-04T19:23:00-05:00", [], "2026-11-04T21:00:00-05:00"),                 # 7:23 PM -> 9 PM
    ("2026-11-04T19:00:00-05:00", [], "2026-11-04T20:00:00-05:00"),                 # exactly an hour
    ("2026-11-04T23:30:00-05:00", [], "2026-11-05T01:00:00-05:00"),                 # past midnight
    ("2026-11-04T19:23:00-05:00", ["2026-11-04"], "2026-11-04T21:00:00-05:00"),     # one left today
    ("2026-11-04T19:23:00-05:00", ["2026-11-04"] * 2, "2026-11-05T17:00:00-05:00"),  # full: next day's slot
    ("2026-11-04T19:23:00-05:00", ["2026-11-04"] * 2 + ["2026-11-05"] * 2, "2026-11-06T17:00:00-05:00"),
    ("2026-11-01T00:30:00-04:00", [], "2026-11-01T01:00:00-05:00"),                 # DST ends: 1:30 EDT -> 1:00 EST
])
def test_asap(now, taken, expected):
    got = release.next_slot(dt.datetime.fromisoformat(now), [dt.date.fromisoformat(d) for d in taken], ASAP)
    assert got.isoformat() == expected


def test_real_config_is_asap(root):
    cfg = release.settings()
    assert cfg["mode"] == "asap" and "60 minutes" in release.describe(cfg)


# --- the sandbox ---------------------------------------------------------------------------------
def test_job_container_gets_the_token_by_name_and_only_its_worktree(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "secret-token")
    cmd = sandbox.docker(["claude", "-p", "x"], [(tmp_path, "/app", "rw")], {"MS_ROOT": "/app"},
                         pass_env=("CLAUDE_CODE_OAUTH_TOKEN",))
    assert "secret-token" not in " ".join(cmd)
    assert cmd[cmd.index("CLAUDE_CODE_OAUTH_TOKEN") - 1] == "-e"
    mounts = [cmd[i + 1] for i, a in enumerate(cmd) if a == "-v"]
    assert mounts == [f"{tmp_path.resolve()}:/app:rw"]


def test_host_map_rewrites_mount_paths(monkeypatch):
    monkeypatch.setenv("MS_HOST_MAP", "/app=/srv/mathshorts")
    assert sandbox.host_path("/app/shorts") == "/srv/mathshorts/shorts"
    assert sandbox.host_path("/apple") == "/apple"


def test_video_jobs_may_preview_and_check_but_script_jobs_may_not():
    assert "Bash(ms preview:*)" in jobs.ALLOWED_VIDEO and "Bash(ms preview:*)" not in jobs.ALLOWED
    assert "Bash(git:*)" in jobs.DENIED and set(jobs.BUDGET_USD) == set(jobs.KINDS)


def test_a_discord_failure_after_upload_does_not_upload_twice(root):
    d, t, yt, s, thread = in_review(root)
    d.tap(video(s)[1]["message"], ACCEPT)
    real_post = d.post

    def flaky(thread, content, files=None, reactions=()):
        if content.startswith("✅ v"):
            raise RuntimeError("Discord timed out")
        return real_post(thread, content, files, reactions)
    d.post = flaky
    assert t.run()["failed"] == [s.name]                    # logged; the tick carries on
    assert video(s)[1]["video_id"] == "vid1"
    d.post = real_post
    t.run()
    assert s.status == "scheduled" and s.data()["youtube"]["video_id"] == "vid1" and yt.n == 1


def test_an_unreadable_short_yaml_doesnt_stop_the_others(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, clock=clock)
    cli.main(["new", "--blank", "Broken"])
    broken = all_shorts()[-1]
    broken.yaml_path.write_text("status: revise\ninsight: one\n  two: three\n")   # what a job wrote on 2026-11-05
    approve(d, t, s)
    assert s.status == "scheduled"
    assert t.run(draft=True)["scripted"]                    # no_room counts the readable ones


def test_a_job_short_yaml_that_wont_load_is_refused(tmp_path):
    p = tmp_path / "short.yaml"
    p.write_text("status: revise\ninsight: Pens need not be squares. A second\n  answer: two squares\n")
    assert "mapping values are not allowed" in jobs.yaml_problem(p)
    p.write_text("title: x\n")
    assert jobs.yaml_problem(p) == "no status"
    p.write_text("status: revise\ninsight: >-\n  A second answer: two squares\n")
    assert jobs.yaml_problem(p) is None


def test_draft_waits_for_a_busy_tick_but_a_plain_tick_skips(root, monkeypatch):
    import threading
    import time as _time
    with tick.lock() as got:
        assert got
        d, t = make(root)
        assert t.run()["skipped"] == "another tick is running"
        monkeypatch.setattr(tick, "DRAFT_WAIT", 5)
        out = {}
        th = threading.Thread(target=lambda: out.update(r=t.run(draft=True)))
        th.start()
        _time.sleep(0.3)
    th.join()
    assert out["r"]["scripted"] and len(all_shorts()) == 1
