# Episode 3 — Agent with Real Tools

**Agentic AI, Unpacked · YouTube Series**

This episode extends the bare-bones ReAct loop from Episode 2 into an agent that can actually do things in the world: search the web, read and write files, call external APIs, and compute arithmetic — all while staying within explicit safety guardrails.

---

## What this episode covers

| Concept | Where to find it |
|---|---|
| Real tool functions | `agent_with_tools.py` lines 55–240 |
| Tool JSON schemas | `agent_with_tools.py` lines 228–320 |
| Tool dispatcher | `agent_with_tools.py` lines 321–341 |
| Agent loop | `agent_with_tools.py` lines 343–390 |
| Guardrails / safety constants | `agent_with_tools.py` lines 41–50 |
| Demo tasks | `agent_with_tools.py` lines 402–437 |
| Manim animations | `Episode 3/ep03_scenes.py` |
| Live demo presenter script | `DEMO_SCRIPT.md` |

---

## Project structure

```
Episode3/
  agent_with_tools.py   — the agent: tools, schemas, loop, demo tasks
  .env.example          — template; copy to .env and fill in your keys
  .gitignore            — keeps .env out of version control
  DEMO_SCRIPT.md        — timestamped walkthrough script for the live demo
  README.md             — this file

Episode 3/              — Manim animation scenes
  ep03_scenes.py        — all visual scenes for the episode

brand.py                — shared colour palette (root level)
viz_kit.py              — shared Manim helpers (root level)
render_all.sh           — renders all scenes, both opaque and transparent
renders/                — output directory (gitignored)
.venv/                  — Python virtualenv (gitignored)
```

---

## Quick start

### 1. Activate the virtualenv

```bash
# From the repo root
source .venv/bin/activate
```

### 2. Configure environment variables

```bash
cd Episode3
cp .env.example .env
# Open .env and fill in the keys you need (see table below)
```

| Variable | Required for | Where to get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | **All tasks** | console.anthropic.com → API Keys |
| `SERPAPI_KEY` | Task 1 — web search | serpapi.com → Dashboard |
| `GITHUB_TOKEN` | Task 2 — GitHub API | github.com → Settings → Developer → Personal access tokens |

> **Tip:** Set `ANTHROPIC_API_KEY` in your shell profile (`~/.zshrc`) so it is always available without needing a `.env` file.

### 3. Run the agent

```bash
python agent_with_tools.py
```

By default only **Task 3** runs (reads a test file and counts words). It requires only `ANTHROPIC_API_KEY`. Tasks 1 and 2 are commented out at the bottom of the file — uncomment them after setting the relevant keys.

---

## Component walkthrough

### Guardrails and safety constants (lines 41–50)

```python
AGENT_WORKSPACE     = os.path.expanduser("~/.agent_workspace")
MAX_STEPS           = 10
MAX_TOKENS_PER_TURN = 2048
SEARCH_MAX_RESULTS  = 5
FILE_MAX_SIZE_MB    = 10
```

Every guardrail is a constant defined once and enforced at the point of action, not in a system prompt.

| Constant | What it caps | Why it matters |
|---|---|---|
| `AGENT_WORKSPACE` | Where the agent can read/write files | Prevents the agent from touching files outside a sandboxed directory |
| `MAX_STEPS` | Agent loop iterations | Stops an infinite loop if the model keeps calling tools without converging |
| `MAX_TOKENS_PER_TURN` | Claude API tokens per call | Keeps responses focused and controls cost per step |
| `SEARCH_MAX_RESULTS` | Search results returned | Prevents flooding the context window with raw search data |
| `FILE_MAX_SIZE_MB` | Write payload size | Stops a runaway write from filling disk |

---

### Tool 1 — `web_search` (lines 55–96)

```python
def web_search(query: str, max_results: int = 3) -> list:
```

