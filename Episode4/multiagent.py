#!/usr/bin/env python3
"""
multiagent.py — Episode 4 of Agentic AI, Unpacked.
A TEAM of agents: an orchestrator that delegates to specialist agents.

The big idea: an agent can be a TOOL for another agent. The orchestrator runs
the same tool-use loop from Episode 3 — except its "tools" are other agents.
Multi-agent is just the loop, nested.

Use case: a trip-planning team.

    Orchestrator (plans + delegates)
        ├─ Researcher  (own loop, has web_search)     — destinations, attractions
        ├─ Analyst     (own loop, has calculator)      — day-by-day budget
        ├─ Writer      (own loop, drafts text)         — the itinerary
        └─ Critic      (own loop, reviews the draft)   — catches gaps before delivery

Every agent function accepts an optional `on_event(indent, kind, text)` callback.
CLI usage leaves it as None and gets the same pretty-printed trace as before.
streamlit_app.py passes its own callback to drive a live UI with the exact same
underlying agents — no logic is duplicated between the two front ends.

Works with EITHER Anthropic or OpenAI — whichever API key is set in .env picks
the provider automatically (see llm_provider.py). Set only one, or set both
and force a choice with LLM_PROVIDER=anthropic|openai.

Run (terminal):
    pip install -r requirements.txt
    cp .env.example .env     # add OPENAI_API_KEY or ANTHROPIC_API_KEY
    python multiagent.py

Run (Streamlit UI):
    pip install -r requirements.txt   # includes streamlit
    streamlit run streamlit_app.py

References:
    - Anthropic, "Building Effective Agents" (orchestrator-workers pattern)
      https://www.anthropic.com/research/building-effective-agents
    - Anthropic, "How we built our multi-agent research system"
      https://www.anthropic.com/engineering/built-multi-agent-research-system
"""

import ast
import json
import operator
import os
import sys

import requests

import llm_provider as llm

# ---- Guardrails (they COMPOUND in multi-agent — see Ep 4 failure modes) ----
SPECIALIST_MAX_STEPS = 5      # researcher / analyst loop cap (they use tools)
COMPOSER_MAX_STEPS = 2        # writer / critic loop cap (no tools, just reasoning)
ORCHESTRATOR_MAX_STEPS = 10   # the manager's loop cap (4 specialists + revisions)
MAX_DELEGATION_DEPTH = 2      # specialists cannot spawn deep chains of agents
MAX_TOKENS = 4096             # a full day-by-day itinerary needs more room than a
                              # one-off answer — too low and the writer's draft gets
                              # cut off mid-itinerary, which reads as "REVISE" to the
                              # critic and burns the orchestrator's step budget


# ======================================================================
# 1) LEAF TOOLS (from Ep 3) — used by specialists
# ======================================================================

def web_search(query: str, max_results: int = 3) -> list:
    """Search the web (SerpAPI). Returns title/url/snippet dicts."""
    try:
        api_key = os.environ.get("SERPAPI_KEY")
        if not api_key:
            # Offline fallback so the demo runs without a key
            return [{"note": f"(no SERPAPI_KEY) pretend results for: {query}"}]
        resp = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": api_key, "num": max_results},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {"title": r.get("title"), "url": r.get("link"), "snippet": r.get("snippet")}
            for r in data.get("organic_results", [])[:max_results]
        ] or [{"note": "no results"}]
    except Exception as e:
        return [{"error": str(e)}]


def format_search_results(results: list) -> str:
    """
    Turn web_search()'s list of dicts into clean, readable text — for the
    MODEL to read (LLMs parse plain sentences better than a Python repr) and
    for the trace displays (terminal + Streamlit) to show, instead of raw
    `[{'title': "...", 'url': "..."}]` dict/brace clutter.
    """
    if not results:
        return "No results found."
    first = results[0]
    if "error" in first:
        return f"Search unavailable right now ({first['error'][:60]}...) — answer from general knowledge instead."
    if "note" in first:
        return first["note"]
    lines = [
        f"{i}. {r.get('title') or '(untitled)'} — {r.get('snippet') or ''}".strip(" —")
        for i, r in enumerate(results, 1)
    ]
    return "\n".join(lines)


def calculator(expression: str):
    """Safe arithmetic (no eval)."""
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
           ast.USub: operator.neg, ast.UAdd: operator.pos}

    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp):
            return ops[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp):
            return ops[type(n.op)](ev(n.operand))
        raise ValueError("unsupported expression")

    try:
        return ev(ast.parse(expression, mode="eval").body)
    except Exception as e:
        return f"Error: {e}"


