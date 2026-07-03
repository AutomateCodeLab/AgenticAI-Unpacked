# Episode 5 — Agent Memory

**Agentic AI, Unpacked · Episode 5**

An agent with three kinds of memory: short-term (the message list), long-term (facts persisted to disk), and semantic (retrieval by *meaning*, via embeddings — the actual mechanism behind RAG). The core insight is that memory isn't magic — it's a list, a file, and a search engine, wired into the same agent loop from Episode 2.

**Use case: a personal AI assistant that remembers you across sessions.**

```
Personal Assistant  (one agent, three memory tools)
    ├─ Short-term  (the growing message list)      — within one session's conversation
    ├─ Long-term   (facts written to ~/.agent_memory.json)  — across sessions
    └─ Semantic    (embeddings + cosine similarity)  — retrieved by meaning, not exact words
```

## What it does

1. You chat with the assistant. Within a session, the message list grows normally (short-term memory) — follow-up questions work.
2. When you tell it something durable (your name, a preference, a decision, a project), it calls `save_memory` to persist that fact to disk with a timestamp and an embedding vector.
3. At the start of *every* turn, it retrieves the memories most semantically relevant to what you just said (`retrieve_memories`, cosine similarity over embeddings) and loads them into context — before it even starts reasoning.
4. Start a brand-new session (fresh message list, nothing carried over) and ask about something you mentioned before. It retrieves the fact from disk and answers correctly — that's the payoff: memory that survives past the conversation that created it.

The nested trace you'll see in the terminal:

```
🧑  Hi! My name is Maneesh, I love hiking, and my project is called Agent Unpacked.
──────────────────────────────────────────────────────────────────────
🔧 save_memory({"text": "The user's name is Maneesh."})
👀 Saved memory: The user's name is Maneesh.
🔧 save_memory({"text": "Maneesh loves hiking."})
👀 Saved memory: Maneesh loves hiking.
🔧 save_memory({"text": "Maneesh's project is called Agent Unpacked."})
👀 Saved memory: Maneesh's project is called Agent Unpacked.
🧠 Thanks for introducing yourself, Maneesh...
──────────────────────────────────────────────────────────────────────
✅ Thanks for introducing yourself, Maneesh! I've noted...

########## brand new session — nothing carried over ##########
🧑  What do you remember about me?
──────────────────────────────────────────────────────────────────────
🧩 pre-loaded 3 memory(ies): Maneesh loves hiking.; The user's name is Maneesh.; ...
🧠 Here's what I remember about you, Maneesh...
──────────────────────────────────────────────────────────────────────
✅ Here's what I remember about you, Maneesh: you love hiking, and your project is called Agent Unpacked.
```

## Two ways to run it

### Terminal (the raw trace, exactly as shown above)

```bash
cd Episode5
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                          # then edit .env — see Keys section below
python agent_with_memory.py                   # runs the built-in two-session demo
python agent_with_memory.py What's my name?   # or ask it anything directly
```

### React UI + FastAPI backend (the live demo used on screen)

React can't import Python directly, so a small FastAPI server (`server.py`) wraps `agent_with_memory.py` and streams the live trace to the browser over Server-Sent Events. Two terminals:

