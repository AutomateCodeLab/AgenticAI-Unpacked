# Agentic AI, Unpacked

> **A YouTube series that strips away the framework magic and shows you exactly how AI agents work — from raw API calls to production patterns.**

Each episode tackles one concept end-to-end: why it matters, how it works under the hood, and a working implementation you can run in minutes.

---

## Series Overview

| Episode | Title | Concept | Code |
|---------|-------|---------|------|
| 1 | What Is an AI Agent? | The agent loop, autonomy vs. automation | — |
| 2 | Build Your First Agent from Scratch | ReAct loop · Tool use · No frameworks | [`Episode2/TinyAgent.py`](Episode2/TinyAgent.py) |
| *(more coming)* | | | |

---

## How to Use This Repo

Every episode folder is **self-contained** — it has its own code, its own README, and its own setup instructions. You don't need to understand the whole series to run one episode.

```
AgenticAISeries/
├── Episode2/
│   ├── TinyAgent.py   ← the runnable code for ep 2
│   └── README.md      ← episode-specific walkthrough
└── README.md          ← you are here
```

---

## Prerequisites (all episodes)

- **Python 3.10+**
- An **Anthropic API key** — get one free at [console.anthropic.com](https://console.anthropic.com)
  - Create a key → "API Keys" → "Create Key" (starts with `sk-ant-…`)
  - Add a small credit under "Billing" — running any script in this repo costs a fraction of a cent

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
cd Episode2
pip install -r requirements.txt
python TinyAgent.py
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

---

## Key Concepts Across the Series

| Concept | First Seen | Description |
|---------|-----------|-------------|
| **ReAct loop** | Ep 2 | Reason → Act → Observe, repeat. The fundamental agent pattern (Yao et al., 2022). |
| **Tool use** | Ep 2 | The model describes *what* to run; your code actually runs it. |
| **Max-steps guard** | Ep 2 | A loop cap that prevents infinite execution — a basic but critical safety primitive. |
| **Tool schema** | Ep 2 | JSON description of a tool's name, purpose, and inputs — the model's "manual" for your code. |

---

## References & Further Reading

- Yao et al. (2022) — [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Anthropic (2024) — [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (Schluntz & Zhang)
- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

---

## Contributing / Issues

Spotted a bug or have a question about the code? Open an issue — I read them all.

---

## License

MIT — do whatever you want with the code. Attribution appreciated but not required.
