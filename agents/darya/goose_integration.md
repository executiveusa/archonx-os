# Goose Integration — Darya's Primary Coding IDE

## What is Goose?
Goose is the CLI-based AI coding IDE from Block (fka Square).
In ArchonX, Goose runs as **PolyGoose** — customized with our extensions.
Repo: git@github.com:executiveusa/pauli-goose-coding-agent-.git

## How Darya Uses Goose

Goose is Darya's **primary coding execution engine** in cloud/CLI mode.
All BMAD Developer phase work runs through Goose.

### Execution Flow
```
Human PRD → Darya (Orchestrator)
  → Goose (PolyGoose CLI) — code implementation
  → FrankenClaw Browser — QA and testing
  → GitHub PR — observability and review
  → Coolify/Vercel — deployment
```

### Goose Session Protocol
```bash
# Start a Goose session for BMAD developer phase
goose session start --name "bead-$(date +%Y%m%d)" --profile darya-archonx

# Give Goose the PAULIWHEEL context
goose run --instructions agents/darya/system_prompt.md

# Batch 5 tasks at a time (BMAD guardrail)
goose run --task "Implement sprint tasks 1-5 from BEAD-XXX"

# Checkpoint after each batch
goose session save
```

### PolyGoose Config (extend goose with ArchonX tools)
Wire Goose to ArchonX MCP servers:
- open-brain MCP (shared memory)
- orgo MCP (desktop control)
- Bright Data MCP (web research)
- archonx toolbox skills (marketing, BMAD, PAULIWHEEL)

### Guardrails
- Run in 2-3 hour bursts only
- Commit to GitHub every sprint (5 tasks max)
- Never force-push to main
- All secrets from env vars — never hardcode
