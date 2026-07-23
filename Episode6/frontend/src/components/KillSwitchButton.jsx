// KillSwitchButton — Layer 6. Always visible, only enabled while a task is
// actually running, so it's obvious this halts THIS run, not "the server".
export default function KillSwitchButton({ running, onKill }) {
  return (
    <button className="kill-switch-btn" disabled={!running} onClick={onKill}>
      ⛔ STOP THIS TASK
    </button>
  );
}
