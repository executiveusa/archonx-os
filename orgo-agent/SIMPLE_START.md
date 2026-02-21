# Simple Orgo Start - One Command

## The Easiest Way

Orgo has a **chat endpoint** that lets you send a prompt directly to an AI that controls the desktop.

### Single API Call

```bash
curl -X POST "https://api.orgo.ai/v1/chat" \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Open VS Code Web at vscode.dev, clone the repo https://github.com/executiveusa/archonx-os, and read the orgo-agent/HANDOFF_PROMPT.md file to begin autonomous operation."
  }'
```

### Or Use the Web Interface

1. Go to: **https://app.orgo.ai**
2. Login with your API token
3. Click **"Chat with Desktop"** or similar feature
4. Type your command in natural language

### Check Orgo's Actual Features

Visit these URLs to see what's available:
- Dashboard: https://app.orgo.ai
- API Docs: https://api.orgo.ai/docs
- Main Docs: https://docs.orgo.ai

---

## If Orgo Doesn't Have Built-in AI

Then you need **one of these alternatives**:

### Alternative 1: Open Hands (Already Have)
You have Open Hands API keys:
```
${OPEN_HANDS_API_KEY}
${OPEN_HANDS_API_KEY_2}
```

Open Hands IS an autonomous coding agent. Use it directly:
```bash
curl -X POST "https://api.openhands.ai/v1/tasks" \
  -H "Authorization: Bearer ${OPEN_HANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Read the file at E:/ACTIVE PROJECTS-PIPELINE/ACTIVE PROJECTS-PIPELINE/AGENT ZERO/Building a Future-Proof Autonomous.txt and begin implementing the autonomous AI agency platform described in it."
  }'
```

### Alternative 2: Use Kilo Code (You're Using It Now!)

**I am Kilo Code** - I can execute the build right now in this workspace!

Just tell me: **"Start building the MVP"** and I'll:
1. Create the Next.js project
2. Setup the database schema
3. Build the BFF architecture
4. Deploy to Vercel

---

## The Simplest Path

**Skip Orgo for now.** Use what's already working:

1. **Kilo Code (me)** - I can build everything in this workspace
2. **Open Hands** - Autonomous coding agent with your API keys
3. **Vercel** - Free deployment with your token

Want me to start building the Luxury Travel Directory MVP right now?
