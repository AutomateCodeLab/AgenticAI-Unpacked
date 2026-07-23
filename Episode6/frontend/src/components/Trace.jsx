import { useEffect, useRef } from "react";
import RiskyActionApproval from "./RiskyActionApproval.jsx";

// Trace — the live agent run, one line per think/tool_call/tool_result, with
// RiskyActionApproval cards rendered inline at the exact point the agent
// paused to ask for one. Auto-scrolls to the newest line/card so a live demo
// never needs a manual scroll to see the thing that just happened.
export default function Trace({ items, approvals, onApprove, onDeny }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [items, approvals]);

  if (items.length === 0) {
    return <div className="trace-empty">Submit a task above to watch the agent run.</div>;
  }
  return (
    <div className="trace-scroll">
      {items.map((item) => {
        if (item.kind === "approval") {
          const a = approvals[item.requestId];
          if (!a) return null;
          return (
            <RiskyActionApproval
              key={item.id}
              tool={a.tool}
              args={a.args}
              status={a.status}
              reason={a.reason}
              sending={a.sending}
              onApprove={() => onApprove(item.requestId)}
              onDeny={() => onDeny(item.requestId)}
            />
          );
        }
        const icon = { think: "🧠", tool_call: "🔧", tool_result: "👀", final: "✅", error: "⚠️", killed: "⛔" }[item.kind] ?? "";
        return (
          <div className={`trace-line ${item.kind}`} key={item.id}>
            {icon} {item.text}
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
