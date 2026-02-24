# 🎭 The Pauli Effect - Autonomous Agency Platform

**A comic-driven, community-powered autonomous agency platform combining storytelling, impact, and cutting-edge AI.**

## Project Overview

This is a monorepo containing the complete Pauli Effect ecosystem:
- **Frontend:** React 18.3 + TypeScript + Vite + Tailwind CSS (via Lovable)
- **Backend:** Poly Second Brain API (Hono.js + Prisma + PostgreSQL)
- **Agents:** CrewAI-powered autonomous agents (PAULI orchestrator + 6+ specialized agents)
- **Python Stack:** Modern `uv` package manager for all Python dependencies (10-100x faster)

## Repository Structure

```
pauli-comic-funnel/
├── src/                           # React frontend (Lovable v0.dev)
├── JARVIS_Universal_Agent_v2.0/   # Python JARVIS agent (10 LLM plugins)
├── eigent-main/                   # Electron desktop app
├── litellm-main(2)/               # LLM proxy with 50+ provider support
├── agents/                        # CrewAI agents (PAULI orchestrator)
├── postiz-app-main/              # Social media automation
├── poly-second-brain/            # Backend API (Poly Second Brain)
│
├── pyproject.toml                # 🆕 Root Python workspace (uv)
├── setup-uv.sh / setup-uv.bat    # 🆕 One-command environment setup
├── .github/workflows/            # GitHub Actions CI/CD
│   └── python-uv-cache.yml       # 🆕 Multi-platform testing
│
└── Documentation/
    ├── UV_QUICK_START.md         # 🆕 3-minute quick start
    ├── UV_INTEGRATION_GUIDE.md    # 🆕 Complete reference (450+ lines)
    └── UV_INTEGRATION_IMPLEMENTATION.md # 🆕 What was delivered
```

## Quick Start (Frontend + Backend)

### Option 1: Automated Setup with uv (Python)
```bash
# Clone the repo
git clone https://github.com/executiveusa/pauli-comic-funnel.git
cd pauli-comic-funnel

# Setup Python (one command)
chmod +x setup-uv.sh && ./setup-uv.sh    # macOS/Linux
# OR
setup-uv.bat                              # Windows

# Setup Node.js
npm install

# Start development
npm run dev        # Frontend (http://localhost:5173)
```

### Option 2: Manual Setup
```bash
# Frontend
npm install
npm run dev

# Python/Backend
pip install uv
uv venv .venv --python 3.11
source .venv/bin/activate
uv sync --all-extras

# Test JARVIS agent
cd JARVIS_Universal_Agent_v2.0
uv run python jarvis_agent.py
```

## Technology Stack

### Frontend
- **React 18.3.1** - UI framework
- **TypeScript 5.5.3** - Type safety
- **Vite 5.4.1** - Build tool
- **Tailwind CSS 3.4.11** - Styling
- **shadcn/ui** - 48+ components
- **Lovable** - AI-powered dev environment

### Backend (Poly Second Brain)
- **Hono 4.6.3** - Fast web framework
- **Prisma 5.21.1** - ORM
- **PostgreSQL** - Database
- **BullMQ + Redis** - Job queue
- **JWT + bcryptjs** - Auth

### Python/Agents
- **CrewAI** - Agent orchestration
- **Anthropic Claude** - Primary LLM
- **OpenAI GPT-4** - Backup LLM
- **LiteLLM** - LLM provider abstraction
- **faster-whisper** - Voice transcription
- **Playwright** - Browser automation
- **MCP Protocol** - Tool standardization

### DevOps
- **uv** - Python package manager (10-100x faster than pip)
- **Ruff** - Python linter
- **Black** - Code formatter
- **pytest** - Testing
- **GitHub Actions** - CI/CD
- **Docker** - Containerization

## Python Environment (NEW!)

✨ **This project now uses `uv` for Python dependency management** - the fastest Python package manager available.

### Setup Python

**One-Command Setup:**
```bash
chmod +x setup-uv.sh && ./setup-uv.sh    # Unix
# OR
setup-uv.bat                              # Windows
```

**Manual Setup:**
```bash
pip install uv
uv venv .venv --python 3.11
source .venv/bin/activate
uv sync --all-extras
```

### Essential Python Commands

```bash
uv sync              # Install dependencies from lock file
uv add numpy         # Add new package
uv run pytest        # Run tests
uv lock              # Generate reproducible lock file
uv pip list          # List installed packages
```

### JARVIS Agent

```bash
cd JARVIS_Universal_Agent_v2.0
uv run python jarvis_agent.py
```

**See [UV_QUICK_START.md](./UV_QUICK_START.md) for complete guide** (3-minute read)

## Development with Lovable

