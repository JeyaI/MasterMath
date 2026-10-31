"""Draft selector: rank catalog puzzles for the next Short.

`rank` is a pure function (no file access), so it's easy to test and to change.
It returns a shortlist with human-readable reasons; the human makes the final pick.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidate:
    record: dict
    score: float
    reasons: list[str] = field(default_factory=list)


def rank(records: list[dict], annotations: dict, used_ids: set[str],
         recent: list[dict], config: dict, n: int = 5) -> list[Candidate]:
    """
    records      catalog records
    annotations  id -> {visual_potential, tags, skip, ...}
    used_ids     catalog ids already turned into Shorts (any status)
    recent       newest-first list of {"tags": [...], "source": ...} for the latest Shorts
    config       config/selector.yaml contents
    """
    w = config.get("weights", {})
    tag_w = config.get("tag_weights", {}) or {}
    window = recent[: config.get("recent_window", 3)]
    recent_tags = {t for r in window for t in (r.get("tags") or [])}
    last_source = recent[0].get("source") if recent else None

    out = []
    for rec in records:
        rid = rec["id"]
        ann = annotations.get(rid) or {}
        if rid in used_ids or ann.get("skip"):
            continue
        visual = int(ann.get("visual_potential", 0) or 0)
        if visual < config.get("min_visual", 4):
            continue
        tags = list(ann.get("tags") or [])
        score = visual * w.get("visual", 1.0)
        reasons = [f"visual {visual}/5" + (" (human)" if ann.get("scored_by") == "human" else "")]
        for t in tags:
            if tag_w.get(t):
                score += tag_w[t]
                reasons.append(f"{t} {tag_w[t]:+g}")
        repeats = [t for t in tags if t in recent_tags]
        if repeats:
            score += w.get("repeat_tag", -1.5) * len(repeats)
            reasons.append(f"recently did {', '.join(repeats)}")
        if last_source and rec.get("source") == last_source:
            score += w.get("repeat_source", -0.3)
            reasons.append("same source as last Short")
        if rec.get("solution"):
            score += w.get("has_solution", 0.5)
            reasons.append("has solution")
        else:
            reasons.append("no solution in book")
        if rec.get("has_figure"):
            score += w.get("has_figure", 0.3)
            reasons.append("has figure")
        out.append(Candidate(rec, round(score, 2), reasons))
    out.sort(key=lambda c: (-c.score, c.record["id"]))
    return out[:n]
