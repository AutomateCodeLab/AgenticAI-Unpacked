#!/usr/bin/env python3
"""
server.py — FastAPI backend for the Episode 6 React UI.

A thin HTTP/SSE wrapper around safe_agent.py. It doesn't reimplement any
guardrail logic — it plugs an `on_event` callback and a custom `approver`
into the SAME run_safe_agent()/request_approval() the terminal demo uses,
running the (synchronous) agent in a background thread and streaming its
events to the browser as Server-Sent Events.

The one genuinely new piece: the human-approval gate has to PAUSE a running
task and wait for a live click in the browser, not just stream one-way. See
`_web_approver()` below — it blocks in 1-second slices so a kill-switch click
can interrupt a pending approval too, without needing a second thread.

Run:
    pip install -r requirements.txt
    cp .env.example .env     # add OPENAI_API_KEY or ANTHROPIC_API_KEY
    uvicorn server:app --reload --port 8000
"""

import asyncio
import json
import os
import threading
import time
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

import llm_provider as llm
from safe_agent import (
    ALLOWED_EMAIL_DOMAINS,
    AUDIT_LOG,
    COST_BUDGET_USD,
    COST_PER_STEP_USD,
    DEMO_INJECTION_PAYLOAD,
    DEMO_TASK,
    MAX_STEPS,
    RATE_LIMIT_PER_MIN,
    RISKY_TOOLS,
    SAFE_TOOLS,
    SANDBOX,
    run_safe_agent,
)

app = FastAPI(title="Episode 6 — Safe Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

APPROVAL_TIMEOUT_S = 120   # auto-deny a pending approval if no human responds

# request_id -> threading.Event; set by /api/approve to unblock the waiting agent
PENDING: dict[str, threading.Event] = {}
# request_id -> the human's decision, read once by the waiting approver
DECISIONS: dict[str, bool] = {}
# task_id -> True once a human clicks the kill switch for that run
KILLED: dict[str, bool] = {}


class RunRequest(BaseModel):
    task_id: str
    task: str
    defended: bool = True   # Layer 3 toggle — False demos the injection vulnerability


class ApproveRequest(BaseModel):
    request_id: str
    approved: bool


class KillRequest(BaseModel):
    task_id: str


@app.post("/api/task/new")
def new_task():
    return {"task_id": str(uuid.uuid4())}


@app.post("/api/approve")
def approve(req: ApproveRequest):
    DECISIONS[req.request_id] = req.approved
    ev = PENDING.get(req.request_id)
    if ev is not None:
        ev.set()
    return {"ok": True}


@app.post("/api/kill")
def kill(req: KillRequest):
    KILLED[req.task_id] = True
    return {"ok": True}


@app.get("/api/audit-log")
def audit_log(task_id: str | None = None):
    if task_id:
        return [e for e in AUDIT_LOG if e.get("task_id") == task_id]
    return AUDIT_LOG


@app.get("/api/config")
def get_config():
    return {
        "llm_provider": llm.PROVIDER,
        "llm_model": llm.MODEL,
        "risky_tools": sorted(RISKY_TOOLS),
        "safe_tools": sorted(SAFE_TOOLS),
        "allowed_email_domains": sorted(ALLOWED_EMAIL_DOMAINS),
        "cost_budget_usd": COST_BUDGET_USD,
        "cost_per_step_usd": COST_PER_STEP_USD,
        "max_steps": MAX_STEPS,
        "rate_limit_per_min": RATE_LIMIT_PER_MIN,
        "demo_task": DEMO_TASK,
    }


@app.post("/api/demo/plant-injection")
def plant_injection():
    """Writes the same prompt-injection payload the CLI demo uses into the
    sandbox, so the UI's 'Try the injection demo' button reproduces exactly
    what `python safe_agent.py` does with no arguments. Returns the file
    content too, so the UI can show exactly what got planted without anyone
    needing to go find the file on disk."""
    path = os.path.join(SANDBOX, "notes.txt")
    with open(path, "w") as f:
        f.write(DEMO_INJECTION_PAYLOAD)
    return {"planted": True, "path": path, "content": DEMO_INJECTION_PAYLOAD, "task": DEMO_TASK}


def _sse(event: str, data) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


def _make_web_approver(task_id: str):
    """
    Blocks the agent's background thread until a human calls /api/approve for
    this request_id — checked in 1-second slices so /api/kill can interrupt a
    PENDING approval too, and so a human who never responds auto-denies after
    APPROVAL_TIMEOUT_S instead of hanging the task forever.
    """
    def approver(request_id: str, tool_name: str, args: dict) -> tuple:
        ev = threading.Event()
        PENDING[request_id] = ev
        deadline = time.monotonic() + APPROVAL_TIMEOUT_S
        try:
            while not ev.wait(timeout=1.0):
                if KILLED.get(task_id, False):
                    return False, "killed"
                if time.monotonic() > deadline:
                    return False, "timeout"
            return DECISIONS.pop(request_id, False), "human"
        finally:
            PENDING.pop(request_id, None)
    return approver


@app.post("/api/task/run")
async def run_task(req: RunRequest):
    loop = asyncio.get_event_loop()
    q: asyncio.Queue = asyncio.Queue()

    last_kind = None

    def on_event(indent: int, kind: str, text: str) -> None:
        nonlocal last_kind
        if kind == "task_started":
            return  # the request body already carries this — skip on the wire
        last_kind = kind
        if kind in ("approval_needed", "approval_resolved", "audit"):
            payload = json.loads(text)
        else:
            payload = {"text": text}
        loop.call_soon_threadsafe(q.put_nowait, (kind, payload))

    def worker():
        try:
            answer = run_safe_agent(
                req.task,
                on_event=on_event,
                approver=_make_web_approver(req.task_id),
                is_killed=lambda: KILLED.get(req.task_id, False),
                task_id=req.task_id,
                defended=req.defended,
            )
            # run_safe_agent already emits a terminal "final" or "killed" event
            # on most exit paths — only synthesize one here for the exit paths
            # that don't (budget exceeded, max-steps reached), so the stream
            # always ends with exactly one terminal event, never two.
            if last_kind not in ("final", "killed"):
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
            kind, payload = item
            yield _sse(kind, payload)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
