# ARCHONX:SYNTHIA — Architecture Topology

**Version:** 0.1.0 — MVP  
**Status:** DRAFT (P0)  
**Date:** 2026-02-21  

---

## 1. System Topology

```
┌──────────────────────────────────────────────────────────────────┐
│                        CONTROL TOWER                             │
│                     (Next.js @ :3000)                            │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ Agent    │  │  Approval    │  │  Run        │  │ Onboard  │ │
│  │ Grid     │  │  Panel       │  │  Timeline   │  │ Flow     │ │
│  └────┬─────┘  └──────┬───────┘  └──────┬──────┘  └────┬─────┘ │
└───────┼────────────────┼─────────────────┼──────────────┼────────┘
        │                │                 │              │
        ▼                ▼                 ▼              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR SERVER                          │
│                   (FastAPI @ :8000)                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   AGENT RUNTIME                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌────────────────────┐   │   │
│  │  │ Planner   │  │ Executor  │  │ Budget / Policy    │   │   │
│  │  │ Loop      │  │ Loop      │  │ Engine             │   │   │
│  │  └─────┬─────┘  └─────┬─────┘  └────────┬───────────┘   │   │
│  └────────┼───────────────┼─────────────────┼───────────────┘   │
│           │               │                 │                    │
│  ┌────────▼───────────────▼─────────────────▼───────────────┐   │
│  │                  CONNECTOR LAYER                          │   │
│  │  ┌─────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐ │   │
│  │  │ Notion  │ │ Orgo │ │ GLM-5  │ │Twilio  │ │Runner  │ │   │
│  │  │ Client  │ │Client│ │ Client │ │Client  │ │Client  │ │   │
│  │  └────┬────┘ └──┬───┘ └───┬────┘ └───┬────┘ └───┬────┘ │   │
│  └───────┼─────────┼─────────┼──────────┼──────────┼────────┘   │
└──────────┼─────────┼─────────┼──────────┼──────────┼─────────────┘
           │         │         │          │          │
           ▼         ▼         ▼          ▼          ▼
     ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────────┐
     │ Notion   │ │ Orgo │ │ Z.ai │ │ Twilio   │ │ Docker       │
     │ API      │ │ API  │ │ API  │ │ API      │ │ Code-Runner  │
     │ (Brain)  │ │(Body)│ │(Mind)│ │(Ears)    │ │ (Hands)      │
     └──────────┘ └──────┘ └──────┘ └──────────┘ └──────────────┘
```

## 2. Component Responsibilities

### 2.1 Control Tower (Next.js)
- **Purpose:** Operator dashboard for multi-agent supervision
- **Tech:** Next.js 15, React 19, TypeScript
- **Port:** 3000
- **Communicates with:** Orchestrator Server (HTTP REST)

### 2.2 Orchestrator Server (FastAPI)
- **Purpose:** Central API, agent lifecycle, tool dispatch, policy enforcement
- **Tech:** Python 3.12, FastAPI, structlog, Pydantic
- **Port:** 8000
- **Routes:**
  - `/healthz`, `/readyz` — probes
  - `/api/tasks` — CRUD → Notion
  - `/api/agents` — spawn/kill/status
  - `/api/approvals` — approve/deny
  - `/api/runner` — code execution proxy
  - `/api/voice` — Twilio webhooks
  - `/api/onboarding` — profile setup

### 2.3 Agent Runtime (packages/core)
- **Purpose:** Planner/executor loop, budget enforcement, policy checks
- **Key classes:** `AgentState`, `Budget`, `PolicyEngine`
- **Model:** GLM-5 via Z.ai API with function calling

### 2.4 Connectors (packages/connectors)
- **Purpose:** Adapters for each external service
- **Clients:** Notion, Orgo, GLM-5, Twilio, Runner
- **Contract:** Every method returns `{ok, data|error, trace_id, redactions}`

### 2.5 Docker Code-Runner (infra/code-runner)
- **Purpose:** Sandboxed command execution
- **Security:** Non-root, read-only FS, /work mount, resource limits, no network by default
- **Port:** 9000
- **API:** `/exec`, `/put-file`, `/get-file`, `/healthz`

## 3. Data Flow: Voice → Task → Execution

```
User calls Twilio number
  → /api/voice/inbound → TwiML gathers speech
  → /api/voice/transcribed ← speech result
  → Notion: create task (status=today, priority=high)
  → Agent runtime picks up task
    → GLM-5: plan execution steps
    → Loop: call tools (Notion/Orgo/Runner)
    → Each step: log to Notion Runs DB
    → If irreversible: create approval → wait for human
    → On completion: update task to done, destroy Orgo computer
  → Twilio: speak completion summary back to user
```

## 4. Deployment Topology (Local Dev)

```
docker-compose up --build
  ├── server        → :8000  (FastAPI)
  ├── control-tower → :3000  (Next.js)
  └── code-runner   → :9000  (sandbox)
```

## 5. Network Security

| Source | Destination | Protocol | Notes |
|--------|-----------|----------|-------|
| Control Tower | Server | HTTP :8000 | Internal Docker network |
| Server | Notion API | HTTPS | Egress allowlisted |
| Server | Orgo API | HTTPS | Egress allowlisted |
| Server | Z.ai API | HTTPS | Egress allowlisted |
| Server | Twilio API | HTTPS | Egress allowlisted |
| Server | Code-Runner | HTTP :9000 | Internal Docker network |
| Code-Runner | (none) | — | Network disabled by default |
