#!/usr/bin/env python3
"""
streamlit_app.py — live UI for the Episode 4 multi-agent trip-planning team.

This is a THIN front end. All the agent logic (orchestrator, researcher,
analyst, writer, critic, guardrails) lives in multiagent.py and is imported
here unchanged — the UI just plugs an `on_event` callback into the same
agent_loop that the terminal demo uses, so what you see on screen is exactly
what the team is actually doing, not a mock-up.

Run:
    cd Episode4
    source .venv/bin/activate
    pip install -r requirements.txt   # includes streamlit
    streamlit run streamlit_app.py
"""

import sys

import streamlit as st

try:
    from multiagent import (
        run_team,
        ORCHESTRATOR_MAX_STEPS,
        SPECIALIST_MAX_STEPS,
        COMPOSER_MAX_STEPS,
        MAX_DELEGATION_DEPTH,
    )
    import llm_provider as llm
except ImportError as e:
    st.set_page_config(page_title="Multi-Agent Trip Planner — Ep 4", page_icon="👔")
    st.error(
        f"**Missing dependency: `{e.name}`**\n\n"
        f"Streamlit is running under a different Python than the one with your "
        f"dependencies installed:\n`{sys.executable}`\n\n"
        "This almost always means another environment (commonly conda's "
        "`base`) is active on top of `.venv` — check your shell prompt for "
        "something like `(.venv) (base)`.\n\n"
        "**Fix — run these from the `Episode4/` folder:**\n"
        "```bash\n"
        "conda deactivate   # repeat until (base) is gone from your prompt\n"
        "source .venv/bin/activate\n"
        "pip install -r requirements.txt\n"
        ".venv/bin/streamlit run streamlit_app.py   # call the venv's streamlit directly\n"
        "```"
    )
    st.stop()
except RuntimeError as e:
    st.set_page_config(page_title="Multi-Agent Trip Planner — Ep 4", page_icon="👔")
    st.error(
        f"**{e}**\n\n"
        "Edit `Episode4/.env` and set `OPENAI_API_KEY=...` or "
        "`ANTHROPIC_API_KEY=...` (either one works — see README.md 'Choose a "
        "provider'), then restart Streamlit."
    )
    st.stop()

# Brand palette — mirrors the series' root brand.py. Not imported directly so
# this app's dependencies stay independent of manim.
BG, ACCENT, ACCENT2, WARN, TEXT, MUTE = (
    "#0B0E14", "#4F9DFF", "#36D6B0", "#FFC857", "#E6EAF2", "#8A93A6",
)


def _rgb(hex_color: str) -> str:
    """'#36D6B0' -> '54, 214, 176' (for use inside an rgba(var(--x), a) CSS call)."""
    h = hex_color.lstrip("#")
    return ", ".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


AGENT_META = {
    "ORCHESTRATOR": {"emoji": "👔", "color": ACCENT},
    "RESEARCHER":   {"emoji": "🔎", "color": ACCENT2},
    "ANALYST":      {"emoji": "📊", "color": ACCENT2},
    "WRITER":       {"emoji": "✍️", "color": ACCENT2},
    "CRITIC":       {"emoji": "🧐", "color": WARN},
}
SPECIALIST_ORDER = ["RESEARCHER", "ANALYST", "WRITER", "CRITIC"]

# Overall pipeline stages, shown as one smooth progress bar above the team
# cards — the "story" view; the cards below are the "detail" view.
STAGES = ["Plan", "Research", "Budget", "Draft", "Review", "Done"]
ROLE_TO_STAGE = {"RESEARCHER": 1, "ANALYST": 2, "WRITER": 3, "CRITIC": 4}
STAGE_ICON = {0: "👔", 1: "🔎", 2: "📊", 3: "✍️", 4: "🧐", 5: "🎉"}