# ======================================================================
# 2) TRACE — one callback interface, two front ends (terminal + Streamlit)
# ======================================================================

def default_trace(indent: int, kind: str, text: str) -> None:
    """Pretty-prints to the terminal. This is the ONLY place print() lives."""
    pad = "    " * indent
    if kind == "banner":
        print(f"\n🧑  TASK: {text}\n" + "═" * 80)
    elif kind == "start":
        print(f"👔 {text}\n")
    elif kind == "agent_start":
        print(pad + "—" * 40 + f"\n{pad}👤 {text}")
    elif kind == "think":
        print(f"{pad}🧠 {text}")
    elif kind == "tool_call":
        print(f"{pad}🔧 {text}")
    elif kind == "tool_result":
        print(f"{pad}👀 {text}")
    elif kind == "final":
        print("═" * 80 + f"\n✅  FINAL:\n{text}\n")


# ======================================================================
# 3) THE GENERIC AGENT LOOP (from Ep 2/3) — every agent uses this
# ======================================================================

def agent_loop(system, task, tools, tool_runner, max_steps, indent=0, on_event=None):
    """
    Run one agent. `indent` is for nested tracing; `on_event` drives the UI.
    Provider-agnostic: talks to llm_provider.chat(), which routes to whichever
    of Anthropic/OpenAI has a key set — this function never knows which one.
    """
    emit = on_event or default_trace
    messages = [{"role": "user", "content": task}]

    for step in range(1, max_steps + 1):
        reply = llm.chat(system, messages, tools, MAX_TOKENS)
        for text in reply.texts:
            emit(indent, "think", text[:90])

        if not reply.is_tool_use:
            return "\n".join(reply.texts).strip()

        llm.append_assistant_turn(messages, reply)
        results = []
        for call in reply.tool_calls:
            emit(indent, "tool_call", f"{call['name']}({json.dumps(call['input'])[:60]})")
            try:
                out = tool_runner(call["name"], call["input"])
            except Exception as e:
                out = f"error: {e}"
            emit(indent, "tool_result", str(out)[:80])
            results.append({"id": call["id"], "output": out})
        llm.append_tool_results(messages, results)

    return "(stopped: hit max steps)"


# ======================================================================
# 4) THE SPECIALISTS — each is an agent with a role + scoped tools
# ======================================================================

def researcher(subtask: str, on_event=None) -> str:
    """A research specialist. Has web_search. Finds destinations/attractions."""
    emit = on_event or default_trace
    emit(1, "agent_start", f"RESEARCHER: {subtask[:60]}")
    tools = [{
        "name": "web_search",
        "description": "Search the web. Returns title/url/snippet.",
        "input_schema": {"type": "object",
                         "properties": {"query": {"type": "string"}},
                         "required": ["query"]},
    }]
    return agent_loop(
        system="You are a travel research specialist. Find accurate, current "
               "information on destinations, attractions, and best times to visit. "
               "Report concise, structured findings. Cite sources.",
        task=subtask, tools=tools,
        tool_runner=lambda n, a: format_search_results(web_search(a["query"])),
        max_steps=SPECIALIST_MAX_STEPS, indent=2, on_event=on_event,
    )


def analyst(subtask: str, on_event=None) -> str:
    """An analysis specialist. Has calculator. Builds the day-by-day budget."""
    emit = on_event or default_trace
    emit(1, "agent_start", f"ANALYST: {subtask[:60]}")
    tools = [{
        "name": "calculator",
        "description": "Evaluate an arithmetic expression.",
        "input_schema": {"type": "object",
                         "properties": {"expression": {"type": "string"}},
                         "required": ["expression"]},
    }]
    return agent_loop(
        system="You are a budget analyst for travel planning. Do precise "
               "calculations and report a clear day-by-day cost breakdown. "
               "Use the SAME currency the user's request was stated in "
               "(US dollars, $, unless told otherwise) for every figure — "
               "never switch to a destination's local currency.",
        task=subtask, tools=tools,
        tool_runner=lambda n, a: calculator(a["expression"]),
        max_steps=SPECIALIST_MAX_STEPS, indent=2, on_event=on_event,
    )


