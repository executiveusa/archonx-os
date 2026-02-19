# 🧰 ARCHONX OS - AGENT TOOLBOX
## Shared Tools for All 64 Agents

**Version:** 1.0.0  
**Location:** `C:\archonx-os-main\archonx\tools\toolbox.md`  
**Last Updated:** 2026-02-19

---

## 📋 TOOL REGISTRY

### 1. Chrome DevTools MCP
**Location:** `archonx/tools/chrome-devtools-mcp/`  
**Repository:** https://github.com/ChromeDevTools/chrome-devtools-mcp.git  
**Status:** ✅ Installed

**Capabilities:**
- Browser automation via Puppeteer
- Performance insights via Chrome DevTools
- Network request analysis
- Screenshots and console inspection
- Source-mapped stack traces

**Usage:**
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

**Available Tools:**
- `chrome_navigate` - Navigate to URL
- `chrome_click` - Click elements
- `chrome_type` - Type text into inputs
- `chrome_screenshot` - Capture browser state
- `chrome_evaluate` - Execute JavaScript
- `chrome_get_console` - Get console messages
- `chrome_get_network` - Get network requests
- `chrome_performance` - Get performance insights

---

### 2. Orgo MCP (Virtual Computer Control)
**Repository:** https://github.com/nickvasilescu/orgo-mcp.git  
**Status:** 📋 Pending Installation

**Capabilities:**
- Create and manage virtual computers
- Take screenshots
- Execute shell commands
- Stream to Twitch
- File operations

**Installation:**
```bash
git clone https://github.com/nickvasilescu/orgo-mcp.git
cd orgo-mcp
pip install -e .
export ORGO_API_KEY="your_key"
```

---

### 3. Bright Data MCP (Research & Scraping)
**Repository:** https://github.com/brightdata/brightdata-mcp.git  
**Status:** 📋 Pending Installation

**Capabilities:**
- Web scraping with residential proxies
- Search engine results
- Structured data extraction
- Anti-bot bypass

---

### 4. Context7 MCP (Updated Data)
**Status:** 📋 Pending Installation

**Capabilities:**
- Query for latest information
- Knowledge base sync
- Real-time data updates

---

### 5. Perplexity MCP (AI Search)
**Status:** 📋 Pending Installation

**Capabilities:**
- AI-powered search
- Citations included
- Real-time information

---

## 🔧 INTERNAL TOOLS

### Remotion Tool
**Location:** `archonx/tools/remotion.py`  
**Purpose:** Video generation via Remotion

### Computer Use Tool
**Location:** `archonx/tools/computer_use.py`  
**Purpose:** Desktop automation

### Analytics Tool
**Location:** `archonx/tools/analytics.py`  
**Purpose:** Usage analytics and metrics

### Deploy Tool
**Location:** `archonx/tools/deploy.py`  
**Purpose:** Deployment automation

### Browser Test Tool
**Location:** `archonx/tools/browser_test.py`  
**Purpose:** Browser testing automation

---

## 📝 TOOL USAGE LOGGING

All agents MUST log tool usage to the canonical log:

```json
{
  "timestamp": "2026-02-19T12:00:00Z",
  "agent_id": "White-Queen",
  "tool": "chrome_screenshot",
  "purpose": "Capture page state for design review",
  "success": true,
  "duration_ms": 450
}
```

Log file: `archonx/logs/tool_usage.jsonl`

---

## 🚀 QUICK START FOR AGENTS

### Pre-Task Tool Check
```bash
# Check available tools
cat archonx/tools/toolbox.md

# Verify Chrome DevTools MCP
npx chrome-devtools-mcp@latest --version

# Check tool logs
tail -f archonx/logs/tool_usage.jsonl
```

### Tool Invocation Pattern
```python
# In skill implementations
from archonx.tools.base import BaseTool

class MySkill(BaseSkill):
    async def execute(self, context):
        chrome_tool = context.tools.get("chrome-devtools")
        if chrome_tool:
            result = await chrome_tool.navigate("https://example.com")
            self.log_tool_usage("chrome_navigate", result)
        return SkillResult(...)
```

---

## 📊 TOOL HEALTH STATUS

| Tool | Status | Last Check | Success Rate |
|------|--------|------------|--------------|
| Chrome DevTools MCP | ✅ Active | 2026-02-19 | 100% |
| Orgo MCP | 📋 Pending | - | - |
| Bright Data MCP | 📋 Pending | - | - |
| Context7 MCP | 📋 Pending | - | - |
| Perplexity MCP | 📋 Pending | - | - |
| Remotion | ✅ Active | 2026-02-19 | 95% |
| Computer Use | ✅ Active | 2026-02-19 | 90% |

---

## 🔐 SECURITY NOTES

1. **API Keys:** Never hardcode API keys in tool configurations
2. **Sensitive Data:** Tools should not expose sensitive browser content
3. **Rate Limiting:** Respect API rate limits for external tools
4. **Audit Trail:** All tool usage is logged for oversight

---

**Document Version:** 1.0.0  
**Maintained By:** ArchonX Orchestrator (White-e1)
