# ArchonX OS Desktop Application

A native desktop control tower for managing, monitoring, and deploying ArchonX agents. Built with Tauri (Rust/WebView), React, and Python FastAPI.

## Features

- 💬 **Multi-Model Chat** - Claude, GPT, and other models with context awareness
- 🚀 **Deployment Management** - Control Coolify deployments from desktop
- 👥 **Agent Monitor** - Real-time status of all 64 ARCHONX agents
- 🎬 **Video Generation** - Create videos with StoryToolkitAI
- 🔍 **Research Tools** - Integrated search and document analysis
- 🖥️ **Computer Control** - Browser and desktop automation (Phase 2)
- 🎤 **Voice Commands** - Voice-triggered agent execution (Phase 2)

## Project Structure

```
archonx-desktop/
├── src/                          # React Frontend
│   ├── components/               # React components
│   ├── App.tsx                   # Main application
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Styles
├── backend/                      # Python FastAPI Backend
│   ├── routes/                   # API routes
│   ├── app.py                    # FastAPI application
│   ├── models.py                 # Data models
│   └── requirements.txt          # Python dependencies
├── package.json                  # Node.js dependencies
├── tauri.conf.json              # Tauri configuration
├── vite.config.ts               # Vite configuration
└── README.md                     # This file
```

## Installation

### Prerequisites

- Node.js 18+ & npm
- Python 3.8+
- Rust (for Tauri development)
- Git

### Setup

1. **Clone and navigate to desktop app:**
   ```bash
   cd archonx-desktop
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Install Python dependencies:**
   ```bash
   npm run backend:install
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development

### Run in development mode:

```bash
npm run dev
```

This starts both the Tauri app and Python backend simultaneously:
- Tauri desktop app: `http://localhost:5173`
- FastAPI backend: `http://127.0.0.1:8000`

### Build for production:

```bash
npm run build
```

Creates native executables for Windows, macOS, and Linux.

## API Endpoints

### Chat
- `GET /api/chat/models` - List available models
- `POST /api/chat` - Send chat message
- `POST /api/chat/stream` - Stream chat response

### Deployments (Coolify)
- `GET /api/deployments` - List all services
- `GET /api/deployments/{uuid}` - Get service details
- `POST /api/deployments/{uuid}/deploy` - Trigger deployment
- `GET /api/deployments/{deployment_id}/logs` - Get deployment logs

### Agents (ARCHONX)
- `GET /api/agents` - List all agents
- `GET /api/agents/{agent_id}` - Get agent details
- `POST /api/agents/{agent_id}/task` - Assign task to agent
- `POST /api/agents/crew/{crew}/task` - Assign task to crew

### Workflows (n8n)
- `GET /api/workflows` - List workflows
- `POST /api/workflows/{workflow_id}/execute` - Execute workflow
- `GET /api/workflows/{workflow_id}/executions` - Get execution history

### Video Generation
- `POST /api/video/generate` - Generate video from script
- `GET /api/video/{job_id}/status` - Get video status
- `POST /api/video/replay/{session_id}` - Render session replay

### Research
- `POST /api/research` - Perform research search
- `GET /api/research/sources` - Get available sources

### Computer Control (Phase 2)
- `POST /api/computer/sessions` - Create control session
- `GET /api/computer/sessions` - List sessions
- `POST /api/computer/sessions/{session_id}/actions` - Execute action
- `WS /ws/computer/{session_id}` - WebSocket for real-time updates

## Configuration

Environment variables are configured in `.env`:

```env
# Claude API
CLAUDE_API_KEY=sk-...
DEFAULT_MODEL=claude-3-5-sonnet

# Coolify
COOLIFY_API_KEY=your-key
COOLIFY_BASE_URL=https://coolify.example.com

# OpenClaw (Agent Control)
OPENCLAW_URL=ws://127.0.0.1:18789

# n8n
N8N_URL=https://n8n.example.com
N8N_API_KEY=your-key
```

## Usage Examples

### Chat with Claude

```typescript
const response = await fetch('http://127.0.0.1:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'claude-3-5-sonnet',
    messages: [{ role: 'user', content: 'Hello!' }]
  })
})
const data = await response.json()
console.log(data.response)
```

### Deploy with Coolify

```bash
curl -X POST http://127.0.0.1:8000/api/deployments/app-uuid/deploy
```

### Get Agent Status

```bash
curl http://127.0.0.1:8000/api/agents
```

### Generate Video

```bash
curl -X POST http://127.0.0.1:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{"script": "This is my video script..."}'
```

## Architecture

### Frontend (React/Tauri)
- Tauri WebView for native desktop app
- React 18 with hooks
- TanStack Query for data fetching
- Shadcn UI components

### Backend (Python/FastAPI)
- FastAPI for REST API
- Integrations with Coolify, OpenClaw, n8n
- WebSocket support for real-time updates
- Pydantic for data validation

### Integrations
- **Coolify**: Deployment management via CoolifyClient
- **OpenClaw**: Agent communication (WebSocket)
- **Claude API**: Multi-model chat interface
- **n8n**: Workflow orchestration
- **StoryToolkitAI**: Video generation (Phase 2)
- **Open Interpreter**: Computer control (Phase 2)
- **Remotion**: Session replay rendering (Phase 2)

## Phase 2: Advanced Features

Upcoming enhancements:

1. **Browser Automation** - Playwright integration for web automation
2. **Desktop Control** - Native desktop application control
3. **Open Interpreter** - Reasoning engine for complex tasks
4. **Session Replay** - Remotion-based video rendering
5. **Voice Commands** - Voice-triggered execution
6. **Live Monitoring** - WebSocket streaming for task execution
7. **Video Publishing** - Automated social media posting

## Testing

```bash
# Run tests
npm run type-check
pytest backend/tests/

# Lint code
npm run lint
```

## Troubleshooting

### Backend connection issues
- Ensure `http://127.0.0.1:8000/api/health` returns 200
- Check that Python backend is running: `npm run backend:dev`

### Missing API keys
- Copy `.env.example` to `.env`
- Fill in your API keys from Coolify, Claude, n8n, etc.

### Module import errors
- Reinstall Python dependencies: `pip install -r backend/requirements.txt`
- Ensure archonx-os repo is in parent directory for integration imports

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)

## License

Part of ArchonX OS - see [LICENSE](../LICENSE)

## Support

- GitHub Issues: https://github.com/executiveusa/archonx-os/issues
- Documentation: https://github.com/executiveusa/archonx-os/wiki

## Roadmap

- [x] Phase 1: Desktop app scaffold with multi-model chat
- [x] Coolify deployment integration
- [x] Agent monitoring dashboard
- [x] Video generation UI
- [x] Research tools integration
- [ ] Phase 2: Browser automation (Playwright)
- [ ] Phase 2: Desktop control (Desktop Commander)
- [ ] Phase 2: Open Interpreter runtime integration
- [ ] Phase 2: Voice command execution
- [ ] Phase 2: Session replay with Remotion
- [ ] Phase 3: Production hardening and optimization
