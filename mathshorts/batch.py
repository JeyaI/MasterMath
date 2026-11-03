"""Nightly batch: approved Shorts -> polished MP4 + upload kit, one at a time.

One broken Short never stops the others: it's marked `failed` with a log in out/logs/.
A lock file stops two batches running at once (e.g. a manual run during the nightly one).

    out/ready/<short>/<short>.mp4   the finished video
    out/ready/<short>/thumbnail.png the frame where the problem is fully posed
    out/ready/<short>/upload.txt    title, description, tags to paste into YouTube Studio
"""
from __future__ import annotations

import datetime as dt
import fcntl
import os
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

from . import paths, render
from .shorts import Short, all_shorts


@contextmanager
def lock():
    p = paths.out() / ".batch.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    f = open(p, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("ms: another batch is already running")
    try:
        yield
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def ready_dir(short: Short) -> Path:
    return paths.out() / "ready" / short.name


def upload_text(short: Short) -> str:
    d = short.data()
    yt = d.get("youtube") or {}
    tags = list(yt.get("tags") or [])
    return (
        f"TITLE (max 100 chars)\n{(yt.get('title') or d.get('title') or short.name).strip()}\n\n"
        f"DESCRIPTION\n{(yt.get('description') or '').strip()}\n\n#shorts #math #puzzle\n\n"
        f"TAGS (comma-separated)\n{', '.join(tags)}\n\n"
        f"THUMBNAIL\nthumbnail.png (in this folder)\n\n"
        f"AFTER UPLOADING\nms published {short.number} <video URL>\n"
    )


def build_one(short: Short, log, kit: Path | None = None) -> Path:
    piece = render.music_piece(short)     # an unknown key should fail before the slow render
    ok, out = short.verify()
    log(f"verify: {'OK' if ok else 'FAILED'}\n{out}\n")
    if not ok:
        raise RuntimeError("verify.py failed")
    build = paths.out() / "build" / short.name
    raw, mlog = render.render_final(short, build)
    log(mlog)
    kit = kit or ready_dir(short)
    if kit.exists():
        shutil.rmtree(kit)
    final = render.mix(raw, kit / f"{short.name}.mp4", piece.key)
    render.thumbnail(raw, build / "beats.json", kit / "thumbnail.png")
    (kit / "upload.txt").write_text(upload_text(short), encoding="utf-8")
    return final


def run(only: Short | None = None, commit: bool = False, echo=print) -> dict:
    targets = [only] if only else [s for s in all_shorts() if s.status == "approved"]
    result = {"ready": [], "failed": [], "skipped": []}
    with lock():
        for s in targets:
            if s.status != "approved":
                result["skipped"].append(s.name)
                echo(f"  {s.name}: skipped (status {s.status!r}; only approved Shorts are built)")
                continue
            stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            log_path = paths.out() / "logs" / f"{s.name}-{stamp}.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as lf:
                try:
                    echo(f"  {s.name}: rendering…")
                    final = build_one(s, lf.write)
                    s.transition("batch_ok")
                    s.update(built_at=stamp, last_error=None)
                    result["ready"].append(s.name)
                    echo(f"  {s.name}: ready  {final}  ({render.duration(final):.1f}s)")
                except Exception as e:  # noqa: BLE001 - isolate every failure
                    lf.write(f"\nFAILED: {e}\n{getattr(e, 'output', '')}")
                    s.transition("batch_fail")
                    s.update(last_error=f"{str(e).splitlines()[0][:200]} (log: {log_path.name})")
                    result["failed"].append(s.name)
                    echo(f"  {s.name}: FAILED  see {log_path}")
        if commit and (result["ready"] or result["failed"]):
            _commit(result)
    return result


def _commit(result: dict) -> None:
    root = paths.root()
    subprocess.run(["git", "add", "shorts"], cwd=root, check=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root)
    if staged.returncode == 0:
        return
    parts = [f"ready: {', '.join(result['ready'])}"] if result["ready"] else []
    parts += [f"failed: {', '.join(result['failed'])}"] if result["failed"] else []
    subprocess.run(["git", "commit", "-q", "-m", f"batch {dt.date.today()}: {'; '.join(parts)}"],
                   cwd=root, check=True, env={**os.environ})
