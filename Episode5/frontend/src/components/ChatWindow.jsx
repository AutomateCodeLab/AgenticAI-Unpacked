import { useEffect, useRef, useState } from "react";
import MemoryChips from "./MemoryChips.jsx";

const TRACE_ICON = { think: "🧠", tool_call: "🔧", tool_result: "👀" };

// Sample messages for a reliable live demo — pick a "Teach" one, send it,
// click "New Session," then pick a "Recall" one to prove cross-session
// memory without typing on camera. Also listed in README.md.
const SAMPLE_MESSAGES = [
  { label: "🧑 Teach: name + hobby + project", text: "Hi! My name is Maneesh, I love hiking, and my project is called Agent Unpacked." },
  { label: "🧑 Teach: tech stack", text: "I'm building a YouTube series about agentic AI, I prefer TypeScript, and my favorite framework is React." },
  { label: "🧑 Teach: personal goal", text: "My name is Alex, I'm vegetarian, and I'm training for a marathon in October." },
  { label: "🔍 Recall: everything", text: "What do you remember about me?" },
  { label: "🔍 Recall: project only", text: "What's my current project called?" },
  { label: "🔍 Recall: preference only", text: "What programming language do I prefer?" },
];

function TraceAccordion({ trace }) {
  if (!trace || trace.length === 0) return null;
  return (
    <details className="trace">
      <summary>🔍 {trace.length} step{trace.length > 1 ? "s" : ""} — show trace</summary>
      {trace.map((t, i) => (
        <div className={`trace-line ${t.kind}`} key={i}>
          {TRACE_ICON[t.kind] || "•"} {t.text}
        </div>
      ))}
    </details>
  );
}

export default function ChatWindow({ sessionId, onTurnComplete, sendChat }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  // Reset the visible conversation whenever the session changes (new session
  // click) — this is the whole point: short-term resets, long-term doesn't.
  useEffect(() => {
    setMessages([]);
  }, [sessionId]);

  async function handleSend() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setBusy(true);

    setMessages((m) => [...m, { role: "user", text }]);
    const assistantIndex = messages.length + 1;
    setMessages((m) => [...m, { role: "assistant", text: "", trace: [], memory: [], pending: true }]);

    const update = (fn) =>
      setMessages((m) => {
        const copy = [...m];
        copy[assistantIndex] = fn(copy[assistantIndex]);
        return copy;
      });

    await sendChat(text, (eventName, data) => {
      if (eventName === "memory") {
        update((msg) => ({ ...msg, memory: data.items || [] }));
      } else if (eventName === "think" || eventName === "tool_call" || eventName === "tool_result") {
        update((msg) => ({ ...msg, trace: [...msg.trace, { kind: eventName, text: data.text }] }));
      } else if (eventName === "final") {
        update((msg) => ({ ...msg, text: data.text, pending: false }));
      } else if (eventName === "error") {
        update((msg) => ({ ...msg, text: `⚠️ ${data.text}`, pending: false }));
      }
    });

    setBusy(false);
    onTurnComplete?.();
  }

  return (
    <div className="main-col">
      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="memory-empty fade-in" key={sessionId}>
            Say hi and tell it something about yourself — then click "New Session" and ask what it remembers.
          </div>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div className="bubble user fade-in" key={i}>{m.text}</div>
          ) : (
            <div className="fade-in" key={i}>
              <MemoryChips items={m.memory} />
              <div className={`bubble assistant${m.pending ? " pending" : ""}`}>
                {m.text || (
                  <span className="thinking-dots">
                    <span></span><span></span><span></span>
                  </span>
                )}
              </div>
              <TraceAccordion trace={m.trace} />
            </div>
          ),
        )}
      </div>
      <div className="composer">
        <select
          className="sample-picker"
          value=""
          disabled={busy}
          onChange={(e) => {
            if (e.target.value) setInput(e.target.value);
            e.target.value = "";
            // Move focus to the text input so Enter sends immediately —
            // without this, focus stays on the <select> and Enter does nothing.
            inputRef.current?.focus();
          }}
        >
          <option value="" disabled>
            Sample message…
          </option>
          {SAMPLE_MESSAGES.map((s) => (
            <option value={s.text} key={s.label}>
              {s.label}
            </option>
          ))}
        </select>
        <input
          ref={inputRef}
          value={input}
          placeholder="Message the assistant…"
          disabled={busy}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} disabled={busy}>
          {busy ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
