# ArchonX OS Agent Rules

## PAULIWHEEL Default
- PAULIWHEEL is the default coding behavior for every coding agent operating in this repository.
- Code-affecting operations must include a bead identifier and execute through beads + Ralphy loop stages (PLAN, IMPLEMENT, TEST, EVALUATE, PATCH, REPEAT).
- Agent Lightning bootstrap is required before other functional changes in any touched repository.

## Context7 Compliance (MANDATORY)
- Before writing ANY code that calls a third-party library or framework, every agent MUST:
  1. Call `context7.resolve-library-id` to find the canonical docs ID for that library
  2. Call `context7.get-library-docs` to fetch the current API reference
  3. Only write code AFTER reading the docs returned by Context7
- Applies to: React, Three.js, @react-three/fiber, Saleor GraphQL, Remotion, FastAPI, httpx, and any other dependency.
- MCP config: `npx -y @upstash/context7-mcp`
- Violating this rule is grounds for `restricted` status (same as failing an ACK).

## Compliance Gates
- Agents must ACK the latest eco-prompt, toolbox version, and contracts hash during scheduled sync meetings.
- Non-ACKed agents are `restricted` and may only heartbeat, request grants, and join meetings.

## Operational Cadence
- Run PAULIWHEEL sync meetings at least 3 times per day.
- Every run must execute verification (build/test where available + `archonx-ops doctor`) and emit machine-readable reports under `ops/reports/`.

## Open Brain MCP — Agent Memory Protocol

### Memory System Overview
All agents have access to a shared pgvector-backed memory layer via the Open Brain MCP server. This enables persistent, searchable memory across agent lifespans and coordination.

### Memory Architecture
- **Thoughts**: Raw memories, notes, insights (searchable by embedding)
- **Entities**: Named concepts (people, places, projects)
- **Repositories**: Linked GitHub repos with descriptions
- **Telemetry**: Event logging and token usage tracking
- **Lightning Events**: Agent lifecycle events

### Mandatory Memory Protocol

**EVERY agent MUST:**

1. **Before starting ANY task** → Call `search_memories` with task context
   ```
   search_memories(
     agent_id="<your_agent_id>",
     query="<task_context>",
     limit=5
   )
   ```
   This retrieves relevant prior context and decisions.

2. **After completing ANY task** → Call `store_memory` with results
   ```
   store_memory(
     agent_id="<your_agent_id>",
     content="<task_result>",
     memory_type="decision|insight|note",
     metadata={...}
   )
   ```
   This ensures continuity and avoids duplicate work.

3. **On agent startup** → Log lightning event
   ```
   log_lightning_event(
     agent_id="<your_agent_id>",
     event_type="agent_start",
     event_data={"version": "1.0", "mode": "production"}
   )
   ```

4. **On significant decisions** → Store as decision memory
   ```
   store_memory(
     agent_id="<your_agent_id>",
     content="<decision>",
     memory_type="decision",
     metadata={"rationale": "...", "impact": "..."}
   )
   ```

### Memory Types
- `note` — General information, observations
- `decision` — Important choices, trade-offs considered
- `insight` — Lessons learned, patterns discovered
- `meeting` — Meeting notes, attendees, action items
- `person` — Person-specific information (contacts, roles)
- `project` — Project context, status, deliverables

### jcodemunch Integration (Token Efficiency)
When enabled (default), Open Brain uses jcodemunch for symbol-level code retrieval instead of full-file reads, achieving 80-99% token savings.

**Agents should NOT directly read large files.** Instead:
1. Use memory search to find prior code analysis
2. If new analysis needed, use jcodemunch symbol retrieval (via MCP)
3. Store findings in memory for future reuse

### Configuration
All agents automatically have access to Open Brain via MCP. Enable in `archonx-config.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "enabled": true,
      "command": "python",
      "args": ["Open-brain-mcp-server/open_brain_mcp_server.py"],
      "env": {
        "SUPABASE_HOST": "31.220.58.212",
        "JCODEMUNCH_ENABLED": "true"
      }
    }
  }
}
```

### Compliance & Violations
- **Not searching memory before task** = redundant work, wasted tokens ✗
- **Not storing results** = knowledge lost, other agents reinvent wheel ✗
- **Direct file reads instead of jcodemunch** = token waste, overruns budget ✗
- **Leaving out task context in memory** = reduced searchability ✗

Violating memory protocol incurs token penalties and may trigger cost guard alerts.
# ArchonX OS Agent Doctrine
**Version:** 2.1.0 | **Authority:** ZTE + PAULIWHEEL

## 1. THE PRIME DIRECTIVE
The ArchonX OS is the primary source of truth for the autonomous agent swarm. Every action must follow the ZTE Protocol:
**WRITE → TEST → FIX → COMMIT → DEPLOY → VERIFY → NOTIFY**

## 2. AGENT RULES (PAULIWHEEL)
- PAULIWHEEL is the default coding behavior.
- Code-affecting operations must include a `bead_id` and execute through Ralphy loop stages (PLAN, IMPLEMENT, TEST, EVALUATE, PATCH, REPEAT).
- Agent Lightning bootstrap is required before other functional changes.
- Minimal diffs only; avoid broad refactors unless required.

