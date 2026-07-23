// AuditLogPanel — Layer 5. Every tool call, approval, and halt lands here
// live as it happens (not just a post-hoc summary), because you can't
// secure what you can't see.
export default function AuditLogPanel({ entries }) {
  return (
    <div className="audit-log">
      {entries.length === 0 && <div className="audit-empty">No activity yet.</div>}
      {entries.map((e, i) => (
        <div className="audit-entry" key={i}>
          <span className="ts">{e.time?.split("T")[1] ?? ""}</span>
          <span className={`event${e.risky ? " risky" : ""}`}>{e.event}</span>
          {e.tool && <div className="meta">{e.tool}{typeof e.approved === "boolean" ? ` · approved=${e.approved}` : ""}</div>}
          {e.step !== undefined && <div className="meta">step {e.step}</div>}
          {e.spent !== undefined && <div className="meta">spent ${e.spent}</div>}
        </div>
      ))}
    </div>
  );
}
