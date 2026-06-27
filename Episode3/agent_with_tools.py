#!/usr/bin/env python3
"""
agent_with_tools.py — Episode 3 of Agentic AI, Unpacked.
Extends Episode 2's tiny_agent.py with REAL tools: search, file I/O, APIs.

Run:
    pip install anthropic requests python-dotenv
    cp .env.example .env
    # edit .env with your SERPAPI_KEY, GITHUB_TOKEN, etc.
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent_with_tools.py

Tools in this file:
    - web_search: search the web using SerpAPI
    - read_file: read a text file from disk
    - write_file: write a file to disk (sandboxed)
    - github_api: call GitHub API directly
    - calculator: safe arithmetic (from Ep 2)

References:
    - Anthropic tool use docs: https://docs.claude.com
    - SerpAPI: https://serpapi.com
    - GitHub API: https://docs.github.com/rest
"""

import json
import os
import ast
import operator
import shutil
import sys
from datetime import date

import requests
from dotenv import load_dotenv
from anthropic import Anthropic

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_HERE, ".env")
_ENV_EXAMPLE_PATH = os.path.join(_HERE, ".env.example")

# ANTHROPIC_API_KEY is required to start; the others degrade gracefully per tool
_REQUIRED_KEYS = {"ANTHROPIC_API_KEY"}
_OPTIONAL_KEYS = {"SERPAPI_KEY", "GITHUB_TOKEN"}


def _bootstrap_env() -> None:
    if not os.path.exists(_ENV_PATH):
        if not os.path.exists(_ENV_EXAMPLE_PATH):
            print("ERROR: No .env or .env.example found in Episode3/. Cannot start.")
            sys.exit(1)
        shutil.copy(_ENV_EXAMPLE_PATH, _ENV_PATH)
        print(f"[setup] Created .env from .env.example — fill in your keys at:\n        {_ENV_PATH}\n")

    load_dotenv(_ENV_PATH)

    # Read placeholder values from .env.example so we can detect unfilled entries
    placeholders: dict[str, str] = {}
    if os.path.exists(_ENV_EXAMPLE_PATH):
        with open(_ENV_EXAMPLE_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    placeholders[key.strip()] = val.strip()

    def _is_unset(key: str) -> bool:
        val = os.environ.get(key, "").strip()
        return not val or val == placeholders.get(key, "")

    missing_required = [k for k in _REQUIRED_KEYS if _is_unset(k)]
    missing_optional = [k for k in _OPTIONAL_KEYS if _is_unset(k)]

    if missing_optional:
        print("[setup] Optional keys not set — some tools will be unavailable:")
        for k in missing_optional:
            print(f"         {k}  →  add to {_ENV_PATH}")
        print()

    if missing_required:
        print("ERROR: Required key(s) are missing or still set to placeholder values:")
        for k in missing_required:
            print(f"         {k}  →  set in {_ENV_PATH}")
        print()
        sys.exit(1)


_bootstrap_env()
client = Anthropic()


def _warn_missing_key(key: str) -> None:
    print(f"\n[config] {key} is not set — add it to {_ENV_PATH} and re-run to enable this tool.\n")
MODEL = "claude-sonnet-4-6"

# Safety: where agents can write files
AGENT_WORKSPACE = os.path.expanduser("~/.agent_workspace")
os.makedirs(AGENT_WORKSPACE, exist_ok=True)

# Guardrails
MAX_STEPS = 10
MAX_TOKENS_PER_TURN = 2048
SEARCH_MAX_RESULTS = 5
FILE_MAX_SIZE_MB = 10


# ======================================================================
# 1) REAL TOOLS — these actually do things
# ======================================================================

def web_search(query: str, max_results: int = 3) -> list:
    """Search the web and return the top results.
    
    Args:
        query: what to search for (e.g. "latest breakthroughs in agentic AI")
        max_results: how many to return (default 3, max 10)
    
    Returns:
        List of dicts with 'title', 'url', 'snippet' keys.
    """
    if max_results > SEARCH_MAX_RESULTS:
        max_results = SEARCH_MAX_RESULTS
    
    try:
        api_key = os.environ.get("SERPAPI_KEY")
        if not api_key:
            _warn_missing_key("SERPAPI_KEY")
            return [{"error": "SERPAPI_KEY not set — web_search unavailable"}]
        
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "num": max_results,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for r in data.get("organic_results", [])[:max_results]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            })
        return results if results else [{"note": "No results found"}]
    except requests.exceptions.Timeout:
        return [{"error": "Search timed out after 10s"}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Search API error: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]


