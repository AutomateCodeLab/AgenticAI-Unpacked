export default function NewSessionButton({ onNewSession, busy }) {
  return (
    <button className="new-session-btn" onClick={onNewSession} disabled={busy}>
      🔄 New Session
    </button>
  );
}
