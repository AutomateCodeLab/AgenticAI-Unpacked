import { useEffect, useRef, useState } from "react";
import * as api from "./api.js";
import TaskRunner from "./components/TaskRunner.jsx";
import Trace from "./components/Trace.jsx";
import ConfigBadge from "./components/ConfigBadge.jsx";
import KillSwitchButton from "./components/KillSwitchButton.jsx";
import AuditLogPanel from "./components/AuditLogPanel.jsx";
import LayerStatus from "./components/LayerStatus.jsx";
import RunMeter from "./components/RunMeter.jsx";

let nextId = 1;

const EMPTY_PULSES = {};

export default function App() {
  const [config, setConfig] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [task, setTask] = useState("");
  const [defended, setDefended] = useState(true);
  const [running, setRunning] = useState(false);
  const [items, setItems] = useState([]);
  const [approvals, setApprovals] = useState({});
  const [auditLog, setAuditLog] = useState([]);
  const [pulses, setPulses] = useState(EMPTY_PULSES);
  const [step, setStep] = useState(0);
  const [killBanner, setKillBanner] = useState(false);
  const [plantedFile, setPlantedFile] = useState(null); // { path, content } from the injection-demo plant
  const [shieldBanner, setShieldBanner] = useState(null); // string message once an injection attempt is confirmed stopped
  const runIdRef = useRef(0);
  const killBannerTimerRef = useRef(null);
  const shieldBannerTimerRef = useRef(null);
  const injectionDemoPendingRef = useRef(false); // set by the plant button, consumed by the next run

  useEffect(() => {
    api.getConfig().then(setConfig).catch(() => {});
  }, []);

  function pushItem(kind, text, requestId) {
    setItems((prev) => [...prev, { id: nextId++, kind, text, requestId }]);
  }

  // Drives the LayerStatus panel: every layer flashes the instant its
  // guardrail actually does something, mirroring the SixLayers animation
  // live in the browser. `autoRevertMs: 0` means "stays lit until the next
  // run resets it" (used for the kill switch and a blown budget).
  function bumpLayer(id, state, detail, autoRevertMs = 1300) {
    setPulses((prev) => {
      const count = (prev[id]?.count ?? 0) + 1;
      if (autoRevertMs) {
        setTimeout(() => {
          setPulses((p2) => (p2[id]?.count !== count ? p2 : { ...p2, [id]: { ...p2[id], state: null, detail: null } }));
        }, autoRevertMs);
      }
      return { ...prev, [id]: { count, state, detail } };
    });
  }

  async function ensureTaskId() {
    if (taskId) return taskId;
    const { task_id } = await api.newTask();
    setTaskId(task_id);
    return task_id;
  }

  async function runTask(taskText, defendedFlag) {
    if (!taskText.trim() || running) return;
    const id = await ensureTaskId();
    const myRun = ++runIdRef.current;
    setRunning(true);
    setItems([]);
    setApprovals({});
    setStep(0);
    setPulses({});
    setPlantedFile(null);
    setShieldBanner(null);
    pushItem("tool_call", `Task started: "${taskText}"`);

    // Per-run injection-outcome tracking, scoped to this one closure so it
    // resets automatically on every run with no separate state to manage.
    // Drives the shield banner: was this the planted attack, and if so,
    // exactly which guardrail is the reason it didn't succeed? We key off
    // the plant button having been clicked (not off sniffing tool_result
    // text for "attacker@evil.com" — the server truncates tool_result to 80
    // chars for the trace, which cuts the payload off before that word).
    let sawInjectionMarker = injectionDemoPendingRef.current;
    injectionDemoPendingRef.current = false;
    let sawAllowlistBlock = false;
    let sawSendEmailAttempt = false;
    let sawSendEmailDenied = false;
    let lastApprovalTool = null;

    await api.streamTask(id, taskText, defendedFlag, (kind, payload) => {
      if (runIdRef.current !== myRun) return; // a newer run superseded this one

      if (kind === "tool_call") {
        // Roughly one loop iteration per tool call — not exact (a step can
        // in principle request more than one), but close enough for a live
        // "this run" indicator, and the server enforces the real max_steps
        // limit regardless of what this counter shows.
        setStep((s) => s + 1);
        const toolName = String(payload.text ?? "").split("(")[0];
        if (toolName === "send_email") sawSendEmailAttempt = true;
        bumpLayer("validation", "pulse", toolName);
        pushItem(kind, payload.text);
        return;
      }
      if (kind === "tool_result") {
        const text = String(payload.text ?? "");
        const allowlistBlocked = /not on allowlist/i.test(text);
        if (allowlistBlocked) sawAllowlistBlock = true;
        if (allowlistBlocked || /outside sandbox|blocked/i.test(text)) {
          bumpLayer("validation", "danger", "blocked");
        } else {
          bumpLayer("validation", "pulse", "checked");
        }
        if (sawInjectionMarker) {
          bumpLayer("injection", "warn", "suspicious content", 1800);
        }
        pushItem(kind, payload.text);
        return;
      }
      if (kind === "audit") {
        setAuditLog((prev) => [...prev, payload]);
        bumpLayer("logging", "pulse", payload.event, 900);
        if (payload.event === "rate_limited") bumpLayer("limits", "warn", "rate limited");
        if (payload.event === "budget_exceeded") bumpLayer("limits", "danger", `$${payload.spent} over budget`, 0);
        return;
      }
      if (kind === "approval_needed") {
        lastApprovalTool = payload.tool;
        setApprovals((prev) => ({
          ...prev,
          [payload.request_id]: { tool: payload.tool, args: payload.args, status: "pending", sending: false },
        }));
        bumpLayer("approval", "warn", `${payload.tool} pending`, 0);
        pushItem("approval", null, payload.request_id);
        return;
      }
      if (kind === "approval_resolved") {
        if (!payload.approved && lastApprovalTool === "send_email") sawSendEmailDenied = true;
        setApprovals((prev) => ({
          ...prev,
          [payload.request_id]: {
            ...prev[payload.request_id],
            status: payload.approved ? "approved" : "denied",
            reason: payload.reason,
            sending: false,
          },
        }));
        bumpLayer("approval", payload.approved ? "ok" : "danger", payload.reason, 2200);
        return;
      }
      if (kind === "killed") {
        bumpLayer("kill", "danger", "halted", 0);
        setKillBanner(true);
        clearTimeout(killBannerTimerRef.current);
        killBannerTimerRef.current = setTimeout(() => setKillBanner(false), 2600);
        pushItem(kind, `Halted by kill switch at step ${payload.text}.`);
        return;
      }
      if (kind === "final") {
        setStep((s) => (s === 0 ? 1 : s)); // a reply with no tool calls is still one step
        if (String(payload.text ?? "").includes("hit max steps")) {
          bumpLayer("limits", "warn", "max steps reached", 2200);
        }
        if (sawInjectionMarker) {
          let msg;
          if (sawAllowlistBlock) {
            msg = "🛡️ Injection attempt BLOCKED — Layer 2's recipient allowlist stopped the email to attacker@evil.com.";
          } else if (sawSendEmailDenied) {
            msg = "🛡️ Injection attempt DENIED — Layer 1 human approval refused the risky action.";
          } else if (!sawSendEmailAttempt) {
            msg = "🛡️ Injection DEFENDED — the agent treated the file as data and never attempted the action.";
          } else {
            msg = "🛡️ Injection attempt did not succeed.";
          }
          setShieldBanner(msg);
          clearTimeout(shieldBannerTimerRef.current);
          shieldBannerTimerRef.current = setTimeout(() => setShieldBanner(null), 5000);
        }
      }
      pushItem(kind, payload.text);
    });

    if (runIdRef.current === myRun) setRunning(false);
  }

  async function handleApprove(requestId) {
    setApprovals((prev) => ({ ...prev, [requestId]: { ...prev[requestId], sending: true } }));
    await api.approve(requestId, true);
  }

  async function handleDeny(requestId) {
    setApprovals((prev) => ({ ...prev, [requestId]: { ...prev[requestId], sending: true } }));
    await api.approve(requestId, false);
  }

  async function handleKill() {
    if (!taskId) return;
    await api.kill(taskId);
  }

  async function handleInjectionDemo() {
    const { task, path, content } = await api.plantInjection();
    injectionDemoPendingRef.current = true;
    setPlantedFile({ path, content });
    setShieldBanner(null);
    setTask(task);
  }

  function handlePreset(presetTask) {
    setTask(presetTask);
  }

  return (
    <div className="app">
      {killBanner && <div className="kill-banner">⛔ TASK HALTED BY KILL SWITCH</div>}
      {!killBanner && shieldBanner && <div className="shield-banner">{shieldBanner}</div>}
      <div className="header">
        <div>
          <h1>🛡️ Safe Agent — Episode 6</h1>
          <div className="sub">Guardrails &amp; safety: human approval, validation, injection defense, hard limits, logging, kill switch</div>
        </div>
        <span className="badge"><span className="live-dot" /> {config ? `${config.llm_provider}/${config.llm_model}` : "connecting…"}</span>
      </div>
      <LayerStatus pulses={pulses} defended={defended} config={config} />
      <div className="app-body">
        <div className="main-col">
          <TaskRunner
            task={task}
            setTask={setTask}
            defended={defended}
            setDefended={setDefended}
            running={running}
            onRun={() => runTask(task, defended)}
            onPreset={handlePreset}
            onInjectionDemo={handleInjectionDemo}
          />
          {plantedFile && !running && (
            <div className="plant-note">
              <div className="plant-note-title">💉 Planted <code>{plantedFile.path}</code> — click <strong>Run task</strong> to see it get caught:</div>
              <pre>{plantedFile.content}</pre>
            </div>
          )}
          <Trace items={items} approvals={approvals} onApprove={handleApprove} onDeny={handleDeny} />
        </div>
        <div className="panel">
          <div>
            <h2>Configuration</h2>
            <ConfigBadge config={config} />
          </div>
          <div>
            <h2>This run</h2>
            <RunMeter config={config} step={step} running={running} />
          </div>
          <div>
            <h2>Kill switch</h2>
            <KillSwitchButton running={running} onKill={handleKill} />
          </div>
          <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
            <h2>Audit log</h2>
            <AuditLogPanel entries={auditLog} />
          </div>
        </div>
      </div>
    </div>
  );
}
