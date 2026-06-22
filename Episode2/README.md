# Episode 2 — Build Your First AI Agent from Scratch

> **Core insight:** An agent is just an LLM running in a loop with tools. That's it. No framework, no magic.

This episode builds a complete, working AI agent in ~60 lines of Python using only the Anthropic SDK. By the end you'll understand exactly what a "tool call" is, why the loop matters, and how the ReAct pattern works at the wire level.

---

## What You'll Build

A `TinyAgent` that can:
- **Reason** about a multi-step task
- **Call tools** (a safe calculator + a live date lookup) when it needs real information
- **Observe** the results and continue reasoning
- **Stop** when it has a final answer — or when a max-steps guard trips

Then you'll run the same question against a plain LLM call (no tools) to feel the gap firsthand.

---

## Files

| File | Purpose |
|------|---------|
| `TinyAgent.py` | The full agent — tools, loop, and comparison demo |

---

## Setup

### 1. Get an Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com) and sign in (or create a free account).
2. Click **"API Keys"** in the left sidebar → **"Create Key"**.
3. Copy the key — it starts with `sk-ant-…`
   (You won't be able to see it again after closing the dialog.)
4. Add a small credit under **"Billing"** — the API is pay-as-you-go. Running this script costs a fraction of a cent.

### 2. Create a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install the dependency

```bash
pip install anthropic
```

### 4. Set your API key

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-...

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

### 5. Run it

```bash
python TinyAgent.py
```

---

## Expected Output

```
=== PLAIN LLM (no tools) — it has to guess ===
Today's date is approximately early 2025... [makes up an answer]

=== AGENT (loop + tools) — it checks and computes ===

🧑  TASK: What is today's date, and how many days are left until 1 January 2027? ...
────────────────────────────────────────────────────────────────
🧠  step 1 · model: I need today's date and then calculate the days remaining.
🔧  step 1 · calling get_current_date({})
👀  step 1 · observed: 2026-06-22
🔧  step 2 · calling calculator({"expression": "(2027-2026)*365 - ..."})
👀  step 2 · observed: 193
────────────────────────────────────────────────────────────────
✅  ANSWER: Today is 2026-06-22. There are 193 days until January 1, 2027 — that's 4,632 hours.
```

The plain LLM has to guess the date (and is usually wrong). The agent calls tools, observes real data, and computes correctly.

---

## How It Works

### The Three-Part Structure

```
TinyAgent.py
├── 1) THE TOOLS        — JSON schemas + Python functions
├── 2) THE LOOP         — the entire agent in ~30 lines
└── 3) CONTRAST         — plain LLM vs. agent, side by side
```

### The Loop (the key idea)

```python
for step in range(1, max_steps + 1):
    resp = client.messages.create(model=MODEL, tools=TOOLS, messages=messages)

    if resp.stop_reason != "tool_use":
        return answer          # model is done

    # run every tool the model requested, feed results back in
    messages.append({"role": "assistant", "content": resp.content})
    for block in resp.content:
        if block.type == "tool_use":
            output = run_tool(block.name, block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
    messages.append({"role": "user", "content": results})
```

Three things to notice:

1. **The model never runs code** — it produces a `tool_use` block describing *what* to call. Your Python runs it.
2. **Results are fed back as messages** — the entire conversation history (including tool results) is sent on every turn. The model reasons over accumulated context.
3. **`max_steps` is the safety valve** — without a cap, a broken tool or confused model could loop indefinitely. Always have one.

### The ReAct Pattern

This is the [ReAct paper](https://arxiv.org/abs/2210.03629) (Yao et al., 2022) expressed in ~10 lines:

```
Reason  →  the model's text output explains its thinking
Act     →  the model emits a tool_use block
Observe →  you run the tool and append the result
           … repeat until stop_reason != "tool_use"
```

### Tool Schemas

The model learns what tools exist from JSON schemas you pass in `tools=`:

```python
{
    "name": "calculator",
    "description": "Evaluate an arithmetic expression, e.g. '24 * 11'.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "A math expression to evaluate."}
        },
        "required": ["expression"],
    },
}
```

Good descriptions → better tool selection. The model reads these descriptions to decide *when* and *how* to use each tool.

---

## Key Concepts

| Concept | What it is |
|---------|-----------|
| **Tool use** | A structured way for the model to request that your code runs a function |
| **`stop_reason`** | `"tool_use"` = model wants to call a tool; anything else = model has a final answer |
| **`tool_use_id`** | Links a tool request to its result — required when you send results back |
| **`max_steps`** | A loop cap — a basic but non-negotiable safety primitive |
| **ReAct** | Reason + Act + Observe — the pattern underlying almost every production agent |

---

## Experiments to Try

1. **Change the task** — ask a question that needs multiple calculator calls
2. **Add a new tool** — try a `web_search` stub or a `get_weather` mock
3. **Lower `max_steps` to 2** — watch the guardrail trip
4. **Remove `get_current_date`** — see the model start guessing again
5. **Print `messages` at each step** — observe the full conversation history grow

---

## References

- Yao et al. (2022) — [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Anthropic (2024) — [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic Tool Use Docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
