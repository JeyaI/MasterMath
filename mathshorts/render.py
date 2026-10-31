"""Rendering: previews (full or one beat), before/after compare, final render and mix.

Previews are versioned so you can always compare against the last one:
    out/preview/<short>/v3.mp4            full preview (+ v3.beats.json, beats.json = latest)
    out/preview/<short>/v4-at-0m12s.mp4   just the beat that contains 0:12
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import paths
from .shorts import Short

PREVIEW = (540, 960, 15)
FINAL = (1080, 1920, 30)
THUMB_LEAD = 0.1  # seconds before the pause beat: its caption crossfade starts exactly on the beat


class RenderError(RuntimeError):
    def __init__(self, msg: str, output: str = ""):
        super().__init__(msg)
        self.output = output


# --- helpers ----------------------------------------------------------------------------
def open_file(path: Path) -> None:
    """Open a video in the desktop's default player: Windows from WSL, macOS, or Linux."""
    try:
        if "microsoft" in Path("/proc/version").read_text().lower():
            win = subprocess.run(["wslpath", "-w", str(path)], capture_output=True, text=True).stdout.strip()
            subprocess.Popen(["explorer.exe", win])
            return
    except OSError:
        pass
    opener = "open" if shutil.which("open") and not shutil.which("xdg-open") else "xdg-open"
    if shutil.which(opener):
        subprocess.Popen([opener, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parse_time(s: str) -> float:
    """'0:12' -> 12.0, '1:05.5' -> 65.5, '12' -> 12.0"""
    s = s.strip()
    if ":" in s:
        m, sec = s.split(":", 1)
        return int(m) * 60 + float(sec)
    return float(s)


def fmt_time(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def duration(video: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json",
                          str(video)], check=True, capture_output=True, text=True)
    return float(json.loads(out.stdout)["format"]["duration"])


def has_audio(video: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def manim(short: Short, size: tuple[int, int, int], name: str, extra: list[str] = (),
          env: dict | None = None) -> tuple[Path, str]:
    """Render scene.py:Short. Returns (mp4 path, combined log). Raises RenderError with the log."""
    w, h, fps = size
    media = paths.out() / "media"
    cmd = ["manim", "render", "--resolution", f"{w},{h}", "--fps", str(fps), "--media_dir", str(media),
           "--disable_caching", "--progress_bar", "none", "-o", name, *extra,
           str(short.folder / "scene.py"), "Short"]
    # Run from the repo root, not the caller's folder: under /mnt/c on WSL that folder can stop
    # resolving (see scripts/nightly.sh), and manim crashes on getcwd() at import.
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=paths.root(),
                       env={**os.environ, **(env or {})})
    log = f"$ {' '.join(cmd)}\n{r.stdout}\n{r.stderr}"
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-15:])
        raise RenderError(f"manim failed for {short.name}:\n{tail}", log)
    hits = sorted(media.rglob(f"{name}.mp4"), key=lambda p: p.stat().st_mtime)
    if not hits:
        raise RenderError(f"manim finished but {name}.mp4 is missing under {media}", log)
    return hits[-1], log


# --- previews ---------------------------------------------------------------------------
def preview_dir(short: Short) -> Path:
    return paths.out() / "preview" / short.name


def _next_version(d: Path) -> int:
    nums = [int(m.group(1)) for p in d.glob("v*.mp4") if (m := re.match(r"v(\d+)", p.name))]
    return max(nums, default=0) + 1


def beats(short: Short) -> list[dict]:
    p = preview_dir(short) / "beats.json"
    return json.loads(p.read_text()) if p.exists() else []


def beat_at(short: Short, t: float) -> tuple[dict, dict | None]:
    bs = beats(short)
    if not bs:
        raise SystemExit(f"ms: no beats.json for {short.name}; run a full `ms preview {short.number}` first")
    i = max((k for k, b in enumerate(bs) if b["t"] <= t), default=0)
    return bs[i], (bs[i + 1] if i + 1 < len(bs) else None)


def preview(short: Short, at: str | None = None) -> dict:
    d = preview_dir(short)
    d.mkdir(parents=True, exist_ok=True)
    v = _next_version(d)
    if at is None:
        beats_tmp = d / f"v{v}.beats.json"
        src, _ = manim(short, PREVIEW, f"{short.name}-v{v}", env={"MS_BEATS_PATH": str(beats_tmp)})
        dst = d / f"v{v}.mp4"
        shutil.copy(src, dst)
        if beats_tmp.exists():
            shutil.copy(beats_tmp, d / "beats.json")
        return {"path": dst, "duration": duration(dst), "version": v, "beat": None}
    t = parse_time(at)
    b, nxt = beat_at(short, t)
    # Manim's -n is "start,end" by animation number; end is exclusive-ish, so stop at the next beat.
    rng = f"{b['anim']},{nxt['anim'] - 1}" if nxt else f"{b['anim']}"
    tag = f"at-{int(t // 60)}m{int(t % 60):02d}s"
    src, _ = manim(short, PREVIEW, f"{short.name}-v{v}-{tag}", extra=["-n", rng])
    dst = d / f"v{v}-{tag}.mp4"
    shutil.copy(src, dst)
    return {"path": dst, "duration": duration(dst), "version": v, "beat": b}


