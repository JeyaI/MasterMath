"""9:16 frame, palette, type and safe zones shared by every Short.

Import this BEFORE building any mobjects:  from lib.layout import *

Coordinates: frame is 9 wide x 16 tall, origin at centre (x in [-4.5, 4.5], y in [-8, 8]).
YouTube's Shorts UI covers the bottom ~20% (title, channel, music ticker) and a
column on the right (like/comment/share buttons), so keep anything that matters
inside SAFE (x in [-3.8, 3.2], y in [-4.6, 7.0]).
"""
from __future__ import annotations

from manim import config, ManimColor

# --- frame -------------------------------------------------------------------
config.frame_height = 16.0
config.frame_width = 9.0
# Only force vertical pixels if nobody (e.g. `ms preview` via --resolution) set them.
if config.pixel_width >= config.pixel_height:
    config.pixel_width, config.pixel_height = 1080, 1920

# --- palette (dark, high contrast for phones) ---------------------------------
BG = ManimColor("#0E1424")
INK = ManimColor("#F2F4F8")        # main text
MUTED = ManimColor("#7F8AA3")      # secondary text, outlines
GRID = ManimColor("#2A3550")       # cell fill before the solve
ACCENT = ManimColor("#FFC24B")     # highlights, cuts, the Level 2 badge
GOOD = ManimColor("#5BD69A")       # the checkmark moment
PIECES = [ManimColor(c) for c in ("#FF8A5B", "#4FC3F7", "#9CCC65", "#F06292")]

config.background_color = BG

# --- type ----------------------------------------------------------------------
# font_size values are ~2x Manim's defaults because the frame is 16 units tall, not 8.
FONT = "Inter"
SIZE_TITLE = 84
SIZE_CAPTION = 64
SIZE_SMALL = 34
SIZE_BADGE = 52

# --- zones ---------------------------------------------------------------------
TITLE_Y = 5.6
STAGE_Y = 1.0        # centre of the puzzle drawing
CAPTION_Y = -3.3
FOOTER_Y = -4.35
SAFE_LEFT, SAFE_RIGHT = -3.8, 3.2
SAFE_W = SAFE_RIGHT - SAFE_LEFT
