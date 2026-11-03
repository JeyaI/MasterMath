"""The script loop: `ms tick` against a fake Discord and a fake job runner."""
import pytest

from mathshorts import cli, tick
from mathshorts.discord import ACCEPT, CROSS
from mathshorts.jobs import JobResult, _env
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
        (folder / "SCRIPT.md").write_text(f"# Script\n{comment or 'first draft'}\n")
        return JobResult(True, short, summary="Frogs swap places.", usage={"total_cost_usd": 1.5})


def make(root, runner=None):
    d = FakeDiscord()
    return d, tick.Tick(d, ME, runner or FakeRunner(), echo=lambda *a: None, commit=False)


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
    assert s.status == "drafting"
    assert f"/draft-short {s.number}" in d.bot_said(thread)[-1]


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
    assert s.status == "drafting"
    assert [e["event"] for e in s.events()] == ["script_done", "comment", "revised", "accept_script"]


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
    assert len(all_shorts()) == 1 and "waiting on you" in r["skipped"]


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
