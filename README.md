# Agentic AI, Unpacked

> **A YouTube series that strips away the framework magic and shows you exactly how AI agents work — from raw API calls to production patterns.**

Each episode tackles one concept end-to-end: why it matters, how it works under the hood, and a working implementation you can run in minutes.

---

## Series Overview

| Episode | Title | Concept | Code |
|---------|-------|---------|------|
| 1 | What Is an AI Agent? | The agent loop, autonomy vs. automation | — |
| 2 | Build Your First Agent from Scratch | ReAct loop · Tool use · No frameworks | [`Episode2/TinyAgent.py`](Episode2/TinyAgent.py) |
| 3 | Real Tools — Web, Files, GitHub & Calculator | Production tool use · Guardrails · Five real tools | [`Episode3/agent_with_tools.py`](Episode3/agent_with_tools.py) |
| 4 | Multi-Agent Team | Orchestrator-workers pattern · Agents as tools for agents · Streamlit UI | [`Episode4/multiagent.py`](Episode4/multiagent.py) |
| 5 | Agent Memory | Short-term/long-term/semantic memory · Embeddings & retrieval (RAG) · React + FastAPI UI | [`Episode5/agent_with_memory.py`](Episode5/agent_with_memory.py) |
| 6 | Guardrails & Safety (Finale) | Human-in-the-loop approval · Prompt-injection defense · Hard limits · Kill switch · Least privilege · React + FastAPI UI | [`Episode6/safe_agent.py`](Episode6/safe_agent.py) |

Episode 6 closes the six-episode foundation arc — loop → tools → team → memory → safety. More episodes are planned beyond it.

---

## How to Use This Repo

Every episode folder is **self-contained** — it has its own code, its own README, and its own setup instructions. You don't need to understand the whole series to run one episode.

```
AgenticAISeries/
├── Episode2/
│   ├── TinyAgent.py          ← the runnable code for ep 2
│   └── README.md             ← episode-specific walkthrough
├── Episode3/
│   ├── agent_with_tools.py   ← the runnable code for ep 3
│   ├── requirements.txt      ← pip dependencies
│   ├── .env.example          ← API key template (copy → .env, fill in real keys)
│   └── README.md             ← full component walkthrough
├── Episode4/
│   ├── multiagent.py         ← orchestrator + specialist agents (the core loop)
│   ├── llm_provider.py       ← runs on either Anthropic or OpenAI
│   ├── streamlit_app.py      ← live UI over the same agents
│   ├── requirements.txt, .env.example
│   └── README.md
├── Episode5/
│   ├── agent_with_memory.py  ← short-term/long-term/semantic memory agent
│   ├── llm_provider.py, embeddings_provider.py
│   ├── server.py             ← FastAPI + SSE backend for the React UI
│   ├── frontend/             ← React (Vite) chat UI
│   ├── requirements.txt, .env.example
│   └── README.md
├── Episode6/
│   ├── safe_agent.py         ← hardened agent: 6 guardrail layers + least privilege
│   ├── llm_provider.py       ← runs on either Anthropic or OpenAI
│   ├── server.py             ← FastAPI + SSE backend, blocking approval + kill-switch
│   ├── frontend/             ← React (Vite) UI — live approvals, layer status, kill switch
│   ├── requirements.txt, .env.example
│   └── README.md
└── README.md                 ← you are here
```

---

## Prerequisites (all episodes)