Searches the web via SerpAPI and returns the top results.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query` | str | required | What to search for |
| `max_results` | int | 3 | How many results to return; hard-capped at `SEARCH_MAX_RESULTS` (5) |

**Returns** — list of dicts, each with:
```python
{"title": str, "url": str, "snippet": str}
```

**Error handling** — never raises. All failures return a list with one error dict:
```python
[{"error": "Search timed out after 10s"}]
[{"error": "SERPAPI_KEY not set in environment"}]
```

**Key design decisions**

- API key pulled from `os.environ.get("SERPAPI_KEY")` — never hardcoded
- `max_results` is clamped to `SEARCH_MAX_RESULTS` even if the model asks for more
- Separate `except` blocks for `Timeout` vs generic `RequestException` — the model reads the error message and adapts its strategy accordingly

---

### Tool 2 — `read_file` (lines 99–121)

```python
def read_file(path: str) -> str:
```

Reads a text file from the agent's sandboxed workspace.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `path` | str | Relative path within `~/.agent_workspace` (e.g. `"notes.txt"`) |

**Returns** — file contents as a string, or an error message string on failure.

**Path-traversal protection**

```python
full_path = os.path.join(AGENT_WORKSPACE, path)
if not os.path.abspath(full_path).startswith(os.path.abspath(AGENT_WORKSPACE)):
    return f"Error: path '{path}' is outside the agent workspace"
```

`os.path.abspath` resolves any `..` sequences before the check. A request like `../../etc/passwd` resolves to a path outside `AGENT_WORKSPACE` and is rejected before the filesystem is touched. The agent receives an error string and can decide how to proceed.

---

### Tool 3 — `write_file` (lines 122–151)

```python
def write_file(path: str, content: str) -> str:
```

Writes content to a file in the agent's workspace.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `path` | str | Relative path within workspace |
| `content` | str | Content to write (UTF-8) |

**Returns** — success message or error string.

**Guardrails applied**

1. **Path-traversal check** — same `abspath` validation as `read_file`
2. **Size limit** — `len(content.encode("utf-8")) > FILE_MAX_SIZE_MB * 1024 * 1024` rejects oversized writes before touching disk
3. **Directory creation** — `os.makedirs(os.path.dirname(full_path), exist_ok=True)` creates parent directories as needed so the agent doesn't need a separate "create directory" tool

---

### Tool 4 — `github_api` (lines 152–193)

```python
def github_api(endpoint: str, method: str = "GET", body: dict = None) -> dict:
```

Calls the GitHub REST API directly.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `endpoint` | str | required | API path, e.g. `"/repos/anthropics/anthropic-sdk-python/issues"` |
| `method` | str | `"GET"` | HTTP method: `"GET"`, `"POST"`, or `"PATCH"` |
| `body` | dict | `None` | JSON request body for POST/PATCH |

**Returns** — parsed JSON response dict, or an error dict:
```python
{"error": "GitHub API 403: rate limit exceeded"}
```

**Key design decisions**

- Token injected via `Authorization: Bearer` header from the environment — the agent never sees the token itself
- Unsupported HTTP methods return an error dict rather than raising, keeping the loop intact
- `HTTPError` is caught separately so the status code is included in the error message, giving the model enough information to decide whether to retry

---

### Tool 5 — `calculator` (lines 194–227)

```python
def calculator(expression: str) -> float:
```

Evaluates a safe arithmetic expression without using `eval`.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `expression` | str | Arithmetic expression, e.g. `"24 * 365 / 12"` |

**Returns** — numeric result (float), or an error string.

**How the safe evaluator works**

The function parses the expression into an AST and walks it using a whitelist of safe node types:

```python
_SAFE_OPS = {
    ast.Add: operator.add,    ast.Sub: operator.sub,
    ast.Mult: operator.mul,   ast.Div: operator.truediv,
    ast.Pow: operator.pow,    ast.Mod: operator.mod,
    ast.USub: operator.neg,   ast.UAdd: operator.pos,
}
```

Any AST node not in the whitelist raises `ValueError("unsupported expression")`, which is caught and returned as an error string. No `eval`, no `exec`, no imports possible.

---

### Tool schemas — the `TOOLS` list (lines 228–320)

The `TOOLS` list is what Claude actually reads to plan which tool to call and what to pass it. Each entry has four parts:

```python
{
    "name": "web_search",           # ← short, unambiguous
    "description": "Search the web for information. Returns the top results with "
                   "titles, URLs, and snippets. Use this to find current information, "
                   "research a topic, or answer questions that require up-to-date data.",
                   # ↑ tells the model WHEN and WHY to use this tool
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What to search for",  # ← tells the model WHAT to pass
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,   # ← constraint enforced at schema level, not runtime
            },
        },
        "required": ["query"],      # ← model knows it must always provide a query
    },
}
```

**Why the description matters most**

The model decides which tool to call by reading each tool's `description`. A vague description (`"do_stuff — does things"`) means the model won't know when to use it. A precise description (`"Search the web. Use for current information or questions that require up-to-date data"`) acts as the model's decision rule.

**Constraints in the schema vs. runtime**

Putting `"minimum": 1, "maximum": 5` in the schema means the model will never ask for 10 results. You don't need a runtime check for that specific constraint — the model respects the schema. Runtime validation (`SEARCH_MAX_RESULTS` clamp) is a second line of defence for cases where the model ignores the schema.

---

### Tool dispatcher — `run_tool` (lines 321–341)

```python
def run_tool(name: str, args: dict) -> str:
```

Routes a tool call from the model to the matching Python function and serialises the result.

```python
if name == "web_search":
    result = web_search(args["query"], args.get("max_results", 3))
