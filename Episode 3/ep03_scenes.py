"""
ep03_scenes.py — Manim animations for "Agentic AI, Unpacked · EP 03"
Agent with Real Tools

Scenes:
  Ep03TitleSting     ~2.5s   transparent overlay  @ 1:00
  ToyVsRealTool      ~8s     full-frame cutaway   @ 1:30
  ToolSchemaAnatomy  ~10s    full-frame cutaway   @ 2:30
  MultiToolChaining  ~10s    full-frame cutaway   @ 11:30
  ErrorRecovery      ~9s     transparent overlay  @ 16:30
  CostGuardrail      ~9s     full-frame cutaway   @ 19:00
  ToolMistakes       ~130s   full-frame cutaway   @ 21:00
  FrameworkDecision  ~62s    full-frame cutaway   @ 23:00
  Ep03Outro          ~25s    full-frame cutaway   @ episode end
  Ep04Teaser         ~19s    full-frame cutaway   @ episode end (post-outro)

Render:
  manim -qh --media_dir ../renders "Episode 3/ep03_scenes.py" <Scene>
  manim -qh -t --media_dir ../renders "Episode 3/ep03_scenes.py" <Scene>
Or use render_all.sh --ep03 at the repo root.
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
    cascade_in, title_card, flow, compare_cols, bullets,
)

RED_ERR = "#FF5C5C"


# ── 1. Ep03TitleSting ──────────────────────────────────────────────────────────

class Ep03TitleSting(Scene):
    """
    EP 03 title card — transparent overlay.
    Matches Ep01/Ep02 style.  ~2.5 s.
    """
    def construct(self):
        content, ul = title_card(
            "AGENTIC AI, UNPACKED",
            sub="EP 03 — REAL TOOLS",
        )
        self.play(FadeIn(content, scale=0.88, rate_func=smooth), run_time=0.5)
        self.play(Create(ul), run_time=0.44)
        self.wait(1.5)


# ── 2. ToyVsRealTool ───────────────────────────────────────────────────────────

class ToyVsRealTool(Scene):
    """
    Toy tool (predictable) vs real tool (messy) — same interface on top.
    Full-frame cutaway.  ~8 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("Same interface. Very different reality.", weight=BOLD, color=TEXT).scale(0.56)
        title.to_edge(UP, buff=0.38)
        self.play(FadeIn(title, shift=DOWN * 0.14, rate_func=smooth), run_time=0.38)

        div = Line(UP * 3.2, DOWN * 2.9, color=MUTE, stroke_width=1.5)

        # ── LEFT: Toy Tool ──
        toy_hdr = Text("TOY TOOL", weight=BOLD, color=ACCENT2).scale(0.58)

        # Shared interface chip (same on both sides)
        toy_iface = node("calculator(expr)", ACCENT2, w=3.6, h=0.72, fs=0.40)
        toy_iface_lbl = caption("schema identical", color=ACCENT2, fs=0.34)
        toy_iface_lbl.next_to(toy_iface, UP, buff=0.08)

        toy_in  = Arrow(LEFT * 1.5, toy_iface.get_left(),  buff=0.08,
                        color=ACCENT2, stroke_width=2, max_tip_length_to_length_ratio=0.18)
        toy_out = Arrow(toy_iface.get_right(), RIGHT * 1.5, buff=0.08,
                        color=ACCENT2, stroke_width=2, max_tip_length_to_length_ratio=0.18)

        toy_tags = VGroup(
            Text("predictable", color=ACCENT2).scale(0.40),
            Text("always works", color=ACCENT2).scale(0.40),
            Text("free",         color=ACCENT2).scale(0.40),
        ).arrange(DOWN, buff=0.22)

        toy_flow = VGroup(toy_in, toy_iface, toy_out)
        toy_flow.arrange(RIGHT, buff=0)
        toy_flow_tagged = VGroup(toy_iface_lbl, toy_flow)
        toy_tags.next_to(toy_flow, DOWN, buff=0.38)
        toy_col = VGroup(toy_hdr, toy_flow_tagged, toy_tags).arrange(DOWN, buff=0.35)

        # ── RIGHT: Real Tool ──
        real_hdr = Text("REAL TOOL", weight=BOLD, color=WARN).scale(0.58)

        real_iface = node("web_search(query)", WARN, w=3.6, h=0.72, fs=0.40)
        real_iface_lbl = caption("schema identical", color=WARN, fs=0.34)
        real_iface_lbl.next_to(real_iface, UP, buff=0.08)

        real_in  = Arrow(LEFT * 1.5, real_iface.get_left(),  buff=0.08,
                         color=WARN, stroke_width=2, max_tip_length_to_length_ratio=0.18)
        real_out = Arrow(real_iface.get_right(), RIGHT * 1.5, buff=0.08,
                         color=WARN, stroke_width=2, max_tip_length_to_length_ratio=0.18)

        real_flow = VGroup(real_in, real_iface, real_out)
        real_flow.arrange(RIGHT, buff=0)
        real_flow_tagged = VGroup(real_iface_lbl, real_flow)

        real_issues = VGroup(
            Text("slow  (network latency)", color=RED_ERR).scale(0.38),
            Text("can fail  (timeout / 429)", color=RED_ERR).scale(0.38),
            Text("costs money  (per call)",   color=RED_ERR).scale(0.38),
            Text("unstructured output",        color=RED_ERR).scale(0.38),
        ).arrange(DOWN, buff=0.20)

        real_col = VGroup(real_hdr, real_flow_tagged, real_issues).arrange(DOWN, buff=0.35)

        # Position columns
        toy_col.next_to(div,  LEFT,  buff=0.55)
        real_col.next_to(div, RIGHT, buff=0.55)
        VGroup(toy_col, div, real_col).move_to(ORIGIN + DOWN * 0.1)

        # Build left
        self.play(FadeIn(toy_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.35)
        self.play(FadeIn(toy_flow_tagged, shift=UP * 0.1, rate_func=smooth), run_time=0.45)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.08) for t in toy_tags],
                               lag_ratio=0.18), run_time=0.5)

        self.play(Create(div), run_time=0.25)

        # Build right
        self.play(FadeIn(real_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.35)
        self.play(FadeIn(real_flow_tagged, shift=UP * 0.1, rate_func=smooth), run_time=0.45)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.08) for t in real_issues],
                               lag_ratio=0.18), run_time=0.6)

        # Highlight: same schema top line
        hl_toy  = highlight_box(toy_iface,  color=ACCENT2, fill_opacity=0.18, buff=0.06)
        hl_real = highlight_box(real_iface, color=WARN,    fill_opacity=0.18, buff=0.06)
        punch = Text("same schema — the agent doesn't care which",
                     weight=BOLD, color=TEXT).scale(0.48)
        punch.to_edge(DOWN, buff=0.42)
        self.play(Create(hl_toy), Create(hl_real), run_time=0.4)
        self.play(FadeIn(punch, shift=UP * 0.15, rate_func=smooth), run_time=0.42)
        self.wait(1.8)


