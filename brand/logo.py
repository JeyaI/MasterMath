"""Master Math USA logo: the 4-piece square from Short 0001 (cross -> square dissection).

The square keeps its natural tilt, atan(1/2) ~ 26.6 deg, the Level 2 answer of the first Short.
Geometry comes straight from bank/0001-greek-cross/verify.py.

Renders (python brand/logo.py does all three):
    Avatar   800x800    channel profile picture (YouTube crops it to a circle)
    Banner   2560x1440  channel banner; text stays inside the 1546x423 safe area
    Mark     1024x1024  transparent PNG of the mark alone, for thumbnails / end cards
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path[:0] = [str(REPO), str(REPO / "bank" / "0001-greek-cross")]

from manim import (  # noqa: E402
    DOWN, LEFT, RIGHT, UP, Circle, Polygon, Scene, Text, VGroup, config, BOLD, MEDIUM,
)
import numpy as np  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from lib.brand import ACCENT, BG, FONT, INK, MUTED, PIECES, TAGLINE  # noqa: E402
from verify import pieces_and_targets  # noqa: E402

import os  # noqa: E402

# Frame shape must match the pixel aspect or the image stretches; main() passes it per render.
_fw, _fh = (float(v) for v in os.environ.get("MS_LOGO_FRAME", "8x8").split("x"))
config.frame_width, config.frame_height = _fw, _fh

SQUARE_CENTRE = (0.5, 1.5)


def mark(size: float = 3.0, gap: float = 0.06) -> VGroup:
    """The 4 pieces assembled into the tilted square, with thin gaps between them.

    `size` is the width of the mark's bounding box in frame units.
    """
    placed = [affinity.translate(p, dx - SQUARE_CENTRE[0], dy - SQUARE_CENTRE[1])
              for p, (dx, dy) in pieces_and_targets()]
    square = unary_union(placed)
    # Seams = piece edges that are NOT on the outer square. Cut a real gap along them only,
    # so the outline stays a crisp square and the gaps are transparent in Mark.
    seams = unary_union([q.boundary for q in placed]).difference(square.exterior.buffer(1e-6))
    band = seams.buffer(gap / 2, cap_style="square", join_style="mitre")
    pieces = []
    for q, col in zip(placed, PIECES):
        q = q.difference(band)
        if q.geom_type != "Polygon":                     # drop slivers left at seam ends
            q = max(q.geoms, key=lambda g: g.area)
        pts = [np.array([x, y, 0.0]) for x, y in list(q.exterior.coords)[:-1]]
        pieces.append(Polygon(*pts, fill_color=col, fill_opacity=1, stroke_width=0))
    g = VGroup(*pieces)
    g.scale_to_fit_width(size)
    return g.move_to([0, 0, 0])


def wordmark(height: float) -> VGroup:
    master = Text("Master Math", font=FONT, weight=BOLD, color=INK)
    usa = Text("USA", font=FONT, weight=BOLD, color=ACCENT)
    word = VGroup(master, usa).arrange(RIGHT, buff=0.32, aligned_edge=DOWN)
    word.scale_to_fit_height(height)
    return word


class Avatar(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(mark(size=4.9))


class Mark(Scene):
    def construct(self):
        self.add(mark(size=6.6))


class Banner(Scene):
    def construct(self):
        self.camera.background_color = BG
        # 16x9 frame; YouTube's always-visible safe area is the middle 1546x423 px of 2560x1440
        # = 9.66 x 2.64 frame units. Everything that matters stays inside it.
        m = mark(size=2.2)
        word = wordmark(height=0.62)
        tag = Text(TAGLINE, font=FONT, weight=MEDIUM, color=MUTED)
        tag.scale_to_fit_height(0.3)
        text = VGroup(word, tag).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        lockup = VGroup(m, text).arrange(RIGHT, buff=0.55).move_to([0, 0, 0])
        if lockup.width > 9.3:
            lockup.scale_to_fit_width(9.3)
        self.add(lockup)


RENDERS = {  # scene: (width, height, frame_w, frame_h, transparent)
    "Avatar": (800, 800, 8, 8, False),
    "Mark": (1024, 1024, 8, 8, True),
    "Banner": (2560, 1440, 16, 9, False),
}


def main(out_dir: Path = REPO / "brand" / "out") -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for scene, (w, h, fw, fh, transparent) in RENDERS.items():
        cmd = ["manim", "render", "--resolution", f"{w},{h}", "-s", "--format", "png",
               "--disable_caching", "--progress_bar", "none", "--media_dir", str(out_dir / "media"),
               "-o", scene.lower(), *(["-t"] if transparent else []), str(Path(__file__)), scene]
        subprocess.run(cmd, check=True, env={**os.environ, "MS_LOGO_FRAME": f"{fw}x{fh}"})
        src = sorted((out_dir / "media").rglob(f"{scene.lower()}*.png"), key=lambda p: p.stat().st_mtime)[-1]
        dst = out_dir / f"{scene.lower()}.png"
        src.replace(dst)
        print(f"{scene:<7} -> {dst}")


if __name__ == "__main__":
    main()