...
return json.dumps(result) if isinstance(result, (dict, list)) else str(result)
```

The dispatcher:
- Applies argument defaults (`args.get("max_results", 3)`)
- Converts structured results (dicts, lists) to JSON strings the model can read
- Converts plain results (numbers, strings) with `str()`
- Returns a string for unknown tool names rather than raising

---

### The agent loop — `run_agent` (lines 343–390)

```python
def run_agent(task: str, max_steps: int = MAX_STEPS) -> str:
```

This is the same ReAct loop from Episode 2, now with real tools.

```
think (model responds) → tool calls? → yes → dispatch → feed results back → think again
                                     → no  → return final answer
```

**Step by step**

```python
resp = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS_PER_TURN,
    tools=TOOLS,          # ← model sees the schema list
    messages=messages,
)
```

1. **Think** — Claude sees the task and tool schemas, produces a response
2. **Check stop reason** — if `resp.stop_reason != "tool_use"`, the model is done; return the answer
3. **Collect tool calls** — iterate `resp.content` for blocks with `type == "tool_use"`
4. **Dispatch** — call `run_tool(block.name, block.input)` for each
5. **Feed results back** — append a `tool_result` message with the matching `tool_use_id`
6. **Loop** — go back to step 1 with the updated messages list

**Error handling inside the loop**

```python
try:
    output = run_tool(block.name, block.input)
    results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
except Exception as e:
    results.append({
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": f"error: {str(e)}",
        "is_error": True,
    })
