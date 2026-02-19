# 🧰 ARCHONX OS - AGENT TOOLBOX
## Shared Tools for All 64 Agents

**Version:** 1.1.0  
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
**Location:** `archonx/tools/orgo-mcp/`  
**Repository:** https://github.com/nickvasilescu/orgo-mcp.git  
**Status:** ✅ Installed

**Capabilities:**
- Create and manage virtual computers
- Take screenshots
- Execute shell commands
- Stream to Twitch
- File operations

**Usage:**
```json
{
  "mcpServers": {
    "orgo": {
      "command": "python",
      "args": ["-m", "orgo_mcp"],
      "env": {
        "ORGO_API_KEY": "your_key"
      }
    }
  }
}
```

**Available Tools:**
- `orgo_create_computer` - Create a virtual computer
- `orgo_screenshot` - Take a screenshot
- `orgo_execute` - Execute shell commands
- `orgo_file_read` - Read files
- `orgo_file_write` - Write files
- `orgo_stream_start` - Start Twitch stream
- `orgo_stream_stop` - Stop streaming

---

### 3. Bright Data MCP (Research & Scraping)
**Location:** `archonx/tools/brightdata-mcp/`  
**Repository:** https://github.com/brightdata/brightdata-mcp.git  
**Status:** ✅ Installed

**Capabilities:**
- Web scraping with residential proxies
- Search engine results
- Structured data extraction
- Anti-bot bypass

**Usage:**
```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "BRIGHT_DATA_API_KEY": "your_key"
      }
    }
  }
}
```

**Available Tools:**
- `brightdata_scrape` - Scrape web pages
- `brightdata_search` - Search engine queries
- `brightdata_extract` - Structured data extraction
- `brightdata_screenshot` - Page screenshots

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

### Grep MCP Tool
**Location:** `archonx/tools/grep_mcp.py`  
**Purpose:** Shared codebase search (`rg`/`grep`) for all crews

**Primary Params:**
- `query` - Text or regex pattern to search
- `include` - Optional glob include filter (for `rg --glob`)
- `max_results` - Cap returned lines to keep outputs bounded

---

## 📝 TOOL USAGE LOGGING

All agents MUST log tool usage to the canonical log:

```python
from archonx.logs.canonical_log import get_logger

logger = get_logger()
logger.log_tool_use(
    agent_id="White-Queen",
    tool="chrome_screenshot",
    purpose="Capture page state for design review",
    success=True,
    duration_ms=450
)
```

Log file: `archonx/logs/agents_{session_id}.jsonl`

---

## 🚀 QUICK START FOR AGENTS

### Pre-Task Tool Check
```bash
# Check available tools
cat archonx/tools/toolbox.md

# Verify Chrome DevTools MCP
npx chrome-devtools-mcp@latest --version

# Check tool logs
tail -f archonx/logs/agents_*.jsonl
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
| Orgo MCP | ✅ Active | 2026-02-19 | - |
| Bright Data MCP | ✅ Active | 2026-02-19 | - |
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

## 📚 MCP SERVER CONFIGURATION

### Complete MCP Config for Claude Desktop
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "orgo": {
      "command": "python",
      "args": ["-m", "orgo_mcp"],
      "env": {
        "ORGO_API_KEY": "${ORGO_API_KEY}"
      }
    },
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "BRIGHT_DATA_API_KEY": "${BRIGHT_DATA_API_KEY}"
      }
    }
  }
}
```

---

**Document Version:** 1.1.0  
**Maintained By:** ArchonX Orchestrator (White-e1)
