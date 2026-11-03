"""When an approved Short goes public (#29): the next open daily slot. Pure, so it's easy to test.

Rules (docs/pipeline-design.md, Publish scheduling): at most `per_day` releases a day (rule 1
caps it at 2), and at least `lead_hours` between approval and release, to leave time for the
stop sign. Settings: `release:` in config/pipeline.yaml.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from zoneinfo import ZoneInfo

from . import paths, yamlio

DEFAULTS = {"time": "17:00", "timezone": "America/New_York", "per_day": 1, "lead_hours": 2}


def settings() -> dict:
    p = paths.config() / "pipeline.yaml"
    cfg = (yamlio.load(p) or {}) if p.exists() else {}
    out = {**DEFAULTS, **(cfg.get("release") or {})}
    out["per_day"] = max(1, min(int(out["per_day"]), 2))         # rule 1
    return out


def next_slot(now: dt.datetime, taken: list[dt.date], cfg: dict | None = None) -> dt.datetime:
    """The earliest release time at least lead_hours after `now` on a day with room.

    `taken` lists the local release dates of Shorts already scheduled or published.
    """
    cfg = {**DEFAULTS, **(cfg or {})}
    tz = ZoneInfo(cfg["timezone"])
    hh, mm = (int(x) for x in str(cfg["time"]).split(":"))
    used = Counter(taken)
    local_now = now.astimezone(tz)
    day = local_now.date()
    while True:
        slot = dt.datetime.combine(day, dt.time(hh, mm), tzinfo=tz)
        if slot >= local_now + dt.timedelta(hours=cfg["lead_hours"]) and used[day] < cfg["per_day"]:
            return slot
        day += dt.timedelta(days=1)


def local_date(value, cfg: dict | None = None) -> dt.date | None:
    """A Short's release date in the channel's time zone, from an ISO time or a plain date."""
    if not value:
        return None
    s = str(value)
    if len(s) == 10:
        return dt.date.fromisoformat(s)
    when = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return when.astimezone(ZoneInfo({**DEFAULTS, **(cfg or {})}["timezone"])).date()