```

If a tool raises unexpectedly, the loop catches it, marks the result `is_error: True`, and continues. The agent loop never dies because a tool misbehaves.

**Max steps guard**

```python
print(f"⛔  Hit max_steps ({max_steps}). Agent stopped.")
return None
```

If the model is stuck calling tools without converging, the loop terminates at `MAX_STEPS` (10). This is the outermost cost guardrail.

---

### Trace output

The loop prints a trace so you can follow every decision:

```
🧠  step 1 · I need to search for this first...
🔧  step 1 · web_search({"query": "agentic AI trends 2026"}...)
👀  step 1 · [{"title": "...", "url": "...", "snippet": "..."}]
🧠  step 2 · I have results, now I'll write the summary...
🔧  step 2 · write_file({"path": "ai_news.txt", "content": "..."}...)
👀  step 2 · File written to ai_news.txt in workspace
✅  FINAL ANSWER:
I searched for agentic AI trends and saved a summary to ai_news.txt.
```

---

## Demo tasks

Three tasks are defined at the bottom of `agent_with_tools.py`:

| Task | What the agent does | Keys required |
|---|---|---|
| `task3` *(default)* | Reads `~/.agent_workspace/test.txt`, counts words | `ANTHROPIC_API_KEY` only |
| `task1` | Searches "latest agentic AI news", writes summary to workspace | + `SERPAPI_KEY` |
| `task2` | Fetches 3 newest issues from `anthropics/anthropic-sdk-python`, writes summary | + `GITHUB_TOKEN` |

To run task1 or task2, uncomment the relevant `run_agent(...)` call at the bottom of the file.

---

## Security notes

### API key handling

All keys are read from environment variables (`os.environ.get(...)`) or loaded from `.env` via `python-dotenv`. The `.env` file is listed in `.gitignore` and must never be committed. If a key is missing, the tool function returns an error dict — the agent adapts rather than crashing.

### File sandbox

Both `read_file` and `write_file` validate that the resolved absolute path starts with `os.path.abspath(AGENT_WORKSPACE)`. A path like `../../etc/shadow` resolves outside the workspace and is rejected before any I/O is attempted.

### No `eval`

The `calculator` tool parses expressions into an AST and walks only whitelisted node types. Arbitrary code execution is not possible regardless of what the model passes.

---

## Episode 3 Manim animations

The file `Episode 3/ep03_scenes.py` contains all visual scenes rendered for the episode.

### Scenes

| Scene | Duration | Type | Placed at | What it shows |
|---|---|---|---|---|
| `Ep03TitleSting` | ~2.5 s | Transparent overlay | 1:00 | Episode title card |
| `ToyVsRealTool` | ~8 s | Full-frame cutaway | 1:30 | Toy tool (predictable) vs real tool (messy, costly) — same schema, different reality |
| `ToolSchemaAnatomy` | ~10 s | Full-frame cutaway | 2:30 | Four parts of a tool schema: name, description, input_schema, examples |
| `MultiToolChaining` | ~10 s | Full-frame cutaway | 11:30 | Agent chains web_search → reason → write_file without being told to |
| `ErrorRecovery` | ~9 s | Transparent overlay | 16:30 | Rate-limit recovery and path-traversal block, shown as terminal trace |
| `CostGuardrail` | ~9 s | Full-frame cutaway | 19:00 | Runaway loop vs MAX_STEPS guardrail |
| `ToolMistakes` | ~130 s | Full-frame cutaway | 21:00 | 6 tool-design mistakes with wrong/better code pairs and a one-line principle |
| `FrameworkDecision` | ~62 s | Full-frame cutaway | 23:00 | "Do you need a framework?" — honest answer, what they add, the warning, the foundation stack |
| `Ep03Outro` | ~25 s | Full-frame cutaway | Episode end | Recap chips, neat-idea-to-production bridge, tutorial vs tool punchline |
| `Ep04Teaser` | ~19 s | Full-frame cutaway | Post-outro | Teaser: three-agent triangle (PLANNER/SEARCH/SYNTHESIS) + "you'll get it" close |

### Rendering a single scene

```bash
# From the repo root, with .venv active

# Opaque MP4 (full-frame cutaway)
manim -qh --media_dir renders "Episode 3/ep03_scenes.py" ToolMistakes

# Transparent MOV (for overlay — verify argb pixel format with ffprobe)
manim -qh -t --media_dir renders "Episode 3/ep03_scenes.py" ToolMistakes
```

Output lands in `renders/videos/ep03_scenes/1080p60/`.

### Rendering all scenes

```bash
# Quick test pass (low quality, fast)
bash render_all.sh --test

# Final renders (opaque + transparent for every scene)
bash render_all.sh
```

---

## Dependencies

```
anthropic          # Claude API client
requests           # HTTP for search and GitHub
python-dotenv      # loads .env into os.environ
manim              # animation engine (Community Edition v0.18+)
```

Install into the repo virtualenv:

```bash
source .venv/bin/activate
pip install anthropic requests python-dotenv manim
```

`ffmpeg` must be available on your PATH for Manim to render video. Check with `ffmpeg -version`; install via `brew install ffmpeg` on macOS.

---

## Live demo script

`DEMO_SCRIPT.md` is a timestamped presenter script for the live coding walkthrough. Each section has:

- `[SCREEN]` — what to display
- `[POINT TO: line N]` — where to scroll in the editor
- `[RUN]` — command to run live
- Talking points to read out loud

The line map at the bottom maps every key section of `agent_with_tools.py` to its line numbers for quick navigation during the demo.
