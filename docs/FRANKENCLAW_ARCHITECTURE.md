# FrankenClaw™ — Assembled Best-of-Breed Agent Architecture

> "We rip good software apart and put the best pieces together."
> — The FrankenStack philosophy / The Pauli Effect

## What Is FrankenClaw?

FrankenClaw™ is the ArchonX agent execution layer, assembled from the best open-source
agent frameworks. Like FrankenStack (our tinkering philosophy), we take what works and
leave the rest.

## Assembled Pieces

### 🔵 From OpenClaw / DuClaw (Baidu)
- Multi-agent coordination protocol
- WebSocket gateway architecture (port 18789)
- Long-term memory and workflow persistence
- **DuClaw inspiration:** Browser-native hosted tier — zero-friction agent access
- **Our version:** Hosted ArchonX dashboard = DuClaw for enterprises

### 🌊 From Open Jarvis (Stanford)
- Layered agent architecture (Intelligence → Engine → Agents → Tools → Learning)
- Hardware auto-scan for optimal model selection
- Local-first AI: 88.7% of tasks on local hardware, 5.3x efficiency gain (2023-2025)
- Energy monitoring (50ms sampling, GPU/CPU/Apple Silicon)
- **Our version:** BAMBU local mode — runs on Bambu's laptop without cloud APIs

### ⚙️ From GStack (Gary Tan)
- **Persistent browser engine** — browser launches once, stays alive
  - Standard: 3-5 second cold start per action
  - GStack/FrankenClaw: 100-200ms per action (25x faster)
  - Auto-shutdown after 30min idle
  - Cookies, sessions, login state persist between commands
- Structured coding workflows: /plan, /qa, /browse, /review
- Playwright + SQLite cookie database access
- **Integrated into:** Darya's browser_agent.py

### 🤖 From OpenHands (All Hands AI)
- BMAD methodology for autonomous coding sprints
- 5-task batch execution with checkpoint reviews
- GitHub PR-based observability (treat agent as junior dev)
- **Integrated into:** Darya-designs microagents

### 🧠 From Agent Zero
- Orchestrator pattern with swarm sub-agents
- Self-improving memory and learning loops

### 🔴 Our Own Additions
- PAULIWHEEL™ loop (PLAN→IMPLEMENT→TEST→EVALUATE→PATCH→REPEAT)
- Dual chess crew rivalry (White vs Black, 32 agents each)
- Agent soul files (.agent-souls/) — identity, ethics, personality per agent
- BENEVOLENCIA ethics filter on all commercial decisions
- Bobby Fischer + Tyrone Protocol governance
- Guardian Fleet — 100+ repo autonomous monitoring

## Client White-Label Delivery

When we deploy ArchonX for an enterprise client, they get:
1. Hosted dashboard (DuClaw-style browser-native access, zero setup)
2. Supported models: GLM-5, DeepSeek, Kimi K 2.5, Claude, GPT-4 (switchable)
3. FrankenClaw browser automation (GStack persistent browser pattern)
4. Local AI option via Open Jarvis layer (private data stays on their machine)
5. DARYA autonomous coding via OpenHands/BMAD
6. All 32 marketing skills pre-loaded and configured for their brand
7. Full PAULIWHEEL governance baked in

## Open Jarvis — Can You Install It Today?

Yes. Open Jarvis runs on Mac, Windows, and Linux. Quick start:
```bash
git clone https://github.com/stanford-oval/open-jarvis
cd open-jarvis
./quick-start.sh  # Auto-installs deps, launches Ollama, starts UI
```
Requirements: 8GB+ RAM, GPU optional but recommended.
Local models via Ollama — no cloud API keys needed.

**Recommendation for ARCHON X packaging:**
Bundle Open Jarvis as the "local intelligence layer" option in BAMBU.
Clients with sensitive data (legal, medical, finance) will want local-only mode.
We configure it to point at their local hardware and our custom soul files.
