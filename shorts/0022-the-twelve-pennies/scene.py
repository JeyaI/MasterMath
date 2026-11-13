"""Draft scene. Build from lib/components.py; import checked numbers/shapes from verify.py."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1]), str(HERE)]

from manim import DOWN, FadeIn, Scene  # noqa: E402

from lib.layout import ACCENT  # noqa: E402
from lib.components import Captions, beat, footer, hook  # noqa: E402


class Short(Scene):
    def construct(self):
        cap = Captions(self)
        beat(self, "hook")
        title = hook("The Twelve Pennies")
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(footer("TODO source credit")), run_time=0.5)
        cap.show("TODO: draft this Short", ACCENT)
        self.wait(2)