def compare(short: Short) -> Path:
    """Side-by-side of the newest preview and the previous one of the same kind (full vs same beat)."""
    d = preview_dir(short)
    vids = sorted(d.glob("v*.mp4"), key=lambda p: int(re.match(r"v(\d+)", p.name).group(1)))
    vids = [p for p in vids if not p.name.endswith("-compare.mp4")]
    if not vids:
        raise SystemExit(f"ms: no previews for {short.name} yet")
    kind = lambda p: re.sub(r"^v\d+", "", p.stem)  # noqa: E731   "" for full, "-at-0m12s" for a beat
    after = vids[-1]
    before = next((p for p in reversed(vids[:-1]) if kind(p) == kind(after)), None)
    if before is None:
        raise SystemExit(f"ms: only one {('full' if not kind(after) else kind(after)[1:])} preview so far; nothing to compare")
    dst = d / f"{before.stem}-vs-{after.stem}-compare.mp4"
    font = next((f for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                              "/usr/share/fonts/truetype/inter/Inter-Bold.ttf") if Path(f).exists()), None)
    lab = (lambda txt: f",drawtext=fontfile={font}:text='{txt}':x=20:y=20:fontsize=36:fontcolor=white:"
                       f"box=1:boxcolor=black@0.5:boxborderw=8") if font else (lambda txt: "")
    graph = (f"[0:v]setpts=PTS-STARTPTS{lab(before.stem)}[a];[1:v]setpts=PTS-STARTPTS{lab(after.stem)}[b];"
             f"[a][b]hstack=inputs=2[v]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(before), "-i", str(after), "-filter_complex", graph,
           "-map", "[v]"] + (["-map", "1:a?"] if has_audio(after) else []) + \
          ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(dst)]
    subprocess.run(cmd, check=True)
    return dst


# --- final render + mix -----------------------------------------------------------------
def render_final(short: Short, build: Path) -> tuple[Path, str]:
    build.mkdir(parents=True, exist_ok=True)
    beats_path = build / "beats.json"
    beats_path.unlink(missing_ok=True)
    src, log = manim(short, FINAL, f"{short.name}-final", env={"MS_BEATS_PATH": str(beats_path)})
    raw = build / "raw.mp4"
    shutil.copy(src, raw)
    return raw, log


def thumbnail(video: Path, beats_path: Path, dest: Path) -> Path:
    """Save the frame just before "Pause and try it", when the problem is fully posed.

    Takes beats from this render, not out/preview, which can be stale or absent on a batch machine.
    """
    bs = json.loads(beats_path.read_text(encoding="utf-8")) if beats_path.exists() else []
    t = next((b["t"] for b in bs if "pause" in b["name"].lower()), None)
    if t is None:
        raise RenderError(f"no thumbnail: {video.parent.name} has no \"Pause and try it\" beat")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(t - THUMB_LEAD, 0):.3f}", "-i", str(video),
                    "-frames:v", "1", "-update", "1", str(dest)], check=True)
    return dest


def _audio():
    import sys
    sys.path.insert(0, str(paths.REPO))
    from lib import audio
    return audio


def music_piece(short: Short):
    """The library Piece a Short asked for. Raises ValueError on an unknown key."""
    return _audio().piece((short.data().get("music") or {}).get("piece"))


def mix(raw: Path, final: Path, piece: str | None = None, music_gain: float = 0.28, lufs: float = -14.0) -> Path:
    dur = duration(raw)
    music = _audio().write_music(raw.parent / "music.wav", dur, piece)
    final.parent.mkdir(parents=True, exist_ok=True)
    norm = f"loudnorm=I={lufs}:TP=-1.5:LRA=11"
    if has_audio(raw):
        # Manim's sound track ends at the last sound effect, so pad it to the full length first.
        graph = (f"[0:a]apad=whole_dur={dur:.3f}[s];[1:a]volume={music_gain}[m];"
                 f"[s][m]amix=inputs=2:duration=longest:normalize=0,{norm}[a]")
    else:
        graph = f"[1:a]volume={music_gain},{norm}[a]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-i", str(music), "-filter_complex", graph,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-t", f"{dur:.3f}", "-movflags", "+faststart", str(final)], check=True)
    return final
