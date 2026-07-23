// LayerStatus — live mirror of the SixLayers animation, right in the browser.
// Each of the six guardrail layers (+ the least-privilege foundation) lights
// up the instant its guardrail actually does something, so a viewer watching
// the screen recording sees defense-in-depth happen, not just hears about it.
const LAYER_DEFS = [
  { id: "approval", n: 1, label: "Human approval" },
  { id: "validation", n: 2, label: "Validation" },
  { id: "injection", n: 3, label: "Injection defense" },
  { id: "limits", n: 4, label: "Limits" },
  { id: "logging", n: 5, label: "Logging" },
  { id: "kill", n: 6, label: "Kill switch" },
];

export default function LayerStatus({ pulses, defended, config }) {
  return (
    <div className="layer-status">
      {LAYER_DEFS.map(({ id, n, label }) => {
        const p = pulses[id];
        const armed = id === "injection"; // always shows its ON/OFF state, not just pulses
        const state = p?.state ?? (armed ? (defended ? "on" : "off") : "idle");
        return (
          <div className={`layer-chip layer-${state}`} key={id}>
            <span className="layer-num">{n}</span>
            <span className="layer-label">{label}</span>
            {p?.detail && <span className="layer-detail">{p.detail}</span>}
            {/* re-keying this span on every pulse restarts the flash animation */}
            <span className="layer-flash" key={p?.count ?? 0} />
          </div>
        );
      })}
      <div className="layer-chip layer-foundation">
        <span className="layer-num">⛊</span>
        <span className="layer-label">Least privilege</span>
        <span className="layer-detail">
          {config ? `${config.safe_tools.length} safe / ${config.risky_tools.length} risky tools` : "…"}
        </span>
      </div>
    </div>
  );
}
