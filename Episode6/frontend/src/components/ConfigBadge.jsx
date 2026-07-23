// ConfigBadge — makes "least privilege" visible: which tools are risky vs
// safe, the email allowlist, and the hard limits, straight from /api/config.
export default function ConfigBadge({ config }) {
  if (!config) return null;
  return (
    <div className="config-badge">
      <div className="row">
        <span className="k">LLM</span>
        <span className="v">{config.llm_provider} / {config.llm_model}</span>
      </div>
      <div className="row">
        <span className="k">Risky tools</span>
        <span className="v tag-list">
          {config.risky_tools.map((t) => <span key={t} className="tag risky">{t}</span>)}
        </span>
      </div>
      <div className="row">
        <span className="k">Safe tools</span>
        <span className="v tag-list">
          {config.safe_tools.map((t) => <span key={t} className="tag safe">{t}</span>)}
        </span>
      </div>
      <div className="row">
        <span className="k">Email allowlist</span>
        <span className="v">{config.allowed_email_domains.join(", ")}</span>
      </div>
      <div className="row">
        <span className="k">Cost budget</span>
        <span className="v">${config.cost_budget_usd.toFixed(2)}</span>
      </div>
      <div className="row">
        <span className="k">Max steps</span>
        <span className="v">{config.max_steps}</span>
      </div>
      <div className="row">
        <span className="k">Rate limit</span>
        <span className="v">{config.rate_limit_per_min}/min</span>
      </div>
    </div>
  );
}
