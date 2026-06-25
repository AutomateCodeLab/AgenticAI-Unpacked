"""
viz_kit.py — reusable Manim builders for "Agentic AI, Unpacked"

STEP-0 polished defaults applied here (2026-06):
  • Entrances: FadeIn + directional shift, rate_func=smooth, cascade via LaggedStart.
  • Glow: soft semi-transparent copy placed behind the mobject.
  • Rounded corners, 2-3 px strokes, consistent inner padding on all nodes.
  • bg_deco() adds a faint dot grid + subtle corner vignette for full-frame scenes.
    (Transparent overlay scenes skip bg_deco — call nothing, leave BG transparent.)
  • Hold timing: callers should self.wait(1.8) on the key frame.
"""

import numpy as np
from manim import *
from brand import BG, ACCENT, ACCENT2, WARN, TEXT, MUTE


# ── Primitive builders ──────────────────────────────────────────────────────────

def node(label, color=ACCENT, w=2.6, h=1.05, fs=0.5):
    """Rounded chip with centred bold label."""
    box = RoundedRectangle(
        corner_radius=0.22, width=w, height=h,
        stroke_color=color, stroke_width=2.5,
        fill_color=BG, fill_opacity=1,
    )
    txt = Text(label, weight=BOLD, color=TEXT).scale(fs)
    # font="Inter"  ← uncomment once Inter is installed system-wide
    txt.move_to(box.get_center())
    return VGroup(box, txt)


def caption(text, color=MUTE, fs=0.42):
    """Muted caption text."""
    return Text(text, color=color).scale(fs)
    # font="Inter"


# ── Glow / emphasis ─────────────────────────────────────────────────────────────

def glow(mob, color=ACCENT, opacity=0.18, expansion=0.16):
    """
    Soft glow: a slightly-larger, semi-transparent copy placed behind mob.
    Add to scene before mob so z-order is correct, or set z_index manually.
    """
    ghost = mob.copy()
    ghost.scale(1 + expansion)
    ghost.set_stroke(width=0)
    ghost.set_fill(color=color, opacity=opacity)
    ghost.move_to(mob.get_center())
    ghost.z_index = mob.z_index - 1
    return ghost


def highlight_box(mob, color=WARN, fill_opacity=0.15, buff=0.1):
    """Highlighted background rectangle around a mobject (for emphasis beats)."""
    return SurroundingRectangle(
        mob, color=color,
        fill_color=color, fill_opacity=fill_opacity,
        stroke_width=1.5, buff=buff,
        corner_radius=0.08,
    )


# ── Background decorations (full-frame scenes only) ─────────────────────────────

def dot_grid(spacing=0.8, dot_radius=0.022, opacity=0.11):
    """Faint background dot grid."""
    fw, fh = 14.22, 8.0
    cols = int(fw / spacing) + 2
    rows = int(fh / spacing) + 2
    return VGroup(*[
        Dot(
            point=np.array([-fw / 2 + i * spacing, -fh / 2 + j * spacing, 0]),
            radius=dot_radius, color=MUTE,
        ).set_opacity(opacity)
        for i in range(cols) for j in range(rows)
    ])


def vignette(opacity=0.38, thickness=1.8):
    """Subtle corner darkening via 4 edge rectangles."""
    fw, fh = 14.22, 8.0
    return VGroup(
        Rectangle(width=fw, height=thickness, fill_color=BG,
                  fill_opacity=opacity, stroke_width=0).move_to(UP  * (fh / 2 - thickness / 2)),
        Rectangle(width=fw, height=thickness, fill_color=BG,
                  fill_opacity=opacity, stroke_width=0).move_to(DOWN * (fh / 2 - thickness / 2)),
        Rectangle(width=thickness, height=fh, fill_color=BG,
                  fill_opacity=opacity, stroke_width=0).move_to(LEFT  * (fw / 2 - thickness / 2)),
        Rectangle(width=thickness, height=fh, fill_color=BG,
                  fill_opacity=opacity, stroke_width=0).move_to(RIGHT * (fw / 2 - thickness / 2)),
    )


