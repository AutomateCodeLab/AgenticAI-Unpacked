#!/usr/bin/env python3
"""
agent_with_memory.py — Episode 5 of Agentic AI, Unpacked.
A personal AI assistant with three kinds of memory:

  - SHORT-TERM  : the message list (per session) — from Ep 2
  - LONG-TERM   : facts saved to disk, loaded back next session
  - SEMANTIC    : memories stored as vectors, retrieved by MEANING (mini-RAG)

At the start of each turn, the agent retrieves the most relevant past
memories (semantic search) and loads them into context — so it "remembers"
about you across completely separate sessions, not just within one
conversation.

Works with EITHER Anthropic or OpenAI (see llm_provider.py — whichever API
key is set in .env picks the provider). Semantic search uses real OpenAI
embeddings if available, else a local hashing fallback (see
embeddings_provider.py) — semantic recall works either way.

Every function accepts an optional `on_event(indent, kind, text)` callback —
the SAME pattern used in Episode 4. CLI usage leaves it as None and gets a
pretty-printed trace; server.py passes its own callback to stream the live
trace over SSE to the React UI. No logic is duplicated between the two.

Run (terminal):
    pip install -r requirements.txt
    cp .env.example .env     # add OPENAI_API_KEY or ANTHROPIC_API_KEY
    python agent_with_memory.py                    # runs the two-session demo
    python agent_with_memory.py What's my name?    # or ask it anything directly

References:
  - RAG: Lewis et al., 2020 — https://arxiv.org/abs/2005.11401
  - Anthropic, "Building Effective Agents" — https://www.anthropic.com/research/building-effective-agents
"""

import json
import os
import sys
import time
import uuid

import numpy as np

import embeddings_provider as emb
import llm_provider as llm

MEMORY_FILE = os.path.expanduser("~/.agent_memory.json")
RETRIEVE_TOP_K = 4
# Similarity threshold is provider-specific (see embeddings_provider.py) —
# local hash and real embedding models have very different cosine-similarity
# ranges, so a single hardcoded number here wouldn't transfer between them.
SIMILARITY_THRESHOLD = emb.SIMILARITY_THRESHOLD
MAX_STEPS = 8
MAX_TOKENS = 1500


# ======================================================================
# 1) TRACE — one callback interface, two front ends (terminal + React UI)
# ======================================================================

def default_trace(indent: int, kind: str, text: str) -> None:
    """Pretty-prints to the terminal. This is the ONLY place print() lives."""
    pad = "    " * indent
    if kind == "banner":
        print(f"\n🧑  {text}\n" + "─" * 70)
    elif kind == "memory":
        items = json.loads(text) if text else []
        if items:
            preview = "; ".join(items)[:100]
            print(f"{pad}🧩 pre-loaded {len(items)} memory(ies): {preview}")
    elif kind == "think":
        print(f"{pad}🧠 {text}")
    elif kind == "tool_call":
        print(f"{pad}🔧 {text}")
    elif kind == "tool_result":
        print(f"{pad}👀 {text}")
    elif kind == "final":
        print("─" * 70 + f"\n✅ {text}\n")


# ======================================================================
# 2) THE MEMORY STORE (long-term + semantic, persisted to disk)
# ======================================================================

def _load_store() -> list:
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _save_store(store: list) -> None:
    with open(MEMORY_FILE, "w") as f:
        json.dump(store, f, indent=2)


def save_memory(text: str) -> str:
    """Persist a durable fact. Stores the text, a timestamp, and its vector."""
    store = _load_store()
    store.append({
        "id": str(uuid.uuid4()),
        "text": text,
        "ts": time.time(),
        "vec": emb.embed(text).tolist(),
        "embed_model": emb.EMBED_MODEL,
    })
    _save_store(store)
    return f"Saved memory: {text}"


def retrieve_memories(query: str, k: int = RETRIEVE_TOP_K) -> list:
    """
    Semantic search: return the k memories most similar to the query.

    Self-healing: if you switch embeddings provider between runs (e.g. added
    OPENAI_API_KEY today, ran with the local fallback yesterday), old vectors
    have the wrong dimension for the current model. Any memory tagged with a
    different embed_model gets re-embedded with the CURRENT one right here,
    before scoring — so a provider switch never crashes on a shape mismatch.
    """
    store = _load_store()
    if not store:
        return []
    changed = False
    for m in store:
        if m.get("embed_model") != emb.EMBED_MODEL:
            m["vec"] = emb.embed(m["text"]).tolist()
            m["embed_model"] = emb.EMBED_MODEL
            changed = True
    if changed:
        _save_store(store)

    q = emb.embed(query)
    scored = []
    for m in store:
        sim = emb.cosine(q, np.array(m["vec"], dtype=np.float32))
        if sim >= SIMILARITY_THRESHOLD:
            scored.append((sim, m["text"]))
    scored.sort(reverse=True)
    return [text for _sim, text in scored[:k]]


def list_memories() -> list:
    """All persisted memories, newest first — for a UI memory panel."""
    store = _load_store()
    changed = False
    for m in store:
        if "id" not in m:   # backfill for memories saved before ids existed
            m["id"] = str(uuid.uuid4())
            changed = True
    if changed:
        _save_store(store)
    return sorted(
        [{"id": m["id"], "text": m["text"], "ts": m["ts"]} for m in store],
        key=lambda m: m["ts"], reverse=True,
    )


