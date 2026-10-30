"""ms - the Math Shorts pipeline CLI.

    ms status                 list every Short and where it is in the pipeline
    ms verify  0001           run bank/0001-*/verify.py            (drafted  -> verified)
    ms preview 0001           fast 540x960 @15fps render to out/preview/
    ms approve 0001           human sign-off on the scene          (verified -> approved)
    ms render  0001 | --all   full 1080x1920 @30fps render         (approved -> rendered)
    ms mix     0001 | --all   music bed + loudness to out/final/   (rendered -> final)

    ms ingest / draft / upload are stubs - see CLAUDE.md for their specs.

Every command is idempotent and only acts on Shorts in the right status, so a
batch run is just `ms render --all && ms mix --all`.
All paths come from MS_* environment variables (see config()), so the same code
runs on a laptop, in Docker, or on a cloud box.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
STATUSES = ["ingested", "drafted", "verified", "approved", "rendered", "final", "scheduled", "published"]


def config() -> dict:
    out = Path(os.environ.get("MS_OUT_DIR", REPO / "out"))
    return {
        "bank": Path(os.environ.get("MS_BANK_DIR", REPO / "bank")),
        "out": out,
        "music_gain": float(os.environ.get("MS_MUSIC_GAIN", "0.28")),
        "lufs": float(os.environ.get("MS_TARGET_LUFS", "-14")),
    }


# --- bank helpers ------------------------------------------------------------------
def find(short_id: str) -> Path:
    hits = sorted(config()["bank"].glob(f"{short_id}-*"))
    if len(hits) != 1:
        sys.exit(f"ms: expected one bank folder for {short_id!r}, found {[h.name for h in hits]}")
    return hits[0]


def load(folder: Path) -> dict:
    return yaml.safe_load((folder / "problem.yaml").read_text())


def set_status(folder: Path, new: str) -> None:
    # Edit the status line in place so comments and formatting in problem.yaml survive.
    p = folder / "problem.yaml"
    text, n = re.subn(r"(?m)^status:[ \t]*\S+", f"status: {new}", p.read_text(), count=1)
    if n != 1:
        sys.exit(f"ms: no status line in {p}")
    p.write_text(text)
    print(f"  {folder.name}: -> {new}")


def require(folder: Path, *allowed: str, force: bool = False) -> bool:
    st = load(folder)["status"]
    if st in allowed or force:
        return True
    print(f"  {folder.name}: skipped (status is {st!r}, needs {' or '.join(allowed)})")
    return False


def targets(args) -> list[Path]:
    if getattr(args, "all", False):
        return sorted(p for p in config()["bank"].iterdir() if (p / "problem.yaml").exists())
    if not args.id:
        sys.exit("ms: give an id or --all")
    return [find(args.id)]


# --- rendering -------------------------------------------------------------------------
def manim(folder: Path, width: int, height: int, fps: int, name: str) -> Path:
    media = config()["out"] / "media"
    cmd = ["manim", "render", "--resolution", f"{width},{height}", "--fps", str(fps),
           "--media_dir", str(media), "--disable_caching", "--progress_bar", "none",
           "-o", name, str(folder / "scene.py"), "Short"]
    subprocess.run(cmd, check=True)
    hits = sorted(media.rglob(f"{name}.mp4"), key=lambda p: p.stat().st_mtime)
    if not hits:
        sys.exit(f"ms: manim finished but {name}.mp4 not found under {media}")
    return hits[-1]


def duration(video: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "json", str(video)], check=True, capture_output=True, text=True)
    return float(json.loads(out.stdout)["format"]["duration"])


def has_audio(video: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    return bool(out.stdout.strip())


# --- commands ------------------------------------------------------------------------
def cmd_status(args):
    for folder in sorted(config()["bank"].iterdir()):
        if (folder / "problem.yaml").exists():
            d = load(folder)
            print(f"{folder.name:<28} {d['status']:<10} {d.get('youtube', {}).get('title', '')}")


def cmd_verify(args):
    for folder in targets(args):
        print(f"verify {folder.name}")
        r = subprocess.run([sys.executable, "verify.py"], cwd=folder)
        if r.returncode != 0:
            sys.exit(f"ms: verify failed for {folder.name}")
        if load(folder)["status"] in ("ingested", "drafted"):
            set_status(folder, "verified")


def cmd_preview(args):
    for folder in targets(args):
        src = manim(folder, 540, 960, 15, f"{folder.name}-preview")
        dst = config()["out"] / "preview" / f"{folder.name}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f"  preview: {dst}  ({duration(dst):.1f}s)")


def cmd_approve(args):
    for folder in targets(args):
        if require(folder, "verified", force=args.force):
            set_status(folder, "approved")


def cmd_render(args):
    for folder in targets(args):
        if not require(folder, "approved", force=args.force):
            continue
        src = manim(folder, 1080, 1920, 30, f"{folder.name}-raw")
        dst = config()["out"] / "render" / f"{folder.name}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f"  render: {dst}  ({duration(dst):.1f}s)")
        set_status(folder, "rendered")


def cmd_mix(args):
    sys.path.insert(0, str(REPO))
    from lib.audio import write_music

    cfg = config()
    for folder in targets(args):
        if not require(folder, "rendered", force=args.force):
            continue
        raw = cfg["out"] / "render" / f"{folder.name}.mp4"
        dur = duration(raw)
        music = write_music(cfg["out"] / "audio" / f"{folder.name}-music.wav", dur)
        final = cfg["out"] / "final" / f"{folder.name}.mp4"
        final.parent.mkdir(parents=True, exist_ok=True)
        if has_audio(raw):
            # Manim's sound track ends at the last sound effect, so pad it to the full length.
            graph = (f"[0:a]apad=whole_dur={dur:.3f}[s];[1:a]volume={cfg['music_gain']}[m];"
                     f"[s][m]amix=inputs=2:duration=longest:normalize=0,"
                     f"loudnorm=I={cfg['lufs']}:TP=-1.5:LRA=11[a]")
        else:
            graph = f"[1:a]volume={cfg['music_gain']},loudnorm=I={cfg['lufs']}:TP=-1.5:LRA=11[a]"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-i", str(music),
                        "-filter_complex", graph, "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-t", f"{dur:.3f}", "-movflags", "+faststart", str(final)], check=True)
        print(f"  final: {final}  ({duration(final):.1f}s)")
        set_status(folder, "final")


def cmd_stub(name: str):
    def run(args):
        sys.exit(f"ms {name}: not built yet - see the '{name}' spec in CLAUDE.md")
    return run


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ms", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    for name, fn in (("verify", cmd_verify), ("preview", cmd_preview), ("approve", cmd_approve),
                     ("render", cmd_render), ("mix", cmd_mix)):
        p = sub.add_parser(name)
        p.add_argument("id", nargs="?")
        p.add_argument("--all", action="store_true")
        p.add_argument("--force", action="store_true", help="ignore the status check")
        p.set_defaults(fn=fn)
    for name in ("ingest", "draft", "upload"):
        p = sub.add_parser(name)
        p.add_argument("rest", nargs="*")
        p.set_defaults(fn=cmd_stub(name))
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
