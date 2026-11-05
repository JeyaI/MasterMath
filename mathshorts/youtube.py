"""YouTube for the video loop (#29, #48): upload the approved version, schedule it, check release.

Only `ms tick` and `ms youtube` use it; jobs never see the token. Review copies go to Discord (#48),
so the only upload is the one you approved, made private with a `publishAt`. It never makes a video
public itself: YouTube releases it at that time.

    ~/.config/mathshorts-youtube-client.json   the OAuth client (Google Cloud, Desktop app)
    ~/.config/mathshorts-youtube-token.json    the channel's token; `ms youtube login` writes it

`Client` is the interface `ms tick` needs; tests pass a fake with the same methods.
Needs `pip install -e ".[upload]"`.
"""
from __future__ import annotations

import datetime as dt
import os
import time
from pathlib import Path

CONFIG = Path.home() / ".config"
CLIENT = CONFIG / "mathshorts-youtube-client.json"
TOKEN = CONFIG / "mathshorts-youtube-token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
REVIEW_PRIVACY = ("unlisted", "private")     # never "public": the API's default is public
HASHTAGS = "#shorts #math #puzzle"


class YouTubeError(RuntimeError):
    pass


class UploadLimitError(YouTubeError):
    """The channel's daily upload cap (`uploadLimitExceeded`), separate from API quota (#47)."""


def credentials(interactive: bool = False):
    """The channel's credentials, refreshed. Only `ms youtube login` may open a sign-in."""
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if creds and creds.valid and not interactive:
        return creds
    try:
        if creds and creds.refresh_token and not interactive:
            creds.refresh(Request())
        elif interactive:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES)
            creds = flow.run_local_server(port=8765, open_browser=False, prompt="consent")
        else:
            raise YouTubeError(f"no YouTube token at {TOKEN}: run `ms youtube login`")
    except RefreshError as e:
        raise YouTubeError(f"the YouTube token no longer works ({e}): run `ms youtube login`") from None
    fd = os.open(TOKEN, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(creds.to_json())
    return creds


def metadata(data: dict) -> dict:
    """Title, description and tags from a Short's short.yaml."""
    yt = data.get("youtube") or {}
    title = (yt.get("title") or data.get("title") or "").strip()
    return {"title": title[:100],
            "description": f"{(yt.get('description') or '').strip()}\n\n{HASHTAGS}".strip(),
            "tags": [str(t) for t in yt.get("tags") or []]}


def stamp(when: dt.datetime) -> str:
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Client:
    def __init__(self, creds=None):
        from googleapiclient.discovery import build
        self.api = build("youtube", "v3", credentials=creds or credentials(), cache_discovery=False)

    def _do(self, request):
        from googleapiclient.errors import HttpError
        try:
            return request.execute()
        except HttpError as e:
            raise YouTubeError(str(e)) from None

    def hello(self) -> str:
        items = self._do(self.api.channels().list(part="snippet", mine=True)).get("items") or []
        if not items:
            raise YouTubeError("this token has no YouTube channel")
        return items[0]["snippet"]["title"]

    def upload(self, path: Path, meta: dict, privacy: str = "unlisted") -> str:
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaFileUpload
        if privacy not in REVIEW_PRIVACY:
            raise YouTubeError(f"refusing to upload as {privacy!r}: review versions are unlisted or private")
        body = {"snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                            "categoryId": "27"},                     # Education
                "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
        media = MediaFileUpload(str(path), mimetype="video/mp4", resumable=True)
        request = self.api.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        try:
            while response is None:
                _, response = request.next_chunk()
        except HttpError as e:
            body = e.content.decode("utf-8", "replace") if isinstance(e.content, bytes) else str(e.content or "")
            if "uploadLimitExceeded" in f"{e} {body}":
                raise UploadLimitError(f"upload: {e}") from None
            raise YouTubeError(f"upload: {e}") from None
        return response["id"]

    def status(self, video_id: str) -> dict:
        """{privacyStatus, publishAt, uploadStatus, processingStatus}; {} if the video is gone."""
        items = self._do(self.api.videos().list(part="status,processingDetails", id=video_id)).get("items")
        if not items:
            return {}
        v = items[0]
        return {**v.get("status", {}), "processingStatus": v.get("processingDetails", {}).get("processingStatus")}

    def wait_processed(self, video_id: str, timeout: int = 600) -> dict:
        deadline = time.time() + timeout
        while True:
            st = self.status(video_id)
            if st.get("processingStatus") in ("succeeded", "failed", "terminated") or time.time() > deadline:
                return st
            time.sleep(10)

    def schedule(self, video_id: str, when: dt.datetime) -> dict:
        """Private with a release time; YouTube makes it public then. Re-reads, since the change lags."""
        at = stamp(when)
        self._do(self.api.videos().update(part="status", body={"id": video_id, "status": {
            "privacyStatus": "private", "publishAt": at, "selfDeclaredMadeForKids": False}}))
        for wait in (0, 10, 20, 30):
            time.sleep(wait)
            st = self.status(video_id)
            if st.get("publishAt") and st.get("privacyStatus") == "private":
                return st
        raise YouTubeError(f"{video_id}: publishAt {at} didn't show up after a minute")

    def unschedule(self, video_id: str) -> None:
        """Back to private with no publishAt: nobody can see it, and a new check mark reschedules it."""
        self._do(self.api.videos().update(part="status", body={"id": video_id, "status": {
            "privacyStatus": "private", "selfDeclaredMadeForKids": False}}))

    def delete(self, video_id: str) -> None:
        self._do(self.api.videos().delete(id=video_id))


def url(video_id: str) -> str:
    return f"https://youtube.com/shorts/{video_id}"
