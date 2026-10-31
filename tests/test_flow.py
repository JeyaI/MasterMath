"""Status machine, `ms new`, notes, approve guards, and batch failure isolation."""
import json
import subprocess

import pytest
from conftest import FIXTURES

from lib import audio
from mathshorts import batch, catalog, cli, render
from mathshorts.shorts import StatusError, all_shorts, find, used_catalog_ids


def make_short(root, number, status, verify_ok=True, scene="raise RuntimeError('broken scene')"):
    d = root / "shorts" / f"{number}-t"
    d.mkdir()
    (d / "short.yaml").write_text(f"id: '{number}'\ntitle: T\nstatus: {status}\ncatalog_id:\ntags: []\n")
    (d / "verify.py").write_text("print('ok')\n" if verify_ok else "raise SystemExit('bad answer')\n")
    (d / "scene.py").write_text(f"from manim import Scene\nclass Short(Scene):\n    def construct(self):\n        {scene}\n")
    return find(number)


def test_transitions_guarded(root):
    s = make_short(root, "0001", "drafting")
    with pytest.raises(StatusError):
        s.transition("publish")
    assert s.transition("approve") == "approved"
    assert s.transition("batch_ok") == "ready"
    assert s.transition("reject") == "drafting"


def test_new_from_catalog_then_approve_guards(root):
    catalog.add_source("dudeney-amusements", file=FIXTURES / "dudeney_sample.txt")
    cli.main(["new", "dudeney-amusements-003"])
    s = all_shorts()[0]
    assert s.name == "0001-the-cross-and-the-square"
    assert s.status == "drafting"
    assert used_catalog_ids() == {"dudeney-amusements-003"}
    assert "Cut a Greek cross" in s.data()["puzzle"]["text"]
    with pytest.raises(SystemExit):                      # same puzzle twice
        cli.main(["new", "dudeney-amusements-003"])
    with pytest.raises(SystemExit):                      # stub verify.py fails -> no approval
        cli.main(["approve", "1"])
    (s.folder / "verify.py").write_text("print('ok')\n")
    s.add_note("caption too small", beat="0:05")
    with pytest.raises(SystemExit):                      # open note blocks approval
        cli.main(["approve", "1"])
    s.notes_path.write_text(s.notes_path.read_text().replace("- [ ]", "- [x]"))
    cli.main(["approve", "1"])
    assert s.status == "approved"


def set_music(s, piece, description):
    s.update(music={"piece": piece}, youtube={"description": description})


def test_new_short_defaults_to_the_library_default_and_credits_it(root, capsys):
    cli.main(["new", "--blank", "T"])
    s = all_shorts()[0]
    assert s.data()["music"]["piece"] == audio.DEFAULT
    assert f"Music: {audio.PIECES[audio.DEFAULT].credit}" in s.data()["youtube"]["description"]


def test_approve_requires_a_known_piece_and_its_credit(root):
    s = make_short(root, "0001", "drafting")
    set_music(s, "wrong-key", "Music: J. S. Bach, Prelude in C, BWV 846.")
    with pytest.raises(SystemExit, match="unknown music piece"):
        cli.main(["approve", "1"])
    set_music(s, "k545", "Music: J. S. Bach, Prelude in C, BWV 846.")
    with pytest.raises(SystemExit, match="must credit its music"):
        cli.main(["approve", "1"])
    assert s.status == "drafting"
    set_music(s, "k545", "Music: W. A. Mozart, Piano Sonata in C, K. 545.")
    cli.main(["approve", "1"])
    assert s.status == "approved"


def test_ms_music_lists_least_recent_first_and_writes_a_wav(root, capsys, monkeypatch):
    make_short(root, "0001", "drafting")                                  # no music: the default
    set_music(make_short(root, "0002", "drafting"), "k545", "")
    cli.main(["music"])
    lines = capsys.readouterr().out.splitlines()[1:]
    assert len(lines) == len(audio.PIECES)
    assert lines[-1].split()[:2] == ["k545", "0002"]
    assert lines[-2].split()[:2] == ["bwv846", "0001"]
    written = []
    monkeypatch.setattr(audio, "write_music", lambda path, dur, key: written.append((path, key)) or path)
    cli.main(["music", "k545"])
    assert written == [(root / "out" / "music" / "k545.wav", "k545")]
    with pytest.raises(SystemExit, match="unknown music piece"):
        cli.main(["music", "nope"])


