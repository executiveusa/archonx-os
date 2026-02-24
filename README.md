# ARCHONX Operating System

**Enterprise AI Infrastructure - 64-Agent Swarm**

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Security](https://img.shields.io/badge/security-AES--256-green.svg)](docs/SECURITY.md)

---

## 🎯 What is ARCHONX?

ARCHONX is a **full operating system** for AI-powered business automation. Not a chatbot. Not a website. A complete turnkey infrastructure deployed to enterprise clients.

- **64 AI Agents** organized as dual chess crews (White + Black, 32 each)
- **Dual Protocol** decision engine (Bobby Fischer + Tyrone Davis)
- **Multi-tenant** architecture with client isolation
- **Real-time** visualization and monitoring
- **Production-grade** security and encryption

## 🏗️ Architecture

```
ARCHONX Kernel
├── 64 Agents (White Crew + Black Crew)
├── Bobby Fischer Protocol (technical correctness)
├── Tyrone Protocol (ethical alignment - LOYALTY, HONOR, TRUTH, RESPECT)
├── OpenClaw Backend (WebSocket gateway on port 18789)
├── Daily Meetings (Pauli's Place - 5 strategic sessions)
└── Tool Dispatch (deploy, analytics, security, testing)
```

### White Crew (32 agents)
- **Pauli** (King) - Strategic decisions
- **Synthia** (Queen) - Tactical execution  
- 2 Rooks, 2 Knights, 2 Bishops, 24 Pawns

### Black Crew (32 agents)
- **Mirror** (King) - Strategic decisions
- **Shadow** (Queen) - Tactical execution
- 2 Rooks, 2 Knights, 2 Bishops, 24 Pawns

Crews compete in friendly rivalry while serving the same client goals.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/executiveusa/archonx-os.git
cd archonx-os

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Boot the kernel
archonx boot

# Check system status
archonx status

# View today's meeting schedule
archonx meetings

# Run GraphBrain in 7-phase loop mode (Ralphy-inspired)
python -m archonx.cli graphbrain run --mode light --loop --max-iterations 3
```

## 🖥️ Working Front End (Mission Console)

ARCHONX now serves a live frontend from `public/index.html` at the root URL.

```bash
# Start API + frontend
uvicorn archonx.server:create_app --factory --host 0.0.0.0 --port 8080 --reload
```

Then open:

- `http://localhost:8080/` (Mission Console UI)
- `http://localhost:8080/api/agents`
- `http://localhost:8080/api/skills`
- `http://localhost:8080/api/flywheel`

How to use this:

1. Click `Refresh Signals` to pull live system metrics.
2. Click `Run Sample Task` to dispatch a collaborative `crew="both"` task.
3. Watch Task Output + Agent Theater events update in the UI.

## ▲ Vercel Link (Project)

Project ID: `prj_T19WSaUiqLmrAewXECfctQyw4jKe`

```bash
# Requires Vercel CLI + token in environment
npm i -g vercel
vercel link --project prj_T19WSaUiqLmrAewXECfctQyw4jKe
vercel --prod
```

If your token is stored in your own secret manager, export it before deploy:

```bash
setx VERCEL_TOKEN "<your-token>"
```

##  Requirements

- Python 3.11+
- 8GB RAM minimum (16GB recommended)
- Docker (for deployment)
- PostgreSQL or SQLite (for pattern library)

## 🔒 Security

ARCHONX implements defense-in-depth security:

- **Encryption**: AES-256-GCM at rest, TLS 1.3 in transit
- **Anti-scraping**: Rate limiting, bot detection
- **Prompt injection defense**: Input sanitization
- **Audit logging**: Immutable logs for all actions
- **Auto-rollback**: Automated deployment rollback on failures

See [SECURITY.md](docs/SECURITY.md) for details.

## 🧪 Testing

```bash
# Run full test suite
pytest

# Run specific test modules
pytest tests/test_kernel.py
pytest tests/test_security.py

# Run integration tests
pytest tests/integration/

# Coverage report
pytest --cov=archonx --cov-report=html
```

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design
- [API Reference](docs/API.md) - Endpoints and schemas
- [Deployment Guide](docs/DEPLOYMENT.md) - Production setup
- [Security Best Practices](docs/SECURITY.md) - Hardening guide

## 🤖 AI Integration (ChatGPT App Store Ready)

ARCHONX is optimized for AI discovery and integration:

- `/public/llm.txt` - ChatGPT App Store metadata
- `/public/robots.txt` - AI-friendly crawling rules
- OpenAPI spec for function calling
- OAuth 2.0 authentication flow
- Structured data (JSON-LD) on all endpoints

## 🎨 The Four Pillars (Tyrone Protocol)

Every decision in ARCHONX passes through:

1. **LOYALTY** - Build together, no half-measures
2. **HONOR** - Do what we say, ship what we promise
3. **TRUTH** - Data-driven only, Bobby Fischer style
4. **RESPECT** - Speed beats power, respect the craft

Named in honor of Tyrone Davis (boxer, Culture Shock Sports founder).

## 🏆 Bobby Fischer Protocol

Technical decision validation:

1. Calculate 5-10 moves ahead
2. Data-driven only (no guessing)
3. Confidence threshold ≥ 0.7
4. Pattern matching from history
5. Rollback plan required

## 📅 Daily at Pauli's Place

5 mandatory meetings (all times UTC):

- **08:00** - Morning Briefing  
- **12:00** - Chess Match (strategy learning)
- **15:00** - Card Games (probability training)
- **18:00** - War Room (tactical discussion)
- **21:00** - Evening Review

## 🌐 Deployment

### Turnkey Client Instance

```bash
archonx deploy --client ClientName --config client-config.json
```

### Docker Deployment

```bash
docker build -t archonx:latest .
docker run -p 18789:18789 -p 8080:8080 archonx:latest
```

### Vercel Fleet Inventory Sync

```bash
# Required: VERCEL_TOKEN
python scripts/vercel_fleet_sync.py
```

Outputs:

- `data/vercel/projects.json`
- `data/vercel/repo_map.json`

### Kubernetes (Production)

```bash
kubectl apply -f k8s/
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete guide.

## 🔧 Configuration

Edit `archonx-config.json`:

```json
{
  "protocol": {
    "min_depth": 5,
    "preferred_depth": 10,
    "confidence_threshold": 0.7
  },
  "openclaw": {
    "gateway_port": 18789,
    "channels": ["whatsapp", "telegram", "slack"]
  },
  "meetings": {
    "morning_briefing": "08:00 UTC",
    "chess_match": "12:00 UTC",
    "card_games": "15:00 UTC",
    "war_room": "18:00 UTC",
    "evening_review": "21:00 UTC"
  }
}
```

## 📊 Monitoring

Access dashboards:

- Chessboard View: `http://localhost:8080/chessboard`
- Metrics Dashboard: `http://localhost:8080/dashboard`
- Pauli's Place: `http://localhost:8080/meetings`
- API Health: `http://localhost:8080/health`

## 🤝 Contributing

ARCHONX is proprietary software. For licensing inquiries, contact:

- **The Pauli Effect**: [Contact Info]
- **New World Kids**: [Nonprofit Partnership Inquiries]

## 📄 License

Proprietary - © 2026 The Pauli Effect

Built with the Four Pillars: LOYALTY, HONOR, TRUTH, RESPECT
built by the pauli effect

---

**"Speed beats power"** - Tyrone Davis

For humanity. For the 7-generation vision.

## 🧠 GraphBrain Runtime

GraphBrain is the ArchonX ecosystem intelligence runtime that indexes repositories, builds co-occurrence graphs, detects cross-repo bridges/gaps, and emits work orders for Agent-Zero (reasoning) and Devika (execution).

### Commands

```bash
archonx graphbrain run --mode=full
archonx graphbrain run --mode=light
archonx graphbrain init-repo executiveusa/archonx-os --path .
archonx graphbrain propagate --all
```

### Outputs

GraphBrain writes machine-readable artifacts to:

- `data/graphbrain/global_graph.json`
- `data/graphbrain/repo_graphs/<repo>.json`
- `data/graphbrain/similarity.json`
- `data/graphbrain/consolidation_candidates.json`
- `data/graphbrain/risk_findings.json`
- `data/graphbrain/work_orders.json`
- `data/audit/graphbrain.log` (append-only hash audit lines)
- `data/dashboard/registry.json`
- `data/dashboard/status.json`

### Adding a repository

1. Add repo slug to `data/graphbrain/targets.json` (`{"repos": ["owner/repo"]}`) or rely on defaults.
2. Run `archonx graphbrain init-repo <owner/repo> --path <local-path>` to install mandatory `.archonx/` controls.
3. Run `archonx graphbrain propagate --all` to apply ecosystem-wide propagation (PR-ready where credentials exist; dry-run report otherwise).

### Interpreting results

- High similarity pairs in `similarity.json` and `consolidation_candidates.json` indicate merge/shared-module opportunities.
- `risk_findings.json` lists security/reporting risks (insecure HTTP or non-allowlisted endpoints).
- `work_orders.json` is the actionable queue for Agent-Zero + Devika.

### Ecosystem Gap Audit

Use the deterministic gap-audit runner to compare intended architecture vs detected implementation:

```bash
python ops/audit/ecosystem_gap_audit.py --workspace /workspace --spec docs/audit/required_architecture_spec.json
```

Reports are emitted to `ops/reports/gap-audit/` as JSON + Markdown, including sectioned findings and remediation bundles per missing capability.