def forget_one(memory_id: str) -> bool:
    """Delete a single memory by id — the individual counterpart to forget_all()."""
    store = _load_store()
    remaining = [m for m in store if m.get("id") != memory_id]
    if len(remaining) == len(store):
        return False
    _save_store(remaining)
    return True


def forget_all() -> None:
    """The delete path — build it from day one."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)


# ======================================================================
# 3) TOOLS the agent can call to manage its own memory
# ======================================================================

TOOLS = [
    {
        "name": "save_memory",
        "description": "Save a durable fact worth remembering across sessions (a name, a preference, a decision, a project detail). Do NOT save trivia or sensitive data that isn't needed.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "The fact to remember, as one clear sentence."}},
            "required": ["text"],
        },
    },
    {
        "name": "recall",
        "description": "Search memory for anything relevant to a topic or question. Use this when the user refers to something they might have told you before.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to recall (e.g. 'the user's project')."}},
            "required": ["query"],
        },
    },
]


def run_tool(name: str, args: dict):
    if name == "save_memory":
        return save_memory(args["text"])
    if name == "recall":
        hits = retrieve_memories(args["query"])
        return json.dumps(hits) if hits else "(no relevant memories found)"
    return f"unknown tool: {name}"


# ======================================================================
# 4) THE GENERIC AGENT LOOP (from Ep 2/3/4) — provider-agnostic
# ======================================================================

def agent_loop(system, messages, tools, tool_runner, max_steps, indent=0, on_event=None):
    """
    Runs steps against an EXISTING `messages` list, mutating it in place by
    appending assistant/tool turns, and returns the final text answer. The
    caller is responsible for appending the new user turn before calling —
    that's what lets a "session" be a real multi-turn conversation (server.py
    keeps growing the same list across chat turns) rather than one-shot.
    """
    emit = on_event or default_trace

    for step in range(1, max_steps + 1):
        reply = llm.chat(system, messages, tools, MAX_TOKENS)
        for text in reply.texts:
            emit(indent, "think", text[:120])

        if not reply.is_tool_use:
            return "\n".join(reply.texts).strip()

        llm.append_assistant_turn(messages, reply)
        results = []
        for call in reply.tool_calls:
            emit(indent, "tool_call", f"{call['name']}({json.dumps(call['input'])[:70]})")
            try:
                out = tool_runner(call["name"], call["input"])
            except Exception as e:
                out = f"error: {e}"
            emit(indent, "tool_result", str(out)[:100])
            results.append({"id": call["id"], "output": out})
        llm.append_tool_results(messages, results)

    return "(stopped: hit max steps)"


# ======================================================================
# 5) run_agent — pre-loads memory, then runs the loop
# ======================================================================

def run_agent(user_message: str, messages: list = None, max_steps: int = MAX_STEPS,
              on_event=None) -> tuple:
    """
    messages=None means a completely fresh conversation (a new "session" —
    this is what proves cross-session recall: nothing here, everything from
    disk). Pass an existing list back in to continue the SAME session across
    multiple turns (server.py does this via its SESSIONS dict).

    Returns (answer, messages) — the caller should hold onto `messages` to
    pass back in on the next turn of the same session.
    """
    emit = on_event or default_trace
    if messages is None:
        messages = []

    emit(0, "banner", user_message)

    relevant = retrieve_memories(user_message)
    emit(0, "memory", json.dumps(relevant))
    memory_context = ""
    if relevant:
        memory_context = "What you remember about this user:\n- " + "\n- ".join(relevant)

    system = (
        "You are a helpful personal assistant with long-term memory. "
        "Use the remembered facts below when relevant. "
        "When the user tells you something durable and useful (a name, a "
        "preference, a decision, a project detail), call save_memory to keep "
        "it.\n\n" + memory_context
    )

    messages.append({"role": "user", "content": user_message})
    answer = agent_loop(system, messages, TOOLS, run_tool, max_steps, indent=0, on_event=on_event)
    emit(0, "final", answer)
    return answer, messages


# ======================================================================
# 6) DEMO — two SEPARATE "sessions" to prove cross-session memory
# ======================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AGENT WITH MEMORY — Episode 5 — Personal Assistant")
    print(f"Memory file: {MEMORY_FILE} | Embeddings: {emb.EMBED_MODEL} | LLM: {llm.PROVIDER}/{llm.MODEL}")
    print("=" * 70)

    if len(sys.argv) > 1:
        # Ask it anything directly, e.g.:
        #   python agent_with_memory.py What do you remember about my project?
        run_agent(" ".join(sys.argv[1:]))
    else:
        # Fresh start for a clean demo
        forget_all()

        print("\n########## SESSION 1 — teaching it about me ##########")
        run_agent("Hi! My name is Maneesh. I build agentic AI, I prefer Python, "
                  "and my current project is called Agent Unpacked.")

        print("\n########## SESSION 2 — brand new session, nothing carried over ##########")
        # Note: messages=None here = a fresh message list. The ONLY way it can
        # answer is by retrieving from persisted memory.
        run_agent("What do you remember about my project and my language preference?")
