// api.js — thin fetch wrapper around the FastAPI backend (server.py).
// Vite's dev proxy forwards /api -> http://localhost:8000 (see vite.config.js).

export async function newSession() {
  const res = await fetch("/api/session/new", { method: "POST" });
  return res.json();
}

export async function getMemories() {
  const res = await fetch("/api/memories");
  return res.json();
}

export async function deleteMemories() {
  const res = await fetch("/api/memories", { method: "DELETE" });
  return res.json();
}

export async function deleteMemory(id) {
  const res = await fetch(`/api/memories/${encodeURIComponent(id)}`, { method: "DELETE" });
  return res.json();
}

export async function getConfig() {
  const res = await fetch("/api/config");
  return res.json();
}

/**
 * Streams the live agent trace for one chat turn. `/api/chat` is a POST with
 * a JSON body, so this uses fetch + ReadableStream (not EventSource, which
 * only supports GET) and manually splits the response on SSE's blank-line
 * frame boundaries.
 *
 * onEvent(eventName, data) fires for each event: "memory" | "think" |
 * "tool_call" | "tool_result" | "final" | "error".
 */
export async function streamChat(sessionId, message, onEvent) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
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