def writer(subtask: str, on_event=None) -> str:
    """A writing specialist. No tools — drafts the itinerary."""
    emit = on_event or default_trace
    emit(1, "agent_start", f"WRITER: {subtask[:60]}")
    return agent_loop(
        system="You are a clear, concise travel writer. Turn the given research "
               "and budget into a tight, well-structured day-by-day itinerary. "
               "No fluff. Use the EXACT budget figures and currency given to "
               "you in the input — never invent your own numbers, and never "
               "convert to a destination's local currency if the input used "
               "a different one (e.g. keep USD/$ as USD/$, do not switch to yen).",
        task=subtask, tools=[],
        tool_runner=lambda n, a: "",
        max_steps=COMPOSER_MAX_STEPS, indent=2, on_event=on_event,
    )


def critic(subtask: str, on_event=None) -> str:
    """
    A review specialist. No tools — checks the draft itinerary for gaps
    before it goes to the user. This is the 4th specialist: quality control.
    """
    emit = on_event or default_trace
    emit(1, "agent_start", f"CRITIC: {subtask[:60]}")
    return agent_loop(
        system="You are a meticulous travel-plan reviewer. Given a draft "
               "itinerary and the original requirements (budget, duration, "
               "destinations), check for completeness, budget consistency, and "
               "clarity. CRITICALLY: verify the itinerary uses the SAME "
               "currency as the original requirements — if it switched to a "
               "different currency (e.g. the request said dollars but the "
               "draft is in yen), or the totals don't add up to the stated "
               "budget, that is a REVISE, not an APPROVED. If it fully meets "
               "the requirements, reply starting with 'APPROVED:' followed by "
               "one sentence why. If something is missing or wrong, reply "
               "starting with 'REVISE:' followed by the specific fix needed.",
        task=subtask, tools=[],
        tool_runner=lambda n, a: "",
        max_steps=COMPOSER_MAX_STEPS, indent=2, on_event=on_event,
    )


def write_with_review(subtask: str, on_event=None, max_review_rounds: int = 2) -> str:
    """
    Writer drafts, then the draft is AUTOMATICALLY routed through the critic
    before it comes back to the orchestrator. If the critic says REVISE, the
    writer gets ONE focused revision — and the REVISED draft is checked again,
    up to `max_review_rounds` total review passes, so a fix that introduces a
    new problem (e.g. drifting currency) doesn't slip through unverified.

    This is a deliberate guardrail, not just a convenience: relying on the
    orchestrator LLM to (a) remember to call the critic and (b) paste the full
    draft verbatim into a revision subtask is exactly the "telephone game"
    failure mode this episode teaches — a stateless specialist call that
    silently drops context. Making review+revision a fixed pipeline stage
    means the final draft is reviewed every time, regardless of what the
    top-level orchestrator's response happens to say it's about to do.
    """
    draft = writer(subtask, on_event=on_event)
    for _ in range(max_review_rounds):
        verdict = critic(
            f"Original requirements:\n{subtask}\n\nDraft itinerary:\n{draft}",
            on_event=on_event,
        )
        if not verdict.strip().upper().startswith("REVISE"):
            break
        draft = writer(
            "Revise the following draft itinerary based on the critic's "
            "feedback. Return the FULL corrected itinerary, not just the "
            f"changed part.\n\nOriginal requirements:\n{subtask}\n\n"
            f"Previous draft:\n{draft}\n\nCritic feedback:\n{verdict}",
            on_event=on_event,
        )
    return draft


# ======================================================================
# 5) THE ORCHESTRATOR — specialists are its tools
# ======================================================================

ORCHESTRATOR_TOOLS = [
    {
        "name": "call_researcher",
        "description": "Delegate a research subtask to the researcher agent (it can search the web). Give it ONE clear research question about destinations, attractions, or timing.",
        "input_schema": {"type": "object",
                         "properties": {"subtask": {"type": "string"}},
                         "required": ["subtask"]},
    },
    {
        "name": "call_analyst",
        "description": "Delegate a budget/calculation subtask to the analyst agent. Provide the numbers and what to compute.",
        "input_schema": {"type": "object",
                         "properties": {"subtask": {"type": "string"}},
                         "required": ["subtask"]},
    },
    {
        "name": "call_writer",
        "description": "Delegate a drafting subtask to the writer agent. Provide the research and budget, and the desired itinerary format. The draft is AUTOMATICALLY routed through the critic (and revised once if needed) before it's returned to you — you get back an already-reviewed itinerary.",
        "input_schema": {"type": "object",
                         "properties": {"subtask": {"type": "string"}},
                         "required": ["subtask"]},
    },
    {
        "name": "call_critic",
        "description": "OPTIONAL extra review pass. call_writer already routes every draft through the critic automatically, so you only need this if you want a SECOND, independent review of an already-approved draft.",
        "input_schema": {"type": "object",
                         "properties": {"subtask": {"type": "string"}},
                         "required": ["subtask"]},
    },
]


