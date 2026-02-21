# ARCHONX:SYNTHIA — Local Development Runbook

**Version:** 0.1.0 — MVP  
**Date:** 2026-02-21  

---

## Prerequisites

| Tool | Min Version | Check Command |
|------|------------|---------------|
| Docker Engine | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| Node.js | 22+ | `node --version` |
| Python | 3.12+ | `python --version` |
| Git | 2.40+ | `git --version` |

## Quick Start (5 minutes)

### 1. Clone and enter the repo

```bash
cd archonx-os-main/archonx-synthia
```

### 2. Create your .env file

```bash
cp .env.example .env
# Fill in your API keys — see "Required Env Vars" below
```

### 3. Launch the stack

```bash
cd infra
docker compose up --build
```

This starts:
- **Server** at http://localhost:8000
- **Control Tower** at http://localhost:3000
- **Code Runner** at http://localhost:9000 (internal)

### 4. Verify health

```bash
curl http://localhost:8000/healthz
# → {"ok": true, "service": "synthia-server", "version": "0.1.0"}
```

Open http://localhost:3000 to see the Control Tower UI.

## Required Env Vars

| Variable | Source | Required for MVP? |
|----------|--------|-------------------|
| `ORGO_API_KEY` | Orgo dashboard | Yes |
| `ZAI_API_KEY` | Z.ai console | Yes |
| `NOTION_TOKEN` | Notion integrations | Yes |
| `NOTION_TASKS_DB_ID` | Notion → Copy DB ID | Yes |
| `NOTION_RUNS_DB_ID` | Notion → Copy DB ID | Yes |
| `NOTION_ARTIFACTS_DB_ID` | Notion → Copy DB ID | Yes |
| `NOTION_APPROVALS_DB_ID` | Notion → Copy DB ID | Yes |
| `NOTION_PROFILES_DB_ID` | Notion → Copy DB ID | Yes |
| `NOTION_AGENTS_DB_ID` | Notion → Copy DB ID | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio console | For voice only |
| `TWILIO_AUTH_TOKEN` | Twilio console | For voice only |
| `TWILIO_NUMBER` | Twilio console | For voice only |
| `BASE_URL` | Your ngrok/public URL | For Twilio webhooks |

## Development Without Docker

### Server (Python)

```bash
cd apps/server
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### Control Tower (Node.js)

```bash
cd apps/control-tower
npm install
npm run dev
```

### Code Runner

```bash
cd infra/code-runner
pip install -r requirements.txt
python runner_api.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | `netstat -ano | findstr :8000` then kill the process |
| Docker build fails | Try `docker compose build --no-cache` |
| Notion 401 | Check `NOTION_TOKEN` and that integration is shared with DBs |
| Orgo timeout | Check `ORGO_API_KEY` and network connectivity |
| CORS error in browser | Ensure UI is on `localhost:3000` and server on `localhost:8000` |

## Twilio Webhook Setup (Voice)

1. Install ngrok: `npm i -g ngrok` or download from ngrok.com
2. Run: `ngrok http 8000`
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Set `BASE_URL=https://abc123.ngrok.io` in `.env`
5. In Twilio Console → Phone Number → Voice → Webhook:
   - URL: `https://abc123.ngrok.io/api/voice/inbound`
   - Method: POST
