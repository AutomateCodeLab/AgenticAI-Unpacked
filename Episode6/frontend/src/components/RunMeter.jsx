// RunMeter — Layer 4 (hard limits) made visible in real time: how many of
// the max_steps this run has used, and how much of the cost budget it has
// burned, both derived live from the streamed trace (no polling).
export default function RunMeter({ config, step, running }) {
  if (!config) return null;
  const maxSteps = config.max_steps;
  const spent = step * config.cost_per_step_usd;
  const budget = config.cost_budget_usd;
  const stepPct = Math.min(100, (step / maxSteps) * 100);
  const spentPct = Math.min(100, (spent / budget) * 100);

  return (
    <div className={`run-meter${running ? "" : " idle"}`}>
      <div className="run-meter-row">
        <span className="k">Steps</span>
        <span className="v">{step} / {maxSteps}</span>
      </div>
      <div className="meter-track"><div className="meter-fill" style={{ width: `${stepPct}%` }} /></div>
      <div className="run-meter-row">
        <span className="k">Budget</span>
        <span className="v">${spent.toFixed(2)} / ${budget.toFixed(2)}</span>
      </div>
      <div className="meter-track"><div className={`meter-fill${spentPct > 80 ? " warn" : ""}`} style={{ width: `${spentPct}%` }} /></div>
    </div>
  );
}
