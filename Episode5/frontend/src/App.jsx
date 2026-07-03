import { useCallback, useEffect, useState } from "react";
import ChatWindow from "./components/ChatWindow.jsx";
import MemoryPanel from "./components/MemoryPanel.jsx";
import NewSessionButton from "./components/NewSessionButton.jsx";
import Toast from "./components/Toast.jsx";
import { deleteMemories, deleteMemory, getConfig, getMemories, newSession, streamChat } from "./api.js";

const POLL_MS = 6000;

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [config, setConfig] = useState(null);
  const [memories, setMemories] = useState([]);
  const [switching, setSwitching] = useState(false);
  const [forgetting, setForgetting] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = useCallback((msg) => {
    setToast({ msg, id: Date.now() });
  }, []);

  const refreshMemories = useCallback(() => {
    getMemories().then(setMemories).catch(() => {});
  }, []);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});
    newSession().then((r) => setSessionId(r.session_id));
    refreshMemories();
  }, [refreshMemories]);

  // Keep the memory panel LIVE without waiting for a chat turn: poll on an
  // interval, and immediately refetch whenever the tab regains focus (e.g.
  // memory was cleared/changed elsewhere — the CLI, another tab, a server
  // restart). A stale panel showing facts that no longer exist server-side
  // is exactly the kind of "looks broken" gap a reactive UI shouldn't have.
  useEffect(() => {
    const interval = setInterval(refreshMemories, POLL_MS);
    const onVisible = () => {
      if (document.visibilityState === "visible") refreshMemories();
    };
    document.addEventListener("visibilitychange", onVisible);
    window.addEventListener("focus", onVisible);
    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisible);
      window.removeEventListener("focus", onVisible);
    };
  }, [refreshMemories]);

  async function handleNewSession() {
    setSwitching(true);
    try {
      const r = await newSession();
      setSessionId(r.session_id);
      // Intentionally NOT clearing `memories` here — persisted long-term
      // memory survives a new session. That's the entire point of this demo.
      showToast("🔄 New session started — long-term memory is untouched");
    } finally {
      setSwitching(false);
    }
  }

  async function handleForget() {
    setForgetting(true);
    try {
      const r = await deleteMemories();
      refreshMemories();
      showToast(`🗑️ Forgot ${r.deleted} memor${r.deleted === 1 ? "y" : "ies"}`);
    } finally {
      setForgetting(false);
    }
  }

  async function handleForgetOne(id) {
    await deleteMemory(id);
    refreshMemories();
    showToast("🗑️ Forgot that memory");
  }

  const sendChat = useCallback(
    (text, onEvent) => streamChat(sessionId, text, onEvent),
    [sessionId],
  );

  return (
    <div className="app">
      <div className="main-col" style={{ gridColumn: "1" }}>
        <div className="header">
          <div>
            <h1>🧠 Personal AI Assistant</h1>
            <div className="sub">Episode 5 · Short-term, long-term & semantic memory</div>
          </div>
          {config && (
            <span className="badge">
              LLM: <b>{config.llm_provider}</b>/{config.llm_model} · Embeddings:{" "}
              <b>{config.embed_provider}</b>
            </span>
          )}
        </div>
        {sessionId ? (
          <ChatWindow
            sessionId={sessionId}
            sendChat={sendChat}
            onTurnComplete={refreshMemories}
          />
        ) : (
          <div className="memory-empty">Starting a session…</div>
        )}
      </div>
      <div className="panel">
        <h2>
          Long-term memory
          <span className="live-dot" title="Live-synced" />
        </h2>
        <NewSessionButton onNewSession={handleNewSession} busy={switching} />
        <MemoryPanel
          memories={memories}
          onForget={handleForget}
          onForgetOne={handleForgetOne}
          forgetting={forgetting}
        />
      </div>
      <Toast toast={toast} />
    </div>
  );
}
