"""
ep04_scenes.py — Manim animations for "Agentic AI, Unpacked · EP 04"
Multi-Agent Systems

Scenes:
  Ep04TitleSting      ~2.5s   transparent overlay  @ 1:15
  OneAgentVsTeam      ~8s     full-frame cutaway   @ 1:15 (thumbnail energy)
  OrchestratorPattern ~10s    full-frame cutaway   @ 3:00
  NestedLoop          ~9s     full-frame cutaway   @ 8:30
  TeamTrace           ~10s    transparent overlay  @ 11:30
  TeamFailureModes    ~10s    full-frame cutaway   @ 17:00
  WhenNotToTeam       ~7s     full-frame cutaway   @ 22:00

Render:
  manim -qh --media_dir ../renders Episode4/ep04_scenes.py <Scene>
  manim -qh -t --media_dir ../renders Episode4/ep04_scenes.py <Scene>
Or: ./render_all.sh ep04
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
    """Slightly smaller node variant for tighter layouts."""
    box = RoundedRectangle(
        corner_radius=0.18, width=w, height=h,
        stroke_color=color, stroke_width=2.5,
        fill_color=BG, fill_opacity=1,
    )
    txt = Text(label, weight=BOLD, color=TEXT).scale(fs)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


def task_chip(label, color=WARN, w=1.9, h=0.55):
    """Small chip for 'TASK', 'SUBTASK', 'FINAL ANSWER' etc."""
    box = RoundedRectangle(
        corner_radius=0.12, width=w, height=h,
        stroke_color=color, stroke_width=2,
        fill_color=BG, fill_opacity=1,
    )
    txt = Text(label, weight=BOLD, color=color).scale(0.36)
    txt.move_to(box.get_center())
    return VGroup(box, txt)


def delegate_arrow(start, end, color=ACCENT):
    return Arrow(
        start, end, buff=0.12, color=color, stroke_width=2.5,
        max_tip_length_to_length_ratio=0.12,
    )


def result_arrow(start, end, color=ACCENT2):
    return Arrow(
        start, end, buff=0.12, color=color, stroke_width=2,
        max_tip_length_to_length_ratio=0.12,
    )


def trace_line(marker, label, content="", m_color=WARN, l_color=None, c_color=MUTE, fs=0.38):
    """One line of an agent trace display."""
    l_color = l_color or m_color
    parts = [Text(marker, color=m_color).scale(fs)]
    if label:
        parts.append(Text(label, weight=BOLD, color=l_color).scale(fs))
    if content:
        parts.append(Text(content, color=c_color).scale(fs))
    return VGroup(*parts).arrange(RIGHT, buff=0.18)


# ── 1. Ep04TitleSting ──────────────────────────────────────────────────────────

class Ep04TitleSting(Scene):
    """EP 04 title card — transparent overlay.  ~2.5 s."""
    def construct(self):
        content, ul = title_card(
            "AGENTIC AI, UNPACKED",
            sub="EP 04 — MULTI-AGENT SYSTEMS",
        )
        self.play(FadeIn(content, scale=0.88, rate_func=smooth), run_time=0.5)
        self.play(Create(ul), run_time=0.44)
        self.wait(1.5)


# ── 2. OneAgentVsTeam ─────────────────────────────────────────────────────────

class OneAgentVsTeam(Scene):
    """
    One agent does tasks sequentially; a team works in parallel.
    Full-frame cutaway.  ~8 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("One Agent  vs  A Team", weight=BOLD, color=TEXT).scale(0.62)
        title.to_edge(UP, buff=0.42)
        self.play(FadeIn(title, shift=DOWN * 0.15, rate_func=smooth), run_time=0.38)

        div = Line(UP * 3.5, DOWN * 3.5, color=MUTE, stroke_width=1.5)
        self.play(Create(div), run_time=0.28)

        # ── LEFT: ONE AGENT ─────────────────────────────────────────────────
        left_hdr = Text("ONE AGENT", weight=BOLD, color=ACCENT2).scale(0.56)
        agent_n  = small_node("AGENT", ACCENT2, w=2.5, h=0.9, fs=0.46)

        t1 = small_node("TASK 1", MUTE, w=2.3, h=0.65, fs=0.38)
        t2 = small_node("TASK 2", MUTE, w=2.3, h=0.65, fs=0.38)
        t3 = small_node("TASK 3", MUTE, w=2.3, h=0.65, fs=0.38)
        queue = VGroup(t1, t2, t3).arrange(DOWN, buff=0.14)

        seq_lbl = caption("one task at a time", fs=0.38)

        left_hdr.move_to(LEFT * 3.4 + UP * 2.45)
        agent_n.next_to(left_hdr, DOWN, buff=0.32)
        queue.next_to(agent_n, DOWN, buff=0.22)
        seq_lbl.next_to(queue, DOWN, buff=0.22)

        arr_q = Arrow(
            agent_n.get_bottom(), t1.get_top(),
            buff=0.08, color=MUTE, stroke_width=2,
            max_tip_length_to_length_ratio=0.16,
        )

        self.play(FadeIn(left_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.32)
        self.play(FadeIn(agent_n, scale=0.9, rate_func=smooth), run_time=0.4)
        self.play(Create(arr_q), run_time=0.28)
        for t in [t1, t2, t3]:
            self.play(FadeIn(t, shift=DOWN * 0.1, rate_func=smooth), run_time=0.35)
            self.wait(0.18)
        self.play(FadeIn(seq_lbl), run_time=0.28)

        # ── RIGHT: A TEAM ────────────────────────────────────────────────────
        right_hdr = Text("A TEAM", weight=BOLD, color=WARN).scale(0.56)
        orch      = small_node("ORCHESTRATOR", ACCENT, w=3.0, h=0.9, fs=0.42)

        r_n = small_node("RESEARCHER", ACCENT2, w=1.55, h=0.70, fs=0.28)
        a_n = small_node("ANALYST",    ACCENT2, w=1.55, h=0.70, fs=0.28)
        w_n = small_node("WRITER",     ACCENT2, w=1.55, h=0.70, fs=0.28)
        c_n = small_node("CRITIC",     WARN,    w=1.55, h=0.70, fs=0.28)
        specs = VGroup(r_n, a_n, w_n, c_n).arrange(RIGHT, buff=0.16)

        par_lbl = caption("works in parallel", fs=0.38)

        right_hdr.move_to(RIGHT * 3.4 + UP * 2.45)
        orch.next_to(right_hdr, DOWN, buff=0.32)
        specs.next_to(orch, DOWN, buff=0.75)
        specs.move_to(RIGHT * 3.4 + specs.get_center()[1] * UP)
        par_lbl.next_to(specs, DOWN, buff=0.22)

        arr_r = delegate_arrow(orch.get_bottom(), r_n.get_top())
        arr_a = delegate_arrow(orch.get_bottom(), a_n.get_top())
        arr_w = delegate_arrow(orch.get_bottom(), w_n.get_top())
        arr_c = delegate_arrow(orch.get_bottom(), c_n.get_top())

        self.play(FadeIn(right_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.32)
        self.play(FadeIn(orch, scale=0.9, rate_func=smooth), run_time=0.4)

        # Arrows fan out simultaneously, then all specialists appear at once
        self.play(
            LaggedStart(Create(arr_r), Create(arr_a), Create(arr_w), Create(arr_c), lag_ratio=0.15),
            run_time=0.6,
        )
        self.play(
            LaggedStart(
                FadeIn(r_n, shift=DOWN * 0.12, rate_func=smooth),
                FadeIn(a_n, shift=DOWN * 0.12, rate_func=smooth),
                FadeIn(w_n, shift=DOWN * 0.12, rate_func=smooth),
                FadeIn(c_n, shift=DOWN * 0.12, rate_func=smooth),
                lag_ratio=0.09,
            ),
            run_time=0.7,
        )

        # Glow all 4 simultaneously — the "alive" moment
        self.play(
            r_n[0].animate.set_stroke(color=ACCENT2, width=3.5),
            a_n[0].animate.set_stroke(color=ACCENT2, width=3.5),
            w_n[0].animate.set_stroke(color=ACCENT2, width=3.5),
            c_n[0].animate.set_stroke(color=WARN, width=3.5),
            run_time=0.38,
        )
        self.play(FadeIn(par_lbl), run_time=0.28)

        # Caption
        cap = Text(
            "stop building a super-agent.  build a team.",
            color=WARN, weight=BOLD,
        ).scale(0.52)
        cap.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(cap, shift=UP * 0.18, rate_func=smooth), run_time=0.48)
        self.wait(1.8)


# ── 3. OrchestratorPattern ────────────────────────────────────────────────────

class OrchestratorPattern(Scene):
    """
    Orchestrator receives task, delegates to specialists, collects results,
    emits final answer.  Full-frame cutaway.  ~10 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("The Orchestrator Pattern", weight=BOLD, color=TEXT).scale(0.58)
        title.to_edge(UP, buff=0.42)
        self.play(FadeIn(title, shift=DOWN * 0.15, rate_func=smooth), run_time=0.38)

        # Orchestrator node at top-centre
        orch = small_node("ORCHESTRATOR", ACCENT, w=3.2, h=0.92, fs=0.44)
        orch.move_to(UP * 1.9)
        self.play(FadeIn(orch, scale=0.88, rate_func=smooth), run_time=0.45)
        self.wait(0.2)

        # Task chip drops in from above
        tc = task_chip("TASK", WARN, w=1.8, h=0.54)
        tc.move_to(UP * 3.5)
        self.play(FadeIn(tc, shift=DOWN * 0.2), run_time=0.3)
        self.play(tc.animate.move_to(orch.get_center()).scale(0.7), run_time=0.42)
        self.play(FadeOut(tc), orch[0].animate.set_fill(color=WARN, opacity=0.08), run_time=0.25)
        self.play(orch[0].animate.set_fill(color=BG, opacity=1.0), run_time=0.22)

        # Four specialist nodes
        r_n = small_node("RESEARCHER", ACCENT2, w=2.2, h=0.82, fs=0.34)
        a_n = small_node("ANALYST",    ACCENT2, w=2.2, h=0.82, fs=0.34)
        w_n = small_node("WRITER",     ACCENT2, w=2.2, h=0.82, fs=0.34)
        c_n = small_node("CRITIC",     WARN,    w=2.2, h=0.82, fs=0.34)
        r_n.move_to(LEFT  * 5.3  + DOWN * 0.5)
        a_n.move_to(LEFT  * 1.75 + DOWN * 0.5)
        w_n.move_to(RIGHT * 1.75 + DOWN * 0.5)
        c_n.move_to(RIGHT * 5.3  + DOWN * 0.5)

        # Delegate arrows (solid ACCENT, downward)
        da_r = delegate_arrow(orch.get_bottom(), r_n.get_top())
        da_a = delegate_arrow(orch.get_bottom(), a_n.get_top())
        da_w = delegate_arrow(orch.get_bottom(), w_n.get_top())
        da_c = delegate_arrow(orch.get_bottom(), c_n.get_top(), WARN)

        sub_r = caption("research",  fs=0.32)
        sub_a = caption("analyse",   fs=0.32)
        sub_w = caption("write",     fs=0.32)
        sub_c = caption("review",    fs=0.32, color=WARN)
        sub_r.next_to(da_r.get_center(), LEFT,  buff=0.14)
        sub_a.next_to(da_a.get_center(), LEFT,  buff=0.14)
        sub_w.next_to(da_w.get_center(), RIGHT, buff=0.14)
        sub_c.next_to(da_c.get_center(), RIGHT, buff=0.14)

        for arr, sub, spec in [(da_r, sub_r, r_n), (da_a, sub_a, a_n),
                                (da_w, sub_w, w_n), (da_c, sub_c, c_n)]:
            self.play(Create(arr), FadeIn(sub), run_time=0.36)
            self.play(FadeIn(spec, shift=DOWN * 0.15, rate_func=smooth), run_time=0.36)
            self.wait(0.15)

        self.wait(0.3)

        # Result arrows come back up one by one (ACCENT2, offset to avoid overlap)
        # Use slight left/right offsets so they don't perfectly overlap delegates
        ra_r = result_arrow(
            r_n.get_top()  + RIGHT * 0.35,
            orch.get_bottom() + LEFT * 0.9,
        )
        ra_a = result_arrow(
            a_n.get_top()  + RIGHT * 0.25,
            orch.get_bottom() + LEFT * 0.3,
        )
        ra_w = result_arrow(
            w_n.get_top()  + LEFT  * 0.25,
            orch.get_bottom() + RIGHT * 0.3,
        )
        ra_c = result_arrow(
            c_n.get_top()  + LEFT  * 0.35,
            orch.get_bottom() + RIGHT * 0.9,
        )

        for ra in [ra_r, ra_a, ra_w, ra_c]:
            self.play(Create(ra), run_time=0.34)
            self.wait(0.16)

        self.wait(0.25)

        # Final answer chip emerges from the orchestrator going DOWN
        fa = task_chip("FINAL ANSWER", WARN, w=2.8, h=0.60)
        fa.move_to(DOWN * 2.4)
        fa_arr = delegate_arrow(orch.get_center() + DOWN * 0.46, fa.get_top(), WARN)

        self.play(Create(fa_arr), run_time=0.35)
        self.play(FadeIn(fa, scale=0.9, rate_func=smooth), run_time=0.42)

        # Caption
        cap = caption("specialists report UP,  not sideways", color=WARN, fs=0.44)
        cap.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(cap, shift=UP * 0.15, rate_func=smooth), run_time=0.4)
        self.wait(1.8)


# ── 4. NestedLoop ─────────────────────────────────────────────────────────────

class NestedLoop(Scene):
    """
    Multi-agent isn't a new mechanism — the same loop, nested.
    Full-frame cutaway.  ~9 s.
    """
    def construct(self):
        self.add(bg_deco())

        outer_lbl = Text("ORCHESTRATOR loop", weight=BOLD, color=MUTE).scale(0.40)
        outer_lbl.to_edge(UP, buff=0.55)
        self.play(FadeIn(outer_lbl, shift=DOWN * 0.1), run_time=0.32)

        # Outer loop — 4 nodes in a horizontal flow at top half
        labels  = ["GOAL", "THINK", "ACT", "OBSERVE"]
        colors  = [WARN,   ACCENT,  ACCENT, ACCENT2]
        widths  = [2.1,    2.1,     2.1,    2.4]
        o_nodes = [small_node(l, c, w=w, h=0.80, fs=0.40)
                   for l, c, w in zip(labels, colors, widths)]
        o_flow  = VGroup(*o_nodes).arrange(RIGHT, buff=0.55)
        o_flow.move_to(UP * 1.75)

        o_arrows = [
            Arrow(
                o_nodes[i].get_right(), o_nodes[i + 1].get_left(),
                buff=0.08, color=TEXT, stroke_width=2,
                max_tip_length_to_length_ratio=0.15,
            )
            for i in range(3)
        ]
        # Return arrow from OBSERVE back to GOAL (below the row)
        ret = CurvedArrow(
            o_nodes[3].get_bottom() + RIGHT * 0.25,
            o_nodes[0].get_bottom() + LEFT  * 0.25,
            angle=PI / 2,
            color=MUTE, stroke_width=1.8,
        )

        self.play(
            LaggedStart(*[FadeIn(n, shift=UP * 0.14, rate_func=smooth) for n in o_nodes],
                        lag_ratio=0.18),
            run_time=0.85,
        )
        self.play(
            LaggedStart(*[Create(a) for a in o_arrows], lag_ratio=0.15),
            run_time=0.55,
        )
        self.play(Create(ret), run_time=0.38)
        self.wait(0.4)

        # Highlight ACT node
        act = o_nodes[2]
        self.play(
            act[0].animate.set_stroke(color=WARN, width=3.5),
            act[1].animate.set_color(WARN),
            o_arrows[1].animate.set_color(WARN),
            run_time=0.38,
        )
        tool_lbl = caption("delegates to: researcher", color=WARN, fs=0.38)
        tool_lbl.next_to(act, DOWN, buff=0.28)
        self.play(FadeIn(tool_lbl, shift=DOWN * 0.1), run_time=0.32)
        self.wait(0.3)

        # Inner loop reveals below ACT — a dashed-border box containing a mini-loop
        inner_lbl = Text("RESEARCHER loop", weight=BOLD, color=ACCENT2).scale(0.38)

        i_nodes = [
            small_node("think",   ACCENT,  w=1.55, h=0.60, fs=0.32),
            small_node("act",     ACCENT,  w=1.55, h=0.60, fs=0.32),
            small_node("observe", ACCENT2, w=1.65, h=0.60, fs=0.32),
        ]
        i_flow = VGroup(*i_nodes).arrange(RIGHT, buff=0.38)
        i_arrows = [
            Arrow(
                i_nodes[j].get_right(), i_nodes[j + 1].get_left(),
                buff=0.07, color=ACCENT2, stroke_width=1.8,
                max_tip_length_to_length_ratio=0.15,
            )
            for j in range(2)
        ]
        i_ret = CurvedArrow(
            i_nodes[2].get_bottom() + RIGHT * 0.2,
            i_nodes[0].get_bottom() + LEFT  * 0.2,
            angle=PI / 2,
            color=MUTE, stroke_width=1.5,
        )

        inner_lbl.next_to(i_flow, UP, buff=0.22)
        inner_content = VGroup(inner_lbl, i_flow)
        inner_content.move_to(DOWN * 1.55)

        inner_box = SurroundingRectangle(
            inner_content, color=ACCENT2, buff=0.32,
            corner_radius=0.2, stroke_width=1.8,
        )

        zoom_arr = Arrow(
            act.get_bottom(), inner_box.get_top(),
            buff=0.10, color=WARN, stroke_width=2,
            max_tip_length_to_length_ratio=0.14,
        )

        self.play(Create(zoom_arr), run_time=0.38)
        self.play(
            Create(inner_box),
            FadeIn(inner_lbl, shift=DOWN * 0.1, rate_func=smooth),
            run_time=0.42,
        )
        self.play(
            LaggedStart(*[FadeIn(n, shift=DOWN * 0.1) for n in i_nodes], lag_ratio=0.18),
            run_time=0.6,
        )
        self.play(
            LaggedStart(Create(i_arrows[0]), Create(i_arrows[1]), lag_ratio=0.2),
            Create(i_ret),
            run_time=0.45,
        )
        self.wait(0.35)

        # Result arrow: inner observe back to outer OBSERVE
        result_arr = CurvedArrow(
            i_nodes[2].get_right() + RIGHT * 0.15,
            o_nodes[3].get_bottom() + DOWN  * 0.12,
            angle=-PI / 2.8,
            color=ACCENT2, stroke_width=2,
        )
        res_lbl = caption("result", color=ACCENT2, fs=0.36)
        res_lbl.next_to(result_arr.get_center(), RIGHT, buff=0.12)
        self.play(Create(result_arr), FadeIn(res_lbl), run_time=0.48)

        # Caption
        punch = Text(
            "same loop.  nested.  that's the whole trick.",
            color=WARN, weight=BOLD,
        ).scale(0.52)
        punch.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(punch, shift=UP * 0.18, rate_func=smooth), run_time=0.45)
        self.wait(1.8)


# ── 5. TeamTrace ──────────────────────────────────────────────────────────────

class TeamTrace(Scene):
    """
    Nested terminal trace — orchestrator delegating, specialists running.
    Transparent overlay over face-cam.  ~10 s.  Pace ~0.7 s per line.
    """
    def construct(self):
        terminal = RoundedRectangle(
            corner_radius=0.28, width=13.2, height=7.4,
            fill_color=BG, fill_opacity=0.93,
            stroke_color=MUTE, stroke_width=1.5,
        )
        self.add(terminal)

        bar = Rectangle(
            width=13.2, height=0.36,
            fill_color=MUTE, fill_opacity=0.12, stroke_width=0,
        )
        bar.align_to(terminal, UP).shift(DOWN * 0.18)
        self.add(bar)

        FS = 0.38
        INDENT = RIGHT * 0.85   # one indent level

        # Build rows with manual indentation via shift after arrange
        rows_spec = [
            # (indent, marker, label, content, marker_color, content_color)
            (0, "👔", "ORCHESTRATOR:", "plan 4 jobs",       WARN,    TEXT),
            (1, "👤", "RESEARCHER",    "",                   ACCENT2, TEXT),
            (2, "🔧", "web_search",    "(\"best time to visit Kyoto\")", ACCENT, MUTE),
            (2, "👀", "found 5 spots", "",                  ACCENT2, TEXT),
            (1, "👤", "ANALYST",       "",                   ACCENT2, TEXT),
            (2, "🔧", "calculator",    "(3000 / 5)",         ACCENT,  MUTE),
            (2, "👀", "$600 / day budget", "",               ACCENT2, TEXT),
            (1, "👤", "WRITER",        "drafting itinerary...", ACCENT2, MUTE),
            (1, "👤", "CRITIC",        "reviewing draft...", WARN,    MUTE),
            (2, "👀", "approved ✅",   "",                   WARN,    TEXT),
            (0, "✅", "ORCHESTRATOR:", "assembled final itinerary", ACCENT2, TEXT),
        ]

        rows = VGroup()
        for indent, marker, label, content, m_color, c_color in rows_spec:
            row = trace_line(marker, label, content, m_color=m_color, c_color=c_color, fs=FS)
            rows.add(row)

        rows.arrange(DOWN, buff=0.24, aligned_edge=LEFT)

        # Apply indentation after arrange
        for row, (indent, *_) in zip(rows, rows_spec):
            row.shift(INDENT * indent)

        rows.move_to(terminal.get_center()).shift(LEFT * 0.2)

        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.07, rate_func=smooth), run_time=0.30)
            self.wait(0.40)

        self.wait(1.8)


# ── 6. TeamFailureModes ───────────────────────────────────────────────────────

class TeamFailureModes(Scene):
    """
    4 ways agent teams fail + the fix.  Full-frame cutaway.  ~10 s.
    Screenshot-clean — one row at a time.
    """
    def construct(self):
        self.add(bg_deco())

        heading = Text("4 ways agent teams fail", weight=BOLD, color=TEXT).scale(0.72)
        heading.to_edge(UP, buff=0.52)
        ul = Line(
            heading.get_left()  + DOWN * 0.04,
            heading.get_right() + DOWN * 0.04,
            color=ACCENT, stroke_width=3,
        ).next_to(heading, DOWN, buff=0.10)

        self.play(FadeIn(heading, shift=DOWN * 0.15, rate_func=smooth), run_time=0.4)
        self.play(Create(ul), run_time=0.3)

        # Column headers
        fail_col_hdr = Text("FAILURE", weight=BOLD, color=RED_D).scale(0.42)
        fix_col_hdr  = Text("FIX",     weight=BOLD, color=ACCENT2).scale(0.42)

        div = Line(UP * 2.4, DOWN * 3.0, color=MUTE, stroke_width=1.2).move_to(ORIGIN)

        fail_col_hdr.next_to(div, LEFT,  buff=0.5).align_to(ul, DOWN).shift(DOWN * 0.45)
        fix_col_hdr.next_to(div,  RIGHT, buff=0.5).align_to(fail_col_hdr, UP)

        self.play(
            Create(div),
            FadeIn(fail_col_hdr, shift=DOWN * 0.08),
            FadeIn(fix_col_hdr,  shift=DOWN * 0.08),
            run_time=0.35,
        )

        failures = [
            ("telephone game",    "pass structured results"),
            ("runaway delegation","set a depth limit"),
            ("cost explosion",    "per-agent step caps + budget"),
            ("one agent blocks all", "timeouts + graceful degradation"),
        ]

        row_start_y = fail_col_hdr.get_bottom()[1] - 0.55
        row_gap     = 0.90
        FS          = 0.43

        for i, (fail, fix) in enumerate(failures):
            y = row_start_y - i * row_gap

            x_mark = Text("✗", color=RED_D).scale(FS)
            fail_t  = Text(fail, color=TEXT).scale(FS * 0.88)
            left_g  = VGroup(x_mark, fail_t).arrange(RIGHT, buff=0.2)
            left_g.next_to(div, LEFT, buff=0.5)
            left_g.set_y(y)

            check  = Text("✓", color=ACCENT2).scale(FS)
            fix_t  = Text(fix, color=ACCENT2).scale(FS * 0.88)
            right_g = VGroup(check, fix_t).arrange(RIGHT, buff=0.2)
            right_g.next_to(div, RIGHT, buff=0.5)
            right_g.set_y(y)

            # Reveal ✗ first, brief beat, then ✓
            self.play(FadeIn(left_g, shift=LEFT * 0.08, rate_func=smooth), run_time=0.38)
            self.wait(0.25)
            self.play(FadeIn(right_g, shift=RIGHT * 0.08, rate_func=smooth), run_time=0.38)
            self.wait(0.32)

        self.wait(1.8)


# ── 7. WhenNotToTeam ──────────────────────────────────────────────────────────

class WhenNotToTeam(Scene):
    """
    Most tasks don't need a team.  Cost comparison + caption.
    Full-frame cutaway.  ~7 s.
    """
    def construct(self):
        self.add(bg_deco())

        # Big headline in two parts: first line "Most tasks" (plain), second "DON'T need a team."
        line1 = Text("Most tasks", color=TEXT, weight=BOLD).scale(1.05)
        line2_dont = Text("DON'T", color=WARN, weight=BOLD).scale(1.25)
        line2_rest = Text(" need a team.", color=TEXT, weight=BOLD).scale(1.05)
        line2 = VGroup(line2_dont, line2_rest).arrange(RIGHT, buff=0.1)
        headline = VGroup(line1, line2).arrange(DOWN, buff=0.22)
        headline.move_to(UP * 1.7)

        self.play(FadeIn(line1, shift=DOWN * 0.2, rate_func=smooth), run_time=0.42)
        self.play(
            FadeIn(line2_dont, scale=0.88, rate_func=smooth),
            FadeIn(line2_rest, shift=LEFT  * 0.08),
            run_time=0.48,
        )
        self.wait(0.4)

        # Cost comparison: two boxes side by side
        solo_box = RoundedRectangle(
            corner_radius=0.2, width=3.6, height=1.5,
            stroke_color=ACCENT2, stroke_width=2.5,
            fill_color=BG, fill_opacity=1,
        )
        solo_n   = Text("1 agent", weight=BOLD, color=ACCENT2).scale(0.56)
        solo_cost = Text("~ 6¢  per task", color=TEXT).scale(0.46)
        solo_inner = VGroup(solo_n, solo_cost).arrange(DOWN, buff=0.18)
        solo_inner.move_to(solo_box.get_center())
        solo_g = VGroup(solo_box, solo_inner)

        team_box = RoundedRectangle(
            corner_radius=0.2, width=3.6, height=1.5,
            stroke_color=WARN, stroke_width=3.5,
            fill_color=BG, fill_opacity=1,
        )
        team_n   = Text("team of 5", weight=BOLD, color=WARN).scale(0.56)
        team_cost = Text("~ 60¢  per task", color=TEXT).scale(0.46)
        team_inner = VGroup(team_n, team_cost).arrange(DOWN, buff=0.18)
        team_inner.move_to(team_box.get_center())
        team_g = VGroup(team_box, team_inner)

        vs_lbl = Text("vs", color=MUTE).scale(0.55)
        cost_row = VGroup(solo_g, vs_lbl, team_g).arrange(RIGHT, buff=0.5)
        cost_row.move_to(DOWN * 0.6)

        self.play(
            FadeIn(solo_g, shift=RIGHT * 0.1, rate_func=smooth),
            FadeIn(vs_lbl),
            run_time=0.42,
        )
        self.play(FadeIn(team_g, shift=LEFT * 0.1, rate_func=smooth), run_time=0.42)

        # Glow on team box to show its cost weight
        team_glow = solo_box.copy().move_to(team_box.get_center())
        team_glow.scale(1.08).set_stroke(width=0).set_fill(color=WARN, opacity=0.10)
        team_glow.z_index = team_box.z_index - 1
        self.play(FadeIn(team_glow), run_time=0.35)

        # Caption
        cap = caption("add agents only when they earn it", color=WARN, fs=0.46)
        cap.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(cap, shift=UP * 0.18, rate_func=smooth), run_time=0.42)
        self.wait(1.8)
