# ARCHONX:SYNTHIA

> Always-on enterprise-safe agent OS — computer-use, voice control, mission control dashboard.

---

## What is Synthia?

Synthia is an ARCHONX module that orchestrates AI agents with:

- **Brain** — Notion databases (Tasks, Runs, Artifacts, SOPs, Profiles, Approvals, Agents)
- **Body** — Orgo ephemeral computers (desktop per agent)
- **Hands** — Orgo mouse/keyboard/browser + Docker code-runner sandbox
- **Ears/Mouth** — Twilio voice (push-to-talk MVP)
- **Mind** — GLM-5 (Z.ai) with function calling

All supervised from a **Control Tower** web dashboard with live agent views,
approval gates, and kill switches.

## Quick Start

```bash
# 1. Set up env vars
cp .env.example .env
# Fill in your API keys

# 2. Launch
cd infra
docker compose up --build

# 3. Verify
curl http://localhost:8000/healthz
# Open http://localhost:3000 for Control Tower
```

## Repo Structure

```
archonx-synthia/
├── apps/
│   ├── server/           # FastAPI orchestrator (Python)
│   └── control-tower/    # Next.js dashboard (TypeScript)
├── packages/
│   ├── core/             # Agent runtime, policy engine, tool contracts
│   ├── connectors/       # Notion, Orgo, GLM-5, Twilio, Runner clients
│   └── schemas/          # Notion DB manifest, tool JSON schemas
├── infra/
│   ├── docker-compose.yml
│   └── code-runner/      # Sandboxed code execution service
├── docs/
│   ├── prd/              # Product requirements
│   ├── arch/             # Architecture diagrams
│   ├── security/         # Threat model
│   └── runbooks/         # Operational guides
├── .env.example
└── README.md
```

## Safety Model

1. **No password/vault access** — agents never see raw credentials
2. **Scoped API tokens only** — least-privilege, rotation-friendly
3. **Approval gates** — payments, external comms, destructive actions require human OK
4. **Tool allowlisting** — only declared tools; no arbitrary shell
5. **Network egress control** — default deny, domain allowlist per job
6. **Ephemeral compute** — Orgo desktops destroyed after each job
7. **Audit trail** — every tool call logged with redacted I/O
8. **Budget limits** — max steps, tool calls, runtime per task + kill switch

## Required Env Vars

See [.env.example](.env.example) for the full list. Key variables:

| Variable | Source |
|----------|--------|
| `ORGO_API_KEY` | Orgo dashboard |
| `ZAI_API_KEY` | Z.ai console |
| `NOTION_TOKEN` | Notion integrations |
| `NOTION_*_DB_ID` | Notion database IDs (7 databases) |
| `TWILIO_*` | Twilio console (voice MVP) |
| `BASE_URL` | Public webhook URL (ngrok for dev) |

## BMAD A2A Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| P0 | Discovery & Setup | ✅ Complete |
| P1 | PRD + Architecture | 🔲 Awaiting approval |
| P2 | Data Model + Notion schema | 🔲 |
| P3 | Integrations (Orgo, GLM-5, Twilio, Runner) | 🔲 |
| P4 | UX + Control Tower UI | 🔲 |
| P5 | Multi-agent spawning + budgets + approvals | 🔲 |
| P6 | Hardening checklist + deployment runbook | 🔲 |
| P7 | Production deploy + monitoring | 🔲 |

## Docs

- [PRD](docs/prd/00-overview.md)
- [Architecture](docs/arch/00-topology.md)
- [Threat Model](docs/security/00-threat-model.md)
- [Local Dev Runbook](docs/runbooks/00-local-dev.md)
- [Notion Schema Manifest](packages/schemas/notion_manifest.yaml)

## License

Proprietary — The Pauli Effect / ARCHONX. All rights reserved.