def read_file(path: str) -> str:
    """Read a text file and return its contents.
    
    Args:
        path: relative path within the agent workspace (e.g. "notes.txt")
    
    Returns:
        File contents as a string, or an error message.
    """
    try:
        full_path = os.path.join(AGENT_WORKSPACE, path)
        # Safety: prevent path traversal
        if not os.path.abspath(full_path).startswith(os.path.abspath(AGENT_WORKSPACE)):
            return f"Error: path '{path}' is outside the agent workspace"
        
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file '{path}' not found in workspace"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Write content to a file in the agent workspace.
    
    Args:
        path: relative path within workspace (e.g. "output.txt")
        content: what to write
    
    Returns:
        Success message or error.
    """
    try:
        full_path = os.path.join(AGENT_WORKSPACE, path)
        # Safety: prevent path traversal
        if not os.path.abspath(full_path).startswith(os.path.abspath(AGENT_WORKSPACE)):
            return f"Error: path '{path}' is outside the agent workspace"
        
        # Safety: file size limit
        if len(content.encode("utf-8")) > FILE_MAX_SIZE_MB * 1024 * 1024:
            return f"Error: file would exceed {FILE_MAX_SIZE_MB}MB limit"
        
        # Create parent directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written to {path} in workspace"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def github_api(endpoint: str, method: str = "GET", body: dict = None) -> dict:
    """Call the GitHub API.
    
    Args:
        endpoint: API path (e.g. "/repos/anthropics/anthropic-sdk-python/issues")
        method: HTTP method (GET, POST, etc.)
        body: optional JSON body for POST/PATCH
    
    Returns:
        Parsed JSON response or error dict.
    """
    try:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            _warn_missing_key("GITHUB_TOKEN")
            return {"error": "GITHUB_TOKEN not set — github_api unavailable"}
        
        url = f"https://api.github.com{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=body or {}, timeout=10)
        elif method == "PATCH":
            resp = requests.patch(url, headers=headers, json=body or {}, timeout=10)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}
        
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"GitHub API {e.response.status_code}: {e.response.text[:200]}"}
    except requests.exceptions.Timeout:
        return {"error": "GitHub API request timed out"}
    except Exception as e:
        return {"error": f"GitHub API error: {str(e)}"}


def calculator(expression: str) -> float:
    """Evaluate a safe arithmetic expression.
    
    Args:
        expression: e.g. "24 * 365 / 12"
    
    Returns:
        Numeric result or error message.
    """
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
    
    try:
        return _safe_eval(ast.parse(expression, mode="eval").body)
    except Exception as e:
        return f"Error: {str(e)}"


# ======================================================================
# 2) TOOL SCHEMAS — what the model sees
# ======================================================================

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information. Returns the top results with titles, URLs, and snippets. Use this to find current information, research a topic, or answer questions that require up-to-date data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for (e.g. 'latest breakthroughs in agentic AI')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "How many results to return (1-5, default 3)",
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file from the agent workspace. Use this to load documents, notes, or data that the agent should analyze.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path relative to workspace (e.g. 'notes.txt' or 'data/results.json')",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file in the agent workspace. Use this to save analysis, reports, or structured output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path relative to workspace (e.g. 'output.txt')",
                },
                "content": {
                    "type": "string",
                    "description": "What to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "github_api",
        "description": "Call the GitHub API directly. Requires GITHUB_TOKEN in environment. Use for fetching repos, issues, PRs, user data, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint path (e.g. '/repos/anthropics/anthropic-sdk-python/issues')",
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PATCH"],
                    "description": "HTTP method (default GET)",
                },
                "body": {
                    "type": "object",
                    "description": "Request body for POST/PATCH (optional)",
                },
            },
            "required": ["endpoint"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a safe arithmetic expression (no eval, just math).",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression (e.g. '24 * 365 / 12')",
                },
            },
            "required": ["expression"],
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    """Dispatch a tool call to the matching function."""
    if name == "web_search":
        result = web_search(args["query"], args.get("max_results", 3))
    elif name == "read_file":
        result = read_file(args["path"])
    elif name == "write_file":
        result = write_file(args["path"], args["content"])
    elif name == "github_api":
        result = github_api(args["endpoint"], args.get("method", "GET"), args.get("body"))
    elif name == "calculator":
        result = calculator(args["expression"])
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return json.dumps(result) if isinstance(result, (dict, list)) else str(result)


# ======================================================================
# 3) THE AGENT LOOP (from Ep 2, same structure)
# ======================================================================

def run_agent(task: str, max_steps: int = MAX_STEPS) -> str:
    """Run an agent task with real tools."""
    print(f"\n🧑  TASK: {task}\n" + "─" * 80)
    messages = [{"role": "user", "content": task}]
    
    for step in range(1, max_steps + 1):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_PER_TURN,
            tools=TOOLS,
            messages=messages,
        )
        
        # Show the model's reasoning
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                print(f"🧠  step {step} · {block.text.strip()[:100]}")
        
        # Done if no more tool calls
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text").strip()
            print("─" * 80)
            print(f"✅  FINAL ANSWER:\n{answer}\n")
            return answer
        
        # Otherwise, run tools and feed results back
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"🔧  step {step} · {block.name}({json.dumps(block.input)[:60]}...)")
                try:
                    output = run_tool(block.name, block.input)
                    print(f"👀  step {step} · {output[:80]}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    })
                except Exception as e:
                    print(f"⚠️   step {step} · error: {e}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"error: {str(e)}",
                        "is_error": True,
                    })
        messages.append({"role": "user", "content": results})
    
    print(f"⛔  Hit max_steps ({max_steps}). Agent stopped.")
    return None


# ======================================================================
# 4) DEMO TASKS
# ======================================================================

if __name__ == "__main__":
    # Task 1: search and save
    task1 = (
        "Search for the latest news about agentic AI, "
        "then save a summary to 'ai_news.txt' in the workspace."
    )
    
    # Task 2: multi-step (if GITHUB_TOKEN is set)
    task2 = (
        "Find the latest 3 issues in the anthropic-sdk-python repo, "
        "summarize them, and save to 'github_issues.txt'."
    )
    
    # Task 3: simple (no external API)
    task3 = (
        "I want to read 'test.txt' from my workspace, "
        "count the words in it, and tell me the result."
    )
    
    print("\n" + "=" * 80)
    print("AGENT WITH REAL TOOLS — Episode 3")
    print("=" * 80)
    
    print(f"\nWorkspace: {AGENT_WORKSPACE}")
    print(f"Max steps: {MAX_STEPS}, Max tokens: {MAX_TOKENS_PER_TURN}")
    
    # Create a test file for task 3
    test_file = os.path.join(AGENT_WORKSPACE, "test.txt")
    with open(test_file, "w") as f:
        f.write("The quick brown fox jumps over the lazy dog. " * 5)
    print(f"Created test file: {test_file}")
    
    # Run task 3 (doesn't need API keys)
    # run_agent(task3)
    
    # Uncomment to run tasks 1 and 2 (requires SERPAPI_KEY, GITHUB_TOKEN)
    # run_agent(task1)
    run_agent(task2)