```bash
# Terminal 1 — backend
cd Episode5
source .venv/bin/activate
uvicorn server:app --reload --port 8000

# Terminal 2 — frontend
cd Episode5/frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite's dev server proxies `/api/*` straight to the FastAPI backend on port 8000 (see `frontend/vite.config.js`), so there's no CORS setup needed.

**What's in the UI:**
- **Chat window** — a normal back-and-forth conversation; short-term memory (the message list) persists across turns within the session. Bubbles and memory chips fade in, and a genuinely animated "thinking" indicator (bouncing dots) shows while the agent is working, not a static "…".
- **Sample message picker** — a dropdown of ready-to-use "Teach" and "Recall" messages next to the input, so you can drive a reliable demo without typing on camera (see "Sample queries" below). Picking one fills and focuses the input — press Enter to send.
- **Memory chips** — above each assistant reply, the exact facts retrieved and injected for that turn — semantic recall made visible, not invisible.
- **Live trace** — a collapsible per-turn accordion showing the 🧠/🔧/👀 steps, same events the terminal prints, just rendered live via SSE.
- **Long-term memory panel** — every persisted fact, with a relative timestamp. Click an item to expand it (shows the exact save time) and reveal a **✕ Delete this memory** button for removing just that one fact — the individual counterpart to "Forget all." It's genuinely reactive: it refetches after every turn, on an interval, and whenever the tab regains focus — so if memory changes outside the current turn (another tab, a CLI run, `forget_all()`), the panel catches up within seconds instead of showing stale data until a manual reload. A newly-added memory pulses in with a highlight animation; a small pulsing "live" dot next to the heading signals it's actively synced.
- **🔄 New Session** — clears the visible chat (a fresh message list — short-term memory reset) but does **not** touch the memory panel. Ask "what do you remember about me?" right after clicking it — that's the whole point of the episode, provable live. Fires a toast confirmation.
- **🗑️ Forget all** — calls the delete path (`forget_all()`). Build this from day one; memory is stored user data. Also fires a toast confirmation.
- **Branded dark theme** (`frontend/src/index.css`) — mirrors the series' `brand.py` palette.

`server.py` doesn't reimplement any agent logic — it plugs an `on_event` callback into the exact same `agent_loop()`/`run_agent()` the terminal uses, running it in a background thread and relaying events onto an SSE stream. Nothing about the agent changes between the terminal and the browser.

### Sample queries

The UI's sample-message dropdown ships with these — pick a "Teach" one, send it, click **New Session**, then pick a "Recall" one to prove cross-session memory reliably, without typing live:

| Type | Message |
|---|---|
| 🧑 Teach | "Hi! My name is Maneesh, I love hiking, and my project is called Agent Unpacked." |
| 🧑 Teach | "I'm building a YouTube series about agentic AI, I prefer TypeScript, and my favorite framework is React." |
| 🧑 Teach | "My name is Alex, I'm vegetarian, and I'm training for a marathon in October." |
| 🔍 Recall | "What do you remember about me?" |
| 🔍 Recall | "What's my current project called?" |
| 🔍 Recall | "What programming language do I prefer?" |

## Choose a provider

The assistant runs on **either Anthropic (Claude) or OpenAI (GPT)** for the chat model — you only need ONE API key. `llm_provider.py` detects which key is set in `.env` and routes every call there.

- Set only `OPENAI_API_KEY` → runs on GPT.
- Set only `ANTHROPIC_API_KEY` → runs on Claude.
- Set **both** → `OPENAI_API_KEY` wins by default. Force a choice with `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` in `.env`.
- Override the model with `LLM_MODEL=...` (defaults: `gpt-4.1` for OpenAI, `claude-sonnet-4-6` for Anthropic).

**Semantic embeddings are independent of the chat provider.** If `OPENAI_API_KEY` is set, `embeddings_provider.py` uses real OpenAI embeddings (`text-embedding-3-small`) for more accurate recall — this works even if `LLM_PROVIDER=anthropic`. Without it, memory falls back to a local hashing embedding (no API key needed at all) — semantic recall still works, just less precisely.

**Note on similarity thresholds:** real embedding models spread short, topically different sentences across a much lower raw cosine-similarity range than the local hash embedding does. `embeddings_provider.py` uses a different `SIMILARITY_THRESHOLD` per provider (0.04 for OpenAI, 0.15 for local) — a threshold tuned for one embedding space does not transfer to another; always calibrate empirically rather than reusing a "reasonable-looking" constant.

### Getting an OpenAI API key

1. Go to <https://platform.openai.com/signup> and create/sign in to an account.
2. Add a payment method under **Settings → Billing**.
3. Go to <https://platform.openai.com/api-keys> and click **Create new secret key**.
4. Copy the key immediately — OpenAI only shows it once. It looks like `sk-...`.
5. Paste it into `Episode5/.env` as `OPENAI_API_KEY=sk-...`.

### Getting an Anthropic API key

1. Go to <https://console.anthropic.com> and create/sign in to an account.
2. Add a payment method under **Settings → Billing**.
3. Go to **Settings → API Keys** and click **Create Key**.
4. Copy the key (`sk-ant-...`) and paste it into `Episode5/.env` as `ANTHROPIC_API_KEY=sk-ant-...`.

## Keys

Edit `Episode5/.env`:

| Key | Required? | Notes |
|---|---|---|
| `OPENAI_API_KEY` | One of these two | Runs the LLM on GPT, and enables real embeddings for semantic memory. |
| `ANTHROPIC_API_KEY` | One of these two | Runs the LLM on Claude. Embeddings still fall back to local hashing unless `OPENAI_API_KEY` is also set. |
| `LLM_PROVIDER` | No | Force `openai` or `anthropic` if both keys above are set. |
| `LLM_MODEL` | No | Override the default model for the active provider. |

Never commit `.env`. It is listed in `.gitignore`.

## Guardrails — memory-specific failure modes

| Constant | Value | What it caps / controls |
|---|---|---|
| `RETRIEVE_TOP_K` | 4 | Max memories injected into context per turn — keeps token cost bounded as the store grows |
| `SIMILARITY_THRESHOLD` | 0.04 (OpenAI) / 0.15 (local) | Ignores weak matches so irrelevant memories don't get injected |
| `MAX_STEPS` | 8 | The agent's own tool-use loop cap |
| `MAX_TOKENS` | 1500 | Max tokens per API call |

**Memory failure modes covered in the code:** every memory is timestamped (so newer facts can be preferred over stale ones), `forget_all()` is the delete path built in from day one (not bolted on later), and re-embedding is self-healing — switching embeddings provider between runs doesn't crash on a dimension mismatch, it just recomputes affected vectors on next retrieval. **What this code does NOT do for you:** validate that a saved memory isn't a prompt-injection payload, or judge what's too sensitive to store — that's a human decision the episode covers as the responsible-use section, not something a constant can fix.

## Project structure

```
Episode5/
├── agent_with_memory.py    # the agent: memory store, retrieval, tools, agent_loop + CLI demo
├── llm_provider.py          # Anthropic/OpenAI adapter — picks provider from whichever key is set
├── embeddings_provider.py    # real OpenAI embeddings or local hash fallback, self-healing
├── server.py                  # FastAPI + SSE — thin wrapper, same agent logic as the CLI
├── requirements.txt            # anthropic, openai, fastapi, uvicorn, python-dotenv, numpy, requests
├── .env.example / .gitignore / README.md
└── frontend/
    ├── package.json, vite.config.js, index.html
    └── src/
        ├── main.jsx, App.jsx, index.css, api.js
        └── components/
            ├── ChatWindow.jsx      # conversation + per-turn trace accordion
            ├── MemoryChips.jsx      # facts retrieved/injected for a turn
            ├── MemoryPanel.jsx       # persisted long-term memory list, live-polled
            ├── NewSessionButton.jsx  # resets short-term, proves long-term survives
            └── Toast.jsx              # brief confirmation on New Session / Forget All
```

## References

- Lewis et al., 2020, *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — arXiv:2005.11401 (the RAG paper)
- Anthropic, *Building Effective Agents*
- MemGPT (Packer et al., 2023) — arXiv:2310.08560
