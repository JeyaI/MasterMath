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
    # --rescore leaves it alone too
    catalog.add_source("dudeney-amusements", file=f, rescore=True)
    assert catalog.annotations()[key]["visual_potential"] == 2


def test_rescore_updates_heuristic_entries_only_and_keeps_notes(root):
    from mathshorts import yamlio
    f = FIXTURES / "dudeney_sample.txt"
    catalog.add_source("dudeney-amusements", file=f)
    ann = catalog.annotations()
    key = "dudeney-amusements-003"
    want = ann[key]["visual_potential"]
    ann[key]["visual_potential"] = 1 if want != 1 else 2    # a score from an older heuristic
    ann[key]["notes"] = "keep me"
    ann[key]["skip"] = True
    yamlio.save(catalog.annotations_path(), ann)
    info = catalog.add_source("dudeney-amusements", file=f, rescore=True)
    assert info["annotations_rescored"] == 1
    entry = catalog.annotations()[key]
    assert entry["visual_potential"] == want
    assert entry["notes"] == "keep me" and entry["skip"] is True


def test_heuristic_bonuses_do_not_stack():
    wordy = "cut the square into pieces along the line of the figure"
    rec = {"section": "Various Geometrical Puzzles", "solution": "x"}
    score = lambda **kw: catalog.heuristic({**rec, **kw})["visual_potential"]
    assert score(text="", has_figure=False) == 4
    assert score(text="", has_figure=True) == 4             # a figure alone earns nothing
    assert score(text=wordy, has_figure=False) == 4         # nor do keywords alone
    assert score(text=wordy, has_figure=True) == 5
    dissection = {**rec, "section": "Various Dissection Puzzles"}
    assert catalog.heuristic({**dissection, "text": "", "has_figure": True})["visual_potential"] == 4


def test_difficulty_heuristic():
    easy = {"section": "Age And Kinship Puzzles", "text": "How old is Rover?", "solution": "Ten."}
    assert catalog.difficulty(easy) == 1
    assert catalog.heuristic(easy)["difficulty"] == 1
    long_text = "word " * 200
    hard = {"section": "Magic Square Problems", "text": long_text + " In how many ways can it be done?",
            "solution": "It is impossible. " + "x" * 1600}
    assert catalog.difficulty(hard) == 5                    # capped
    assert catalog.difficulty({**easy, "text": "1 2 3 4 5 6 7 8"}) == 2


def test_difficulty_backfills_old_heuristic_entries_but_not_human_ones(root):
    from mathshorts import yamlio
    f = FIXTURES / "dudeney_sample.txt"
    catalog.add_source("dudeney-amusements", file=f)
    ann = catalog.annotations()
    for k in ann:                                           # entries from before #53 have no difficulty
        del ann[k]["difficulty"]
    ann["dudeney-amusements-001"]["scored_by"] = "human"
    yamlio.save(catalog.annotations_path(), ann)
    catalog.add_source("dudeney-amusements", file=f)
    ann = catalog.annotations()
    assert ann["dudeney-amusements-002"]["difficulty"] in range(1, 6)
    assert "difficulty" not in ann["dudeney-amusements-001"]
    # a human's difficulty survives --rescore
    ann["dudeney-amusements-001"]["difficulty"] = 5
    yamlio.save(catalog.annotations_path(), ann)
    catalog.add_source("dudeney-amusements", file=f, rescore=True)
    assert catalog.annotations()["dudeney-amusements-001"]["difficulty"] == 5
