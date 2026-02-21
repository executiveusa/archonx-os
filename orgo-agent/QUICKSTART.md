# Orgo Quick Start Guide

## What is Orgo?

Orgo provides **ephemeral desktop instances** that AI agents can control remotely. Think of it as a cloud computer that an AI can use to browse the web, run code, and interact with applications.

## How to Use Orgo

### Step 1: Get Your API Token

You already have the token:
```
${ORGO_API_TOKEN}
```

### Step 2: Create a Desktop Instance

Use the Orgo API to create a desktop instance:

```bash
curl -X POST "https://api.orgo.ai/v1/desktops" \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "os": "windows",
    "duration": 3600
  }'
```

### Step 3: Get the Stream URL

The API will return a response like:
```json
{
  "desktop_id": "desktop_xxx",
  "stream_url": "https://stream.orgo.ai/desktop_xxx",
  "status": "running"
}
```

Open the `stream_url` in your browser to see the desktop.

### Step 4: Control the Desktop

You can send commands to the desktop:

```bash
# Open a browser
curl -X POST "https://api.orgo.ai/v1/desktops/desktop_xxx/command" \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "open_browser",
    "url": "https://vscode.dev"
  }'

# Type text
curl -X POST "https://api.orgo.ai/v1/desktops/desktop_xxx/command" \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "type",
    "text": "Hello from Orgo!"
  }'

# Take a screenshot
curl -X POST "https://api.orgo.ai/v1/desktops/desktop_xxx/command" \
  -H "Authorization: Bearer ${ORGO_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "screenshot"
  }'
```

## Using Orgo with MCP (Model Context Protocol)

Orgo provides an MCP server that allows AI assistants like Claude to control desktops directly.

### MCP Configuration

Add this to your MCP settings:

```json
{
  "mcpServers": {
    "orgo": {
      "command": "npx",
      "args": ["-y", "@orgo/mcp-server"],
      "env": {
        "ORGO_API_TOKEN": "${ORGO_API_TOKEN}"
      }
    }
  }
}
```

### Available MCP Tools

Once connected, the AI can use these tools:

1. **orgo_create_desktop** - Create a new desktop instance
2. **orgo_list_desktops** - List all active desktops
3. **orgo_screenshot** - Take a screenshot
4. **orgo_click** - Click at coordinates
5. **orgo_type** - Type text
6. **orgo_press_key** - Press a keyboard key
7. **orgo_open_url** - Open a URL in browser
8. **orgo_run_command** - Run a terminal command
9. **orgo_read_file** - Read a file from the desktop
10. **orgo_write_file** - Write a file to the desktop

## Quick Test

To quickly test if Orgo is working:

1. Go to: https://app.orgo.ai
2. Login with your API token
3. Click "Create Desktop"
4. Watch the desktop spawn

## Troubleshooting

### "I see a Google page and nothing happens"

This means:
1. The desktop was created successfully
2. But no commands are being sent to it

**Solution:** You need to send commands via the API or MCP. The desktop doesn't do anything automatically - it waits for your instructions.

### How to Make the Agent Work

The Orgo desktop is like a blank slate. You need to:

1. **Send commands** via API or MCP
2. **Or** use an AI assistant with MCP integration

If you're using Claude Desktop with MCP:
1. Configure the MCP server (see above)
2. Restart Claude Desktop
3. Ask Claude to "Create an Orgo desktop and open VS Code"

## Example: Autonomous Agent Script

Here's a Python script that creates a desktop and performs tasks:

```python
import requests
import time

API_TOKEN = "${ORGO_API_TOKEN}"
BASE_URL = "https://api.orgo.ai/v1"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Create desktop
response = requests.post(
    f"{BASE_URL}/desktops",
    headers=headers,
    json={"os": "windows", "duration": 3600}
)
desktop = response.json()
desktop_id = desktop["desktop_id"]
print(f"Desktop created: {desktop_id}")
print(f"View at: {desktop['stream_url']}")

# Wait for desktop to be ready
time.sleep(10)

# Open VS Code Web
requests.post(
    f"{BASE_URL}/desktops/{desktop_id}/command",
    headers=headers,
    json={"action": "open_url", "url": "https://vscode.dev"}
)

# Take screenshot
response = requests.post(
    f"{BASE_URL}/desktops/{desktop_id}/command",
    headers=headers,
    json={"action": "screenshot"}
)
print(f"Screenshot: {response.json()}")
```

## Next Steps

1. **Test the API** - Create a desktop and send basic commands
2. **Setup MCP** - Configure Claude Desktop or other MCP client
3. **Run the Handoff Prompt** - Once MCP is working, the agent can execute autonomously

---

**Need Help?**
- Docs: https://docs.orgo.ai
- API Reference: https://api.orgo.ai/docs
- Support: support@orgo.ai
