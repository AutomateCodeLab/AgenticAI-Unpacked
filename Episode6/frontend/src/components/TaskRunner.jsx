// TaskRunner — the composer. Submitting a task starts one SSE-streamed run;
// this is "submit a task, watch it run, respond to approvals live", not
// open-ended chat, because guardrails apply within a single task's tool loop.
//
// PRESETS cover the four flagship on-screen moments in one click each, so a
// live demo never stalls on typing: a safe read (no approval at all), a
// risky write (approval demo with nothing malicious involved), a risky send
// to an allowlisted address (approve -> succeeds), and the injection attempt
// (approve -> still blocked by Layer 2's allowlist). Layer numbers in the
// labels match the SixLayers animation so viewers can map click -> layer.
// Task text is deliberately explicit (exact filename + exact content) so the
// model reliably calls the intended tool on the first turn instead of asking
// a clarifying question — important for a live, one-take demo.
const PRESETS = [
  { label: "🔎 Safe: read & summarize", task: "Read notes.txt from the workspace and summarize its contents in two sentences.", hint: "no approval needed — read_file is a safe tool" },
  { label: "📝 Risky: write a file", task: "Write the exact text 'All systems operational. No incidents today.' to a file named status.txt in the workspace.", hint: "Layer 1 demo — write_file pauses for Approve/Deny" },
  { label: "📧 Risky: email (allowlisted)", task: "Send an email to team@mycompany.com with the subject 'Status' and the body 'All systems operational.'", hint: "approve it — mycompany.com passes the Layer 2 allowlist" },
];

export default function TaskRunner({ task, setTask, defended, setDefended, running, onRun, onPreset, onInjectionDemo }) {
  return (
    <div className="composer">
      <div className="composer-row">
        <input
          value={task}
          onChange={(e) => setTask(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !running && task.trim()) onRun(); }}
          placeholder="Describe a task for the agent…"
          disabled={running}
        />
        <button onClick={onRun} disabled={running || !task.trim()}>
          {running ? "Running…" : "Run task"}
        </button>
      </div>
      <div className="preset-row">
        {PRESETS.map((p) => (
          <button
            key={p.label}
            className="preset-btn"
            disabled={running}
            title={p.hint}
            onClick={() => onPreset(p.task)}
          >
            {p.label}
          </button>
        ))}
      </div>
      <div className="sample-row">
        <button disabled={running} onClick={onInjectionDemo} className="injection-btn">💉 Try the injection demo</button>
        <label className={`defended-toggle${defended ? "" : " off"}`}>
          <input
            type="checkbox"
            checked={defended}
            disabled={running}
            onChange={(e) => setDefended(e.target.checked)}
          />
          {defended ? "Layer 3 defense: ON" : "Layer 3 defense: OFF (vulnerable)"}
        </label>
      </div>
    </div>
  );
}
