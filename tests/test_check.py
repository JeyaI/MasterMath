"""`ms check`: a dry run of a small scene with one fault of each kind."""
import pytest

from mathshorts import check, cli
from mathshorts.shorts import find

SCENE = '''
from manim import Scene
from lib.components import CENTRE_X, Captions, beat, countdown, hook, label


class Short(Scene):
    def construct(self):
        beat(self, "hook")
        self.add(hook("How many squares?"))
        cap = Captions(self)
        cap.show("Count every square")
        cap.show("Pause and try it")
        countdown(self, 5, center=[CENTRE_X, 1, 0])
        a, b = label("7 overlapping"), label("9 overlapping")
        off = label("off the edge", size=30).move_to([4.2, 0, 0])
        self.add(a.move_to([CENTRE_X, 0, 0]), b.move_to([CENTRE_X, 0, 0]), off)
        self.wait(0.5)
        self.remove(a, b, off)
        cap.show("30 squares ✓")
        beat(self, "Level 2")
        self.add(label("Now with 12 dots").move_to([CENTRE_X, 4, 0]))
        self.wait(1)
        cap.show("Comment just the number ↓")
        self.wait(3)
'''

YAML = '''id: '0001'
title: T
status: drafting
catalog_id:
tags: []
level1: {answer: "40 squares"}
level2: {statement: "Now with 8 dots", answer: 3}
captions: ["Count every square", "Pause and try it", "30 squares ✓", "Comment just the number ↓", "Never shown"]
music: {piece: k545}
youtube: {description: "Music: W. A. Mozart, Piano Sonata in C, K. 545."}
'''


@pytest.fixture
def short(root):
    d = root / "shorts" / "0001-t"
    d.mkdir()
    (d / "short.yaml").write_text(YAML)
    (d / "verify.py").write_text("print('ok')\n")
    (d / "scene.py").write_text(SCENE)
    return find("0001")


def test_check_finds_one_fault_of_each_kind(short, capsys):
    found = {(f.level, f.rule, f.message.split(",")[0]) for f in check.run(short)}
    messages = " | ".join(m for _, _, m in found)
    rules = {(lvl, rule) for lvl, rule, _ in found}
    assert ("warning", "duration") in rules                       # about 12 s: a target, not a cap
    assert ("error", "safe-zone") in rules and "'off the edge'" in messages
    assert ("error", "overlap") in rules and "'7 overlapping' overlaps '9 overlapping'" in messages
    assert "is held 3.5 s" in messages                             # 0.45 s fade + 3 s, under 10 s
    assert "'30 squares ✓' shows 30" in messages                   # payoff vs level1's 40
    assert "'Never shown' never appears" in messages
    assert "'Now with 12 dots' shows 12" in messages               # Level 2 number not in yaml
    assert not any(r == "music" for _, r in rules)
    assert not any("'7 overlapping' shows" in m for m in messages.split(" | "))   # not a checked beat
    with pytest.raises(SystemExit):
        cli.main(["check", "1"])
    assert "error(s)" in capsys.readouterr().out


def test_word_count_treats_equations_as_equations():
    assert check.words("36 miles ✓") == 2
    assert check.words("Another…") == 1
    assert check.words("1 + 1 + 2 = 4") is None
    assert check.words(r"\frac{x}{x-5} = \frac{x-5}{x-9}") is None


def test_superscripts_match_latex():
    assert check.norm("2⁸ = 256") == check.norm("2^8 = 256")
