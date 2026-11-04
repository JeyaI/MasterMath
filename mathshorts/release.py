"""When an approved Short goes public (#29, #44). Pure, so it's easy to test.

`mode: asap` (#44): the first full hour at least `asap_minutes` after the approval (a check mark at
7:23 PM goes public at 9:00 PM), if that day still has room; otherwise the next `slot` below.
`mode: slot`: the next open daily slot.

Slot rules (docs/pipeline-design.md, Publish scheduling): at most `per_day` releases a day (rule 1
caps it at 2), at least `lead_hours` between approval and release, to leave time for the stop
sign, and no earlier than `days_ahead` days after the approval (1 = tomorrow at the soonest).
Settings: `release:` in config/pipeline.yaml.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from zoneinfo import ZoneInfo

from . import paths, yamlio

DEFAULTS = {"mode": "slot", "asap_minutes": 60, "time": "17:00", "timezone": "America/New_York", "per_day": 1, "lead_hours": 2, "days_ahead": 0}


def settings() -> dict:
    p = paths.config() / "pipeline.yaml"
    cfg = (yamlio.load(p) or {}) if p.exists() else {}
    out = {**DEFAULTS, **(cfg.get("release") or {})}
    out["per_day"] = max(1, min(int(out["per_day"]), 2))         # rule 1
    return out


def next_slot(now: dt.datetime, taken: list[dt.date], cfg: dict | None = None) -> dt.datetime:
    """When a Short approved at `now` goes public (see the module docstring).

    `taken` lists the local release dates of Shorts already scheduled or published.
    """
    cfg = {**DEFAULTS, **(cfg or {})}
    tz = ZoneInfo(cfg["timezone"])
    hh, mm = (int(x) for x in str(cfg["time"]).split(":"))
    used = Counter(taken)
    local_now = now.astimezone(tz)
    day = local_now.date() + dt.timedelta(days=int(cfg["days_ahead"]))
    if cfg["mode"] == "asap":
        soon = asap_time(now, cfg)
        if used[soon.date()] < cfg["per_day"]:
            return soon
        day = soon.date() + dt.timedelta(days=1)                  # day full: the next day's slot
    while True:
        slot = dt.datetime.combine(day, dt.time(hh, mm), tzinfo=tz)
        if slot >= local_now + dt.timedelta(hours=cfg["lead_hours"]) and used[day] < cfg["per_day"]:
            return slot
        day += dt.timedelta(days=1)


def asap_time(now: dt.datetime, cfg: dict) -> dt.datetime:
    """The first full hour at least asap_minutes after `now`, local time (computed in UTC, so DST is safe)."""
    earliest = now.astimezone(dt.timezone.utc) + dt.timedelta(minutes=int(cfg["asap_minutes"]))
    hour = earliest.replace(minute=0, second=0, microsecond=0)
    if hour < earliest:
        hour += dt.timedelta(hours=1)
    return hour.astimezone(ZoneInfo(cfg["timezone"]))


def describe(cfg: dict) -> str:
    """How the approval message words the release time."""
    if cfg.get("mode") == "asap":
        return f"on the hour, at least {cfg['asap_minutes']} minutes from now ({cfg['time']} next day if today is full)"
    return f"at the next open {cfg['time']} slot"


def local_date(value, cfg: dict | None = None) -> dt.date | None:
    """A Short's release date in the channel's time zone, from an ISO time or a plain date."""
    if not value:
        return None
    s = str(value)
    if len(s) == 10:
        return dt.date.fromisoformat(s)
    when = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return when.astimezone(ZoneInfo({**DEFAULTS, **(cfg or {})}["timezone"])).date()