def bg_deco():
    """Combined dot grid + vignette — call self.add(bg_deco()) at scene start."""
    return VGroup(dot_grid(), vignette())


# ── Entrance helpers ─────────────────────────────────────────────────────────────

def cascade_in(scene, mobjects, shift=UP * 0.16, lag=0.13, rt=0.6):
    """Staggered FadeIn cascade across a list of mobjects."""
    scene.play(
        LaggedStart(
            *[FadeIn(m, shift=shift, rate_func=smooth) for m in mobjects],
            lag_ratio=lag, run_time=rt,
        )
    )


# ── Composite builders ───────────────────────────────────────────────────────────

def title_card(headline, sub=None, sub_color=WARN):
    """
    Returns (content_group, underline).
    Typical usage:
        content, ul = title_card("HEADLINE", sub="sub text")
        self.play(FadeIn(content, scale=0.88))
        self.play(Create(ul))
    """
    h = Text(headline, weight=BOLD, color=TEXT).scale(1.1)
    # font="Inter"
    parts = [h]
    if sub:
        s = Text(sub, weight=BOLD, color=sub_color).scale(0.55)
        # font="Inter"
        s.next_to(h, DOWN, buff=0.28)
        parts.append(s)
    content = VGroup(*parts)
    ul = Line(
        h.get_left()  + DOWN * 0.05,
        h.get_right() + DOWN * 0.05,
        color=ACCENT, stroke_width=4,
    )
    ul.next_to(content, DOWN, buff=0.12)
    return content, ul


def flow(steps, colors=None, w=2.4, h=0.9, fs=0.44, buff=0.9):
    """Left-to-right node flow. Returns (nodes_vgroup, arrows_list)."""
    if colors is None:
        colors = [ACCENT] * len(steps)
    nodes = [node(s, c, w=w, h=h, fs=fs) for s, c in zip(steps, colors)]
    grp   = VGroup(*nodes).arrange(RIGHT, buff=buff)
    arrows = [
        Arrow(
            nodes[i].get_right(), nodes[i + 1].get_left(),
            buff=0.1, color=TEXT, stroke_width=2,
            max_tip_length_to_length_ratio=0.18,
        )
        for i in range(len(nodes) - 1)
    ]
    return grp, arrows


def compare_cols(left_title, left_items, right_title, right_items,
                 left_color=ACCENT2, right_color=ACCENT,
                 title_fs=0.55, item_fs=0.42):
    """Two-column A-vs-B layout. Returns (left_col, divider, right_col)."""
    def col(title, items, color):
        t    = Text(title, weight=BOLD, color=color).scale(title_fs)
        rows = VGroup(*[Text(it, color=TEXT).scale(item_fs) for it in items])
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rows.next_to(t, DOWN, buff=0.4)
        return VGroup(t, rows)

    left  = col(left_title,  left_items,  left_color)
    right = col(right_title, right_items, right_color)
    div   = Line(UP * 3.2, DOWN * 3.2, color=MUTE, stroke_width=1.5)
    left.next_to(div,  LEFT,  buff=0.7)
    right.next_to(div, RIGHT, buff=0.7)
    return left, div, right


def bullets(items, color=TEXT, bullet_color=ACCENT, fs=0.48, spacing=0.52):
    """Bullet list mobject — reveal children one at a time via FadeIn."""
    lines = VGroup()
    for text in items:
        b   = Text("▸", color=bullet_color).scale(fs * 0.9)
        lbl = Text(text,  color=color).scale(fs)
        lines.add(VGroup(b, lbl).arrange(RIGHT, buff=0.22))
    lines.arrange(DOWN, buff=spacing, aligned_edge=LEFT)
    return lines


def stat_display(number, label, num_color=WARN, lbl_color=MUTE):
    """Big number + small label."""
    n = Text(str(number), weight=BOLD, color=num_color).scale(2.5)
    l = Text(label, color=lbl_color).scale(0.6)
    return VGroup(n, l).arrange(DOWN, buff=0.25)
