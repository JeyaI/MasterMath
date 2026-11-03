"""The YouTube test's verdict must not call a locked upload "automatic"."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "youtube_test.py"
spec = importlib.util.spec_from_file_location("youtube_test", path)
youtube_test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(youtube_test)
verdict = youtube_test.verdict


def test_private_upload_scheduled_is_automatic():
    assert verdict(True, False, True).startswith("not locked: fully automatic")


def test_nothing_scheduled_is_not_automatic():
    assert verdict(True, False, False) == "not locked, but cannot schedule"


def test_locked_upload_wins_even_if_schedule_accepted():
    assert verdict(False, True, True).startswith("locked")