def test_batch_mixes_the_shorts_piece_and_fails_early_on_an_unknown_one(root, monkeypatch):
    good = make_short(root, "0001", "approved")
    good.update(music={"piece": "k545"})
    bad = make_short(root, "0002", "approved")
    bad.update(music={"piece": "J. S. Bach (free text)"})
    rendered, mixed = [], []

    def fake_final(short, build):
        rendered.append(short.number)
        build.mkdir(parents=True, exist_ok=True)
        return build / "raw.mp4", ""

    def fake_mix(raw, final, piece):
        mixed.append(piece)
        final.parent.mkdir(parents=True, exist_ok=True)
        return final

    monkeypatch.setattr(render, "render_final", fake_final)
    monkeypatch.setattr(render, "mix", fake_mix)
    monkeypatch.setattr(render, "thumbnail", lambda *a: None)
    monkeypatch.setattr(render, "duration", lambda v: 45.0)
    batch.run()
    assert rendered == ["0001"] and mixed == ["k545"]
    assert good.status == "ready"
    assert bad.status == "failed" and "unknown music piece" in bad.data()["last_error"]


def test_batch_isolates_failures(root):
    bad_verify = make_short(root, "0001", "approved", verify_ok=False)
    bad_scene = make_short(root, "0002", "approved")
    waiting = make_short(root, "0003", "drafting")
    r = batch.run(echo=lambda *a: None)
    assert r["failed"] == ["0001-t", "0002-t"]
    assert bad_verify.status == "failed" and "verify" in bad_verify.data()["last_error"]
    assert bad_scene.status == "failed" and "manim failed" in bad_scene.data()["last_error"]
    assert waiting.status == "drafting"
    assert len(list((root / "out" / "logs").glob("*.log"))) == 2


def fake_final(short, build, beats):
    """Stand in for manim: a 6 s clip, red until 3 s and blue after, plus this render's beats."""
    build.mkdir(parents=True, exist_ok=True)
    raw = build / "raw.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=red:s=108x192:r=30:d=3",
                    "-f", "lavfi", "-i", "color=blue:s=108x192:r=30:d=3", "-filter_complex",
                    "concat=n=2:v=1", "-pix_fmt", "yuv420p", str(raw)], check=True)
    (build / "beats.json").write_text(json.dumps(beats), encoding="utf-8")
    return raw, "fake manim log"


def test_batch_kit_has_thumbnail_from_before_the_pause_beat(root, monkeypatch):
    s = make_short(root, "0001", "approved")
    beats = [{"t": 0.0, "anim": 0, "name": "hook"}, {"t": 3.0, "anim": 3, "name": "Pause and try it"}]
    monkeypatch.setattr(render, "render_final", lambda short, build: fake_final(short, build, beats))
    r = batch.run(echo=lambda *a: None)
    assert r["ready"] == ["0001-t"]
    kit = root / "out" / "ready" / s.name
    assert "thumbnail.png" in (kit / "upload.txt").read_text()
    png = kit / "thumbnail.png"
    size = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                           str(png)], capture_output=True, text=True, check=True).stdout.strip()
    assert size == "108,192"
    pixel = subprocess.run(["ffmpeg", "-v", "error", "-i", str(png), "-frames:v", "1", "-vf", "crop=1:1",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    assert pixel[0] > 200 and pixel[2] < 50       # red: before the beat, not after it


def test_batch_fails_a_short_with_no_pause_beat(root, monkeypatch):
    s = make_short(root, "0001", "approved")
    monkeypatch.setattr(render, "render_final", lambda short, build: fake_final(
        short, build, [{"t": 0.0, "anim": 0, "name": "hook"}]))
    r = batch.run(echo=lambda *a: None)
    assert r["failed"] == ["0001-t"]
    assert "Pause and try it" in s.data()["last_error"]


def test_reject_and_published(root, capsys):
    s = make_short(root, "0001", "ready")
    (root / "out" / "ready" / s.name).mkdir(parents=True)
    cli.main(["reject", "1", "0:20 captions overlap"])
    assert s.status == "drafting" and s.open_notes()
    assert not (root / "out" / "ready" / s.name).exists()
    s.update(status="ready")
    cli.main(["published", "1", "https://youtube.com/shorts/AbC_dEf-123"])
    assert s.status == "published" and s.data()["youtube"]["video_id"] == "AbC_dEf-123"


def test_render_survives_a_working_directory_that_no_longer_resolves(root, tmp_path, monkeypatch):
    # Under /mnt/c on WSL a shell's working directory can stop resolving; manim dies on getcwd().
    gone = tmp_path / "gone"
    gone.mkdir()
    monkeypatch.chdir(gone)
    gone.rmdir()
    short = make_short(root, "0001", "approved")
    with pytest.raises(render.RenderError) as e:
        render.manim(short, (90, 160, 5), "cwd-test")
    assert "broken scene" in e.value.output      # manim started and reached the scene
