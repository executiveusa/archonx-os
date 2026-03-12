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
