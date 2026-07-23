// RiskyActionApproval — Layer 1, the flagship interaction. Renders inline in
// the trace the moment an "approval_needed" event arrives; the agent's
// background thread is genuinely blocked server-side until Approve/Deny is
// clicked (or it times out / gets killed) — see server.py's _make_web_approver.
export default function RiskyActionApproval({ tool, args, status, reason, sending, onApprove, onDeny }) {
  if (status === "pending") {
    return (
      <div className="approval-card">
        <div className="title">⛔ APPROVAL REQUIRED — {tool}</div>
        <div className="args">{JSON.stringify(args, null, 2)}</div>
        <div className="actions">
          <button className="approve-btn" disabled={sending} onClick={onApprove}>Approve</button>
          <button className="deny-btn" disabled={sending} onClick={onDeny}>Deny</button>
        </div>
      </div>
    );
  }
  const approved = status === "approved";
  return (
    <div className="approval-card resolved">
      <div className="title">{tool}</div>
      <div className="args">{JSON.stringify(args, null, 2)}</div>
      <div className={`resolution ${approved ? "approved" : "denied"}`}>
        {approved ? "✓ Approved" : "✗ Denied"} ({reason})
      </div>
    </div>
  );
}
