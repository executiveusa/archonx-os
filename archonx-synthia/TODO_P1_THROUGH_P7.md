# ARCHONX:SYNTHIA™ — P1 through P7 Task Breakdown

> PAULIWHEEL™ execution plan for autonomous agent completion.
> Each task has a BEAD ID, responsible agent (Rainbow Protocol™), and acceptance criteria.

---

## ✅ P0: Skeleton (COMPLETE — BEAD-013)
- [x] FastAPI server with 24 routes
- [x] Next.js 15 Control Tower shell
- [x] Docker sandbox (code-runner)
- [x] docker-compose.yml (3 services)
- [x] Pydantic settings + .env.example
- [x] Policy engine (7 actions, 22 tools, 4 egress)
- [x] 5 connector stubs
- [x] Notion DB manifest + GLM-5 tool definitions
- [x] PRD, architecture, threat model, runbook
- [x] .gitignore hardened, secrets stripped

---

## 🟣 P1: Agent Runtime — SYNTHIA™ Core Loop

**Owner:** SYNTHIA™ (🟣) | **BEAD:** BEAD-015

- [ ] **P1.1** Implement `run_agent_loop()` in `packages/core/agent_runtime.py`
  - Accept task payload (goal, constraints, tools_allowed)
  - Initialize agent state (step counter, tool call counter, budget)
  - Enter PAULIWHEEL™ loop: plan → tool_call → evaluate → repeat
  - Emit structured logs via structlog at each step
  - Respect `max_steps_per_task`, `max_tool_calls_per_task`, `max_runtime_minutes_per_task`
  - **Test:** Unit test with mock tool calls, verify budget enforcement

- [ ] **P1.2** Wire Orgo MCP connector (`packages/connectors/orgo_client.py`)
  - Implement `create_desktop()`, `send_command()`, `screenshot()`, `read_file()`, `write_file()`
  - Auth via `ORGO_API_TOKEN` env var
  - Timeout + retry logic (3 retries, exponential backoff)
  - **Test:** Integration test against Orgo API (or mock)

- [ ] **P1.3** Wire GLM-5 connector (`packages/connectors/glm5_client.py`)
  - Implement `reason()` method accepting tool definitions + context
  - Map 13 GLM-5 tool definitions from `packages/schemas/tool_definitions.json`
  - **Test:** Unit test with mock GLM-5 responses

- [ ] **P1.4** Wire Notion connector (`packages/connectors/notion_client.py`)
  - Implement CRUD for all 7 databases in `packages/schemas/notion_manifest.yaml`
  - Task state persistence (create, update status, query by agent)
  - **Test:** Integration test against Notion API

- [ ] **P1.5** Agent identity initialization
  - Load agent identities from `orgo-agent/AGENT_IDENTITIES/registry.json`
  - Create startup sequence that registers agents with Notion Agents DB
  - **Test:** Verify all 11 agents registered

---

## 🔵 P2: Connector Integration — ARIA™

**Owner:** ARIA™ (🔵) | **BEAD:** BEAD-016

- [ ] **P2.1** Complete Twilio connector (`packages/connectors/twilio_client.py`)
  - Implement `make_call()`, `send_sms()`, `get_call_status()`
  - TwiML generation for voice responses
  - **Test:** Unit test with mock Twilio client

- [ ] **P2.2** Complete Runner connector (`packages/connectors/runner_client.py`)
  - Implement `exec_code()`, `put_file()`, `get_file()`, `health_check()`
  - Timeout enforcement matching `RUNNER_MAX_RUNTIME_SECONDS`
  - **Test:** Integration test against code-runner container

- [ ] **P2.3** Cross-connector error handling
  - Unified error response format: `{ok: bool, data: any, error: str, trace_id: str}`
  - Circuit breaker pattern for external services
  - **Test:** Fault injection tests

- [ ] **P2.4** Connector health dashboard endpoint
  - `/api/health/connectors` returns status of all 5 connectors
  - **Test:** Verify all connectors report status

---

## 🟢 P3: Policy Engine + Approvals — NEXUS™

**Owner:** NEXUS™ (🟢) | **BEAD:** BEAD-017

- [ ] **P3.1** Human-in-the-loop approval workflow
  - Intercept tool calls matching `APPROVAL_REQUIRED_ACTIONS` from `policy.py`
  - Create Notion approval record, pause agent, wait for resolution
  - Resume/abort based on approval decision
  - **Test:** E2E test: trigger approval → resolve → verify agent resumes

- [ ] **P3.2** Budget enforcement middleware
  - Track per-task step/call/runtime counters
  - Auto-abort when budget exceeded
  - Emit budget-exceeded event to Control Tower
  - **Test:** Unit test budget limits

- [ ] **P3.3** Egress proxy enforcement
  - Validate all outbound HTTP requests against `PROXY_ALLOWLIST`
  - Block + log unauthorized egress attempts
  - **Test:** Verify blocked domain returns 403

---

## 📞 P4: Voice Agent — ECHO™

**Owner:** ECHO™ (🩵) | **BEAD:** BEAD-018

- [ ] **P4.1** Inbound voice webhook (`/api/voice/inbound`)
  - Accept Twilio webhook, return TwiML gather
  - Language detection (English/Spanish/French)
  - **Test:** POST mock Twilio payload, verify TwiML response

