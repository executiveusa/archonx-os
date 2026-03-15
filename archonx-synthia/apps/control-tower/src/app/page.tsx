"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ── Types ───────────────────────────────────────────────── */
interface Agent {
  agent_id: string;
  status: string;
  current_task: string | null;
  computer_id: string | null;
}

interface Approval {
  approval_id: string;
  action: string;
  context: string;
  status: string;
}

/* ── Page ────────────────────────────────────────────────── */
export default function ControlTower() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [health, setHealth] = useState<string>("checking…");

  useEffect(() => {
    fetch(`${API}/healthz`)
      .then((r) => r.json())
      .then((d) => setHealth(d.ok ? "online" : "degraded"))
      .catch(() => setHealth("offline"));

    fetch(`${API}/api/agents`)
      .then((r) => r.json())
      .then((d) => setAgents(d.data ?? []))
      .catch(() => {});

    fetch(`${API}/api/approvals`)
      .then((r) => r.json())
      .then((d) => setApprovals(d.data ?? []))
      .catch(() => {});
  }, []);

  return (
    <main style={{ padding: "2rem", maxWidth: 1400, margin: "0 auto" }}>
      {/* ── Header ───────────────────────────────────────── */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #222",
          paddingBottom: "1rem",
          marginBottom: "2rem",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.8rem", letterSpacing: "0.05em" }}>
            SYNTHIA{" "}
            <span style={{ fontSize: "0.9rem", color: "#666" }}>Control Tower</span>
          </h1>
          <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#555" }}>
            ARCHONX Multi-Agent Supervision
          </p>
        </div>
        <StatusBadge label="Server" value={health} />
      </header>

      {/* ── Agent Grid ───────────────────────────────────── */}
      <section>
        <h2 style={sectionTitle}>Agents</h2>
        {agents.length === 0 ? (
          <EmptyState text="No agents running. Spawn one to get started." />
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem" }}>
            {agents.map((a) => (
              <AgentCard key={a.agent_id} agent={a} />
            ))}
          </div>
        )}
      </section>

      {/* ── Approvals Panel ──────────────────────────────── */}
      <section style={{ marginTop: "2rem" }}>
        <h2 style={sectionTitle}>Pending Approvals</h2>
        {approvals.length === 0 ? (
          <EmptyState text="No pending approvals." />
        ) : (
          approvals.map((ap) => (
            <ApprovalRow key={ap.approval_id} approval={ap} />
          ))
        )}
      </section>
    </main>
  );
}

/* ── Sub-components ─────────────────────────────────────── */
function StatusBadge({ label, value }: { label: string; value: string }) {
  const color = value === "online" ? "#22c55e" : value === "offline" ? "#ef4444" : "#eab308";
  return (
    <div style={{ textAlign: "right" }}>
      <span style={{ fontSize: "0.75rem", color: "#555" }}>{label}</span>
      <br />
      <span style={{ color, fontWeight: 600, fontSize: "0.9rem" }}>● {value}</span>
    </div>
  );
}

function AgentCard({ agent }: { agent: Agent }) {
  return (
    <div
      style={{
        background: "#111118",
        border: "1px solid #222",
        borderRadius: 8,
        padding: "1rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>{agent.agent_id}</strong>
        <span style={{ fontSize: "0.8rem", color: agent.status === "running" ? "#22c55e" : "#888" }}>
          {agent.status}
        </span>
      </div>
      <p style={{ fontSize: "0.85rem", color: "#666", margin: "0.5rem 0" }}>
        Task: {agent.current_task ?? "none"}
      </p>
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
        <button style={btnStyle}>Open Orgo</button>
        <button style={{ ...btnStyle, borderColor: "#ef4444", color: "#ef4444" }}>Kill</button>
      </div>
    </div>
  );
}

function ApprovalRow({ approval }: { approval: Approval }) {
  return (
    <div
      style={{
        background: "#111118",
        border: "1px solid #333",
        borderRadius: 6,
        padding: "0.75rem 1rem",
        marginBottom: "0.5rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <div>
        <strong style={{ fontSize: "0.9rem" }}>{approval.action}</strong>
        <p style={{ fontSize: "0.8rem", color: "#666", margin: "0.25rem 0 0" }}>
          {approval.context}
        </p>
      </div>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button style={{ ...btnStyle, borderColor: "#22c55e", color: "#22c55e" }}>Approve</button>
        <button style={{ ...btnStyle, borderColor: "#ef4444", color: "#ef4444" }}>Deny</button>
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "2rem",
        color: "#444",
        border: "1px dashed #222",
        borderRadius: 8,
      }}
    >
      {text}
    </div>
  );
}

/* ── Styles ──────────────────────────────────────────────── */
const sectionTitle: React.CSSProperties = {
  fontSize: "1.1rem",
  marginBottom: "1rem",
  color: "#999",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};

const btnStyle: React.CSSProperties = {
  background: "transparent",
  border: "1px solid #444",
  borderRadius: 4,
  color: "#ccc",
  padding: "0.35rem 0.75rem",
  fontSize: "0.8rem",
  cursor: "pointer",
};
