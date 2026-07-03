"""
ep05_scenes.py — Manim animations for "Agentic AI, Unpacked · EP 05"
Memory: short-term, long-term, semantic (mini-RAG)

Scenes:
  Ep05TitleSting      ~2.5s   transparent overlay  @ 1:15
  GoldfishProblem     ~7s     full-frame cutaway   @ 1:15
  ThreeMemories       ~9s     full-frame cutaway   @ 3:00
  ContextWindowFills  ~7s     transparent overlay  @ 7:30
  EmbeddingRetrieval  ~11s    full-frame cutaway   @ 12:30 (signature visual)
  CrossSessionRecall  ~9s     transparent overlay  @ 18:30 (the payoff)
  RememberVsForget    ~9s     full-frame cutaway   @ 23:00

Render:
  manim -qh --media_dir ../renders Episode5/ep05_scenes.py <Scene>
  manim -qh -t --media_dir ../renders Episode5/ep05_scenes.py <Scene>
Or: ./render_all.sh ep05
"""

import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from manim import *
import numpy as np
from brand import BG, ACCENT, ACCENT2, WARN, TEXT, MUTE
from viz_kit import (
    node, caption, glow, highlight_box, bg_deco,
    cascade_in, title_card,
)


# ── Local helpers ──────────────────────────────────────────────────────────────

def small_node(label, color=ACCENT, w=2.4, h=0.78, fs=0.40):
    box = RoundedRectangle(
        corner_radius=0.18, width=w, height=h,
        stroke_color=color, stroke_width=2.5,
        fill_color=BG, fill_opacity=1,
    )
    txt = Text(label, weight=BOLD, color=TEXT).scale(fs)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


def chip(label, color=MUTE, w=1.4, h=0.5, fs=0.30):
    box = RoundedRectangle(
        corner_radius=0.10, width=w, height=h,
        stroke_color=color, stroke_width=2,
        fill_color=BG, fill_opacity=1,
    )
    txt = Text(label, color=color).scale(fs)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


def trace_line(marker, label, content="", m_color=WARN, l_color=None, c_color=MUTE, fs=0.38):
    l_color = l_color or m_color
    parts = [Text(marker, color=m_color).scale(fs)]
    if label:
        parts.append(Text(label, weight=BOLD, color=l_color).scale(fs))
    if content:
        parts.append(Text(content, color=c_color).scale(fs))
    return VGroup(*parts).arrange(RIGHT, buff=0.18)


def dot_with_label(point, label, color=ACCENT2, fs=0.32, direction=UP):
    d = Dot(point=point, radius=0.09, color=color)
    lbl = Text(label, color=TEXT).scale(fs)
    lbl.next_to(d, direction, buff=0.14)
    return VGroup(d, lbl)


# ── 1. Ep05TitleSting ──────────────────────────────────────────────────────────

class Ep05TitleSting(Scene):
    """EP 05 title card — transparent overlay.  ~2.5 s."""
    def construct(self):
        content, ul = title_card(
            "AGENTIC AI, UNPACKED",
            sub="EP 05 — MEMORY",
        )
        self.play(FadeIn(content, scale=0.88, rate_func=smooth), run_time=0.5)
        self.play(Create(ul), run_time=0.44)
        self.wait(1.5)


# ── 2. GoldfishProblem ────────────────────────────────────────────────────────

