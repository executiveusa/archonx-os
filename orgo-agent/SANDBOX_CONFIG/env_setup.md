# Sandbox Environment Setup

## Overview

This document provides instructions for setting up the Orgo sandbox environment for the Autonomous AI Agency Platform.

## Prerequisites

- Orgo API access with token: `${ORGO_API_TOKEN}`
- GitHub account with repository access
- VS Code Web access (vscode.dev)

## Step 1: Create Orgo Instance

```bash
# Request Windows desktop instance via Orgo API
curl -X POST https://api.orgo.ai/v1/instances \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "os": "windows",
    "duration": "24h",
    "resources": {
      "cpu": 4,
      "memory": "16GB",
      "storage": "100GB"
    }
  }'
```

## Step 2: Access VS Code Web

1. Navigate to: `https://vscode.dev`
2. Connect to the Orgo instance
3. Install required extensions (see vscode_extensions.json)

## Step 3: Clone Repositories

```bash
# Clone main repository
git clone https://github.com/executiveusa/archonx-os.git

# Clone Agent Zero fork
git clone https://github.com/executiveusa/agent-zero-Fork.git

# Clone UI/UX Pro Max skill
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git

# Clone Cult Directory Template
git clone https://github.com/nolly-studio/cult-directory-template.git
```

## Step 4: Setup Environment Variables

Create `.env` files in the sandbox:

### LLM Keys (`credentials/llm_keys.env`)
```env
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
GLM_API_KEY=${GLM_API_KEY}
```

### MCP Keys (`credentials/mcp_keys.env`)
```env
ORGO_API_TOKEN=${ORGO_API_TOKEN}
NOTION_API_TOKEN=${NOTION_API_TOKEN}
```

### Supabase (`credentials/supabase.env`)
```env
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

### Deployment (`credentials/deployment.env`)
```env
VERCEL_TOKEN=${VERCEL_TOKEN}
VERCEL_PROJECT_ID=${VERCEL_PROJECT_ID}
COOLIFY_API_TOKEN=${COOLIFY_API_TOKEN}
```

### GitHub (`credentials/github.env`)
```env
GH_PAT=${GH_PAT}
```

### Telecom (`credentials/telecom.env`)
```env
TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
TWILIO_SECRET=${TWILIO_SECRET}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
```

## Step 5: Install Dependencies

```bash
# Install Node.js dependencies
npm install -g pnpm
pnpm install

# Install Python dependencies
pip install -r requirements.txt

# Install Supabase CLI
npm install -g supabase

# Install Vercel CLI
npm install -g vercel
```

## Step 6: Verify Setup

```bash
# Run health check
npm run health-check

# Verify database connection
supabase status

# Verify Vercel connection
vercel whoami
```

## Security Notes

1. **Never commit .env files** to GitHub
2. **Rotate API keys** every 30 days
3. **Use environment variables** for all secrets
4. **Enable 2FA** on all accounts
5. **Monitor API usage** for anomalies

## Next Steps

After setup is complete:
1. Run `WORKFLOWS/phase1_mvp.md`
2. Initialize agent identities
3. Begin MVP development
