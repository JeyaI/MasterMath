from mathshorts.selector import rank

CFG = {"min_visual": 4, "recent_window": 2,
       "weights": {"visual": 1.0, "repeat_tag": -1.5, "repeat_source": -0.3, "has_solution": 0.5, "has_figure": 0.3},
       "tag_weights": {"dissection": 0.5, "money": -1.0}}


def rec(i, src="a", solution=True, figure=False):
    return {"id": f"{src}-{i}", "source": src, "number": i, "title": f"P{i}", "text": "",
            "solution": "x" if solution else None, "has_figure": figure}


def test_filters_used_skipped_and_low_visual():
    recs = [rec(1), rec(2), rec(3), rec(4)]
    ann = {"a-1": {"visual_potential": 5}, "a-2": {"visual_potential": 3},
           "a-3": {"visual_potential": 5, "skip": True}, "a-4": {"visual_potential": 5}}
    got = [c.record["id"] for c in rank(recs, ann, {"a-4"}, [], CFG)]
    assert got == ["a-1"]


def test_variety_and_tag_weights_reorder():
    recs = [rec(1), rec(2)]
    ann = {"a-1": {"visual_potential": 5, "tags": ["dissection"]},
           "a-2": {"visual_potential": 5, "tags": ["routes"]}}
    # with no history, the dissection bonus wins
    assert rank(recs, ann, set(), [], CFG)[0].record["id"] == "a-1"
    # after a recent dissection Short, the variety penalty flips the order
    recent = [{"tags": ["dissection"], "source": "a"}]
    top = rank(recs, ann, set(), recent, CFG)[0]
    assert top.record["id"] == "a-2"
    assert any("same source" in r for r in top.reasons)
