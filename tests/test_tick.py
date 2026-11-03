"""The script and video loops: `ms tick` against a fake Discord, YouTube, job runner and sandbox."""
import datetime as dt

import pytest

from mathshorts import cli, jobs, release, sandbox, tick
from mathshorts.discord import ACCEPT, CROSS, STOP
from mathshorts.jobs import JobResult, _env
from mathshorts.youtube import YouTubeError
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
        if kind == "script":
            cli.main(["new", "--blank", "Six Frogs", "--scripting"])
            short = all_shorts()[-1].name
        folder = find(short.split("-")[0]).folder
        (folder / "verify.py").write_text("print('ok')\n" if self.verify_ok else "raise SystemExit('wrong')\n")
        if kind in ("animate", "revise_video"):
            (folder / "scene.py").write_text(f"# scene\n# {comment or 'first cut'}\n")
        else:
            (folder / "SCRIPT.md").write_text(f"# Script\n{comment or 'first draft'}\n")
        return JobResult(True, short, summary="Frogs swap places.", usage={"total_cost_usd": 1.5})


class FakeYouTube:
    def __init__(self, fail_uploads=0):
        self.videos, self.deleted, self.n, self.fail_uploads = {}, [], 0, fail_uploads

    def upload(self, path, meta, privacy):
        if self.fail_uploads:
            self.fail_uploads -= 1
            raise YouTubeError("HTTP 503")
        assert privacy == "unlisted"
        self.n += 1
        vid = f"vid{self.n}"
        self.videos[vid] = {"privacyStatus": privacy, "title": meta["title"], "bytes": path.read_bytes()}
        return vid

    def wait_processed(self, vid):
        return {"processingStatus": "succeeded"}

    def schedule(self, vid, when):
        self.videos[vid].update(privacyStatus="private", publishAt=when)

    def unschedule(self, vid):
        self.videos[vid].update(privacyStatus="unlisted", publishAt=None)

    def status(self, vid):
        return dict(self.videos.get(vid, {}))

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
    first = d.threads[thread][0]
    assert "Script v1" in first["content"] and "Frogs swap places." in first["content"]
    assert list(first["files"]) == [f"{s.number}-script-v1.md"]
    assert d.reactors(thread, first["id"], ACCEPT) == {BOT}         # pre-added for you to tap
    assert [e["event"] for e in s.events()] == ["script_done"]
    assert s.events()[0]["usage"] == {"total_cost_usd": 1.5}


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


def test_accepted_script_is_animated_uploaded_unlisted_and_posted(root):
    d, t, yt, s, thread = in_review(root)
    assert s.status == "video_review"
    v, ver = video(s)
    assert v["version"] == 1 and yt.videos[ver["video_id"]]["privacyStatus"] == "unlisted"
    assert yt.videos[ver["video_id"]]["bytes"] == (root / "out" / "review" / s.name / "v1.mp4").read_bytes()
    post = d.threads[thread][-1]
    assert "Video v1" in post["content"] and f"youtube.com/shorts/{ver['video_id']}" in post["content"]
    assert post["id"] == ver["message"] and d.reactors(thread, post["id"], ACCEPT) == {BOT}
    assert ver["sha256"] == tick.sha256(root / "out" / "review" / s.name / "v1.mp4")


def test_reply_on_a_video_revises_it_and_deletes_the_old_upload(root):
    runner = FakeRunner()
    d, t, yt, s, thread = in_review(root, runner=runner)
    old = video(s)[1]["video_id"]
    d.say(thread, ME, "0:12 slow down the slide")
    t.run()
    assert runner.calls[-1] == ("revise_video", s.name, "0:12 slow down the slide")
    v, ver = video(s)
    assert s.status == "video_review" and v["version"] == 2 and ver["video_id"] != old
    assert yt.deleted == [old]


def test_check_mark_schedules_that_exact_upload_at_the_next_slot(root):
    d, t, yt, s, thread = in_review(root)
    vid = video(s)[1]["video_id"]
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    assert s.status == "scheduled"
    when = dt.datetime.fromisoformat(s.data()["youtube"]["publish_at"])
    assert when.isoformat() == "2026-11-04T17:00:00-05:00"          # today, 5 PM New York; 5 h away
    assert yt.videos[vid] == {**yt.videos[vid], "privacyStatus": "private", "publishAt": when}
    assert s.data()["youtube"]["video_id"] == vid
    assert d.reactors(thread, d.threads[thread][-1]["id"], STOP) == {BOT}


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
    vid = video(s)[1]["video_id"]
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    d.tap(s.data()["video"]["approved"]["message"], STOP)
    t.run()
    assert s.status == "video_review" and yt.videos[vid]["privacyStatus"] == "unlisted"
    assert not s.data()["youtube"]["publish_at"]
    t.run()                                    # the old check mark is on the old message: no re-approval
    assert s.status == "video_review"
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    assert s.status == "scheduled"


def test_release_check_records_it_as_published(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, clock=clock)
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    t.run()
    assert s.status == "scheduled"                      # not due yet
    clock.t = NOON + dt.timedelta(hours=6)
    yt.release_due()
    t.run()
    assert s.status == "published" and s.data()["youtube"]["published_at"] == "2026-11-04"
    assert d.bot_said(thread)[-1].startswith("🎉 Live")


def test_a_late_release_is_flagged_once(root):
    clock = Clock()
    d, t, yt, s, thread = in_review(root, clock=clock)
    d.tap(video(s)[1]["message"], ACCEPT)
    t.run()
    clock.t = NOON + dt.timedelta(hours=8)               # YouTube never released it
    t.run()
    t.run()
    assert s.status == "scheduled"
    assert sum("was due to go public" in c for c in d.bot_said(thread)) == 1


def test_failed_upload_keeps_the_render_and_retries_without_a_new_job(root):
    runner = FakeRunner()
    d, t, yt, s, thread = in_review(root, yt=FakeYouTube(fail_uploads=2), runner=runner)
    assert s.status == "animating" and s.data()["video"]["pending"]["version"] == 1
    t.run()
    assert sum("upload failed" in c for c in d.bot_said(thread)) == 1
    jobs_before = len(runner.calls)
    t.run()
    assert s.status == "video_review" and len(runner.calls) == jobs_before


def test_no_youtube_pauses_video_jobs_only(root):
    d, t = make(root, yt=False)
    t._yt, t.yt_error = None, None
    t.yt = lambda: None                                   # noqa: E731 - as if the token expired
    t.run(draft=True)
    s = all_shorts()[0]
    d.tap(current_message(s), ACCEPT)
    r = t.run()
    assert s.status == "animating" and r["paused"]


def test_failing_ms_check_twice_needs_attention(root):
    d, t, yt, s, thread = in_review(root, checks=FakeChecks(check_ok=False))
    assert s.status == "needs_attention" and "ms check" in s.data()["last_error"]
    assert yt.videos == {}


def test_cross_on_a_video_abandons_and_deletes_uploads(root):
    d, t, yt, s, thread = in_review(root)
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


def test_two_a_day_at_most():
    now = dt.datetime.fromisoformat("2026-11-04T12:00:00-05:00")
    day = [dt.date(2026, 11, 4)]
    assert release.next_slot(now, day, {**NY, "per_day": 2}).date() == dt.date(2026, 11, 4)
    assert release.next_slot(now, day * 2, {**NY, "per_day": 2}).date() == dt.date(2026, 11, 5)


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
