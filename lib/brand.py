"""Brand constants with no side effects: safe to import from any scene, any frame shape.

lib/layout.py (the 9:16 Short frame) and brand/logo.py (avatar, banner) both use these.
"""
from manim import ManimColor

BRAND = "Master Math USA"
TAGLINE = "Puzzles, solved in motion"
FONT = "Inter"

BG = ManimColor("#0E1424")
INK = ManimColor("#F2F4F8")        # main text
MUTED = ManimColor("#7F8AA3")      # secondary text, outlines
GRID = ManimColor("#2A3550")       # cell fill before the solve
ACCENT = ManimColor("#FFC24B")     # highlights, cuts, the Level 2 badge, "USA"
GOOD = ManimColor("#5BD69A")       # the checkmark moment
PIECES = [ManimColor(c) for c in ("#FF8A5B", "#4FC3F7", "#9CCC65", "#F06292")]
