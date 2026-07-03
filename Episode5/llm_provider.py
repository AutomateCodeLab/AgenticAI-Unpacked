#!/usr/bin/env python3
"""
llm_provider.py — a thin adapter so agent_with_memory.py runs on EITHER
Anthropic (Claude) or OpenAI (GPT), picked automatically from whichever API
key is set. Only ONE key needs to be present in .env:

    OPENAI_API_KEY      -> uses GPT (Chat Completions API, function calling)
    ANTHROPIC_API_KEY   -> uses Claude (Messages API, native tool use)

If BOTH are set, OPENAI_API_KEY wins by default (this repo's current
provider), unless you force one explicitly:

    LLM_PROVIDER=anthropic   # or openai
    LLM_MODEL=gpt-4o         # optional override of the default model

Every provider-specific detail (message shapes, tool schema, response
parsing) lives in this one file. agent_with_memory.py never imports
`anthropic` or `openai` directly — it only calls chat(), append_assistant_turn(),
and append_tool_results(), and reads the normalized Reply. That's what makes
switching providers a one-file change instead of a rewrite.

(This file is identical in spirit to Episode4/llm_provider.py — copied here
rather than shared/imported across episodes so each episode's folder stays
independently runnable on its own.)
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4.1",
}


def _detect_provider() -> str:
    forced = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if forced in ("anthropic", "openai"):
        return forced
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        return "anthropic"
    raise RuntimeError(
        "No LLM API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in "
        "Episode5/.env — see README.md 'Choose a provider' for how to get "
        "either one."
    )


PROVIDER = _detect_provider()
MODEL = os.environ.get("LLM_MODEL", "").strip() or DEFAULT_MODELS[PROVIDER]

if PROVIDER == "anthropic":
    from anthropic import Anthropic
    _client = Anthropic()
else:
    from openai import OpenAI
    _client = OpenAI()


class Reply:
    """Normalized response — the same shape regardless of provider."""

    def __init__(self, texts, tool_calls, raw_assistant_msg, is_tool_use):
        self.texts = texts                            # list[str]
        self.tool_calls = tool_calls                   # list[{"id","name","input"}]
        self.raw_assistant_msg = raw_assistant_msg      # provider-native message to append
        self.is_tool_use = is_tool_use                  # bool


def _openai_tools(tools):
    """Convert this project's Anthropic-shaped tool schema to OpenAI's function-calling shape."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


def chat(system: str, messages: list, tools: list, max_tokens: int) -> Reply:
    """
    messages: the portable conversation so far — a list of plain
    {"role": "user"/"assistant"/..., "content": ...} dicts. Use
    append_assistant_turn()/append_tool_results() to keep growing it in the
    shape the active provider expects.
    """
    if PROVIDER == "anthropic":
        resp = _client.messages.create(
            model=MODEL, max_tokens=max_tokens, system=system,
            tools=tools, messages=messages,
        )
        texts = [b.text.strip() for b in resp.content if b.type == "text" and b.text.strip()]
        tool_calls = [
            {"id": b.id, "name": b.name, "input": b.input}
            for b in resp.content if b.type == "tool_use"
        ]
        return Reply(texts, tool_calls, resp.content, resp.stop_reason == "tool_use")

    # openai
    oa_messages = [{"role": "system", "content": system}] + messages
    resp = _client.chat.completions.create(
        model=MODEL,
        max_completion_tokens=max_tokens,
        messages=oa_messages,
        tools=_openai_tools(tools) if tools else None,
    )
    msg = resp.choices[0].message
    texts = [msg.content.strip()] if msg.content and msg.content.strip() else []
    tool_calls = [
        {
            "id": tc.id,
            "name": tc.function.name,
            "input": json.loads(tc.function.arguments or "{}"),
        }
        for tc in (msg.tool_calls or [])
    ]
    assistant_msg = {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": [
            {
                "id": tc.id, "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in (msg.tool_calls or [])
        ] or None,
    }
    return Reply(texts, tool_calls, assistant_msg, bool(msg.tool_calls))


def append_assistant_turn(messages: list, reply: Reply) -> None:
    """Append the assistant's turn to the portable message list."""
    if PROVIDER == "anthropic":
        messages.append({"role": "assistant", "content": reply.raw_assistant_msg})
    else:
        messages.append(reply.raw_assistant_msg)


def append_tool_results(messages: list, results: list) -> None:
    """results: list of {"id": <call id>, "output": <tool output>}."""
    if PROVIDER == "anthropic":
        messages.append({
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": r["id"], "content": str(r["output"])}
                for r in results
            ],
        })
    else:
        for r in results:
            messages.append({
                "role": "tool",
                "tool_call_id": r["id"],
                "content": str(r["output"]),
            })
