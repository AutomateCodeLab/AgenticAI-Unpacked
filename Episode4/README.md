# Episode 4 — Multi-Agent Team

**Agentic AI, Unpacked · Episode 4**

A team of agents: an orchestrator that delegates to specialist agents. The core insight is that *an agent can be a tool for another agent* — multi-agent is just the single-agent loop, nested.

**Use case: a trip-planning team.**

```
Orchestrator  (plans + delegates)
    ├─ Researcher  (own loop  │  tool: web_search)     — attractions, timing
    ├─ Analyst     (own loop  │  tool: calculator)      — day-by-day budget
    ├─ Writer      (own loop  │  no tools — composes)   — the itinerary
    └─ Critic      (own loop  │  no tools — reviews)    — quality control before delivery
```

## What it does

1. You give the orchestrator a trip-planning task (destination, budget, duration).
2. The orchestrator runs its own ReAct loop. Its "tools" are the four specialists (`call_researcher`, `call_analyst`, `call_writer`, `call_critic`).
3. Each specialist call spins up a *separate* agent loop with its own system prompt, tools, and step cap.
4. Researcher finds attractions/neighborhoods, Analyst computes the budget, Writer drafts the itinerary. Before it ever reaches the orchestrator, `call_writer` automatically routes that draft through the Critic (and one revision + re-check if needed) — a fixed pipeline stage, not something the orchestrator LLM has to remember to do.
5. The orchestrator delivers the last critic-reviewed draft directly — it doesn't retype it, which avoids truncating a multi-thousand-token itinerary a second time.

The nested trace you'll see in the terminal:

```
👔 ORCHESTRATOR planning...
🧠 I'll delegate research first…
🔧 call_researcher({"subtask": "…"})
    ────────────────────────
    👤 RESEARCHER: …
        🧠 I'll search for Kyoto attractions…
        🔧 web_search({"query": "…"})
        👀 [(no SERPAPI_KEY) pretend results for: …]
        🧠 Based on the results…
🔧 call_analyst({"subtask": "…"})
    ────────────────────────
    👤 ANALYST: …
        🧠 I'll compute the daily budget…
        🔧 calculator({"expression": "…"})
        👀 600
🔧 call_writer({"subtask": "…"})
    ────────────────────────
    👤 WRITER: …
        🧠 Here is the day-by-day itinerary…
🔧 call_critic({"subtask": "…"})
    ────────────────────────
    👤 CRITIC: …
        🧠 APPROVED: covers both cities, budget checks out…
🧠 Synthesising…
✅ FINAL: …
```

## Two ways to run it

### Terminal (the raw trace, exactly as shown above)

```bash
cd Episode4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env — see Keys section below
python multiagent.py                          # runs the built-in demo task
python multiagent.py Plan a 3-day trip to Rome for 2 people, $1200 budget.   # or any task of your own
```

### Streamlit UI (the live demo used on screen)

```bash
cd Episode4
source .venv/bin/activate
pip install -r requirements.txt   # same file, already includes streamlit
streamlit run streamlit_app.py
```

`streamlit_app.py` is a thin front end — it imports `run_team` and the guardrail
constants straight from `multiagent.py` and plugs a UI callback into the same
`agent_loop`. Nothing about the agents changes between the terminal and the
browser; you're watching the identical logic, just rendered live.

**What's in the UI:**
- **Sidebar** — provider/model badge, guardrails, the sample-request picker, and Run/Clear.
- **Progress bar** — one smooth animated bar (Plan → Research → Budget → Draft → Review → Done) with a live stage label, so you always know where the team is at a glance.
- **Team status row** — 4 cards (Researcher, Analyst, Writer, Critic) that pulse/glow while active, then check off "done" — each card collapses to done the moment that specialist's work returns, not just at the very end.
- **Live trace** — expandable per-agent panels showing each specialist's own 🧠/🔧/👀 loop, color-coded (blue = delegating/tool calls, gray = tool results, green = "finished" confirmations). Each specialist's result is shown exactly once — the orchestrator's own echo of it is suppressed instead of duplicating the panel above.
- **Clean tool output** — `web_search` results render as readable numbered text (`1. Title — snippet`), not a raw Python `[{'title': ...}]` dict dump.
- **Final itinerary** — a bordered card, a **🎈 balloons** flourish on completion, plus a **Download (.md)** button. The result persists across reruns (e.g. clicking Download itself), so it doesn't vanish.

**If you see `ModuleNotFoundError: No module named 'anthropic'`** when running
`streamlit run streamlit_app.py`, check your shell prompt — if it shows both
`(.venv)` *and* `(base)`, a conda base environment is also active and its
`streamlit` (which has no `anthropic` installed) is shadowing the one in
`.venv` on your `PATH`. Fix it by either:
- running the venv's own binary explicitly: `.venv/bin/streamlit run streamlit_app.py`, or
- running `conda deactivate` before `source .venv/bin/activate`.