- [ ] **P4.2** Speech → AI → TTS pipeline
  - Receive transcribed speech via `/api/voice/transcribed`
  - Send to GLM-5 for reasoning → generate response
  - Return TwiML with AI-generated speech
  - **Test:** E2E test with mock speech input

- [ ] **P4.3** Call recording + logging
  - Store call transcripts in Notion Runs DB
  - Link to associated task/agent
  - **Test:** Verify transcript stored after call

---

## 🖥️ P5: Control Tower Dashboard — PRISM™

**Owner:** PRISM™ (🌈) | **BEAD:** BEAD-019

- [ ] **P5.1** Agent status grid (real-time)
  - WebSocket connection to server
  - Display all 11 agents with status (idle/running/error/waiting_approval)
  - Color-coded per Rainbow Protocol™
  - **Test:** Verify WebSocket updates render correctly

- [ ] **P5.2** Task management panel
  - Create/view/cancel tasks
  - Task detail view with step-by-step execution log
  - **Test:** CRUD operations via UI

- [ ] **P5.3** Approval panel
  - List pending approvals with context
  - One-click approve/reject
  - **Test:** Approval resolution via UI updates server

- [ ] **P5.4** Metrics dashboard (ORACLE™ data)
  - Tasks completed/failed/pending
  - Tool calls per agent
  - Budget utilization gauges
  - **Test:** Verify metrics update after task completion

---

## 🟠 P6: Deployment + CI/CD — VECTOR™

**Owner:** VECTOR™ (🟠) | **BEAD:** BEAD-020

- [ ] **P6.1** Docker build pipeline
  - Multi-stage Dockerfiles for server + runner
  - `docker compose build` succeeds with zero errors
  - **Test:** `docker compose up -d` → all 3 services healthy

- [ ] **P6.2** Vercel deployment (Control Tower)
  - `vercel.json` configuration
  - Environment variables set via Vercel CLI
  - **Test:** `vercel --prod` succeeds, health check passes

- [ ] **P6.3** Coolify deployment (Server + Runner)
  - Coolify application configs
  - Docker Compose from `infra/docker-compose.yml`
  - **Test:** Services accessible on target host

- [ ] **P6.4** CI/CD pipeline
  - GitHub Actions workflow: lint → test → build → deploy
  - Branch protection on main
  - **Test:** Push to PR triggers full pipeline

---

## 🔴 P7: Security Hardening + Production — CIPHER™

**Owner:** CIPHER™ (🔴) | **BEAD:** BEAD-021

- [ ] **P7.1** Secret rotation automation
  - Script to rotate all 16 credentials documented in HANDOFF_SPEC.md
  - Update env files + Vercel/Coolify vars + Notion tokens
  - **Test:** Rotation script completes, all services still healthy

- [ ] **P7.2** Rate limiting
  - Per-IP rate limiting on all public endpoints
  - Per-agent rate limiting on tool calls
  - **Test:** Verify 429 after limit exceeded

- [ ] **P7.3** Audit logging
  - Structured audit log for all agent actions
  - Tamper-evident log chain (hash chaining)
  - Ship to external log aggregator
  - **Test:** Verify audit trail for complete task lifecycle

- [ ] **P7.4** ACIP v1.3 integration
  - Prompt-injection defense on all LLM inputs
  - Checksum verification for skill bundles
  - Audit-mode tags for trust boundary enforcement
  - **Test:** Inject malicious prompt → verify detection + block

- [ ] **P7.5** USM (Universal Skills Manager) integration
  - Install USM skill from github.com/jacob-bd/universal-skills-manager
  - Scan all skills before installation (20+ security checks)
  - Sync skills across agent tools (Claude, Cursor, OpenClaw)
  - **Test:** Install skill → verify scan report → verify installation

- [ ] **P7.6** Penetration testing checklist
  - [ ] SQL injection on all DB queries
  - [ ] XSS on Control Tower inputs
  - [ ] SSRF on proxy/egress
  - [ ] Path traversal on code-runner
  - [ ] Auth bypass on API endpoints
  - [ ] Secret leakage in logs/responses
  - [ ] Container escape attempts
  - **Test:** All checks pass with zero findings

- [ ] **P7.7** OpenClaw security hardening
  - Follow https://aimaker.substack.com/p/openclaw-security-hardening-guide
  - SSH key-only access, no public gateway exposure
  - Scoped credentials per agent
  - VPS firewall rules
  - **Test:** Security audit passes

---

## Summary

| Phase | Tasks | Owner | BEAD |
|-------|-------|-------|------|
| P0 ✅ | 10 | Builder | BEAD-013 |
| P1 | 5 | SYNTHIA™ | BEAD-015 |
| P2 | 4 | ARIA™ | BEAD-016 |
| P3 | 3 | NEXUS™ | BEAD-017 |
| P4 | 3 | ECHO™ | BEAD-018 |
| P5 | 4 | PRISM™ | BEAD-019 |
| P6 | 4 | VECTOR™ | BEAD-020 |
| P7 | 7 | CIPHER™ | BEAD-021 |
| **Total** | **40** | | |

---

*Generated under PAULIWHEEL™ discipline. Each task follows Ralphy Loop™: PLAN→IMPLEMENT→TEST→EVALUATE→PATCH→REPEAT.*