# Sample queries — each one is phrased to force all four specialists to fire
# (a destination/timing question, a budget number to crunch, a draft to write,
# and enough moving parts that the critic usually finds something). Good for a
# reliable live demo, and listed in README.md for anyone following along.
SAMPLE_QUERIES = {
    "Kyoto + Tokyo, 5 days, $3,000, 2 people": (
        "Plan a 5-day trip to Kyoto and Tokyo, Japan for two people with a total "
        "budget of $3,000 (excluding flights). Research the must-see attractions "
        "and the best neighborhood to stay in each city, compute a realistic "
        "day-by-day budget breakdown, write a full day-by-day itinerary, and have "
        "it reviewed for completeness and budget accuracy before finalizing."
    ),
    "Bali honeymoon, 4 days, $2,000, 2 people": (
        "Plan a romantic 4-day honeymoon trip to Bali for two people with a total "
        "budget of $2,000 (excluding flights). Research the best beaches, "
        "waterfalls, and a highly-rated adults-only or couples resort area. "
        "Compute a day-by-day budget breakdown covering stay, food, and "
        "activities. Write a full day-by-day romantic itinerary, and have it "
        "reviewed for completeness and budget accuracy before finalizing."
    ),
    "NYC solo business trip, 3 days, $1,500": (
        "Plan an efficient 3-day solo business trip to New York City with a "
        "total budget of $1,500 (excluding flights). Research a well-connected "
        "neighborhood to stay in near Midtown and 2-3 highly rated dinner spots "
        "for client meetings. Compute a day-by-day budget breakdown for hotel, "
        "meals, and local transport. Write a tight day-by-day schedule that "
        "leaves evenings free, and have it reviewed for completeness and budget "
        "accuracy before finalizing."
    ),
    "Paris + Rome family trip, 7 days, $6,000, 4 people": (
        "Plan a 7-day family trip to Paris and Rome for a family of four (2 "
        "adults, 2 kids) with a total budget of $6,000 (excluding flights). "
        "Research kid-friendly attractions and a family-sized apartment or "
        "connecting rooms in each city. Compute a day-by-day budget breakdown "
        "for lodging, meals, and activities. Write a full day-by-day itinerary "
        "paced for kids, and have it reviewed for completeness and budget "
        "accuracy before finalizing."
    ),
}

st.set_page_config(page_title="Multi-Agent Trip Planner — Ep 4", page_icon="👔", layout="wide")