- **Python 3.10+**
- An **Anthropic API key** — get one free at [console.anthropic.com](https://console.anthropic.com)
  - Create a key → "API Keys" → "Create Key" (starts with `sk-ant-…`)
  - Add a small credit under "Billing" — running any script in this repo costs a fraction of a cent
- **Episodes 4+ also run on OpenAI** as an alternative to Anthropic — either key works, see that episode's README for setup. Episodes 5 and 6's React UIs additionally need **Node.js 18+**.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/AutomateCodeLab/AgenticAI-Unpacked.git
cd AgenticAI-Unpacked

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate.bat     # Windows (CMD)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)

# 3. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...   # macOS / Linux
# set ANTHROPIC_API_KEY=sk-ant-...    # Windows CMD
# $env:ANTHROPIC_API_KEY="sk-ant-…"  # Windows PowerShell

# 4. Go to an episode and follow its README
cd Episode3
pip install -r requirements.txt
cp .env.example .env   # fill in your real keys
python agent_with_tools.py
```

---

## Episode Summaries

### Episode 1 — What Is an AI Agent?
Covers the conceptual foundation: what separates an "agent" from a plain LLM call, the perception-reason-act loop, and where autonomy actually lives in these systems. No code for this episode — it's a visual explainer.

### Episode 2 — Build Your First Agent from Scratch
**The core insight:** an agent is an LLM running in a loop with tools. No framework, no magic — about 60 lines of Python that implement the full ReAct (Reason + Act) pattern from scratch using Claude's native tool-use API.

You will see:
- How to define tools as JSON schemas the model can read
- How the model *requests* a tool call (it never runs code itself — you do)
- The observe → reason → act loop that makes an agent more than a chatbot
- A side-by-side comparison: a plain LLM call vs. the same question with tool access

→ **Code:** [`Episode2/TinyAgent.py`](Episode2/TinyAgent.py)

### Episode 3 — Real Tools: Web, Files, GitHub & Calculator

**The core insight:** toy string-manipulation tools won't prepare you for production. This episode wires five real tools to the same ReAct loop from Episode 2 and shows you every hard problem that appears — guardrails, sandboxing, error recovery, and safe expression evaluation.

The five tools:

| Tool | What it does | Key dependency |
| ---- | ------------ | -------------- |
| `web_search` | Live web search via SerpAPI | `SERPAPI_KEY` |
| `read_file` | Reads files inside a sandboxed workspace | — |
| `write_file` | Writes files (path-traversal protected) | — |
| `github_api` | Fetches repo info / issues from GitHub API | `GITHUB_TOKEN` |
| `calculator` | Evaluates math via safe AST parsing (no `eval`) | — |

You will see:

- How to write a JSON tool schema the model can parse (name, description, `input_schema`, required)
- How the `run_tool` dispatcher maps model requests to Python functions
- Guardrails in practice: `MAX_STEPS=10`, `MAX_TOKENS_PER_TURN=2048`, file-size cap, search result cap
- Why `eval()` is dangerous and how AST-based math parsing eliminates that risk
- Path-traversal protection: confining file access to `AGENT_WORKSPACE` using `os.path.abspath`
- Error recovery: the agent reads tool errors, adjusts its plan, and retries

→ **Code:** [`Episode3/agent_with_tools.py`](Episode3/agent_with_tools.py)  
→ **Setup:** copy `.env.example` → `.env` and fill in the three API keys listed there

### Episode 4 — Multi-Agent Team

**The core insight:** an agent can be a *tool* for another agent. A multi-agent system isn't a new mechanism — it's the same ReAct loop from Episode 2, nested: an orchestrator's "tools" are other agents, each running its own loop.

The team (a trip-planning use case):

| Agent | Role | Tools |
| ----- | ---- | ----- |
| Orchestrator | Plans + delegates to specialists | `call_researcher`, `call_analyst`, `call_writer`, `call_critic` |
| Researcher | Finds attractions/neighborhoods | `web_search` |
| Analyst | Computes the day-by-day budget | `calculator` |
| Writer | Drafts the itinerary | — |
| Critic | Reviews the draft before it ships | — |

You will see:

- The orchestrator-workers pattern — Anthropic's recommended structure for complex work
- Why the writer→critic review is a fixed code pipeline, not a prompt instruction the orchestrator has to remember
- Guardrails that compound in multi-agent: per-agent step caps, a global delegation depth limit
- Running the same agent code on **either Anthropic or OpenAI** (`llm_provider.py`)
- A Streamlit UI over the identical agent loop — same logic, terminal or browser

→ **Code:** [`Episode4/multiagent.py`](Episode4/multiagent.py)  
→ **UI:** from `Episode4/`, run `streamlit run streamlit_app.py`  
→ **Setup:** copy `.env.example` → `.env`, set either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### Episode 5 — Agent Memory

**The core insight:** an LLM is stateless — a chat only "remembers" because the app re-sends the whole history every turn. Real memory means going further: persisting facts beyond a single conversation, and retrieving them by *meaning*, not exact words — the actual mechanism behind RAG.

Three kinds of memory, one agent (a personal-assistant use case):

| Kind | What it is | Where it lives |
| ---- | ---------- | -------------- |
| Short-term | The growing message list | In memory, for one session |
| Long-term | Durable facts the agent chooses to save | A JSON file on disk |
| Semantic | Facts retrieved by meaning via embeddings | Cosine similarity over vectors |

You will see:

- Why a single similarity threshold doesn't transfer between embedding models — it's calibrated per provider, not a universal constant
- Self-healing retrieval: switching embeddings provider between runs re-embeds old vectors instead of crashing on a dimension mismatch
- Proving cross-session memory live: teach it a fact, start a brand-new session, ask about it, watch it retrieve from disk
- A React + FastAPI UI streaming the live agent trace over Server-Sent Events, with a memory panel you can watch update in real time

→ **Code:** [`Episode5/agent_with_memory.py`](Episode5/agent_with_memory.py)  
→ **UI:** from `Episode5/`, run `uvicorn server:app --reload --port 8000`, then in a second terminal `cd frontend && npm run dev`  
→ **Setup:** copy `.env.example` → `.env`, set either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### Episode 6 — Guardrails & Safety (the Finale)

**The core insight:** an agent is risky exactly because it's both *capable* and *autonomous* — a chatbot is capable but not autonomous, a script is autonomous but not capable, an agent is both. Safety isn't one clever trick; it's defense in depth, so that one layer failing isn't game over.

Six layers of defense, on a foundation of least privilege (a personal-admin-assistant use case):

| # | Layer | What it does |
| - | ----- | ------------ |
| 1 | Human-in-the-loop approval | Risky tools (`write_file`, `send_email`) pause for a live Approve/Deny click |
| 2 | Input/output validation | Sandboxed paths, size-bounded output, an email-recipient allowlist |
| 3 | Prompt-injection defense | Tool output framed as untrusted data, never instructions — toggleable to demo the vulnerability |
| 4 | Hard limits | Step count, token count, cost budget, rate limit |
| 5 | Logging | Every tool call, approval, and halt, timestamped and queryable |
| 6 | Kill switch | Checked every loop iteration *and* every second while an approval is pending |

You will see:

- A real, live prompt-injection attack — a file with a hidden instruction the agent either obeys (undefended) or reports as suspicious data (defended), one system-prompt toggle apart
- Why an *approved* risky action can still be blocked by the very next layer (the allowlist), proving defense-in-depth instead of a single point of failure
- A human approval that genuinely pauses a running agent's background thread server-side, waiting for a live click in the browser — not a one-way log stream
- A kill switch that halts a run mid-flight, even mid-approval, without needing the agent's cooperation
- A live UI status strip mirroring the six layers, lighting up each one the instant it actually fires

→ **Code:** [`Episode6/safe_agent.py`](Episode6/safe_agent.py)  
→ **UI:** from `Episode6/`, run `uvicorn server:app --reload --port 8000`, then in a second terminal `cd frontend && npm run dev`  
→ **Setup:** copy `.env.example` → `.env`, set either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

---

## Key Concepts Across the Series

| Concept | First Seen | Description |
|---------|-----------|-------------|
| **ReAct loop** | Ep 2 | Reason → Act → Observe, repeat. The fundamental agent pattern (Yao et al., 2022). |
| **Tool use** | Ep 2 | The model describes *what* to run; your code actually runs it. |
| **Max-steps guard** | Ep 2 | A loop cap that prevents infinite execution — a basic but critical safety primitive. |
| **Tool schema** | Ep 2 | JSON description of a tool's name, purpose, and inputs — the model's "manual" for your code. |
| **Real tool integration** | Ep 3 | Connecting HTTP APIs, file I/O, and computation to the agent loop. |
| **Guardrails** | Ep 3 | Token limits, step caps, file-size caps — safety primitives for production agents. |
| **Safe eval** | Ep 3 | AST-based math parsing instead of `eval()` — eliminates arbitrary code execution risk. |
| **Sandboxing** | Ep 3 | Path-traversal protection via `os.path.abspath` to confine file access. |
| **Error recovery** | Ep 3 | The agent reads tool error messages and self-corrects — no special retry logic needed. |
| **Orchestrator-workers** | Ep 4 | A manager agent delegates to specialist agents, each its own loop — agents as tools for agents. |
| **Dual LLM provider** | Ep 4 | The same agent code runs on either Anthropic or OpenAI, auto-detected from whichever key is set. |
| **Compounding guardrails** | Ep 4 | Per-agent step caps and a delegation depth limit — cost and failure modes multiply with each added agent. |
| **Short/long-term memory** | Ep 5 | The message list (per session) vs. facts persisted to disk (across sessions). |
| **Semantic memory / RAG** | Ep 5 | Retrieving facts by meaning via embeddings + cosine similarity, not exact-word matching. |
| **Self-healing retrieval** | Ep 5 | Switching embedding providers re-computes affected vectors instead of crashing on a dimension mismatch. |
| **Human-in-the-loop approval** | Ep 6 | Risky tool calls genuinely pause execution until a human approves or denies, live. |
| **Prompt-injection defense** | Ep 6 | Framing tool output as untrusted data (never instructions) so hidden commands in fetched content aren't obeyed. |
| **Defense in depth** | Ep 6 | Six independent guardrail layers, so one layer failing isn't the whole story — an approved action can still be blocked by the next layer. |
| **Least privilege** | Ep 6 | Give the agent the minimum access it needs — the guardrail that shrinks the *blast radius* when something slips through. |
| **Kill switch** | Ep 6 | A stop condition checked every loop iteration (and every second during a pending approval) that halts a run without the agent's cooperation. |

---

## References & Further Reading

- Yao et al. (2022) — [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Anthropic (2024) — [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (Schluntz & Zhang)
- Anthropic (2024) — [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- Lewis et al. (2020) — [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — prompt injection, insecure output handling, excessive agency
- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [SerpAPI Documentation](https://serpapi.com/search-api)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Python `ast` module — safe expression parsing](https://docs.python.org/3/library/ast.html)

---

## Contributing / Issues

Spotted a bug or have a question about the code? Open an issue — I read them all.

---

## License

MIT — do whatever you want with the code. Attribution appreciated but not required.
