# ARCHONX:SYNTHIA — Product Requirements Document

**Version:** 0.1.0 — MVP  
**Status:** DRAFT (P0)  
**Date:** 2026-02-21  

---

## 1. Vision

Synthia is an always-on enterprise-safe agent operating system. It coordinates
multiple AI agents that can see, click, type, run code, and communicate —
all under strict human oversight.

**One-line pitch:**  
*"Your team of AI agents, supervised from a Mission Control dashboard, with
computer-use capabilities, voice commands, and ironclad safety guardrails."*

## 2. User Personas

| Persona | Description | Key Need |
|---------|-------------|----------|
| **Operator** | Business owner / exec who issues tasks via voice or dashboard | Fast delegation, approval gates, audit trail |
| **Developer** | Builds templates, adds connectors, extends agent capabilities | Clean APIs, typed contracts, Docker sandbox |
| **Viewer** | Stakeholder who monitors agent progress | Read-only dashboard, run summaries |

## 3. Core Capabilities (MVP)

### 3.1 Voice Interface (Twilio Push-to-Talk)
- Call Synthia's Twilio number
- Speak a task: "Synthia, find 3 open-source voice options and draft a comparison"
- Synthia transcribes → creates Notion task → executes → reports back

### 3.2 Agent Runtime (GLM-5 + Function Calling)
- Planner/executor loop driven by GLM-5 model
- Tools: Notion CRUD, Orgo computer-use, Docker code-runner
- Budget enforcement: max steps, tool calls, runtime per task
- Sub-agent spawning for parallel work

### 3.3 Computer-Use (Orgo)
- Ephemeral desktop per agent
- Mouse/keyboard/browser control
- Live screenshots streamed to Control Tower
- Automatic destruction on job completion (TTL)

### 3.4 Code Sandbox (Docker Runner)
- Isolated container, non-root, read-only FS
- /work mount for file I/O
- Network disabled by default
- Resource-limited (CPU, memory)

### 3.5 Control Tower (Web Dashboard)
- Agent grid: status, task, screenshot, kill switch
- Approval panel: approve/deny irreversible actions
- Run timeline: step-by-step tool call history
- Onboarding flow: first-run profile setup

### 3.6 Brain (Notion)
- 7 databases: Profiles, Tasks, Runs, Artifacts, Approvals, Agents, SOPs
- Single source of truth for all task state
- Audit trail via Runs + Artifacts

## 4. Safety Model (Non-Negotiable)

1. **No password/vault access** — agents never see raw credentials
2. **Scoped API tokens only** — least-privilege, rotation-friendly
3. **Approval gates** — payments, external comms, destructive actions require human OK
4. **Tool allowlisting** — no arbitrary shell; only declared tools
5. **Network egress control** — default deny, domain allowlist per job
6. **Ephemeral compute** — Orgo computers destroyed after use
7. **Audit trail** — every tool call logged with redacted I/O
8. **Budget limits** — time, steps, tool calls with kill switch

## 5. Success Metrics (MVP)

| Metric | Target |
|--------|--------|
| Voice-to-task creation | < 10 seconds |
| Agent loop step latency | < 5 seconds average |
| Dashboard load time | < 2 seconds |
| Zero secrets in logs | 100% |
| Approval gate coverage | 100% for listed actions |

## 6. Out of Scope (MVP)

- Production voice with custom TTS (post-MVP: open-source voices)
- Pendant hardware integration
- Multi-tenant / team features
- Template marketplace
- Billing / usage metering

## 7. Dependencies

| Dependency | Provider | Status |
|-----------|----------|--------|
| GLM-5 model | Z.ai | API key required |
| Orgo computers | Orgo | API key required |
| Notion API | Notion | Integration token required |
| Twilio voice | Twilio | Account SID + auth token required |
| Docker Engine | Local | Required for code-runner |