def orchestrator_tool_runner(name, args, on_event=None, state=None):
    """Route the orchestrator's 'tool' calls to the right specialist agent."""
    subtask = args["subtask"]
    if name == "call_researcher":
        return researcher(subtask, on_event=on_event)
    if name == "call_analyst":
        return analyst(subtask, on_event=on_event)
    if name == "call_writer":
        draft = write_with_review(subtask, on_event=on_event)
        if state is not None:
            state["last_draft"] = draft   # see run_team: this is what gets delivered
        return draft
    if name == "call_critic":
        return critic(subtask, on_event=on_event)
    return f"unknown specialist: {name}"


def run_team(task: str, on_event=None) -> str:
    """The orchestrator: plan, delegate to specialists, review, synthesize."""
    emit = on_event or default_trace
    emit(0, "banner", task)
    emit(0, "start", "ORCHESTRATOR planning...")
    state = {"last_draft": None}
    wrap_up = agent_loop(
        system=(
            "You are an orchestrator managing a team of specialist agents for "
            "trip planning: a researcher (web search for destinations/attractions), "
            "an analyst (day-by-day budget math), and a writer (drafts the "
            "itinerary — every draft is automatically reviewed by a critic and "
            "revised once if needed before it comes back to you, so what you "
            "receive from call_writer is already quality-checked). Break the "
            "user's task into subtasks and delegate each to the right specialist "
            "via your tools. Each specialist call is STATELESS — it has no memory "
            "of earlier calls, so always give it everything it needs in the "
            "subtask itself — including the analyst's EXACT computed figures, "
            "verbatim, when you delegate to the writer (do not just say 'use "
            "the budget' — paste the actual numbers). State the currency "
            "explicitly (default: US dollars, $) in every subtask that "
            "involves money, and never let it drift to a destination's local "
            "currency. If a specialist's output looks cut off mid-sentence, "
            "call it again asking it to continue from exactly where it stopped — "
            "do not treat a partial draft as done. CRITICAL: once call_writer has "
            "returned a complete, reviewed itinerary, do NOT retype or re-paste it "
            "— it is already captured and will be delivered automatically. Your "
            "final response (the one where you stop calling tools) should just be "
            "ONE short sentence confirming it's ready, e.g. 'The reviewed "
            "itinerary is ready below.' Never spend your output budget retyping "
            "content a specialist already produced. Delegate ONE clear subtask at "
            "a time. Do the minimum delegation needed."
        ),
        task=task, tools=ORCHESTRATOR_TOOLS,
        tool_runner=lambda n, a: orchestrator_tool_runner(n, a, on_event=on_event, state=state),
        max_steps=ORCHESTRATOR_MAX_STEPS, indent=0, on_event=on_event,
    )
    # The orchestrator's own final message is just a short sign-off — the real
    # deliverable is the last critic-reviewed draft captured via call_writer.
    # This also sidesteps a real failure mode: asking the orchestrator to
    # retype a multi-thousand-token itinerary as its OWN response risks
    # hitting MAX_TOKENS a second time, for content that already exists.
    result = state["last_draft"] or wrap_up
    emit(0, "final", result)
    return result


# ======================================================================
# 6) DEMO
# ======================================================================

DEMO_TASK = (
    "Plan a 5-day trip to Kyoto and Tokyo, Japan for two people with a total "
    "budget of $3,000 (excluding flights). Research the must-see attractions "
    "and the best neighborhood to stay in each city, compute a realistic "
    "day-by-day budget breakdown, write a full day-by-day itinerary, and have "
    "it reviewed for completeness and budget accuracy before finalizing."
)

if __name__ == "__main__":
    # Pass any task as CLI args, e.g.:
    #   python multiagent.py Plan a 3-day trip to Rome for 2 people, $1200 budget.
    # With no args, runs the demo task below — just here so the script works
    # out of the box with zero setup, same as Episodes 2/3.
    task = " ".join(sys.argv[1:]) or DEMO_TASK

    print("=" * 80)
    print("MULTI-AGENT TEAM — Episode 4 — Trip Planner")
    print(f"Orchestrator max steps: {ORCHESTRATOR_MAX_STEPS} | "
          f"Specialist max steps: {SPECIALIST_MAX_STEPS}")
    print("=" * 80)

    run_team(task)
