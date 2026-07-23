// api.js — thin fetch wrapper around the FastAPI backend (server.py).
// Vite's dev proxy forwards /api -> http://localhost:8000 (see vite.config.js).

export async function newTask() {
  const res = await fetch("/api/task/new", { method: "POST" });
  return res.json();
}

export async function getConfig() {
  const res = await fetch("/api/config");
  return res.json();
}

export async function getAuditLog(taskId) {
  const url = taskId ? `/api/audit-log?task_id=${encodeURIComponent(taskId)}` : "/api/audit-log";
  const res = await fetch(url);
  return res.json();
}

export async function approve(requestId, approved) {
  const res = await fetch("/api/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: requestId, approved }),
  });
  return res.json();
}

export async function kill(taskId) {
  const res = await fetch("/api/kill", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId }),
  });
  return res.json();
}

export async function plantInjection() {
  const res = await fetch("/api/demo/plant-injection", { method: "POST" });
  return res.json();
}

/**
 * Streams the live agent trace for one task run. `/api/task/run` is a POST
 * with a JSON body, so this uses fetch + ReadableStream (not EventSource,
 * which only supports GET) and manually splits the response on SSE's
 * blank-line frame boundaries.
 *
 * onEvent(eventName, data) fires for each event: "think" | "tool_call" |
 * "tool_result" | "approval_needed" | "approval_resolved" | "audit" |
 * "killed" | "final" | "error".
 */
export async function streamTask(taskId, task, defended, onEvent) {
  const res = await fetch("/api/task/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId, task, defended }),
  });
  if (!res.ok || !res.body) {
    onEvent("error", { text: `Request failed (HTTP ${res.status})` });
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      let eventName = "message";
      let dataLine = "";
      for (const line of rawEvent.split("\n")) {
        if (line.startsWith("event:")) eventName = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLine += line.slice(5).trim();
      }
      if (!dataLine) continue;
      try {
        onEvent(eventName, JSON.parse(dataLine));
      } catch {
        onEvent(eventName, dataLine);
      }
    }
  }
}
