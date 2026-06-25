# brand.py — shared colour palette for "Agentic AI, Unpacked"
# Import everywhere; never hard-code colours in a scene.
from manim import config

BG      = "#0B0E14"   # background / near-black
ACCENT  = "#4F9DFF"   # blue  — core / model / primary
ACCENT2 = "#36D6B0"   # teal  — inputs / outputs / success
WARN    = "#FFC857"   # amber — goal / emphasis / the "spicy" bits
TEXT    = "#E6EAF2"   # off-white text
MUTE    = "#8A93A6"   # captions / secondary

config.background_color = BG
# Font: Pango default.  To use Inter: install it system-wide then add font="Inter"
# to every Text(...) call below.