## 3. CONTEXT & MEMORY (Open Brain)
- **Search First**: EVERY agent MUST call `search_memories` before starting a task.
- **Store Always**: EVERY agent MUST call `store_memory` after completion.
- **jcodemunch**: Use symbol-level retrieval via MCP for 90%+ token efficiency.

## 4. SECURITY & VAULT
- **Zero-Trust**: No secrets in code or plaintext. Use `archonx/security/vault.py`.
- **Classification**: Secrets are categorized as CRITICAL, HIGH, MEDIUM, or LOW risk.
- **Audit**: Run `RedteamSkill` or `vault_agent.py` before every deployment.

## 5. REPO COMPLIANCE
Every managed repo must include:
1. `.archonx/reportback.json`
2. `.archonx/toolbox.json`
3. Standard commands: `dev`, `test`, `lint`.

## 6. RUNNER CONTRACT
The ArchonX Ops Runner must:
1. Read eco-prompts from `security/codex/eco-prompts/*.json`.
2. Execute steps in deterministic order.
3. Write machine-readable reports under `ops/reports/`.

## 7. ConX LAYER PROTOCOL
The ConX Layer provides remote machine control as a native ARCHON-X feature.

### Machine Registration
Every connected laptop registers itself via POST /conx/register with:
- hostname (unique machine identifier)
- tunnel_url (Cloudflare tunnel endpoint)
- os (Windows/Mac/Linux)
- mcp_servers (list of wired MCP servers)

### Onboarding New Machine (Human Action Required)
For Windows:
  iwr https://raw.githubusercontent.com/executiveusa/archonx-os/main/scripts/conx-onboard.ps1 | iex

For Mac/Linux:
  curl -fsSL https://raw.githubusercontent.com/executiveusa/archonx-os/main/scripts/conx-onboard.sh | bash

This is the ONLY human action required. Everything else is automated.

### Agent Access Rules
- Agents MAY read files from registered machines via Desktop Commander tunnel
- Agents MAY write files with explicit task authorization
- Agents MAY run shell commands ONLY with human confirmation via Telegram
- Agents MUST log all file operations to Notion
- Agents MUST NOT store credentials from remote machines

## 8. CLI-ANYTHING LAYER PROTOCOL

The CLI-Anything Layer extends ARCHON-X with universal software control - agents can now control ANY installed application (GIMP, Blender, LibreOffice, Audacity, custom enterprise software, etc.).

### How It Works

CLI-Anything auto-generates command-line interfaces for desktop applications:
- **Discovery:** Auto-detects installed apps (GIMP, Blender, Audacity, LibreOffice, etc.)
- **Generation:** Creates JSON-RPC schemas for each app's commands
- **Registry:** Maintains list of available CLIs across network
- **Execution:** Safely executes commands with validation and sandboxing

### Available Applications

**Design & Graphics:**
- GIMP - Image editor (create_image, apply_filter, export_image)
- Inkscape - Vector graphics
- Blender - 3D creation (create_scene, render_scene, add_object)
- Krita - Digital painting

**Office Suite:**
- LibreOffice - Documents, Spreadsheets, Presentations

**Media Production:**
- FFmpeg - Video/audio encoding
- Audacity - Audio editing (open_audio, apply_effect, export_audio)
- OBS - Screen recording/streaming
- Kdenlive - Video editing

**3D/CAD:**
- FreeCAD - 3D modeling
- Blender - Professional 3D suite

### Agent Usage via REST API

```bash
# List all available CLIs
GET /api/skills/cli-anything
→ {skills: {gimp: [...], blender: [...], ...}}

# Get schema for app
GET /api/skills/cli-anything/gimp
→ {commands: {create_image: {...}, apply_filter: {...}, ...}}

# Execute command
POST /api/skills/cli-anything/execute
Body: {app: "gimp", command: "create_image", params: {...}}
→ {status: "success", result: {...}}

# Discover installed apps
GET /api/skills/cli-anything/discover
→ {discovered_apps: [...], total: N}
```

### Agent Access Rules

✓ Agents MAY discover installed applications
✓ Agents MAY execute CLI commands with validation
✓ Agents MAY retrieve command schemas
✓ Agents MAY route commands to specific machines via ConX Layer
✗ Agents MUST NOT bypass validation
✗ Agents MUST NOT execute arbitrary shell
✗ Agents MUST NOT store app credentials
## 8. MANDATORY DESIGN LAW
- Any frontend, visual, dashboard, landing page, product-shell, or brand-surface work MUST load `.archonx/toolbox/skills/mandatory-design-law/SKILL.md` before implementation.
- Steve Krug logic is law for interface clarity: do not make the user think unnecessarily.
- Design work must be both visually intentional and immediately understandable.
- Reviewers must reject functional-but-confusing UI and generic AI-slop design.
- This rule applies to ArchonX itself and every managed repo under its control.
