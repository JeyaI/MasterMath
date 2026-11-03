#!/usr/bin/env python
"""Phase 0 YouTube test (#25): does an unverified API project's upload lock private?

Uploads a blank 5 s card as unlisted and another as private, the pipeline's real flow. Each is set
to private with a publishAt a week away, re-read for up to 2 minutes, then deleted. Nothing ever
goes public: the release time is further off than the delete, and a card stays only if its delete
fails.

Needs ~/.config/mathshorts-youtube-client.json and `pip install -e ".[upload]"`. It prints a
Google sign-in link; sign in as the channel. Result: out/trial/youtube-test.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONFIG = Path.home() / ".config"
CLIENT = CONFIG / "mathshorts-youtube-client.json"
TOKEN = CONFIG / "mathshorts-youtube-token.json"
REPORT = Path(__file__).resolve().parents[1] / "out" / "trial" / "youtube-test.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def verdict(unlisted_stayed: bool, unlisted_scheduled: bool, private_scheduled: bool) -> str:
    """Which row of the design doc's test table this result lands in."""
    if not unlisted_stayed:
        return "locked: upload approved videos by hand and apply for the audit"
    if private_scheduled:
        note = "unlisted can also be scheduled" if unlisted_scheduled else "unlisted cannot be scheduled"
        return f"not locked: fully automatic from a private upload; {note}"
    return "not locked, but cannot schedule"


def credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES)
        creds = flow.run_local_server(port=8765, open_browser=False, prompt="consent")
    fd = os.open(TOKEN, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(creds.to_json())
    return creds


def make_card(path: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "color=c=0x202830:s=1080x1920:r=30:d=5",
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(path)],
        check=True)


def upload(youtube, path: Path, privacy: str) -> str:
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {"title": "API test, will be deleted", "description": "Pipeline test.", "categoryId": "27"},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]


def wait_for_processing(youtube, video_id: str, timeout: int = 300) -> dict:
    deadline = time.time() + timeout
    while True:
        items = youtube.videos().list(part="status,processingDetails", id=video_id).execute()["items"]
        video = items[0] if items else {}
        state = video.get("processingDetails", {}).get("processingStatus")
        if state in ("succeeded", "failed", "terminated") or time.time() > deadline:
            return video
        time.sleep(10)


def schedule(youtube, video_id: str) -> dict:
    """Ask for a release time, keeping YouTube's reply and re-reading in case the change lags."""
    publish_at = datetime.now(timezone.utc) + timedelta(days=7)
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
              "publishAt": publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")}
    reply = youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()
    result = {"reply": reply.get("status"), "reads": []}
    for wait in (0, 30, 90):
        time.sleep(wait)
        read = youtube.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
        result["reads"].append(read)
        if read.get("publishAt"):
            break
    return result


def run_case(youtube, card: Path, privacy: str) -> dict:
    """Upload one card, try to schedule it, and always delete it."""
    from googleapiclient.errors import HttpError

    video_id = upload(youtube, card, privacy)
    print(f"{privacy}: uploaded {video_id}", flush=True)
    case: dict = {"requested": privacy, "video_id": video_id, "scheduled": False}
    try:
        video = wait_for_processing(youtube, video_id)
        case["after_upload"] = video.get("status")
        case["privacy"] = video.get("status", {}).get("privacyStatus")
        print(f"{privacy}: after processing {case['privacy']}", flush=True)
        try:
            case["schedule"] = schedule(youtube, video_id)
            last = case["schedule"]["reads"][-1]
            case["scheduled"] = bool(last.get("publishAt")) and last.get("privacyStatus") == "private"
        except HttpError as e:
            case["schedule_error"] = str(e)
    finally:
        try:
            youtube.videos().delete(id=video_id).execute()
            case["deleted"] = True
        except HttpError as e:
            case["deleted"] = False
            case["delete_error"] = str(e)
            print(f"DELETE FAILED: remove {video_id} in YouTube Studio", file=sys.stderr, flush=True)
    return case


def main() -> int:
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", credentials=credentials())
    report: dict = {"run_at": datetime.now(timezone.utc).isoformat(), "cases": []}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            card = Path(tmp) / "card.mp4"
            make_card(card)
            for privacy in ("unlisted", "private"):
                report["cases"].append(run_case(youtube, card, privacy))
        unlisted, private = report["cases"]
        report["verdict"] = verdict(unlisted.get("privacy") == "unlisted", unlisted["scheduled"], private["scheduled"])
    finally:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps(report, indent=2), flush=True)
    return 0 if all(c["deleted"] for c in report["cases"]) else 1


if __name__ == "__main__":
    sys.exit(main())
