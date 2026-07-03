#!/usr/bin/env python3
"""
server.py — FastAPI backend for the Episode 5 React UI.

A thin HTTP/SSE wrapper around agent_with_memory.py. It doesn't reimplement
any agent logic — it plugs an `on_event` callback into the SAME
run_agent()/agent_loop() the terminal demo uses (via a queue + a background
thread, since the agent code is synchronous), and streams those events to
the browser as Server-Sent Events. React never talks to the LLM directly.

Run:
    pip install -r requirements.txt
    cp .env.example .env     # add OPENAI_API_KEY or ANTHROPIC_API_KEY
    uvicorn server:app --reload --port 8000
"""

import asyncio
import json
import threading
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import embeddings_provider as emb
import llm_provider as llm
from agent_with_memory import (
    forget_all,
    forget_one,
    list_memories,
    run_agent,
)

app = FastAPI(title="Episode 5 — Agent Memory API")

# Vite's dev server proxies /api -> here, but CORS is enabled too in case
# the frontend is ever pointed at this server directly (e.g. a different port).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# session_id -> the growing short-term message list for that session.
# This is genuinely in-memory and per-process — restarting the server clears
# it, same as closing a chat app. The persisted long-term memory file is
# completely separate and unaffected by any of this.
SESSIONS: dict[str, list] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/api/session/new")
def new_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = []
    return {"session_id": session_id}


@app.get("/api/memories")
def get_memories():
    return list_memories()


@app.delete("/api/memories")
def delete_memories():
    before = len(list_memories())
    forget_all()
    return {"deleted": before}


@app.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: str):
    return {"deleted": forget_one(memory_id)}


@app.get("/api/config")
def get_config():
    return {
        "llm_provider": llm.PROVIDER,
        "llm_model": llm.MODEL,
        "embed_provider": emb.EMBED_PROVIDER,
        "embed_model": emb.EMBED_MODEL,
    }


def _sse(event: str, data) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Streams the live agent trace as SSE, then a final "final" event with the
    answer, then closes. Runs the (synchronous) agent in a background thread
    and relays its on_event() calls onto an asyncio queue so the async
    generator below can yield them as they happen, not all at once at the end.
    """
    messages = SESSIONS.setdefault(req.session_id, [])
    loop = asyncio.get_event_loop()
    q: asyncio.Queue = asyncio.Queue()

    def on_event(indent: int, kind: str, text: str) -> None:
        if kind in ("banner", "final"):
            return  # the request body / run_agent's return value already carry this
        if kind == "memory":
            items = json.loads(text) if text else []
            payload = {"items": items}
        else:
            payload = {"indent": indent, "text": text}
        loop.call_soon_threadsafe(q.put_nowait, (kind, payload))

    def worker():
        try:
            answer, _ = run_agent(req.message, messages=messages, on_event=on_event)
            loop.call_soon_threadsafe(q.put_nowait, ("final", {"text": answer}))
        except Exception as e:
            loop.call_soon_threadsafe(q.put_nowait, ("error", {"text": str(e)}))
        finally:
            loop.call_soon_threadsafe(q.put_nowait, None)   # sentinel: stream done

    threading.Thread(target=worker, daemon=True).start()

    async def event_stream():
        while True:
            item = await q.get()
            if item is None:
                break
            kind_out, payload = item
            yield _sse(kind_out, payload)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