st.markdown(
    f"""
    <style>
    @keyframes ep4Pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(var(--pulse-rgb), 0.45); }}
        70%  {{ box-shadow: 0 0 0 14px rgba(var(--pulse-rgb), 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(var(--pulse-rgb), 0); }}
    }}
    @keyframes ep4FadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    div[data-testid="stStatusWidget"] {{ border-radius: 10px; }}
    div[data-testid="stAppViewContainer"] * {{ scroll-behavior: smooth; }}

    .ep4-divider {{
        height: 3px; border-radius: 2px; margin: 0.2rem 0 1.1rem 0;
        background: linear-gradient(90deg, {ACCENT}, {ACCENT2}, {WARN});
    }}
    .ep4-card {{
        border-radius: 12px; padding: 14px 8px; text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.35);
        transition: border-color 0.35s ease, background 0.35s ease,
                    color 0.35s ease, transform 0.25s ease;
    }}
    .ep4-card.active {{ animation: ep4Pulse 1.6s ease-out infinite; transform: scale(1.03); }}
    .ep4-card .ep4-emoji {{ font-size: 1.7rem; line-height: 1; }}
    .ep4-card .ep4-label {{ font-weight: 700; margin-top: 4px; }}
    .ep4-card .ep4-badge {{ font-size: 0.72rem; opacity: 0.85; }}

    .ep4-progress-track {{
        width: 100%; height: 10px; border-radius: 6px; overflow: hidden;
        background: rgba(138, 147, 166, 0.22); margin: 0.35rem 0 0.15rem 0;
    }}
    .ep4-progress-fill {{
        height: 100%; border-radius: 6px;
        background: linear-gradient(90deg, {ACCENT}, {ACCENT2});
        transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .ep4-stage-label {{
        font-size: 0.92rem; color: {MUTE}; margin-bottom: 0.6rem;
        animation: ep4FadeIn 0.4s ease;
    }}
    .ep4-fadein {{ animation: ep4FadeIn 0.5s ease; }}
    .ep4-final-heading {{
        font-size: 1.4rem; font-weight: 700; margin: 0.2rem 0 0.6rem 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar: identity, provider, guardrails, and the run controls ──────────
with st.sidebar:
    st.markdown("### 👔 Agentic AI, Unpacked")
    st.caption("Episode 4 · Multi-Agent Systems")
    st.markdown(f"**Provider** &nbsp; `{llm.PROVIDER}`  \n**Model** &nbsp; `{llm.MODEL}`")

    with st.expander("Guardrails in effect", expanded=False):
        st.markdown(
            f"- **Orchestrator max steps:** {ORCHESTRATOR_MAX_STEPS}\n"
            f"- **Researcher/Analyst max steps:** {SPECIALIST_MAX_STEPS}\n"
            f"- **Writer/Critic max steps:** {COMPOSER_MAX_STEPS}\n"
            f"- **Max delegation depth:** {MAX_DELEGATION_DEPTH}\n\n"
            "Cost compounds in multi-agent — a 5-agent task (orchestrator + 4 "
            "specialists) can be 5x the API calls of a single agent. Caps keep "
            "it bounded."
        )

    st.divider()
    sample_choice = st.selectbox("Sample trip request", list(SAMPLE_QUERIES.keys()))
    task = st.text_area(
        "Trip request (edit freely before running)",
        value=SAMPLE_QUERIES[sample_choice],
        height=160,
        key=f"task_{sample_choice}",   # re-mount with the new sample when selection changes
    )
    col_run, col_clear = st.columns([2, 1])
    run_clicked = col_run.button("🚀 Run the team", type="primary", use_container_width=True)
    clear_clicked = col_clear.button("🗑️ Clear", use_container_width=True)

if clear_clicked:
    for key in ("ep4_result", "ep4_stats", "ep4_stage"):
        st.session_state.pop(key, None)
    st.rerun()

st.title("👔 Multi-Agent Trip Planner")
st.markdown('<div class="ep4-divider"></div>', unsafe_allow_html=True)
st.caption(
    "An orchestrator delegates to four specialist agents (Researcher, "
    "Analyst, Writer, Critic). Each specialist is itself an agent loop — this "
    "is the SAME code as `multiagent.py`, just with a live UI wired in "
    "instead of terminal prints."
)

# ── Overall progress bar — the "story" view of where the team is right now ──
progress_label_slot = st.empty()
progress_bar_slot = st.empty()


def render_progress(stage_index: int) -> None:
    pct = round(100 * stage_index / (len(STAGES) - 1))
    label = STAGES[stage_index]
    icon = STAGE_ICON[stage_index]
    progress_label_slot.markdown(
        f'<div class="ep4-stage-label">{icon}&nbsp; <b>{label}</b> · step {stage_index} of {len(STAGES) - 1}</div>',
        unsafe_allow_html=True,
    )
    progress_bar_slot.markdown(
        f'<div class="ep4-progress-track"><div class="ep4-progress-fill" style="width:{pct}%;"></div></div>',
        unsafe_allow_html=True,
    )


render_progress(st.session_state.get("ep4_stage", 0))

# ── Team status row — lights up live as the orchestrator delegates ─────────
st.markdown("#### Team status")
card_cols = st.columns(4)
card_slots = {role: card_cols[i].empty() for i, role in enumerate(SPECIALIST_ORDER)}
card_state = {role: "idle" for role in SPECIALIST_ORDER}
# Cards that already ran in a prior (persisted) run should render as "done".
for _role in SPECIALIST_ORDER:
    if st.session_state.get("ep4_stage", 0) > ROLE_TO_STAGE.get(_role, 99):
        card_state[_role] = "done"


def render_card(role: str) -> None:
    meta = AGENT_META[role]
    state = card_state[role]
    css_class = "ep4-card active" if state == "active" else "ep4-card"
    if state == "active":
        border, bg, fg, badge = meta["color"], meta["color"] + "26", TEXT, "● running"
    elif state == "done":
        border, bg, fg, badge = meta["color"], "transparent", meta["color"], "✓ done"
    else:
        border, bg, fg, badge = MUTE, "transparent", MUTE, "idle"
    card_slots[role].markdown(
        f"""<div class="{css_class}" style="border:1.5px solid {border}; background:{bg};
                 color:{fg}; --pulse-rgb:{_rgb(meta['color'])};">
              <div class="ep4-emoji">{meta['emoji']}</div>
              <div class="ep4-label">{role.title()}</div>
              <div class="ep4-badge">{badge}</div>
            </div>""",
        unsafe_allow_html=True,
    )


for _role in SPECIALIST_ORDER:
    render_card(_role)

st.markdown("#### Live trace")
trace_container = st.container()
result_area = st.container()

CALL_TO_ROLE = {
    "call_researcher": "RESEARCHER", "call_analyst": "ANALYST",
    "call_writer": "WRITER", "call_critic": "CRITIC",
}


def _clean(text: str) -> str:
    """Collapse embedded newlines so a truncated snippet reads as one tidy line."""
    return " ".join(text.split())


if run_clicked:
    active_boxes = {}          # role -> st.status object (the one CURRENTLY open)
    stats = {"delegations": 0}
    last_delegate = {"role": None}   # which specialist the orchestrator just called
    st.session_state["ep4_stage"] = 0
    render_progress(0)

    def on_event(indent: int, kind: str, text: str) -> None:
        """Bridges multiagent.py's trace events into live Streamlit widgets."""
        if kind == "banner":
            return  # task is already shown in the sidebar
        if kind == "start":
            trace_container.markdown(f"**👔 {text}**")
            return

        if kind == "agent_start":
            role = text.split(":", 1)[0].strip()
            # whichever card was "active" is now done — a new specialist has the floor
            for r, s in card_state.items():
                if s == "active":
                    card_state[r] = "done"
                    render_card(r)
            if role in card_state:
                card_state[role] = "active"
                render_card(role)
                stats["delegations"] += 1
            if role in ROLE_TO_STAGE:
                stage = ROLE_TO_STAGE[role]
                st.session_state["ep4_stage"] = max(st.session_state.get("ep4_stage", 0), stage)
                render_progress(st.session_state["ep4_stage"])
            meta = AGENT_META.get(role, {"emoji": "🤖"})
            box = trace_container.status(
                f"{meta['emoji']} {text}", state="running", expanded=True,
            )
            active_boxes[role] = box
            return

        # Top-level (indent 0) events are the ORCHESTRATOR's own reasoning.
        if indent == 0:
            if kind == "tool_call":
                role = CALL_TO_ROLE.get(text.split("(", 1)[0])
                last_delegate["role"] = role
                label = f"Delegating to **{role.title()}**" if role else _clean(text)
                trace_container.markdown(f":blue[🔧 {label}]")
                return
            if kind == "tool_result":
                # The specialist's own panel (opened above) already showed this
                # result in full — re-printing it here would just duplicate it.
                # Mark that panel done+collapsed right now instead of waiting
                # for the whole run to finish, and leave a one-line confirmation.
                role = last_delegate["role"]
                if role and role in active_boxes:
                    active_boxes[role].update(state="complete", expanded=False)
                    trace_container.markdown(f":green[✅ {role.title()} finished — see panel above.]")
                else:
                    trace_container.write(f"👀 {_clean(text)}")
                last_delegate["role"] = None
                return
            # orchestrator's own "think" narration
            trace_container.write(f"🧠 {_clean(text)}")
            return

        # Nested (indent >= 1): route into the specialist's own panel.
        target = list(active_boxes.values())[-1] if active_boxes else None
        clean = _clean(text)
        if kind == "tool_call":
            line = f":blue[🔧 {clean}]"
        elif kind == "tool_result":
            line = f":gray[👀 {clean}]"
        else:
            line = f"🧠 {clean}"
        if target is not None:
            target.write(line)
        else:
            trace_container.write(line)

    with st.spinner("Team is working..."):
        result = run_team(task, on_event=on_event)

    for r in list(card_state):
        if card_state[r] == "active":
            card_state[r] = "done"
            render_card(r)
    for box in active_boxes.values():
        box.update(state="complete", expanded=False)

    st.session_state["ep4_stage"] = len(STAGES) - 1
    render_progress(st.session_state["ep4_stage"])

    # Stash in session_state so the result survives the rerun that Streamlit
    # triggers when you click the download button below (otherwise it would
    # vanish, since `run_clicked` resets to False on that rerun).
    st.session_state["ep4_result"] = result
    st.session_state["ep4_stats"] = stats
    st.balloons()

if "ep4_result" in st.session_state:
    with result_area:
        st.divider()
        st.markdown('<div class="ep4-final-heading ep4-fadein">✅ Final itinerary</div>', unsafe_allow_html=True)
        stats = st.session_state.get("ep4_stats") or {}
        if stats.get("delegations"):
            st.caption(f"{stats['delegations']} specialist calls made this run.")
        with st.container(border=True):
            st.markdown(st.session_state["ep4_result"])
        st.download_button(
            "⬇️ Download itinerary (.md)",
            data=st.session_state["ep4_result"],
            file_name="itinerary.md",
            mime="text/markdown",
        )
