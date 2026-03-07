# ArchonX Desktop App - Build Assessment & Plan

**Date:** March 7, 2026
**Status:** Planning Phase
**Branch:** `claude/update-coolify-config-ufeib`

---

## Executive Summary

ArchonX OS has a robust server-side infrastructure but **lacks a cohesive desktop application** for end-users to:
- Control and monitor deployments via Coolify
- Deploy and manage AI agents
- Conduct deep research using integrated tools
- Generate videos with StoryToolkitAI
- Chat with multiple AI models with context awareness

**Recommendation:** Build a **custom Tauri + React + Python** desktop app that tightly integrates existing backend tools rather than adopting LibreChat.

---

## Current Ecosystem Analysis

### ✅ What Exists

#### 1. **ARCHONX Kernel** (`/archonx`)
- 64-agent swarm (White + Black crews)
- Bobby Fischer Protocol (decision validation)
- Tyrone Protocol (ethical alignment)
- OpenClaw WebSocket gateway (port 18789)
- Daily meetings orchestration (Pauli's Place)

#### 2. **ARCHONX:SYNTHIA** (`/archonx-synthia`)
- **Server:** FastAPI orchestrator (Python 3.11+)
- **Control Tower:** Next.js web dashboard (basic, browser-only)
- **Agents:** Brain (Notion), Body (Orgo), Hands (mouse/keyboard), Voice (Twilio), Mind (GLM-5)
- **Safety Model:** Approval gates, tool allowlisting, ephemeral compute, audit trails

#### 3. **n8n Workflows** (`/n8n-workflows/StoryToolkitAI-main`)
- Documentary processing via webhooks
- GitHub → Notion sync (daily)
- MCP health check (15min intervals)
- Skills filesystem sync (6hr intervals)
- **Currently:** Hosted on Hostinger, manual import required

#### 4. **Deployment Infrastructure**
- **CoolifyClient** (`/archonx/tools/coolify_client.py`) - Async HTTP wrapper
  - `trigger_deploy()` - Deploy apps by UUID
  - `get_deployment_status()` - Poll deployment progress
  - `list_services()` - List all deployable services
- **Coolify Workflows** - GitHub Actions integration (`.github/workflows/coolify-deploy.yml`)
- Docker Compose support for local dev

#### 5. **Existing Agents & Tools**
- Agent-Lightning (Pauli Comic Funnel)
- Agent-Zero (reasoning)
- Devika (execution)
- JARVIS Universal Agent
- OpenClaw integration
- Benevolencia ecosystem

#### 6. **Backend Capabilities**
- Multi-model API integration (Claude, GLM-5, etc.)
- Orgo ephemeral desktop support
- Notion database management
- Twilio voice control
- Docker code-runner sandbox

### ❌ What's Missing

| Component | Status | Impact |
|-----------|--------|--------|
| **Native Desktop App** | ❌ Missing | Critical - No standalone GUI |
| **Multi-Model Chat UI** | ⚠️ Partial | Web-only, needs enhancement |
| **Agent Deployment UI** | ⚠️ Partial | Control Tower exists but limited |
| **Video Generation UI** | ❌ Missing | StoryToolkitAI exists but no orchestrator UI |
| **Deep Research Tools** | ⚠️ Partial | Tools exist, no integrated dashboard |
| **Integrated Monitoring** | ⚠️ Partial | Dashboard exists, needs enhancement |
| **Model Router/Manager** | ⚠️ Partial | APIs exist, no unified UI |
| **Coolify Dashboard Integration** | ⚠️ Partial | CoolifyClient exists, no UI wrapper |

---

## Architecture Recommendation

### Desktop App Stack

```
┌─────────────────────────────────────────────────────────────┐
│               Tauri Desktop Shell (Rust/WebView)             │
│  - Single-window native app (Windows, macOS, Linux)         │
│  - File system access for local workflows                    │
│  - Native OS integrations (system tray, notifications)      │
└───────────────────┬─────────────────────────────────────────┘
                    │ IPC (Tauri invoke)
┌───────────────────▼─────────────────────────────────────────┐
│         React Frontend (TypeScript + TanStack)               │
│  ┌──────────────────┬──────────────────┬──────────────────┐ │
│  │  Chat Interface  │ Deployment Dash  │  Agent Monitor   │ │
│  ├──────────────────┼──────────────────┼──────────────────┤ │
│  │  Video Gen UI    │  Research Tools  │  Settings/Config │ │
│  └──────────────────┴──────────────────┴──────────────────┘ │
└───────────────────┬─────────────────────────────────────────┘
                    │ WebSocket + HTTP
┌───────────────────▼─────────────────────────────────────────┐
│         Python FastAPI Backend + Orchestrator                │
│  ├─ OpenClaw client (chat routing)                           │
│  ├─ CoolifyClient wrapper (deployments)                      │
│  ├─ n8n workflow triggers + monitoring                       │
│  ├─ StoryToolkitAI orchestrator                              │
│  ├─ Research engine aggregator                               │
│  └─ Notion sync + persistence                                │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬─────────────┐
        │           │           │             │
        ▼           ▼           ▼             ▼
    Coolify     OpenClaw     n8n         StoryToolkitAI
    (Deploy)    (Agents)    (Workflows)   (Video)
```

---

## Phase 1: Foundation (Weeks 1-2)

### 1.1 Project Scaffolding
```bash
archonx-desktop/
├── src-tauri/                    # Rust backend
│   ├── src/
│   │   ├── main.rs
│   │   ├── commands/
│   │   │   ├── chat.rs
│   │   │   ├── deployment.rs
│   │   │   ├── agents.rs
│   │   │   └── video.rs
│   │   └── models.rs
│   └── Cargo.toml
├── src/                          # React frontend
│   ├── components/
│   │   ├── Chat/
│   │   ├── DeploymentDash/
│   │   ├── AgentMonitor/
│   │   ├── VideoGenerator/
│   │   └── ResearchPanel/
│   ├── hooks/
│   ├── contexts/
│   └── App.tsx
├── backend/                      # Python orchestrator
│   ├── app.py                    # FastAPI main
│   ├── routes/
│   │   ├── chat.py               # Claude + model routing
│   │   ├── deployments.py        # Coolify integration
│   │   ├── agents.py             # Agent management
│   │   ├── workflows.py          # n8n integration
│   │   └── video.py              # StoryToolkitAI
│   ├── clients/
│   │   ├── coolify.py            # Enhanced CoolifyClient
│   │   ├── n8n.py                # n8n HTTP client
│   │   ├── openclaw.py           # OpenClaw WebSocket
│   │   ├── story_toolkit.py       # StoryToolkitAI API
│   │   └── notion.py             # Notion sync
│   ├── models.py
│   └── requirements.txt
├── package.json                  # Tauri + React deps
├── tauri.conf.json              # Tauri config
└── README.md
```

### 1.2 Core Dependencies

**Frontend (package.json):**
```json
{
  "dependencies": {
    "react": "^18.3",
    "react-dom": "^18.3",
    "@tauri-apps/api": "^1.5",
    "@tauri-apps/plugin-http": "^0.2",
    "@tanstack/react-query": "^5.28",
    "@tanstack/react-table": "^8.11",
    "zustand": "^4.4",
    "shadcn/ui": "^0.8",
    "tailwindcss": "^3.4",
    "framer-motion": "^10.16",
    "zustand": "^4.4"
  }
}
```

**Backend (requirements.txt):**
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
httpx==0.27.0
websockets==13.0
pydantic==2.9
pydantic-settings==2.5
python-dotenv==1.0
aiofiles==24.1
```

### 1.3 Initial Endpoints

```python
# POST /api/chat
# - body: {"model": "claude-3.5-sonnet", "messages": [...]}
# - routes to OpenClaw or direct API
# - returns: streamed chat response

# GET /api/deployments
# - lists all Coolify services via CoolifyClient
# - returns: [{"uuid": "...", "name": "...", "status": "..."}]

# POST /api/deployments/{uuid}/deploy
# - triggers Coolify deployment
# - returns: {"deployment_id": "...", "status": "queued"}

# GET /api/deployments/{deployment_id}/logs
# - streams deployment logs

# GET /api/agents
# - lists active agents (from ARCHONX kernel)
# - returns agent status, capabilities, crew

# POST /api/workflows/trigger/{workflow_id}
# - triggers n8n workflow via webhook
# - returns: {"execution_id": "...", "status": "queued"}

# GET /api/workflows/{workflow_id}/status
# - polls n8n execution status

# POST /api/video/generate
# - queues StoryToolkitAI job
# - returns: {"job_id": "...", "status": "processing"}

# GET /api/video/{job_id}/status
# - polls video generation progress + output preview
```

---

## Phase 2: Core Integrations (Weeks 3-4)

### 2.1 Chat Engine
- **OpenClaw WebSocket client** for agent routing
- **Claude API** for direct model access
- **Message history** stored in SQLite (local) + Notion (sync)
- **Model switching** (claude-3-5-sonnet, glm-5, etc.)
- **Context awareness** (code snippets, artifacts, file uploads)

### 2.2 Deployment Dashboard
- **Real-time service list** (CoolifyClient → list_services)
- **Deploy button** (triggers trigger_deploy)
- **Live logs** (polling + WebSocket if available)
- **Rollback UI** (auto-rollback on failures)
- **Resource metrics** (if Coolify exposes via API)

### 2.3 Agent Monitor
- **Agent grid** (all 64 agents with status)
- **Crew selector** (White/Black/Both)
- **Agent detail panel** (skills, current task, logs)
- **Task dispatch** (send task to specific agent or crew)
- **Pauli's Place calendar** (5 daily meetings)

### 2.4 n8n Workflow Integration
- **Workflow list** (fetch from n8n API)
- **Trigger UI** (manual execution + schedule preview)
- **Execution history** (show recent runs)
- **Webhook test tool** (send test payloads)

---

## Phase 3: Advanced Features (Weeks 5-6)

### 3.1 Video Generator
- **StoryToolkitAI integration** (orchestrate video jobs)
- **Script editor** (write/edit video scripts)
- **Preview generation** (thumbnail + quick preview)
- **Export options** (MP4, WebM, optimize for platform)
- **Progress tracking** (render pipeline stages)

### 3.2 Research Tools
- **Web search aggregator** (Google, Perplexity, etc.)
- **Document analysis** (PDF upload + extraction)
- **Citation management** (BibTeX, APA export)
- **Research dashboard** (trending topics, saved searches)

### 3.3 Settings & Config
- **API key management** (Coolify, n8n, Claude, etc.)
- **Workflow editor** (basic n8n workflow builder)
- **Agent profiles** (customize crew settings)
- **Auto-sync** (Notion, GitHub, etc.)

---

## Phase 4: Deployment & Hardening (Week 7)

### 4.1 Tauri Packaging
- Build executables (Windows .exe, macOS .dmg, Linux .AppImage)
- Code signing + verification
- Auto-updater setup (GitHub Releases)
- System tray integration

### 4.2 Backend Deployment
- Docker container for Python backend
- Environment variable management (.env)
- Database migrations (SQLite or PostgreSQL)
- Health checks + restart policies

### 4.3 Security Hardening
- Input validation + sanitization
- CORS/CSP headers
- Rate limiting on endpoints
- Audit logging (all actions)
- Encrypted credential storage

---

## Integration Points Summary

| Component | Location | Integration | Status |
|-----------|----------|-----------|--------|
| **Coolify** | `/archonx/tools/coolify_client.py` | Async HTTP wrapper | ✅ Ready |
| **OpenClaw** | `/archonx-synthia/` | WebSocket gateway | ✅ Ready |
| **n8n** | `/n8n-workflows/` | HTTP webhooks + API | ✅ Ready |
| **StoryToolkitAI** | `/n8n-workflows/StoryToolkitAI-main/` | Python SDK | ⚠️ Needs wrapper |
| **Notion** | `/archonx-synthia/` | Notion SDK | ✅ Ready |
| **Agents** | `/archonx/agents/` | ARCHONX kernel | ✅ Ready |
| **Video Gen** | Multiple sources | Remotion, Blender, Synthesia | ⚠️ Needs orchestration |

---

## Success Criteria

- ✅ Desktop app launches on Windows/macOS/Linux
- ✅ Chat with Claude + other models from desktop
- ✅ Deploy Coolify apps via desktop UI
- ✅ Monitor agents and trigger workflows
- ✅ Generate videos with StoryToolkitAI
- ✅ Offline mode works (local SQLite)
- ✅ Auto-sync when online (Notion, Coolify)
- ✅ Runs with <2GB RAM (optimized)
- ✅ <500ms latency for local operations

---

## File Structure After Build

```
/home/user/archonx-os/
├── archonx-desktop/           ← NEW PROJECT
│   ├── src-tauri/
│   ├── src/
│   ├── backend/
│   ├── package.json
│   ├── tauri.conf.json
│   └── README.md
│
├── archonx-synthia/           (enhanced)
│   ├── apps/control-tower/    (keep as fallback web UI)
│   └── apps/server/
│
├── n8n-workflows/             (reference for integration)
├── archonx/                   (kernel - no changes needed)
└── ...
```

---

## Next Steps

1. **Approve architecture** ← You are here
2. **Create Tauri project scaffold**
3. **Build React component library** (Shadcn UI)
4. **Implement FastAPI backend** (routes + clients)
5. **Integrate CoolifyClient** (deployment dash)
6. **Build chat interface** (OpenClaw + Claude)
7. **Add agent monitoring** (live updates)
8. **Implement n8n workflows** (trigger + monitor)
9. **Build video generator UI** (StoryToolkitAI)
10. **Package & deploy** (Tauri release)

---

## Questions to Clarify

- [ ] **Database preference:** SQLite (embedded) or PostgreSQL (external)?
- [ ] **Chat history:** Store locally only, or sync to Notion?
- [ ] **Agent crew default:** White, Black, or Both?
- [ ] **Video export formats:** MP4 only, or WebM/ProRes/other?
- [ ] **Update frequency:** Check Coolify/n8n every 5s, 30s, or 1m?

---

**Ready to start building?** Let me know and I'll scaffold Phase 1 immediately.
