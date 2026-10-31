from conftest import FIXTURES

from mathshorts import catalog
from mathshorts.sources.dudeney import parse


def test_dudeney_puzzles_and_solutions():
    recs = parse((FIXTURES / "dudeney_sample.txt").read_text(), "s")
    assert [r["number"] for r in recs] == [1, 2, 3, 4]
    assert [r["section"] for r in recs] == ["Money Puzzles", "Money Puzzles", "Greek Cross Puzzles", "Greek Cross Puzzles"]
    assert recs[0]["title"] == "A Post-Office Perplexity"
    # solution text on the heading line is kept; a repeated title is dropped
    assert recs[0]["solution"].startswith("It can be done")
    assert recs[1]["solution"].startswith("He saved")
    # a prose line starting "3." stays inside solution 2 instead of hijacking solution 3
    assert "prose line" in recs[1]["solution"]
    assert recs[2]["solution"].startswith("Make two straight cuts")
    # a caps line inside puzzle text is not a section heading
    assert "continues on the next line" in recs[2]["text"]
    assert [r["has_figure"] for r in recs] == [False, False, True, True]


def test_plain_numbered_solutions():
    recs = parse((FIXTURES / "plain_numbered.txt").read_text(), "p")
    assert [r["solution"] for r in recs] == ["Answer one.", "Answer two,\nover two lines."]


def test_real_gutenberg_excerpt():
    """Verbatim from #16713, picked for the places the real text trips a parser."""
    text = (FIXTURES / "dudeney_excerpt.txt").read_text(encoding="utf-8")
    recs = {r["number"]: r for r in parse(text, "s")}
    # headings with no period, and the misprinted "384.--" that must become 284
    assert sorted(recs) == [33, 44, 47, 85, 96, 180, 283, 284, 285]
    assert recs[44]["title"] == "A Census Puzzle"
    assert recs[284]["title"] == "The Cross Target"
    assert recs[285]["section"] == "Combination And Group Problems"
    assert all(r["solution"] for r in recs.values())
    # prose like "96--namely" stays inside solution 85 instead of starting solution 96
    assert "96--namely" in recs[85]["solution"]
    assert recs[96]["solution"].startswith("The sum of all the numbers")
    # a reworded title in the solutions is dropped; the index is not part of the last solution
    assert "REVERSALS" not in recs[33]["solution"]
    assert "Abbot" not in recs[285]["solution"]
    # possessives survive title-casing; box art counts as a figure
    assert recs[47]["title"] == "Rover's Age"
    assert recs[284]["has_figure"] and recs[285]["has_figure"]


def test_add_source_never_overwrites_human_annotations(root):
    f = FIXTURES / "dudeney_sample.txt"
    catalog.add_source("dudeney-amusements", file=f)
    ann = catalog.annotations()
    key = "dudeney-amusements-003"
    assert ann[key]["scored_by"] == "heuristic"
    assert ann[key]["tags"] == ["dissection"]
    # a human edits it...
    ann[key]["visual_potential"] = 2
    ann[key]["scored_by"] = "human"
    from mathshorts import yamlio
    yamlio.save(catalog.annotations_path(), ann)
    # ...and re-scraping leaves it alone
    info = catalog.add_source("dudeney-amusements", file=f)
    assert info["annotations_added"] == 0
    assert catalog.annotations()[key]["visual_potential"] == 2
    assert catalog.get(key)["title"] == "The Cross And The Square"
