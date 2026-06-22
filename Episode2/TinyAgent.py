#!/usr/bin/env python3
"""
tiny_agent.py — Build your first AI agent from scratch (no framework).
Agentic AI, Unpacked · Episode 2

The whole point of this file: an "agent" is just an LLM running in a LOOP
with TOOLS. There's no magic and no framework here — about 60 real lines.

    1. Send the conversation + the list of tools to the model.
    2. If the model asks to use a tool, run it and feed the result back.
    3. Repeat until the model stops asking for tools (it has an answer).
    4. Cap the loop so it can never run forever.

This is the reason-act-observe pattern from the ReAct paper, expressed with
Claude's native tool use.

Get your API key (one-time setup):
    1. Go to https://console.anthropic.com and sign in (or create a free account).
    2. Click "API Keys" in the left sidebar → "Create Key".
    3. Copy the key — it starts with sk-ant-...
       (You won't be able to see it again, so copy it now.)
    4. Add a small amount of credit under "Billing" — the API is pay-as-you-go.
       Running this script costs a fraction of a cent.

Run it:
    # 1. Create and activate a virtual environment (one-time setup)
    python -m venv .venv

    # macOS / Linux — activate:
        source .venv/bin/activate

    # Windows (Command Prompt) — activate:
        .venv\Scripts\activate.bat

    # Windows (PowerShell) — activate:
        .venv\Scripts\Activate.ps1

    # 2. Install the dependency
    pip install anthropic

    # 3. Set your API key and run
    export ANTHROPIC_API_KEY=sk-ant-...      # paste your key here
    python TinyAgent.py

    # On Windows (Command Prompt):
        set ANTHROPIC_API_KEY=sk-ant-...
    # On Windows (PowerShell):
        $env:ANTHROPIC_API_KEY="sk-ant-..."

    # To deactivate the venv when you're done:
        deactivate

References (full list in the Episode 2 notes):
  - Yao et al., 2022, "ReAct: Synergizing Reasoning and Acting in Language
    Models", arXiv:2210.03629
  - Anthropic, "Building Effective Agents" (Schluntz & Zhang, 2024):
    https://www.anthropic.com/research/building-effective-agents
  - Anthropic tool use docs: https://docs.claude.com
"""

import ast
import json
import operator
from datetime import date

from anthropic import Anthropic

client = Anthropic()            # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-sonnet-4-6"     # fast + inexpensive — ideal for a tutorial


# ======================================================================
# 1) THE TOOLS
#    Each tool is two things:
#      (a) a JSON schema the MODEL sees (name, description, input_schema)
#      (b) a plain Python function YOUR code runs.
#    The model never runs code itself — it just asks; you execute.
# ======================================================================

# --- a safe arithmetic evaluator (no eval(), so no arbitrary code) ---
_SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")

def calculator(expression: str):
    """Evaluate basic arithmetic safely."""
    return _safe_eval(ast.parse(expression, mode="eval").body)

def get_current_date():
    """Today's date. The model has no clock of its own — this grounds it."""
    return date.today().isoformat()

# The schema the model reads. Clear names + descriptions = better tool choice.
TOOLS = [
    {
        "name": "get_current_date",
        "description": "Return today's date as YYYY-MM-DD. Use whenever the task depends on what day it is.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression, e.g. '24 * 11' or '(2027-2026)*365'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "A math expression to evaluate."}
            },
            "required": ["expression"],
        },
    },
]

def run_tool(name, args):
    """Dispatch a tool call to the matching Python function."""
    if name == "get_current_date":
        return str(get_current_date())
    if name == "calculator":
        return str(calculator(args["expression"]))
    raise ValueError(f"unknown tool: {name}")


# ======================================================================
# 2) THE LOOP — this is the entire agent.
# ======================================================================

def run_agent(task: str, max_steps: int = 6):
    print(f"\n🧑  TASK: {task}\n" + "─" * 64)
    messages = [{"role": "user", "content": task}]

    for step in range(1, max_steps + 1):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages,
        )

        # Show the model's reasoning for this turn.
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                print(f"🧠  step {step} · model: {block.text.strip()}")

        # The model is finished when it stops asking for tools.
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text").strip()
            print("─" * 64 + f"\n✅  ANSWER: {answer}\n")
            return answer

        # Otherwise: run every tool the model requested, feed results back in.
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"🔧  step {step} · calling {block.name}({json.dumps(block.input)})")
                try:
                    output = run_tool(block.name, block.input)
                    print(f"👀  step {step} · observed: {output}")
                    results.append({
                        "type": "tool_result", "tool_use_id": block.id, "content": output,
                    })
                except Exception as e:                       # tools fail — handle it
                    print(f"⚠️   step {step} · tool error: {e}")
                    results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": f"error: {e}", "is_error": True,
                    })
        messages.append({"role": "user", "content": results})

    print("⛔  stopped: hit max_steps — the guardrail kept it from looping forever.")
    return None


# ======================================================================
# 3) CONTRAST — a plain one-shot call with NO tools, to feel the gap.
# ======================================================================

def plain_llm(prompt: str):
    resp = client.messages.create(
        model=MODEL, max_tokens=512, messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    task = ("What is today's date, and how many days are left until 1 January 2027? "
            "Then convert that number of days into hours.")

    print("\n=== PLAIN LLM (no tools) — it has to guess ===")
    print(plain_llm(task))

    print("\n=== AGENT (loop + tools) — it checks and computes ===")
    run_agent(task)