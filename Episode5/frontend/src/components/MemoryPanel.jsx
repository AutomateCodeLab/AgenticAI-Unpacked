import { useState } from "react";

function relativeTime(ts) {
  const diffSec = Math.max(0, Date.now() / 1000 - ts);
  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

function absoluteTime(ts) {
  return new Date(ts * 1000).toLocaleString();
}

export default function MemoryPanel({ memories, onForget, onForgetOne, forgetting }) {
  const [expandedId, setExpandedId] = useState(null);

  return (
    <div className="memory-list">
      {memories.length === 0 && (
        <div className="memory-empty">
          No long-term memories yet. Tell the assistant something durable — a
          name, a preference, a project — and it'll show up here, persisted to
          disk, surviving a "New Session."
        </div>
      )}
      {memories.map((m) => {
        const expanded = expandedId === m.id;
        return (
          // Keyed by id (stable, server-assigned) so React only mounts a
          // fresh DOM node for a GENUINELY new memory — that's what makes the
          // CSS mount animation (a highlight pulse) play exactly once.
          <div
            className={`memory-item${expanded ? " expanded" : ""}`}
            key={m.id}
            onClick={() => setExpandedId(expanded ? null : m.id)}
            role="button"
            tabIndex={0}
          >
            <div>{m.text}</div>
            <div className="ts">{expanded ? absoluteTime(m.ts) : relativeTime(m.ts)}</div>
            {expanded && (
              <button
                className="memory-item-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onForgetOne(m.id);
                  setExpandedId(null);
                }}
              >
                ✕ Delete this memory
              </button>
            )}
          </div>
        );
      })}
      {memories.length > 0 && (
        <button className="forget-btn" onClick={onForget} disabled={forgetting}>
          {forgetting ? "Forgetting…" : "🗑️ Forget all"}
        </button>
      )}
    </div>
  );
}