class GoldfishProblem(Scene):
    """
    The model is stateless — the app fakes memory by re-sending history.
    Full-frame cutaway.  ~7 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("The Model Remembers Nothing", weight=BOLD, color=TEXT).scale(0.6)
        title.to_edge(UP, buff=0.42)
        self.play(FadeIn(title, shift=DOWN * 0.15, rate_func=smooth), run_time=0.38)

        div = Line(UP * 3.4, DOWN * 3.4, color=MUTE, stroke_width=1.5)
        self.play(Create(div), run_time=0.25)

        # ── LEFT: THE MODEL ─────────────────────────────────────────────────
        left_hdr = Text("THE MODEL", weight=BOLD, color=ACCENT2).scale(0.52)
        left_hdr.move_to(LEFT * 3.5 + UP * 2.35)

        in_chip = chip("\"my name is X\"", ACCENT2, w=2.6, h=0.55, fs=0.28)
        model_n = small_node("MODEL", ACCENT2, w=2.0, h=0.85, fs=0.4)
        out_chip = chip("\"Hi X!\"", ACCENT2, w=1.8, h=0.55, fs=0.3)

        col = VGroup(in_chip, model_n, out_chip).arrange(DOWN, buff=0.35)
        col.next_to(left_hdr, DOWN, buff=0.35)

        self.play(FadeIn(left_hdr, shift=DOWN * 0.1), run_time=0.3)
        self.play(FadeIn(in_chip, shift=DOWN * 0.1), run_time=0.3)
        self.play(FadeIn(model_n, scale=0.9), run_time=0.32)
        self.play(FadeIn(out_chip, shift=DOWN * 0.1), run_time=0.3)

        forget = Text("🗑 forgets", color=MUTE).scale(0.36)
        forget.next_to(col, DOWN, buff=0.28)
        self.play(FadeIn(forget, shift=UP * 0.1), run_time=0.3)
        self.play(Indicate(forget, color=WARN, scale_factor=1.15), run_time=0.5)

        # ── RIGHT: THE APP ───────────────────────────────────────────────────
        right_hdr = Text("THE APP", weight=BOLD, color=ACCENT).scale(0.52)
        right_hdr.move_to(RIGHT * 3.5 + UP * 2.35)

        turns = VGroup(
            chip("turn 1", ACCENT, w=1.3, h=0.45, fs=0.28),
            chip("turn 2", ACCENT, w=1.3, h=0.45, fs=0.28),
            chip("turn 3", ACCENT, w=1.3, h=0.45, fs=0.28),
        ).arrange(DOWN, buff=0.16)
        turns.next_to(right_hdr, DOWN, buff=0.3)

        resend_lbl = caption("re-sends ALL of it, every turn", color=WARN, fs=0.32)
        resend_lbl.next_to(turns, DOWN, buff=0.22)

        self.play(FadeIn(right_hdr, shift=DOWN * 0.1), run_time=0.3)
        self.play(
            LaggedStart(*[FadeIn(t, shift=LEFT * 0.1) for t in turns], lag_ratio=0.25),
            run_time=0.6,
        )
        arrow = Arrow(
            turns.get_bottom() + DOWN * 0.05, resend_lbl.get_top() + UP * 0.05,
            buff=0.06, color=WARN, stroke_width=2, max_tip_length_to_length_ratio=0.2,
        )
        self.play(Create(arrow), FadeIn(resend_lbl), run_time=0.4)

        cap = caption("the model remembers nothing.  we fake it — until now.",
                      color=WARN, fs=0.44)
        cap.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(cap, shift=UP * 0.15, rate_func=smooth), run_time=0.42)
        self.wait(1.6)


# ── 3. ThreeMemories ──────────────────────────────────────────────────────────

class ThreeMemories(Scene):
    """
    Short-term (list), long-term (file), semantic (search) — three panels.
    Full-frame cutaway.  ~9 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("Three Kinds of Memory", weight=BOLD, color=TEXT).scale(0.62)
        title.to_edge(UP, buff=0.42)
        self.play(FadeIn(title, shift=DOWN * 0.15, rate_func=smooth), run_time=0.38)

        # Panel 1: SHORT-TERM
        hdr1 = Text("SHORT-TERM", weight=BOLD, color=ACCENT2).scale(0.44)
        sub1 = caption("a list · this task only", fs=0.32)
        chips1 = VGroup(*[chip(f"msg {i}", ACCENT2, w=1.3, h=0.42, fs=0.26) for i in range(1, 4)])
        chips1.arrange(DOWN, buff=0.14)
        col1 = VGroup(hdr1, chips1, sub1).arrange(DOWN, buff=0.26)
        col1.move_to(LEFT * 4.4)

        # Panel 2: LONG-TERM
        hdr2 = Text("LONG-TERM", weight=BOLD, color=ACCENT).scale(0.44)
        sub2 = caption("a file · across sessions", fs=0.32)
        disk = RoundedRectangle(corner_radius=0.12, width=1.7, height=1.3,
                                 stroke_color=ACCENT, stroke_width=2.5,
                                 fill_color=BG, fill_opacity=1)
        disk_lbl = Text("{ }", color=ACCENT, weight=BOLD).scale(0.5)
        disk_lbl.move_to(disk.get_center())
        disk_grp = VGroup(disk, disk_lbl)
        col2 = VGroup(hdr2, disk_grp, sub2).arrange(DOWN, buff=0.26)
        col2.move_to(ORIGIN)

        # Panel 3: SEMANTIC
        hdr3 = Text("SEMANTIC", weight=BOLD, color=WARN).scale(0.44)
        sub3 = caption("a search over meaning", fs=0.32)
        pts = VGroup(*[
            Dot(point=p, radius=0.07, color=WARN)
            for p in [UP * 0.4 + LEFT * 0.3, UP * 0.15 + RIGHT * 0.35,
                      DOWN * 0.25 + LEFT * 0.15, DOWN * 0.1 + RIGHT * 0.4,
                      UP * 0.5 + RIGHT * 0.05]
        ])
        pts_box = SurroundingRectangle(pts, color=WARN, buff=0.35, corner_radius=0.15, stroke_width=1.8)
        vec_grp = VGroup(pts_box, pts)
        col3 = VGroup(hdr3, vec_grp, sub3).arrange(DOWN, buff=0.26)
        col3.move_to(RIGHT * 4.4)

        for hdr, body, sub in [(hdr1, chips1, sub1), (hdr2, disk_grp, sub2), (hdr3, vec_grp, sub3)]:
            self.play(FadeIn(hdr, shift=DOWN * 0.1), run_time=0.32)
            self.play(FadeIn(body, scale=0.92), run_time=0.4)
            self.play(FadeIn(sub), run_time=0.28)
            self.wait(0.15)

        cap = caption("a list, a file, and a search engine", color=TEXT, fs=0.44)
        cap.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(cap, shift=UP * 0.15, rate_func=smooth), run_time=0.42)
        self.wait(1.8)