### Sample trip requests

The Streamlit UI ships with a dropdown of four ready-to-run requests — each one
is phrased to reliably exercise all four specialists (a research question, a
budget to crunch, a draft to write, and enough moving parts that the critic
usually flags something):

| Sample | Ask |
|---|---|
| Kyoto + Tokyo | 5 days, $3,000, 2 people — attractions + neighborhoods + day-by-day budget + itinerary |
| Bali honeymoon | 4 days, $2,000, 2 people — beaches/waterfalls + couples resort + romantic itinerary |
| NYC solo business trip | 3 days, $1,500, 1 person — Midtown stay + dinner spots + tight schedule |
| Paris + Rome family trip | 7 days, $6,000, 4 people (2 kids) — kid-friendly plan + family lodging |

Pick one from the dropdown, edit it freely if you want, then click **Run the team**.

## Choose a provider

The whole team runs on **either Anthropic (Claude) or OpenAI (GPT)** — you only
need ONE API key. `llm_provider.py` detects which key is set in `.env` and
routes every agent's calls there; `multiagent.py` and `streamlit_app.py` never
know or care which one is active.

- Set only `OPENAI_API_KEY` → runs on GPT.
- Set only `ANTHROPIC_API_KEY` → runs on Claude.
- Set **both** → `OPENAI_API_KEY` wins by default. Force a choice with `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` in `.env`.
- Override the model with `LLM_MODEL=...` (defaults: `gpt-4.1` for OpenAI, `claude-sonnet-4-6` for Anthropic).

### Getting an OpenAI API key

1. Go to <https://platform.openai.com/signup> and create/sign in to an account.
2. Add a payment method under **Settings → Billing** (the API is pay-as-you-go, separate from a ChatGPT subscription).
3. Go to <https://platform.openai.com/api-keys> and click **Create new secret key**.
4. Copy the key immediately — OpenAI only shows it once. It looks like `sk-...`.
5. Paste it into `Episode4/.env` as `OPENAI_API_KEY=sk-...`.

### Getting an Anthropic API key

1. Go to <https://console.anthropic.com> and create/sign in to an account.
2. Add a payment method under **Settings → Billing**.
3. Go to **Settings → API Keys** and click **Create Key**.
4. Copy the key (`sk-ant-...`) and paste it into `Episode4/.env` as `ANTHROPIC_API_KEY=sk-ant-...`.

## Keys

Edit `Episode4/.env`:

| Key | Required? | Notes |
|---|---|---|
| `OPENAI_API_KEY` | One of these two | Runs the team on GPT. See "Getting an OpenAI API key" above. |
| `ANTHROPIC_API_KEY` | One of these two | Runs the team on Claude. See "Getting an Anthropic API key" above. |
| `LLM_PROVIDER` | No | Force `openai` or `anthropic` if both keys above are set. |
| `LLM_MODEL` | No | Override the default model for the active provider. |
| `SERPAPI_KEY` | No | Real web search. Without it the researcher uses a placeholder — the team still runs. |

Never commit `.env`. It is listed in `.gitignore`.

## Guardrails — and why they matter more in multi-agent

| Constant | Value | What it caps |
|---|---|---|
| `SPECIALIST_MAX_STEPS` | 5 | Researcher / Analyst loop (they use tools) |
| `COMPOSER_MAX_STEPS` | 2 | Writer / Critic loop (no tools, just reasoning) |
| `ORCHESTRATOR_MAX_STEPS` | 10 | The manager's planning loop (4 specialists + a possible revision pass) |
| `MAX_DELEGATION_DEPTH` | 2 | How deep specialists can sub-delegate |
| `MAX_TOKENS` | 4096 | Max tokens per API call — a full day-by-day itinerary needs real room; too low and drafts truncate mid-sentence |

**Cost compounds.** A 5-agent task (orchestrator + 4 specialists) can make 5× as many API calls as a single agent — before you count each specialist's own tool calls, or a critic-triggered revision pass. Set low caps; raise them deliberately.

## Project structure

```
Episode4/
├── multiagent.py       # orchestrator + 4 specialists + trace callback + CLI demo
├── llm_provider.py     # Anthropic/OpenAI adapter — picks provider from whichever key is set
├── streamlit_app.py    # live UI — imports multiagent.py, adds an on_event callback
├── requirements.txt    # anthropic, openai, requests, python-dotenv, streamlit
├── .env.example        # key template (safe to commit)
├── .env                # your real keys (gitignored)
└── .gitignore
```

## References

- Anthropic, *Building Effective Agents* — orchestrator-workers pattern
- Anthropic, *How we built our multi-agent research system*