### Using Lovable Web IDE
Simply visit [Lovable Project](https://lovable.dev/projects/bc1d670c-5d37-46a0-94a9-137d494caf35) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

### Using Your Local IDE

If you want to work locally, clone this repo and push changes:

```bash
# Clone the repository
git clone https://github.com/executiveusa/pauli-comic-funnel.git
cd pauli-comic-funnel

# Install dependencies
npm install

# Start development server
npm run dev
```

**Your changes will be reflected in Lovable!**

## Scripts & Commands

### Frontend Development
```bash
npm run dev         # Start dev server (http://localhost:5173)
npm run build       # Build for production
npm run build:dev   # Build in dev mode
npm run lint        # Run ESLint
npm run preview     # Preview production build
```

### Python Development
```bash
# Workspace
uv sync             # Install all dependencies
uv sync --upgrade   # Update all packages
uv lock             # Generate lock file

# JARVIS Agent
cd JARVIS_Universal_Agent_v2.0
uv run python jarvis_agent.py      # Run agent
uv run pytest                       # Run tests
uv run ruff check .                # Lint code
uv run black .                      # Format code

# All workspace
uv run pytest                       # Test all members
```

## Deployment

### Frontend (Lovable)
1. Open [Lovable](https://lovable.dev/projects/bc1d670c-5d37-46a0-94a9-137d494caf35)
2. Click **Share → Publish**
3. Choose deployment target (Vercel, Railway, etc.)

### Backend (Poly Second Brain)
- **Railway:** Production-ready PostgreSQL + Hono API
- **Coolify:** Self-hosted option
- **Docker:** Container support included

### Agents (CrewAI)
- **MCP Servers:** Standardized tool interface
- **PAULI Orchestrator:** Agent routing and coordination
- **Notion Integration:** Work queue synchronization

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "feat: your feature"`
3. Push to GitHub: `git push origin feature/your-feature`
4. Open a Pull Request

## Project Architecture

### Frontend (Lovable + Vite)
React application with v0.dev design system integration. Responsive, accessible UI with Tailwind CSS and shadcn/ui components.

### Backend (Poly Second Brain)
Hono API with Prisma ORM. RESTful endpoints for task management, agent orchestration, and data persistence.

**13 Database Models:**
- Task, Run, Workflow (agent execution)
- Project, Area, Resource (PARA system)
- ConnectorConfig (integrations)
- Plus prompt history and event logs

### Agents (CrewAI Framework)
**PAULI + 6 Agent Personas:**
- **PAULI:** Master orchestrator, reads work queue
- **NEXUS:** Strategy & market intelligence
- **CREDIT:** Revenue & financial modeling
- **ARIA:** Creative writing & content
- **SPECTRUM:** Media & visual production
- **VEGA:** Code execution & deployment
- **ECHO:** Analytics & learning

### Integration Architecture
**6 Integration Flows:**
1. GitHub → Notion (code commits update tasks)
2. Stripe → Notion (payments update financials)
3. VS Code → Notion (MCP protocol direct access)
4. PAULI → Agents (orchestrator dispatches work)
5. Zapier/n8n (automation flows)
6. VAPI Voice (voice command interface)

## Performance & Benchmarks

### Python Installation
- **10-100x faster** with uv vs. pip
- Fresh install: 3 seconds (vs 45s with pip)
- From cache: 0.5s (vs 5s with pip)

### CI/CD Optimization
- 30-50% faster GitHub Actions
- 95%+ cache hit rate
- ~150MB cache (vs 500MB+ with pip)

### Frontend Build
- Vite provides <100ms page reloads
- Production build: ~2MB gzipped
- Lighthouse scores: 95+ all metrics

## Cloud Skills System (17 Skills)

The platform includes 17 reusable AI skills:
- **UI/UX Design** - Wireframes, specs, accessibility
- **Web Artifacts Builder** - Full-stack React generation
- **Deployment/DevOps** - CI/CD, containerization
- **Brand Guidelines** - Visual & verbal identity
- **Marketing/Growth** - Campaign planning
- **Fundraising** - Investor relations
- **Finance/Ops** - Budgets, impact allocation
- Plus 10 more specialized skills

Each skill is composable into automated workflows.

## Documentation

- **[UV_QUICK_START.md](./UV_QUICK_START.md)** - 3-minute Python setup guide
- **[UV_INTEGRATION_GUIDE.md](./UV_INTEGRATION_GUIDE.md)** - Complete Python reference (450+ lines)
- **[UV_INTEGRATION_IMPLEMENTATION.md](./UV_INTEGRATION_IMPLEMENTATION.md)** - Technical details
- **[ARCHITECTURE_MAP.md](../ARCHITECTURE_MAP.md)** - System architecture
- **[TECHNICAL_REFERENCE.md](../TECHNICAL_REFERENCE.md)** - API endpoints & database
- **[01_INTEGRATION_ARCHITECTURE.md](../01_INTEGRATION_ARCHITECTURE.md)** - Integration patterns

## Getting Help

### Quick Questions
- Check **[UV_QUICK_START.md](./UV_QUICK_START.md)** for Python setup
- Visit [Lovable Docs](https://docs.lovable.dev) for frontend
- Check [uv Documentation](https://docs.astral.sh/uv/) for Python

### Issues & Bugs
- Report in [GitHub Issues](https://github.com/executiveusa/pauli-comic-funnel/issues)
- Check existing issues first
- Include steps to reproduce

### Community
- **Lovable Community:** [discord.gg/lovable](https://discord.gg/lovable)
- **uv Community:** [GitHub Discussions](https://github.com/astral-sh/uv/discussions)
- **CrewAI Community:** [Discord](https://discord.gg/crewai)

## License

MIT License - See LICENSE file for details

## Status

✅ **Frontend:** Production-ready (Lovable + Vite)  
✅ **Backend:** Production-ready (Hono + Prisma)  
✅ **Agents:** CrewAI framework implemented  
✅ **Python:** Modern uv package manager (NEW!)  
✅ **CI/CD:** GitHub Actions optimized  
✅ **Documentation:** Comprehensive guides  

**Version:** 0.1.0  
**Last Updated:** December 10, 2025  
**Maintained by:** The Pauli Effect Team