# ── 3. ToolSchemaAnatomy ───────────────────────────────────────────────────────

class ToolSchemaAnatomy(Scene):
    """
    Four parts of a tool schema the model reads.
    Full-frame cutaway.  ~10 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("Anatomy of a Tool Schema", weight=BOLD, color=TEXT).scale(0.62)
        title.to_edge(UP, buff=0.38)
        self.play(FadeIn(title, shift=DOWN * 0.14, rate_func=smooth), run_time=0.38)

        # Centre chip
        centre = node("TOOL SCHEMA", WARN, w=3.2, h=1.0, fs=0.52)
        centre.move_to(ORIGIN + DOWN * 0.1)
        self.play(FadeIn(centre, scale=0.88, rate_func=smooth), run_time=0.45)
        self.wait(0.2)

        # Four satellite parts: (label, sublabel, color, position)
        parts = [
            ("NAME",         "short, obvious",             ACCENT,  UP    * 2.3 + LEFT  * 3.5),
            ("DESCRIPTION",  "what + when, one sentence",  ACCENT2, UP    * 2.3 + RIGHT * 3.5),
            ("INPUT_SCHEMA", "args, types, required",      ACCENT,  DOWN  * 2.3 + LEFT  * 3.5),
            ("EXAMPLES",     "e.g. in the description",    WARN,    DOWN  * 2.3 + RIGHT * 3.5),
        ]

        part_nodes = []
        for label, sublabel, color, pos in parts:
            chip = node(label, color, w=3.2, h=0.80, fs=0.42)
            sub  = caption(sublabel, color=MUTE, fs=0.36)
            sub.next_to(chip, DOWN, buff=0.10)
            grp = VGroup(chip, sub)
            grp.move_to(pos)
            part_nodes.append((grp, chip, color, pos))

        for grp, chip, color, pos in part_nodes:
            # Arrow from centre to part
            arr = Arrow(
                centre.get_center(), pos,
                buff=0.55, color=color, stroke_width=1.8,
                max_tip_length_to_length_ratio=0.14,
            )
            self.play(
                Create(arr),
                FadeIn(grp, shift=(pos - ORIGIN) * 0.08, rate_func=smooth),
                run_time=0.48,
            )
            self.wait(0.15)

        # Glow + emphasise DESCRIPTION
        desc_grp = part_nodes[1][0]
        desc_chip = part_nodes[1][1]
        g = glow(desc_chip, color=ACCENT2, opacity=0.22, expansion=0.12)
        self.play(FadeIn(g), desc_chip[0].animate.set_stroke(color=ACCENT2, width=4),
                  run_time=0.4)

        # Eye icon side note
        eye_lbl = Text("the model reads this to plan", weight=BOLD, color=ACCENT2).scale(0.44)
        eye_lbl.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(eye_lbl, shift=UP * 0.14, rate_func=smooth), run_time=0.4)
        self.wait(1.8)


# ── 4. MultiToolChaining ───────────────────────────────────────────────────────

class MultiToolChaining(Scene):
    """
    The agent chains web_search -> reason -> write_file on its own.
    Full-frame cutaway.  ~10 s.  Signature Ep3 visual.
    """
    def construct(self):
        self.add(bg_deco())

        # Task chip at top
        task_chip = node(
            "search top frameworks, then save a comparison",
            WARN, w=9.0, h=0.85, fs=0.42,
        )
        task_chip.to_edge(UP, buff=0.55)
        self.play(FadeIn(task_chip, shift=DOWN * 0.15, rate_func=smooth), run_time=0.45)

        # Agent chip in centre-left
        agent = node("AGENT", ACCENT, w=2.2, h=0.88, fs=0.50)
        agent.move_to(LEFT * 3.2 + DOWN * 0.2)
        self.play(FadeIn(agent, scale=0.88, rate_func=smooth), run_time=0.38)

        # Arrow: task -> agent
        ta = Arrow(task_chip.get_bottom(), agent.get_top(),
                   buff=0.1, color=WARN, stroke_width=2,
                   max_tip_length_to_length_ratio=0.14)
        self.play(Create(ta), run_time=0.28)
        self.wait(0.15)

        # Step 1: web_search
        search_chip = node("web_search(\"AI frameworks\")", ACCENT, w=4.2, h=0.80, fs=0.38)
        search_chip.move_to(ORIGIN + UP * 0.5)
        a1 = Arrow(agent.get_right(), search_chip.get_left(),
                   buff=0.1, color=ACCENT, stroke_width=2,
                   max_tip_length_to_length_ratio=0.15)
        self.play(Create(a1), FadeIn(search_chip, shift=RIGHT * 0.1, rate_func=smooth),
                  run_time=0.48)

        results_lbl = caption("results: LangChain, AutoGen, CrewAI ...", color=ACCENT2, fs=0.38)
        results_lbl.next_to(search_chip, RIGHT, buff=0.22)
        self.play(FadeIn(results_lbl, shift=LEFT * 0.08, rate_func=smooth), run_time=0.38)
        self.wait(0.2)

        # Step 2: reason/synthesize (internal, shown as a think moment)
        think_chip = node("reason + synthesize", MUTE, w=3.4, h=0.72, fs=0.40)
        think_chip.move_to(ORIGIN + DOWN * 0.8)
        a2 = Arrow(search_chip.get_bottom(), think_chip.get_top(),
                   buff=0.1, color=MUTE, stroke_width=2,
                   max_tip_length_to_length_ratio=0.15)
        self.play(Create(a2), FadeIn(think_chip, shift=DOWN * 0.1, rate_func=smooth),
                  run_time=0.45)
        self.wait(0.2)

        # Step 3: write_file
        write_chip = node("write_file(\"comparison.txt\")", ACCENT2, w=4.2, h=0.80, fs=0.38)
        write_chip.move_to(ORIGIN + RIGHT * 3.8 + DOWN * 0.2)
        a3 = Arrow(think_chip.get_right(), write_chip.get_left(),
                   buff=0.1, color=ACCENT2, stroke_width=2,
                   max_tip_length_to_length_ratio=0.15)
        file_icon = Text("file", color=ACCENT2, weight=BOLD).scale(0.42)
        file_icon.next_to(write_chip, RIGHT, buff=0.18)
        self.play(Create(a3), FadeIn(write_chip, shift=RIGHT * 0.1, rate_func=smooth),
                  run_time=0.48)
        self.play(FadeIn(file_icon, shift=LEFT * 0.08), run_time=0.28)
        self.wait(0.2)

        # Caption reveal
        cap_line = Text(
            "you didn't say \"first search, then write\" — it planned that",
            color=WARN, weight=BOLD,
        ).scale(0.44)
        cap_line.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(cap_line, shift=UP * 0.15, rate_func=smooth), run_time=0.5)
        self.wait(1.8)


# ── 5. ErrorRecovery ───────────────────────────────────────────────────────────

class ErrorRecovery(Scene):
    """
    Two error-recovery sequences: rate-limited search, then path-traversal block.
    Transparent overlay over face-cam.  ~9 s.
    """
    def construct(self):
        # Terminal container (transparent-safe: no bg_deco)
        terminal = RoundedRectangle(
            corner_radius=0.28, width=13.2, height=7.4,
            fill_color=BG, fill_opacity=0.92,
            stroke_color=MUTE, stroke_width=1.5,
        )
        self.add(terminal)

        bar = Rectangle(
            width=13.2, height=0.36,
            fill_color=MUTE, fill_opacity=0.12, stroke_width=0,
        )
        bar.align_to(terminal, UP).shift(DOWN * 0.18)
        self.add(bar)

        FS = 0.37

        def row(marker, text, m_col, t_col=TEXT, is_err=False):
            m = Text(marker, color=m_col).scale(FS)
            t = Text(text,   color=t_col).scale(FS)
            r = VGroup(m, t).arrange(RIGHT, buff=0.20)
            r.is_err = is_err  # tag for pacing
            return r

        # Section A: rate-limit recovery
        sec_a = Text("— search rate-limited, agent adapts —",
                     color=MUTE).scale(FS * 0.85)
        sec_a.is_err = False

        lines_a = [
            row("tool",    "web_search(\"agentic AI trends\")",       ACCENT),
            row("observe", "ERROR: rate limited (HTTP 429)",          RED_ERR, RED_ERR, is_err=True),
            row("think",   "search failed, try a narrower query",     WARN),
            row("tool",    "web_search(\"agentic AI 2026\")",         ACCENT),
            row("observe", "3 results returned",                      ACCENT2, ACCENT2),
            row("done",    "recovered",                               ACCENT2, ACCENT2),
        ]

        # Section B: path-traversal block
        sec_b = Text("— file write blocked by sandbox —",
                     color=MUTE).scale(FS * 0.85)
        sec_b.is_err = False

        lines_b = [
            row("tool",    "write_file(\"/etc/passwd\", ...)",        ACCENT),
            row("observe", "ERROR: path outside safe directory",      RED_ERR, RED_ERR, is_err=True),
            row("think",   "blocked — I'll write to a safe path",     WARN),
            row("tool",    "write_file(\"output.txt\", ...)",         ACCENT),
            row("observe", "file written to workspace",               ACCENT2, ACCENT2),
        ]

        all_rows = [sec_a] + lines_a + [sec_b] + lines_b
        stack = VGroup(*all_rows)
        stack.arrange(DOWN, buff=0.19, aligned_edge=LEFT)
        stack.move_to(terminal.get_center()).shift(LEFT * 0.2 + DOWN * 0.1)

        for r in all_rows:
            self.play(FadeIn(r, shift=RIGHT * 0.06, rate_func=smooth), run_time=0.30)
            self.wait(0.52 if getattr(r, "is_err", False) else 0.28)

        self.wait(1.5)


# ── 6. CostGuardrail ───────────────────────────────────────────────────────────

class CostGuardrail(Scene):
    """
    Runaway loop vs guardrailed loop: max_steps caps the spend.
    Full-frame cutaway.  ~9 s.
    """
    def construct(self):
        self.add(bg_deco())

        title = Text("Every tool call costs money.", weight=BOLD, color=TEXT).scale(0.62)
        title.to_edge(UP, buff=0.38)
        self.play(FadeIn(title, shift=DOWN * 0.14, rate_func=smooth), run_time=0.38)

        div = Line(UP * 3.0, DOWN * 3.0, color=MUTE, stroke_width=1.5)

        # ── LEFT: no guardrails ──
        left_hdr = Text("NO GUARDRAILS", weight=BOLD, color=WARN).scale(0.56)

        # Spinning loop (three small chips in a triangle)
        t1 = node("think", WARN, w=1.8, h=0.65, fs=0.38).move_to(UP * 1.0 + LEFT * 0.3)
        t2 = node("call",  WARN, w=1.8, h=0.65, fs=0.38).move_to(DOWN * 0.5 + RIGHT * 0.9)
        t3 = node("obs",   WARN, w=1.8, h=0.65, fs=0.38).move_to(DOWN * 0.5 + LEFT * 1.5)
        loop_grp = VGroup(t1, t2, t3)
        loop_grp.scale(0.82)

        c1 = CurvedArrow(t1.get_right(), t2.get_top(),   angle=-PI/3, color=WARN, stroke_width=2)
        c2 = CurvedArrow(t2.get_left(),  t3.get_right(), angle=-PI/3, color=WARN, stroke_width=2)
        c3 = CurvedArrow(t3.get_top(),   t1.get_left(),  angle=-PI/3, color=WARN, stroke_width=2)

        # Cost counter — plain Text to avoid LaTeX dependency
        cost_txt = Text("$ 0.06", color=RED_ERR, weight=BOLD).scale(0.72)

        left_content = VGroup(loop_grp, cost_txt).arrange(DOWN, buff=0.55)
        left_col = VGroup(left_hdr, left_content).arrange(DOWN, buff=0.42)

        # ── RIGHT: guardrailed ──
        right_hdr = Text("max_steps = 10", weight=BOLD, color=ACCENT2).scale(0.56)

        r1 = node("think", ACCENT2, w=1.8, h=0.65, fs=0.38).move_to(UP * 1.0 + LEFT * 0.3)
        r2 = node("call",  ACCENT2, w=1.8, h=0.65, fs=0.38).move_to(DOWN * 0.5 + RIGHT * 0.9)
        r3 = node("obs",   ACCENT2, w=1.8, h=0.65, fs=0.38).move_to(DOWN * 0.5 + LEFT * 1.5)
        rloop_grp = VGroup(r1, r2, r3)
        rloop_grp.scale(0.82)

        step_lbl = Text("1 / 10", weight=BOLD, color=ACCENT2).scale(0.58)
        step_lbl.next_to(rloop_grp, DOWN, buff=0.18)

        right_content = VGroup(rloop_grp, step_lbl).arrange(DOWN, buff=0.55)
        right_col = VGroup(right_hdr, right_content).arrange(DOWN, buff=0.42)

        left_col.next_to(div,  LEFT,  buff=0.65)
        right_col.next_to(div, RIGHT, buff=0.65)
        VGroup(left_col, div, right_col).move_to(ORIGIN + DOWN * 0.1)

        # Build left
        self.play(FadeIn(left_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.35)
        self.play(LaggedStart(FadeIn(t1), FadeIn(t2), FadeIn(t3), lag_ratio=0.2), run_time=0.5)
        self.play(Create(c1), Create(c2), Create(c3), run_time=0.4)
        self.play(FadeIn(cost_txt), run_time=0.3)

        # Cost climbing: $0.06 → $0.60 → $6.00 → flash "$$$"
        for new_val in ("$ 0.60", "$ 6.00"):
            new_t = Text(new_val, color=RED_ERR, weight=BOLD).scale(0.72)
            new_t.move_to(cost_txt.get_center())
            self.play(ReplacementTransform(cost_txt, new_t), run_time=0.55)
            cost_txt = new_t

        overflow = Text("$$$", weight=BOLD, color=RED_ERR).scale(1.1)
        overflow.move_to(cost_txt.get_center())
        self.play(FadeOut(cost_txt), FadeIn(overflow, scale=0.85), run_time=0.35)

        self.play(Create(div), run_time=0.25)

        # Build right
        self.play(FadeIn(right_hdr, shift=DOWN * 0.1, rate_func=smooth), run_time=0.35)
        self.play(LaggedStart(FadeIn(r1), FadeIn(r2), FadeIn(r3), lag_ratio=0.2), run_time=0.5)

        # Tick 1→10 (show 3 ticks for pacing)
        for n in ("3 / 10", "7 / 10", "10 / 10"):
            new_lbl = Text(n, weight=BOLD, color=ACCENT2).scale(0.58)
            new_lbl.move_to(step_lbl.get_center())
            self.play(ReplacementTransform(step_lbl, new_lbl), run_time=0.28)
            step_lbl = new_lbl
            self.wait(0.12)

        stop_chip = node("STOP", ACCENT2, w=2.4, h=0.72, fs=0.50)
        stop_chip.next_to(rloop_grp, DOWN, buff=0.22)
        self.play(FadeOut(step_lbl), FadeIn(stop_chip, shift=UP * 0.14, scale=0.9), run_time=0.42)

        # Bottom caption
        cap = Text("the cap is the budget", weight=BOLD, color=ACCENT2).scale(0.50)
        cap.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(cap, shift=UP * 0.14, rate_func=smooth), run_time=0.42)
        self.wait(1.8)


# ── 7. ToolMistakes ────────────────────────────────────────────────────────────

class ToolMistakes(Scene):
    """
    6 tool-design mistakes, each with wrong vs better code + a principle line.
    Full-frame cutaway.  ~130 s (2 min 10 s).

    Timing breakdown:
      Intro            5.3 s
      6 x mistake    ~19.7 s  = 118.2 s
      Summary          6.4 s
      Total           ~130  s
    """

    _MISTAKES = [
        {
            "num": "#1",  "title": "Vague Schema",
            "wrong":  ["def do_stuff(input: any):",
                       '    """Does things. Returns stuff."""'],
            "wrong_note": "Model: when do I use this? What do I pass?",
            "better": ["def fetch_rows(query: str, param: str):",
                       '    """SQL lookup. Returns rows as JSON."""'],
            "better_note": "Model knows exactly when and how to call it.",
            "principle": "The description is what the model plans from.",
        },
        {
            "num": "#2",  "title": "Overloaded Tool",
            "wrong":  ["def do_everything(action, input=None,",
                       "                  path=None, endpoint=None):",
                       "    # search + file I/O + API + calc - all one fn"],
            "wrong_note": "Model is confused about what to use when.",
            "better": ["web_search(query)       read_file(path)",
                       "write_file(path)        calculator(expr)"],
            "better_note": "One tool, one job. Each schema is unmistakable.",
            "principle": "Specific tools = clear decisions.",
        },
        {
            "num": "#3",  "title": "No Error Handling",
            "wrong":  ["def call_api(endpoint):",
                       "    resp = requests.get(endpoint)",
                       "    return resp.json()   # raises on 429, timeout"],
            "wrong_note": "Tool crashes - agent crashes - task fails.",
            "better": ["except requests.exceptions.Timeout:",
                       '    return {"error": "timed out after 10s"}'],
            "better_note": "Agent reads the error and decides what to do.",
            "principle": "Tools return errors. Agents adapt.",
        },
        {
            "num": "#4",  "title": "No Rate Limits",
            "wrong":  ["def web_search(query, max_results=None):",
                       "    # no cap - model requests 100 results",
                       "    # no step limit - agent loops forever"],
            "wrong_note": "100 searches. 1000 files. Costs spiral.",
            "better": ["SEARCH_MAX_RESULTS = 5",
                       "FILE_MAX_SIZE_MB   = 10",
                       "MAX_STEPS          = 10"],
            "better_note": "Hard limits defined once, enforced everywhere.",
            "principle": "Your limits are your budget.",
        },
        {
            "num": "#5",  "title": "Hardcoded Secrets",
            "wrong":  ['api_key = "sk-ant-api03-abc123..."',
                       "# committed to git, shared, leaked"],
            "wrong_note": "Code shared once = key compromised forever.",
            "better": ['api_key = os.environ.get("ANTHROPIC_API_KEY")',
                       "# or: load_dotenv()  ->  reads from .env"],
            "better_note": ".env is gitignored. Key stays out of source.",
            "principle": "If the code leaks, the key leaks.",
        },
        {
            "num": "#6",  "title": "No Logging",
            "wrong":  ["# tool called...",
                       "# something went wrong...",
                       "# no trace, no args, no result recorded"],
            "wrong_note": "No idea what happened or why it failed.",
            "better": ['print(f"tool   * {name}({str(args)[:60]})")',
                       "result = run_tool(name, args)",
                       'print(f"result * {result[:80]}")'],
            "better_note": "Every call + result visible. Debug in 60s.",
            "principle": "You can't debug what you can't see.",
        },
    ]

    def construct(self):
        self.add(bg_deco())

        # ── INTRO (5.3 s) ─────────────────────────────────────────────────────
        heading = Text("6 Ways to Design Tools Wrong", weight=BOLD, color=TEXT).scale(0.72)
        heading.move_to(UP * 0.5)
        ul_intro = Line(
            heading.get_left()  + DOWN * 0.04,
            heading.get_right() + DOWN * 0.04,
            color=ACCENT, stroke_width=3,
        ).next_to(heading, DOWN, buff=0.10)
        sub = Text("Recognize these. Avoid them.", color=MUTE).scale(0.50)
        sub.next_to(ul_intro, DOWN, buff=0.45)

        self.play(FadeIn(heading, shift=DOWN * 0.14, rate_func=smooth), run_time=0.50)
        self.play(Create(ul_intro), run_time=0.32)
        self.play(FadeIn(sub, shift=UP * 0.12, rate_func=smooth), run_time=0.40)
        self.wait(3.58)
        self.play(FadeOut(VGroup(heading, ul_intro, sub)), run_time=0.50)
        # 0.50+0.32+0.40+3.58+0.50 = 5.30 s

        # ── 6 MISTAKE CARDS (6 x ~19.7 s = 118.2 s) ──────────────────────────
        for m in self._MISTAKES:
            self._show_mistake(m)

        # ── SUMMARY (6.4 s) ───────────────────────────────────────────────────
        sum_title = Text("The 6 Rules", weight=BOLD, color=TEXT).scale(0.65)
        sum_title.to_edge(UP, buff=0.42)
        rules = VGroup(*[
            Text(f"  {i+1}.  {t}", color=ACCENT2).scale(0.45)
            for i, t in enumerate([
                "Precise schema descriptions",
                "One tool, one job",
                "Return errors, never raise",
                "Hard limits on every boundary",
                "Secrets from the environment",
                "Log every call and result",
            ])
        ]).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        rules.next_to(sum_title, DOWN, buff=0.42)

        self.play(FadeIn(sum_title, shift=DOWN * 0.12, rate_func=smooth), run_time=0.42)
        for r in rules:
            self.play(FadeIn(r, shift=UP * 0.08, rate_func=smooth), run_time=0.28)
            self.wait(0.22)
        self.wait(3.00)
        # 0.42 + 6*(0.28+0.22) + 3.00 = 6.42 s

    def _show_mistake(self, m):
        """Render one mistake card.  Target: ~19.7 s per card."""
        FS_CODE      = 0.36
        FS_NOTE      = 0.40
        FS_PRINCIPLE = 0.50

        # ── Build wrong block ───────────────────────────────────────────────
        wrong_hdr = Text("x  Wrong", weight=BOLD, color=RED_ERR).scale(0.46)
        wrong_code = VGroup(*[
            Text(line, color=RED_ERR).scale(FS_CODE)
            for line in m["wrong"]
        ]).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        wrong_note = Text(m["wrong_note"], color=MUTE).scale(FS_NOTE)
        wrong_inner = VGroup(wrong_hdr, wrong_code, wrong_note)
        wrong_inner.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        wrong_bg = SurroundingRectangle(
            wrong_inner, color=RED_ERR, fill_color=RED_ERR,
            fill_opacity=0.07, stroke_width=1.2, buff=0.22, corner_radius=0.14,
        )

        # ── Build better block ──────────────────────────────────────────────
        better_hdr = Text("ok  Better", weight=BOLD, color=ACCENT2).scale(0.46)
        better_code = VGroup(*[
            Text(line, color=ACCENT2).scale(FS_CODE)
            for line in m["better"]
        ]).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        better_note = Text(m["better_note"], color=MUTE).scale(FS_NOTE)
        better_inner = VGroup(better_hdr, better_code, better_note)
        better_inner.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        better_bg = SurroundingRectangle(
            better_inner, color=ACCENT2, fill_color=ACCENT2,
            fill_opacity=0.07, stroke_width=1.2, buff=0.22, corner_radius=0.14,
        )

        # ── Build title ─────────────────────────────────────────────────────
        num_txt   = Text(m["num"],   weight=BOLD, color=MUTE).scale(0.46)
        title_txt = Text(m["title"], weight=BOLD, color=WARN).scale(0.64)
        title_row = VGroup(num_txt, title_txt).arrange(RIGHT, buff=0.28)
        ul = Line(
            title_row.get_left()  + DOWN * 0.04,
            title_row.get_right() + DOWN * 0.04,
            color=WARN, stroke_width=2,
        ).next_to(title_row, DOWN, buff=0.14)
        title_block = VGroup(title_row, ul)

        # ── Build principle ─────────────────────────────────────────────────
        principle = Text(m["principle"], weight=BOLD, color=TEXT).scale(FS_PRINCIPLE)

        # ── Stack & centre the whole card ───────────────────────────────────
        wrong_panel  = VGroup(wrong_bg,  wrong_inner)
        better_panel = VGroup(better_bg, better_inner)
        card = VGroup(title_block, wrong_panel, better_panel, principle)
        card.arrange(DOWN, buff=0.35)
        card.move_to(ORIGIN)

        # ── Animate — title (3.03 s) ────────────────────────────────────────
        self.play(FadeIn(title_row, shift=DOWN * 0.12, rate_func=smooth), run_time=0.45)
        self.play(Create(ul), run_time=0.28)
        self.wait(2.30)

        # ── Animate — wrong block (6.58 s) ──────────────────────────────────
        self.play(FadeIn(wrong_bg, rate_func=smooth), run_time=0.30)
        self.play(FadeIn(wrong_hdr, shift=RIGHT * 0.08, rate_func=smooth), run_time=0.35)
        self.play(
            LaggedStart(*[FadeIn(l, shift=RIGHT * 0.06, rate_func=smooth)
                          for l in wrong_code], lag_ratio=0.18),
            run_time=0.55,
        )
        self.play(FadeIn(wrong_note, shift=UP * 0.06, rate_func=smooth), run_time=0.38)
        self.wait(5.00)

        # ── Animate — better block (6.08 s) ─────────────────────────────────
        self.play(FadeIn(better_bg, rate_func=smooth), run_time=0.30)
        self.play(FadeIn(better_hdr, shift=RIGHT * 0.08, rate_func=smooth), run_time=0.35)
        self.play(
            LaggedStart(*[FadeIn(l, shift=RIGHT * 0.06, rate_func=smooth)
                          for l in better_code], lag_ratio=0.18),
            run_time=0.55,
        )
        self.play(FadeIn(better_note, shift=UP * 0.06, rate_func=smooth), run_time=0.38)
        self.wait(4.50)

        # ── Animate — principle (3.45 s) ────────────────────────────────────
        self.play(FadeIn(principle, shift=UP * 0.14, rate_func=smooth), run_time=0.45)
        self.wait(3.00)

        # ── Fade out (0.55 s) ────────────────────────────────────────────────
        self.play(FadeOut(VGroup(
            title_row, ul,
            wrong_bg, wrong_inner,
            better_bg, better_inner,
            principle,
        )), run_time=0.55)
        # card total: 3.03+6.58+6.08+3.45+0.55 = 19.69 s


# ── 8. FrameworkDecision ───────────────────────────────────────────────────────

class FrameworkDecision(Scene):
    """
    "Do you need a framework?" — question -> honest answer -> what they add ->
    the warning -> the foundation stack.
    Full-frame cutaway.  ~62 s (1 min 2 s).

    Timing:
      Intro question        8.0 s
      Honest answer         4.5 s
      Frameworks wrap       6.5 s
      5 capabilities       20.5 s
      The warning          10.0 s
      Foundation stack     12.5 s
      Total                62.0 s
    """

    def construct(self):
        self.add(bg_deco())

        # ── 1. INTRO QUESTION (8.0 s) ─────────────────────────────────────────
        recap = Text(
            "Ep 2: built the loop.   Ep 3: wired real tools.",
            color=MUTE,
        ).scale(0.46)
        question = Text(
            "Do you need a framework now?",
            weight=BOLD, color=TEXT,
        ).scale(0.72)
        VGroup(recap, question).arrange(DOWN, buff=0.55).move_to(ORIGIN)

        self.play(FadeIn(recap, shift=DOWN * 0.10, rate_func=smooth), run_time=0.45)
        self.wait(0.50)
        self.play(FadeIn(question, shift=DOWN * 0.14, rate_func=smooth), run_time=0.50)
        self.wait(6.05)
        self.play(FadeOut(VGroup(recap, question)), run_time=0.50)
        # 0.45+0.50+0.50+6.05+0.50 = 8.00 s

        # ── 2. HONEST ANSWER (4.5 s) ──────────────────────────────────────────
        answer = Text("Probably, yes.", weight=BOLD, color=WARN).scale(1.0)
        sub    = Text("but now you'll use it right.", color=ACCENT2).scale(0.52)
        VGroup(answer, sub).arrange(DOWN, buff=0.42).move_to(ORIGIN)

        self.play(FadeIn(answer, scale=0.85, rate_func=smooth), run_time=0.50)
        self.play(FadeIn(sub, shift=UP * 0.10, rate_func=smooth), run_time=0.40)
        self.wait(3.10)
        self.play(FadeOut(VGroup(answer, sub)), run_time=0.50)
        # 0.50+0.40+3.10+0.50 = 4.50 s

        # ── 3. FRAMEWORKS WRAP YOUR LOOP (6.5 s) ──────────────────────────────
        loop_chip = node("your loop", ACCENT, w=2.8, h=0.88, fs=0.46)
        loop_chip.move_to(DOWN * 0.55)

        fw_chips = VGroup(
            node("LangGraph",     MUTE, w=2.3, h=0.70, fs=0.40),
            node("AutoGen",       MUTE, w=2.3, h=0.70, fs=0.40),
            node("Anthropic SDK", MUTE, w=2.3, h=0.70, fs=0.40),
        ).arrange(RIGHT, buff=0.50)
        fw_chips.move_to(UP * 1.25)

        wrapper = SurroundingRectangle(
            VGroup(fw_chips, loop_chip),
            color=ACCENT2, stroke_width=1.5, buff=0.48, corner_radius=0.22,
        )
        wrap_cap = Text(
            "they wrap the loop you already understand",
            color=ACCENT2,
        ).scale(0.44)
        wrap_cap.to_edge(DOWN, buff=0.45)

        self.play(FadeIn(loop_chip, scale=0.88, rate_func=smooth), run_time=0.38)
        self.play(
            LaggedStart(*[FadeIn(c, shift=DOWN * 0.12, rate_func=smooth) for c in fw_chips],
                        lag_ratio=0.22),
            run_time=0.60,
        )
        self.play(Create(wrapper), run_time=0.45)
        self.play(FadeIn(wrap_cap, shift=UP * 0.10, rate_func=smooth), run_time=0.38)
        self.wait(4.19)
        self.play(FadeOut(VGroup(loop_chip, fw_chips, wrapper, wrap_cap)), run_time=0.50)
        # 0.38+0.60+0.45+0.38+4.19+0.50 = 6.50 s

        # ── 4. WHAT FRAMEWORKS ADD (20.5 s) ───────────────────────────────────
        fw_title = Text("What frameworks add:", weight=BOLD, color=TEXT).scale(0.60)
        fw_title.to_edge(UP, buff=0.45)
        self.play(FadeIn(fw_title, shift=DOWN * 0.12, rate_func=smooth), run_time=0.38)

        CAPS = [
            ("State persistence",   "multi-turn conversations, long-running agents"),
            ("Retries + fallbacks",  "if a tool fails, try again or pivot"),
            ("Observability",        "logging, tracing, debugging"),
            ("Structured output",    "guaranteed format on the final answer"),
            ("Multiple agents",      "coordination, message passing"),
        ]

        cap_rows = []
        for cap_title, cap_detail in CAPS:
            t   = Text(cap_title,  weight=BOLD, color=ACCENT2).scale(0.48)
            d   = Text(cap_detail, color=MUTE).scale(0.40)
            row = VGroup(t, d).arrange(RIGHT, buff=0.28)
            cap_rows.append(row)

        cap_group = VGroup(*cap_rows).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        cap_group.next_to(fw_title, DOWN, buff=0.50)

        for row in cap_rows:
            self.play(FadeIn(row, shift=UP * 0.10, rate_func=smooth), run_time=0.42)
            self.wait(3.20)

        self.wait(1.52)
        self.play(FadeOut(VGroup(fw_title, cap_group)), run_time=0.50)
        # 0.38 + 5*(0.42+3.20) + 1.52 + 0.50 = 20.50 s

        # ── 5. THE WARNING (10.0 s) ────────────────────────────────────────────
        warn_box = RoundedRectangle(
            corner_radius=0.22, width=10.5, height=0.92,
            fill_color=WARN, fill_opacity=0.12,
            stroke_color=WARN, stroke_width=1.8,
        )
        warn_box.move_to(UP * 1.3)
        warn_txt = Text("But here's the thing.", weight=BOLD, color=WARN).scale(0.60)
        warn_txt.move_to(warn_box.get_center())

        simple_txt = Text(
            "You don't need a framework for a simple agent.",
            color=TEXT,
        ).scale(0.48)
        simple_txt.next_to(warn_box, DOWN, buff=0.42)

        blackbox_txt = Text(
            "Use it before you understand it  =  black box surprises.",
            color=RED_ERR,
        ).scale(0.46)
        blackbox_txt.next_to(simple_txt, DOWN, buff=0.30)

        self.play(
            FadeIn(warn_box, rate_func=smooth),
            FadeIn(warn_txt, shift=DOWN * 0.08, rate_func=smooth),
            run_time=0.45,
        )
        self.wait(0.50)
        self.play(FadeIn(simple_txt, shift=UP * 0.10, rate_func=smooth), run_time=0.42)
        self.wait(1.50)
        self.play(FadeIn(blackbox_txt, shift=UP * 0.10, rate_func=smooth), run_time=0.42)
        self.wait(6.21)
        self.play(FadeOut(VGroup(warn_box, warn_txt, simple_txt, blackbox_txt)), run_time=0.50)
        # 0.45+0.50+0.42+1.50+0.42+6.21+0.50 = 10.00 s

        # ── 6. THE FOUNDATION (12.5 s) ─────────────────────────────────────────
        found_title = Text("The foundation.", weight=BOLD, color=TEXT).scale(0.62)
        found_title.to_edge(UP, buff=0.42)
        self.play(FadeIn(found_title, shift=DOWN * 0.12, rate_func=smooth), run_time=0.38)

        LAYER_W  = 7.0
        LAYER_H  = 0.75
        Y_BOTTOM = -1.30

        LAYERS = [
            ("THE LOOP",   ACCENT,  "the engine"),
            ("REAL TOOLS", ACCENT2, "the hands"),
            ("GUARDRAILS", WARN,    "the safety net"),
        ]

        stack_mobs = []
        for i, (lyr_label, lyr_color, lyr_sub) in enumerate(LAYERS):
            box = Rectangle(
                width=LAYER_W - i * 0.28, height=LAYER_H,
                fill_color=lyr_color, fill_opacity=0.16,
                stroke_color=lyr_color, stroke_width=2,
            )
            lbl = Text(lyr_label, weight=BOLD, color=lyr_color).scale(0.44)
            sub = Text(lyr_sub,   color=MUTE).scale(0.34)
            VGroup(lbl, sub).arrange(RIGHT, buff=0.26).move_to(box.get_center())
            layer = VGroup(box, lbl, sub)
            layer.move_to(UP * (Y_BOTTOM + i * (LAYER_H + 0.04)))
            stack_mobs.append(layer)

        fw_box = Rectangle(
            width=LAYER_W - 3 * 0.28, height=LAYER_H,
            fill_color=MUTE, fill_opacity=0.07,
            stroke_color=MUTE, stroke_width=1.2,
        )
        fw_lbl = Text("FRAMEWORKS +",              weight=BOLD, color=MUTE).scale(0.42)
        fw_sub = Text("everything else, optional", color=MUTE).scale(0.34)
        VGroup(fw_lbl, fw_sub).arrange(RIGHT, buff=0.26).move_to(fw_box.get_center())
        fw_layer = VGroup(fw_box, fw_lbl, fw_sub)
        fw_layer.move_to(UP * (Y_BOTTOM + 3 * (LAYER_H + 0.04)))

        p1 = Text(
            "The loop, tools, and guardrails are the foundation.",
            weight=BOLD, color=TEXT,
        ).scale(0.44)
        p2 = Text("Everything else is layers on top.", color=ACCENT2).scale(0.44)
        principle = VGroup(p1, p2).arrange(DOWN, buff=0.20)
        principle.next_to(stack_mobs[0], DOWN, buff=0.55)

        for layer in stack_mobs:
            self.play(FadeIn(layer, shift=UP * 0.12, rate_func=smooth), run_time=0.42)
            self.wait(0.40)

        self.play(FadeIn(fw_layer, shift=UP * 0.12, rate_func=smooth), run_time=0.42)
        self.wait(0.60)
        self.play(FadeIn(principle, shift=UP * 0.12, rate_func=smooth), run_time=0.50)
        self.wait(8.14)
        # 0.38 + 3*(0.42+0.40) + (0.42+0.60) + 0.50+8.14 = 12.50 s

        # Grand total: 8.00+4.50+6.50+20.50+10.00+12.50 = 62.00 s


# ── 9. Ep03Outro ───────────────────────────────────────────────────────────────

class Ep03Outro(Scene):
    """
    Episode 3 closing stamp: recap chips → neat-idea-to-production bridge →
    tutorial-vs-tool punchline.
    Full-frame cutaway.  ~25 s.

    Timing:
      Recap chips          8.0 s
      Neat idea -> prod   10.0 s
      Tutorial -> Tool     7.0 s
      Total               25.0 s
    """

    def construct(self):
        self.add(bg_deco())

        # ── 1. RECAP (8.0 s) ─────────────────────────────────────────────────
        heading = Text("Episode 3.", weight=BOLD, color=TEXT).scale(0.80)
        heading.move_to(UP * 2.2)
        ul = Line(
            heading.get_left()  + DOWN * 0.04,
            heading.get_right() + DOWN * 0.04,
            color=ACCENT, stroke_width=3,
        ).next_to(heading, DOWN, buff=0.14)

        CHIPS = [
            ("Real tools",      ACCENT),
            ("Error handling",  RED_ERR),
            ("Cost awareness",  WARN),
            ("Guardrails",      ACCENT2),
        ]
        chip_list = [node(lbl, col, w=3.0, h=0.72, fs=0.42) for lbl, col in CHIPS]
        row1 = VGroup(chip_list[0], chip_list[1]).arrange(RIGHT, buff=0.45)
        row2 = VGroup(chip_list[2], chip_list[3]).arrange(RIGHT, buff=0.45)
        chip_grid = VGroup(row1, row2).arrange(DOWN, buff=0.35)
        chip_grid.next_to(ul, DOWN, buff=0.52)

        sub_cap = caption("search · files · APIs · the full stack", color=MUTE, fs=0.40)
        sub_cap.next_to(chip_grid, DOWN, buff=0.38)

        self.play(FadeIn(heading, shift=DOWN * 0.14, rate_func=smooth), run_time=0.40)
        self.play(Create(ul), run_time=0.30)
        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.10, rate_func=smooth) for c in chip_list],
                        lag_ratio=0.22),
            run_time=1.50,
        )
        self.play(FadeIn(sub_cap, shift=UP * 0.08, rate_func=smooth), run_time=0.38)
        self.wait(4.92)
        self.play(FadeOut(VGroup(heading, ul, chip_grid, sub_cap)), run_time=0.50)
        # 0.40+0.30+1.50+0.38+4.92+0.50 = 8.00 s

        # ── 2. THE BRIDGE (10.0 s) ────────────────────────────────────────────
        neat_chip = node("neat idea",              MUTE,    w=2.8, h=0.85, fs=0.46)
        ship_chip = node("shipping in production", ACCENT2, w=3.8, h=0.85, fs=0.40)
        VGroup(neat_chip, ship_chip).arrange(RIGHT, buff=2.2).move_to(ORIGIN)

        bridge = Arrow(
            neat_chip.get_right(), ship_chip.get_left(),
            buff=0.12, color=ACCENT, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.12,
        )
        bridge_cap = Text("the stuff in between", weight=BOLD, color=TEXT).scale(0.52)
        bridge_cap.next_to(bridge, DOWN, buff=0.30)

        self.play(FadeIn(neat_chip, shift=RIGHT * 0.10, rate_func=smooth), run_time=0.40)
        self.wait(0.30)
        self.play(Create(bridge), run_time=0.55)
        self.play(FadeIn(ship_chip, shift=LEFT * 0.10, rate_func=smooth), run_time=0.40)
        self.play(FadeIn(bridge_cap, shift=UP * 0.08, rate_func=smooth), run_time=0.38)
        self.wait(7.47)
        self.play(FadeOut(VGroup(neat_chip, bridge, ship_chip, bridge_cap)), run_time=0.50)
        # 0.40+0.30+0.55+0.40+0.38+7.47+0.50 = 10.00 s

        # ── 3. TUTORIAL -> TOOL (7.0 s) ───────────────────────────────────────
        tutorial_txt = Text("tutorial.",  color=MUTE).scale(0.72)
        arrow_sep    = Text("->",  weight=BOLD, color=ACCENT).scale(0.88)
        tool_txt     = Text("tool.", weight=BOLD, color=ACCENT2).scale(1.10)
        main_row = VGroup(tutorial_txt, arrow_sep, tool_txt).arrange(RIGHT, buff=0.30)
        main_row.move_to(UP * 0.3)

        diff_cap = Text(
            "not just how it works — how to make it work for real.",
            color=MUTE,
        ).scale(0.44)
        diff_cap.next_to(main_row, DOWN, buff=0.55)

        self.play(FadeIn(tutorial_txt, shift=RIGHT * 0.10, rate_func=smooth), run_time=0.40)
        self.wait(0.22)
        self.play(FadeIn(arrow_sep, rate_func=smooth), run_time=0.25)
        self.play(FadeIn(tool_txt, scale=0.85, rate_func=smooth), run_time=0.45)
        self.play(FadeIn(diff_cap, shift=UP * 0.10, rate_func=smooth), run_time=0.38)
        self.wait(5.30)
        # 0.40+0.22+0.25+0.45+0.38+5.30 = 7.00 s

        # Grand total: 8.00+10.00+7.00 = 25.00 s


# ── 10. Ep04Teaser ─────────────────────────────────────────────────────────────

class Ep04Teaser(Scene):
    """
    Teaser for Episode 4: multi-agent systems.
    Full-frame cutaway.  ~19 s.

    Timing:
      Title card           3.0 s
      Three agents + links 9.0 s
      Closing line         7.0 s
      Total               19.0 s
    """

    def construct(self):
        self.add(bg_deco())

        # ── 1. TITLE CARD (3.0 s) ─────────────────────────────────────────────
        next_ep  = Text("Next episode.", color=MUTE).scale(0.46)
        ep4_line = Text(
            "Episode 4: Multi-Agent Systems", weight=BOLD, color=TEXT,
        ).scale(0.68)
        VGroup(next_ep, ep4_line).arrange(DOWN, buff=0.35).move_to(ORIGIN)

        self.play(FadeIn(next_ep,  shift=DOWN * 0.10, rate_func=smooth), run_time=0.35)
        self.wait(0.20)
        self.play(FadeIn(ep4_line, shift=DOWN * 0.14, rate_func=smooth), run_time=0.45)
        self.wait(1.50)
        self.play(FadeOut(VGroup(next_ep, ep4_line)), run_time=0.50)
        # 0.35+0.20+0.45+1.50+0.50 = 3.00 s

        # ── 2. THREE AGENTS + CONNECTIONS (9.0 s) ─────────────────────────────
        planner   = node("PLANNER",   ACCENT,  w=2.6, h=0.85, fs=0.46)
        search    = node("SEARCH",    ACCENT2, w=2.6, h=0.85, fs=0.46)
        synthesis = node("SYNTHESIS", WARN,    w=2.6, h=0.85, fs=0.46)

        planner.move_to(UP * 1.40)
        search.move_to(DOWN * 0.75 + LEFT  * 3.00)
        synthesis.move_to(DOWN * 0.75 + RIGHT * 3.00)

        plan_lbl = caption("planning",  color=MUTE, fs=0.36)
        srch_lbl = caption("search",    color=MUTE, fs=0.36)
        syn_lbl  = caption("synthesis", color=MUTE, fs=0.36)
        plan_lbl.next_to(planner,   UP,   buff=0.16)
        srch_lbl.next_to(search,    DOWN, buff=0.16)
        syn_lbl.next_to(synthesis,  DOWN, buff=0.16)

        a1 = Arrow(
            planner.get_bottom(), search.get_top(),
            buff=0.12, color=ACCENT, stroke_width=2,
            max_tip_length_to_length_ratio=0.14,
        )
        a2 = Arrow(
            planner.get_bottom(), synthesis.get_top(),
            buff=0.12, color=ACCENT, stroke_width=2,
            max_tip_length_to_length_ratio=0.14,
        )
        a3 = Arrow(
            search.get_right(), synthesis.get_left(),
            buff=0.12, color=MUTE, stroke_width=1.8,
            max_tip_length_to_length_ratio=0.14,
        )

        agent_cap = caption("how they talk to each other", color=MUTE, fs=0.40)
        agent_cap.next_to(VGroup(srch_lbl, syn_lbl), DOWN, buff=0.42)

        self.play(
            LaggedStart(
                FadeIn(planner,   shift=DOWN  * 0.10, rate_func=smooth),
                FadeIn(search,    shift=RIGHT * 0.10, rate_func=smooth),
                FadeIn(synthesis, shift=LEFT  * 0.10, rate_func=smooth),
                lag_ratio=0.30,
            ),
            run_time=1.20,
        )
        self.play(
            LaggedStart(
                FadeIn(plan_lbl, rate_func=smooth),
                FadeIn(srch_lbl, rate_func=smooth),
                FadeIn(syn_lbl,  rate_func=smooth),
                lag_ratio=0.25,
            ),
            run_time=0.55,
        )
        self.play(
            LaggedStart(Create(a1), Create(a2), Create(a3), lag_ratio=0.30),
            run_time=0.80,
        )
        self.play(FadeIn(agent_cap, shift=UP * 0.08, rate_func=smooth), run_time=0.35)
        self.wait(5.60)
        self.play(FadeOut(VGroup(
            planner, search, synthesis,
            plan_lbl, srch_lbl, syn_lbl,
            a1, a2, a3, agent_cap,
        )), run_time=0.50)
        # 1.20+0.55+0.80+0.35+5.60+0.50 = 9.00 s

        # ── 3. CLOSING (7.0 s) ────────────────────────────────────────────────
        complex_txt = Text("It gets more complex.",                  color=WARN).scale(0.58)
        follow1     = Text("But if you've followed along so far —",  color=MUTE).scale(0.50)
        follow2     = Text("you'll get it.",   weight=BOLD, color=ACCENT2).scale(0.80)
        VGroup(complex_txt, follow1, follow2).arrange(DOWN, buff=0.35).move_to(DOWN * 0.10)

        self.play(FadeIn(complex_txt, shift=DOWN * 0.10, rate_func=smooth), run_time=0.40)
        self.wait(0.40)
        self.play(FadeIn(follow1, shift=DOWN * 0.10, rate_func=smooth), run_time=0.35)
        self.play(FadeIn(follow2, scale=0.85,         rate_func=smooth), run_time=0.45)
        self.wait(5.40)
        # 0.40+0.40+0.35+0.45+5.40 = 7.00 s

        # Grand total: 3.00+9.00+7.00 = 19.00 s
