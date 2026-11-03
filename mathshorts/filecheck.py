"""File and upload match checks (#27; STUBS, not yet implemented).

These are the "File and upload match" gate in docs/pipeline-design.md: they let a Short the system
uploaded go public without anyone watching it again. Nothing calls them yet. They raise instead of
returning no findings, so an unfinished check can never be mistaken for a passing one.
"""
from __future__ import annotations

from pathlib import Path

from .check import Finding
from .shorts import Short

# What check_kit will enforce on the final mp4.
WIDTH, HEIGHT, FPS = 1080, 1920, 30
VIDEO_CODEC, AUDIO_CODEC = "h264", "aac"
DURATION_TOL = 0.5          # seconds between the file and the scene probe's duration


def check_kit(short: Short, kit: Path) -> list[Finding]:
    """The ready kit before upload. Planned: ffprobe the mp4 for size, fps, codecs, an audio stream
    and duration (within DURATION_TOL of the probe); thumbnail.png and upload.txt exist; write the
    mp4's sha256 to kit/manifest.json."""
    raise NotImplementedError("file check is a stub (#27)")


def check_upload(short: Short, video_id: str) -> list[Finding]:
    """The video after upload. Planned: videos.list (snippet, contentDetails, status, processingDetails)
    and compare title, description and duration with short.yaml and the kit's manifest; processing
    must have succeeded. YouTube exposes no file hash, so duration is the proxy for "same file"."""
    raise NotImplementedError("upload match is a stub (#27)")