# ── 4. ContextWindowFills ─────────────────────────────────────────────────────

class ContextWindowFills(Scene):
    """
    The message list grows, the context window fills, then two fixes appear.
    Transparent overlay.  ~7 s.
    """
    def construct(self):
        lbl = Text("context window", color=MUTE).scale(0.4)
        lbl.to_edge(UP, buff=0.6)
        self.play(FadeIn(lbl, shift=DOWN * 0.1), run_time=0.3)

        track = RoundedRectangle(corner_radius=0.1, width=8.0, height=0.6,
                                  stroke_color=MUTE, stroke_width=2,
                                  fill_color=BG, fill_opacity=1)
        track.next_to(lbl, DOWN, buff=0.25)
        self.play(Create(track), run_time=0.3)

        fill = Rectangle(width=0.01, height=0.5, fill_color=ACCENT2, fill_opacity=0.9, stroke_width=0)
        fill.move_to(track.get_left() + RIGHT * 0.05, aligned_edge=LEFT)
        self.add(fill)

        widths = [1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 7.8]
        colors = [ACCENT2] * 4 + [WARN] * 3
        for w, c in zip(widths, colors):
            new_fill = Rectangle(width=w, height=0.5, fill_color=c, fill_opacity=0.9, stroke_width=0)
            new_fill.move_to(track.get_left() + RIGHT * (0.05 + w / 2), aligned_edge=LEFT)
            new_fill.align_to(track, LEFT).shift(RIGHT * 0.1)
            self.play(Transform(fill, new_fill), run_time=0.28)

        self.wait(0.2)
        warn_lbl = caption("almost full — and expensive", color=WARN, fs=0.36)
        warn_lbl.next_to(track, DOWN, buff=0.3)
        self.play(FadeIn(warn_lbl, shift=UP * 0.1), run_time=0.3)
        self.wait(0.3)

        # Two fixes
        fix1 = small_node("SUMMARIZE\nold turns", ACCENT, w=2.6, h=0.9, fs=0.3)
        fix2 = small_node("OFFLOAD\nto memory", ACCENT2, w=2.6, h=0.9, fs=0.3)
        fixes = VGroup(fix1, fix2).arrange(RIGHT, buff=0.8)
        fixes.next_to(warn_lbl, DOWN, buff=0.4)

        self.play(FadeOut(warn_lbl), run_time=0.2)
        self.play(
            LaggedStart(
                FadeIn(fix1, shift=UP * 0.1, rate_func=smooth),
                FadeIn(fix2, shift=UP * 0.1, rate_func=smooth),
                lag_ratio=0.25,
            ),
            run_time=0.6,
        )

        # Bar drops back to green
        small_fill = Rectangle(width=1.4, height=0.5, fill_color=ACCENT2, fill_opacity=0.9, stroke_width=0)
        small_fill.move_to(track.get_left() + RIGHT * (0.05 + 0.7), aligned_edge=LEFT)
        self.play(Transform(fill, small_fill), run_time=0.5)
        relief_lbl = caption("back under control", color=ACCENT2, fs=0.36)
        relief_lbl.next_to(fixes, DOWN, buff=0.3)
        self.play(FadeIn(relief_lbl), run_time=0.3)
        self.wait(1.5)


# ── 5. EmbeddingRetrieval ─────────────────────────────────────────────────────

class EmbeddingRetrieval(Scene):
    """
    Text -> embedding (vector) -> meaning space; query finds nearest neighbors.
    Full-frame cutaway.  ~11 s.  Signature visual.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("Embeddings & Semantic Retrieval", weight=BOLD, color=TEXT).scale(0.56)
        title.to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.15, rate_func=smooth), run_time=0.38)

        space_lbl = caption("meaning space", color=MUTE, fs=0.36)
        space_lbl.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(space_lbl), run_time=0.3)

        space_box = RoundedRectangle(corner_radius=0.2, width=10.5, height=5.2,
                                      stroke_color=MUTE, stroke_width=1.5,
                                      fill_color=BG, fill_opacity=1)
        space_box.next_to(space_lbl, DOWN, buff=0.25)
        self.play(Create(space_box), run_time=0.4)

        # Memory dots placed in the space (arbitrary but legible layout)
        db_pt = space_box.get_center() + LEFT * 2.6 + UP * 1.3
        pg_pt = space_box.get_center() + LEFT * 1.7 + UP * 0.9
        weather_pt = space_box.get_center() + RIGHT * 3.0 + UP * 1.6
        food_pt = space_box.get_center() + RIGHT * 2.4 + DOWN * 1.5
        travel_pt = space_box.get_center() + LEFT * 0.3 + DOWN * 1.8

        db_dot = dot_with_label(db_pt, "\"the database\"", ACCENT2, fs=0.3, direction=UP)
        pg_dot = dot_with_label(pg_pt, "\"the Postgres setup\"", ACCENT2, fs=0.3, direction=DOWN)
        weather_dot = dot_with_label(weather_pt, "\"favorite weather\"", MUTE, fs=0.28, direction=UP)
        food_dot = dot_with_label(food_pt, "\"favorite food\"", MUTE, fs=0.28, direction=DOWN)
        travel_dot = dot_with_label(travel_pt, "\"travel plans\"", MUTE, fs=0.28, direction=DOWN)

        for d in [db_dot, pg_dot, weather_dot, food_dot, travel_dot]:
            self.play(FadeIn(d, scale=0.7), run_time=0.3)

        self.wait(0.2)

        # Highlight that db + pg are close despite different words
        close_box = SurroundingRectangle(VGroup(db_dot, pg_dot), color=ACCENT2,
                                          buff=0.35, corner_radius=0.15, stroke_width=2)
        close_lbl = caption("different words, close in meaning", color=ACCENT2, fs=0.3)
        close_lbl.next_to(close_box, LEFT, buff=0.2).shift(UP * 0.3)
        self.play(Create(close_box), FadeIn(close_lbl), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(close_box), FadeOut(close_lbl), run_time=0.3)

        # Query arrives
        query_pt = space_box.get_center() + LEFT * 2.1 + UP * 1.15
        query_dot = Dot(point=query_pt + DOWN * 0.9 + LEFT * 0.4, radius=0.11, color=WARN)
        query_lbl = Text("\"what did I say about the database?\"", color=WARN).scale(0.3)
        query_lbl.next_to(query_dot, DOWN, buff=0.16)
        self.play(FadeIn(query_dot, scale=0.6), FadeIn(query_lbl, shift=UP * 0.1), run_time=0.45)

        # Draw lines to nearest neighbors
        line1 = Line(query_dot.get_center(), db_dot[0].get_center(), color=WARN, stroke_width=2.5)
        line2 = Line(query_dot.get_center(), pg_dot[0].get_center(), color=WARN, stroke_width=2.5)
        self.play(Create(line1), Create(line2), run_time=0.5)

        self.play(
            db_dot[0].animate.set_color(WARN).scale(1.3),
            pg_dot[0].animate.set_color(WARN).scale(1.3),
            run_time=0.4,
        )

        cap = Text(
            "different words, same meaning — distance finds it. this is RAG.",
            color=WARN, weight=BOLD,
        ).scale(0.42)
        cap.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(cap, shift=UP * 0.15, rate_func=smooth), run_time=0.45)
        self.wait(1.8)


# ── 6. CrossSessionRecall ─────────────────────────────────────────────────────

class CrossSessionRecall(Scene):
    """
    Session 1 saves facts; session 2 (clean slate) retrieves and answers.
    Transparent overlay.  ~9 s.  The payoff moment.
    """
    def construct(self):
        terminal = RoundedRectangle(
            corner_radius=0.28, width=13.2, height=7.4,
            fill_color=BG, fill_opacity=0.93,
            stroke_color=MUTE, stroke_width=1.5,
        )
        self.add(terminal)

        bar = Rectangle(width=13.2, height=0.36, fill_color=MUTE, fill_opacity=0.12, stroke_width=0)
        bar.align_to(terminal, UP).shift(DOWN * 0.18)
        self.add(bar)

        FS = 0.38
        rows_spec = [
            (0, "", "SESSION 1", "", ACCENT, TEXT),
            (0, "🧑", "", "my name is Maneesh, project Agent Unpacked", MUTE, TEXT),
            (0, "🔧", "save_memory", "(...)", ACCENT, MUTE),
            (0, "👀", "saved", "", ACCENT2, TEXT),
        ]

        rows = VGroup()
        for indent, marker, label, content, m_color, c_color in rows_spec:
            row = trace_line(marker, label, content, m_color=m_color, c_color=c_color, fs=FS)
            rows.add(row)
        rows.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        rows.move_to(terminal.get_center() + UP * 2.0).align_to(terminal, LEFT).shift(RIGHT * 0.6)

        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.07, rate_func=smooth), run_time=0.3)
            self.wait(0.32)

        # Divider — session boundary
        div_lbl = Text("— new session, nothing carried over —", color=WARN, weight=BOLD).scale(0.36)
        div_lbl.next_to(rows, DOWN, buff=0.4)
        div_line = Line(
            div_lbl.get_left() + LEFT * 0.3, div_lbl.get_right() + RIGHT * 0.3,
            color=WARN, stroke_width=1.5,
        ).next_to(div_lbl, DOWN, buff=0.12)
        self.play(FadeIn(div_lbl, scale=0.9), Create(div_line), run_time=0.5)
        self.wait(0.4)

        rows2_spec = [
            (0, "", "SESSION 2", "", ACCENT, TEXT),
            (0, "🧑", "", "what's my project?", MUTE, TEXT),
            (0, "🔧", "recall", "('project')", ACCENT, MUTE),
            (0, "👀", "Agent Unpacked", "", ACCENT2, TEXT),
            (0, "✅", "Your project is Agent Unpacked", "", WARN, TEXT),
        ]
        rows2 = VGroup()
        for indent, marker, label, content, m_color, c_color in rows2_spec:
            row = trace_line(marker, label, content, m_color=m_color, c_color=c_color, fs=FS)
            rows2.add(row)
        rows2.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        rows2.next_to(div_line, DOWN, buff=0.35).align_to(rows, LEFT)

        for row in rows2:
            self.play(FadeIn(row, shift=RIGHT * 0.07, rate_func=smooth), run_time=0.3)
            self.wait(0.32)

        self.wait(1.6)


# ── 7. RememberVsForget ───────────────────────────────────────────────────────

class RememberVsForget(Scene):
    """
    Keep durable facts, let go of sensitive/one-off noise.
    Full-frame cutaway.  ~9 s.
    """
    def construct(self):
        self.add(bg_deco())

        heading = Text("What to Remember, What to Forget", weight=BOLD, color=TEXT).scale(0.6)
        heading.to_edge(UP, buff=0.48)
        ul = Line(
            heading.get_left() + DOWN * 0.04, heading.get_right() + DOWN * 0.04,
            color=ACCENT, stroke_width=3,
        ).next_to(heading, DOWN, buff=0.1)
        self.play(FadeIn(heading, shift=DOWN * 0.15, rate_func=smooth), run_time=0.4)
        self.play(Create(ul), run_time=0.3)

        keep_hdr = Text("KEEP", weight=BOLD, color=ACCENT2).scale(0.5)
        forget_hdr = Text("LET GO", weight=BOLD, color=WARN).scale(0.5)
        div = Line(UP * 2.6, DOWN * 3.0, color=MUTE, stroke_width=1.2)

        keep_hdr.next_to(div, LEFT, buff=1.6).align_to(ul, DOWN).shift(DOWN * 0.4)
        forget_hdr.next_to(div, RIGHT, buff=1.6).align_to(keep_hdr, UP)

        self.play(Create(div), FadeIn(keep_hdr, shift=DOWN * 0.08), FadeIn(forget_hdr, shift=DOWN * 0.08),
                  run_time=0.4)

        keep_items = ["names & stated preferences", "decisions made", "durable project context"]
        forget_items = ["sensitive data not needed", "one-off trivia", "anything user wouldn't want back"]

        row_y = keep_hdr.get_bottom()[1] - 0.55
        gap = 0.85
        FS = 0.38

        for i, (k, f) in enumerate(zip(keep_items, forget_items)):
            y = row_y - i * gap
            check = Text("✓", color=ACCENT2).scale(FS)
            k_txt = Text(k, color=TEXT).scale(FS * 0.85)
            left_g = VGroup(check, k_txt).arrange(RIGHT, buff=0.2)
            left_g.next_to(div, LEFT, buff=0.5).set_y(y)

            cross = Text("✗", color=WARN).scale(FS)
            f_txt = Text(f, color=WARN).scale(FS * 0.85)
            right_g = VGroup(cross, f_txt).arrange(RIGHT, buff=0.2)
            right_g.next_to(div, RIGHT, buff=0.5).set_y(y)

            self.play(FadeIn(left_g, shift=LEFT * 0.08, rate_func=smooth), run_time=0.35)
            self.play(FadeIn(right_g, shift=RIGHT * 0.08, rate_func=smooth), run_time=0.35)
            self.wait(0.25)

        cap = caption("memory is data — build the delete path from day one.", color=WARN, fs=0.42)
        cap.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap, shift=UP * 0.15, rate_func=smooth), run_time=0.42)
        self.wait(1.8)
