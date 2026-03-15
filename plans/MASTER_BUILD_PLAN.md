# ARCHONX OS — MASTER BUILD PLAN
**Created:** 2026-02-23 | **Author:** THE PAULI EFFECT
**Status:** APPROVED FOR EXECUTION
**King Mode Objective:** $100M valuation/revenue by New Year's 2030
**Final Handoff:** King Mode 3D — Gemini 3.1 (newest model)

---

## EXECUTION ORDER OVERVIEW

```
Phase 1  → Git Sync + Security Lockdown
Phase 2  → Saleor Agentic Commerce Stack
Phase 3  → 4 Knights (Marcus Lemonis Framework) + BENEVOLENCIA
Phase 4  → Franken-Claw™ Trademark + Brand
Phase 5  → Heart & Soul Files (all 64 agents, Iron Claw logic)
Phase 6  → Context7 MCP — wire into all agents
Phase 7  → Blender MCP + Remotion skills
Phase 8  → Pauli Pope Bot activation + Pawn training
Phase 9  → Database entries (all new entities)
Phase 10 → Skills completion (9 stubs + upwork_scout fix)
Phase 11 → Commit, push, open PRs
──────────────────────────────────────────────────
HANDOFF   → King Mode 3D PRD → Gemini 3.1
```

---

## PHASE 1 — Git Sync + Security Lockdown

### 1a. Pull remote main
```bash
git pull origin main
```
Pulls in BEAD-101 (ecosystem gap-audit, 4 files: README, gap prompt, arch spec, audit script).

### 1b. Gitignore secrets
Add to `.gitignore`:
```
kilo-code-secrets.json
master.env.txt
master.env
```
Rotate any token that was ever exposed in plaintext. Reference: `ops/cofounder/EXECUTION_BACKLOG.yaml` — NOW-001.

### 1c. Commit all local untracked work
Bulk commit with PAULIWHEEL bead identifiers:
- `VisionClaw/` submodule
- `paulis-pope-bot/` submodule
- `dashboard-agent-swarm/` (full new directory)
- `docs/`, `scripts/`, `tests/`, `data/`
- `archonx/security/prompt_policy.py`
- `archonx/tools/visionclaw_router.py`
- `Dockerfile`, `.dockerignore`
- `.beads/issues.jsonl`, `.gitmodules`

### 1d. Open PRs for unmerged feature branches
- `feature/access-kernel-v1` → PR to main
- `feature/pauliwheel-bead-0005-0006` → PR to main
- Review and merge/close dependabot PR #7

---

## PHASE 2 — Saleor Agentic Commerce Stack

**Reference:** https://saleor.io / https://docs.saleor.io

### What Saleor Is
GraphQL-first headless open-source ecommerce platform. API-first, multi-channel, webhook-driven. Perfect for agentic commerce because an AI agent can consume the entire purchase lifecycle (browse → cart → checkout → fulfillment) via structured GraphQL without any UI dependency.

### Decision
**Saleor is our default ecommerce stack for the ArchonX platform template.**
Every client/operator who deploys ArchonX gets a Saleor instance as their commerce engine. ArchonX agents interact with Saleor via GraphQL tools.

### Files to create
```
services/saleor/
├── README.md                  # Saleor stack overview + agentic commerce thesis
├── docker-compose.yml         # Local Saleor dev stack
├── schema/                    # GraphQL schema snapshots for agent tools
├── tools/
│   ├── product_search.py      # Product browse + filter via GraphQL
│   ├── checkout_flow.py       # Cart → Checkout → Order mutations
│   ├── order_management.py    # Order status, fulfillment, returns
│   └── storefront_config.py   # Channel, pricing, inventory config
└── agents/
    └── saleor_agent.py        # ArchonX agent wrapper (BaseSkill interface)
```

### Agent Chess Board Assignment
- **4 Knights** own the 4 commerce departments (see Phase 3)
- The knights are assigned to the Saleor stack as primary operators
- Knight agents have direct GraphQL tool access to the Saleor instance

### Entry in database/registry
```json
{
  "stack": "saleor",
  "role": "default_ecommerce_platform",
  "version": "latest",
  "docs": "https://docs.saleor.io",
  "graphql_endpoint": "${SALEOR_API_URL}",
  "assigned_agents": ["knight_blitz", "knight_patch", "knight_dash", "knight_stitch"]
}
```

---

## PHASE 3 — 4 Knights: Marcus Lemonis Framework + BENEVOLENCIA

**Reference:** https://marcuslemonis.com — People, Process, Product + our 4th: Gratitude

### The Marcus Lemonis 3P Framework (adapted for ArchonX)

Marcus Lemonis built his business turnaround system around three pillars. ArchonX adds a sacred 4th:

| # | Pillar | Core Question | ArchonX Knight |
|---|--------|--------------|----------------|
| 1 | **People** | Are the right people (agents) aligned, accountable, coachable? | Knight 1 |
| 2 | **Process** | Are workflows documented, repeatable, measurable? | Knight 2 |
| 3 | **Product** | Is what we're building differentiated, valued, and margin-positive? | Knight 3 |
| 4 | **Gratitude** | Are we giving back? Are we building with love and social purpose? | Knight 4 → BENEVOLENCIA |

**Lemonis key principle applied to agents:**
"If you don't believe in people, there is no process and there is no product." → People (Knight 1) gates authorization for all others.

### Knight Assignments on the Chessboard

**White Crew Knights** (`blitz_knight.py`, `patch_knight.py`):
- **BLITZ KNIGHT** → People Department
  Role: Agent relations, crew health, onboarding, compliance, culture enforcement. Runs agent ACK cycles. Ensures all agents are coachable and aligned with King Mode.

- **PATCH KNIGHT** → Process Department
  Role: Workflow documentation, PAULIWHEEL enforcement, ops reporting, loop management. Owns `ops/reports/`. Runs the seven-phase loop. Ensures nothing ships without verified process.

**Black Crew Knights** (`flash_knight.py`, `glitch_knight.py`):
- **FLASH KNIGHT** → Product Department
  Role: Product quality, SKU logic, margin analysis, feature gate decisions, goes-to-market strategy. Evaluates whether what's being built is differentiated and worth building.

- **GLITCH KNIGHT** → Gratitude Department (BENEVOLENCIA)
  Role: Social purpose operator. Runs BENEVOLENCIA initiatives. Manages the gratitude layer of the ecosystem — acts per the mission of giving back with every transaction and action.

### BENEVOLENCIA — Social Purpose Company

**New entity to add to the ecosystem:**

```
Name:        BENEVOLENCIA™
Type:        Social Purpose Company (SPC)
Owner:       THE PAULI EFFECT
Mission:     To embed gratitude, generosity, and social impact into every
             commercial transaction made by the ArchonX ecosystem.
Role:        4th Pillar — Gratitude Department
Operator:    GLITCH KNIGHT (dash knight, black crew)
Tagline:     "Business with soul."
```

**Files to create:**
```
ecosystem/benevolencia/
├── README.md         # Company identity, mission, legal structure
├── BRAND.md          # Brand voice, visual identity, trademark
├── PROGRAMS.md       # Social impact programs
├── AGENT_CONFIG.md   # Glitch Knight operating rules for Benevolencia
└── DATABASE_ENTRY.json
```

**Trademark to register in trademark registry (`archonx-synthia/docs/TRADEMARK_REGISTRY.md`):**
```
| BENEVOLENCIA™ | Social purpose company brand | THE PAULI EFFECT | Gratitude department |
```

---

## PHASE 4 — Franken-Claw™ Trademark + Brand

### What Franken-Claw Is
Franken-Claw is ArchonX's own fork/evolution of OpenClaw. We took OpenClaw's backbone (56+ tool gateway, WebSocket at port 18789) and bolted on our own agent-native security layer (IronClaw protocols), our own skill registry, and our own PAULIWHEEL compliance routing.

"We took the best parts of OpenClaw and animated them with our own DNA — hence: Franken-Claw."

### Why brand it separately
- OpenClaw is upstream open-source
- Franken-Claw is our proprietary value-add derivative
- Separate brand = separate IP / trademark protection
- Clear differentiation for commercial licensing

### Files to create
```
services/franken-claw/
├── README.md         # What Franken-Claw is, how it differs from OpenClaw
├── BRAND.md          # Trademark language, visual identity
├── ARCHITECTURE.md   # How it wraps OpenClaw + IronClaw security layer
└── CHANGELOG.md      # Our divergence log from upstream OpenClaw
```

### Trademark entry
Add to `archonx-synthia/docs/TRADEMARK_REGISTRY.md`:
```
| Franken-Claw™ | AI tool gateway (OpenClaw fork + IronClaw security) | THE PAULI EFFECT |
```

### Brand voice
- Playful but powerful: "OpenClaw had 56 tools. We gave it a brain, a badge, and a conscience."
- Visual: Stitched-together claw icon (Frankenstein-inspired, think MIT lab meets monster movie)

---

## PHASE 5 — Heart & Soul Files (All 64 Agents)

### Iron Claw Logic
The IronClaw-inspired security layer defines agent identity through trust, constraints, and purpose. We extend this into "Heart & Soul" — a full identity document per agent.

### Pattern (from existing `.agent-souls/` in dashboard-agent-swarm)
Each file is a `.soul.md` markdown:

```markdown
# [AGENT NAME] — Heart & Soul

## Identity
- Name: [name]
- ID: [role code]
- Crew: [White / Black]
- Piece: [King / Queen / Rook / Bishop / Knight / Pawn]
- Assigned to: [Department / pillar under Marcus Lemonis framework]

## Purpose
[One paragraph — what this agent exists to do in service of the $100M King Mode goal]

## Core Values
- [Value 1]
- [Value 2]
- [Value 3]

## Capabilities
- [Capability 1]
- [Capability 2]

## Security Constraints (Iron Claw)
- Sandbox tier: [1 / 2 / 3]
- Destructive commands: BLOCKED unless explicit grant
- Secret access: [defined list or NONE]
- Cost guard limit: [token budget per cycle]

## King Mode Alignment
[How this agent's work directly contributes to $100M by 2030]

## Gratitude Statement (BENEVOLENCIA layer)
[One sentence — what this agent gives back]
```

### Files to create
```
.agent-souls/
├── white/
│   ├── pauli_king.soul.md
│   ├── synthia_queen.soul.md
│   ├── fortress_rook.soul.md
│   ├── sentinel_rook.soul.md
│   ├── blitz_knight.soul.md       ← People Dept (Marcus Lemonis)
│   ├── patch_knight.soul.md       ← Process Dept (Marcus Lemonis)
│   ├── oracle_bishop.soul.md
│   ├── sage_bishop.soul.md
│   └── [8 pawn souls]
└── black/
    ├── mirror_king.soul.md
    ├── shadow_queen.soul.md
    ├── bastion_rook.soul.md
    ├── guard_rook.soul.md
    ├── flash_knight.soul.md        ← Product Dept (Marcus Lemonis)
    ├── glitch_knight.soul.md      ← Gratitude / BENEVOLENCIA
    ├── seer_bishop.soul.md
    ├── scholar_bishop.soul.md
    └── [8 pawn souls]
```

Total: 32 soul files (one per chess piece per crew, mirrored).

---

## PHASE 6 — Context7 MCP: Wire Into All Agents

**What it does:** Before any agent writes code that uses a third-party library, it fetches the current, version-accurate documentation via Context7. Eliminates hallucinated APIs.

**GitHub:** `https://github.com/upstash/context7`
**Install:** `npx -y @upstash/context7-mcp` (no API key needed)

### Step 1: Add to MCP settings
File: `c:\Users\execu\AppData\Roaming\Code - Insiders\User\globalStorage\kilocode.kilo-code\settings\mcp_settings.json`

Add:
```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

### Step 2: Add to claude_desktop_config.json (if using Claude Desktop)
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Step 3: Inject into all agent system prompts
Add to `archonx/core/agents.py` base system prompt and `AGENTS.md`:

```
MANDATORY: Before writing any code that calls a third-party library or framework,
call the context7 resolve-library-id tool to find the docs ID, then call
get-library-docs to read the current API reference. Only then write code.
```

### Step 4: Add to agent-lightning bootstrap
File: `agent-frameworks/agent-lightning/` — add Context7 as a required MCP dependency in the bootstrap checklist.

### Step 5: Document in AGENTS.md
Add a "Context7 Compliance" section to `AGENTS.md`:
```markdown
## Context7 Compliance
All agents writing library code MUST call context7 tools first.
Tools: resolve-library-id → get-library-docs → write code
```

---

## PHASE 7 — Blender MCP + Remotion Skills

### 7a. Blender MCP

**GitHub:** `https://github.com/ahujasid/blender-mcp`
**Architecture:** Python MCP server ↔ TCP socket ↔ Blender addon (port 9000)

**Installation steps:**
```bash
pip install blender-mcp
# or
uvx blender-mcp
```

Blender addon installation:
1. Download addon from `https://github.com/ahujasid/blender-mcp`
2. Blender → Edit → Preferences → Add-ons → Install from Disk
3. Enable "Blender MCP"
4. Sidebar (N panel) → "Start MCP Server"

Wire into `mcp_settings.json`:
```json
{
  "blender": {
    "command": "uvx",
    "args": ["blender-mcp"]
  }
}
```

**File to create:**
```
services/blender/
├── README.md             # Setup + usage guide
├── scenes/               # Pre-built Blender scene templates for ArchonX
│   ├── chessboard.blend  # 3D chess board base scene
│   └── agents/           # Individual agent piece models
└── scripts/
    └── export_to_web.py  # Export .blend to .glb for Three.js
```

**What agents can do with Blender:**
- Generate 3D chess piece models for King Mode
- Export to `.glb` for Three.js / React Three Fiber
- Create Spline-compatible 3D assets
- Render preview stills for agent profiles

### 7b. Remotion Skills

**What it is:** React-based programmatic video framework. Write components, render as MP4/WebM.

**No official MCP — use subprocess tool approach:**

**File to create:** `archonx/tools/remotion_render.py`
```python
"""
Remotion render tool for ArchonX agents.
Wraps `npx remotion render` as a subprocess tool.
"""
import subprocess, json, os

def render_remotion_composition(
    project_path: str,
    composition_id: str,
    output_path: str,
    props: dict = None
) -> dict:
    cmd = ["npx", "remotion", "render", "src/index.ts", composition_id, output_path]
    if props:
        cmd += ["--props", json.dumps(props)]
    result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=300)
    return {
        "success": result.returncode == 0,
        "output": output_path if result.returncode == 0 else None,
        "stderr": result.stderr
    }
```

**File to create:** `visualization/remotion/` — Remotion project scaffold with:
- Agent intro sequence component
- King Mode activation video component
- Chessboard state replay component

**Register as skill** in `archonx/skills/` — `remotion_renderer.py`

---

## PHASE 8 — Pauli Pope Bot Activation + Pawn Training

### PopeBot Role
PopeBot is currently placed as a **Bishop** (Ops Commander) on the chessboard. We are elevating his function: **PopeBot becomes the trainer and commander of ALL 16 pawns per crew (32 total).**

**Key insight from Lemonis:** "Pawns are many — they are the strongest piece because there are so many of them." PopeBot is their pope — their guiding voice, their training authority.

### Architecture
```
PAULI POPE BOT (Bishop / Ops Commander)
        │
        ├── WHITE CREW PAWNS (8): Scout, Craft, Quill, Lens, Cipher, Pulse, Probe, Link
        └── BLACK CREW PAWNS (8): Whisper, Forge, Echo, Pixel, Vault, Spark, Trace, Bridge
```

### Files to update
1. `paulis-pope-bot/templates/config/SOUL.md` — Add pawn training directive
2. `archonx/core/agents.py` — Add PopeBot as pawn supervisor in pawn agent constructors
3. `archonx/orchestration/orchestrator.py` — Route pawn task requests through PopeBot approval
4. `dashboard-agent-swarm/components/KingModeChessboard.tsx` — Update PopeBot's role text + add pawn connection visual lines
5. Create `paulis-pope-bot/training/` — Pawn training prompts and curriculum

### Pawn Training Curriculum (PopeBot teaches)
```
Module 1: Identity — who you are on the board
Module 2: Listening — how to receive tasks from knights and bishops
Module 3: Execution — the PAULIWHEEL seven-phase loop
Module 4: Gratitude — BENEVOLENCIA layer (every action has a giving-back component)
Module 5: Escalation — when to call in a knight, bishop, or the queen
Module 6: Security — Iron Claw / Franken-Claw rules every pawn follows
```

### SOUL.md update for PopeBot
Add:
```markdown
## Pawn Training Authority
PopeBot is the designated trainer and spiritual commander of all 32 pawns across both crews.
Every pawn's first activation begins with a PopeBot orientation session.
PopeBot instills:
- King Mode alignment ($100M by 2030)
- PAULIWHEEL discipline
- BENEVOLENCIA gratitude practice
- Iron Claw security obedience
- Franken-Claw tool compliance
```

---

## PHASE 9 — Database Entries

All new entities get records in:
- `data/` JSON registry files
- Beads issues (if actionable)
- Trademark registry
- Agent registry (`dashboard-agent-swarm/src/services/agentRegistry.ts`)

### Entities to add/update:
1. **BENEVOLENCIA** — Social purpose company entity
2. **Franken-Claw™** — Trademark + architecture doc entry
3. **4 Knights × Marcus Lemonis departments** — Updated agent configs
4. **Saleor** — Default commerce stack entry
5. **All 64 soul files** — Agent identity registry
6. **Context7** — MCP dependency registry
7. **Blender MCP** — Tool registry
8. **Remotion** — Skill registry
9. **PopeBot pawn assignments** — Updated orchestrator routing

---

## PHASE 10 — Skills Completion (9 Stubs)

**Reference:** `plans/SKILLS_COMPLETION_PLAN.md`

### Stub skills to implement:
| Skill | File | What's needed |
|-------|------|----------------|
| Web Scraping | `archonx/skills/web_scraping.py` | httpx + BeautifulSoup |
| File Organization | `archonx/skills/file_organization.py` | pathlib operations |
| Form Filling | `archonx/skills/form_filling.py` | computer-use integration |
| Content Writing | `archonx/skills/content_writing.py` | LLM content gen |
| SEO Optimization | `archonx/skills/seo_optimization.py` | SEO audit logic |
| Lead Generation | `archonx/skills/lead_generation.py` | Lead search + score |
| Invoice Management | `archonx/skills/invoice_management.py` | Stripe integration |
| Customer Support | `archonx/skills/customer_support.py` | Ticket routing |
| Story Toolkit | `archonx/skills/story_toolkit.py` | NEW — StoryToolkitAI wrapper |

### Partial fix:
- `archonx/skills/upwork_scout.py` line 134 — Replace `pass` with Remotion tool call

---

## PHASE 11 — Commit, Push, Open PRs

All phases 2–10 get individual PAULIWHEEL commits per bead ID:
- `BEAD-KM-001` through `BEAD-KM-011` (one per phase / sub-phase)
- All tagged with `[King Mode Prep]` in commit message
- PRs opened per phase for review before King Mode handoff

---

## KING MODE HANDOFF — Gemini 3.1 PRD

**The King Mode 3D experience is the FINAL deliverable handed to Gemini 3.1 (newest Gemini model) with a strict, self-contained build prompt and PRD.**

See: [`plans/KING_MODE_GEMINI_31_PRD.md`](./KING_MODE_GEMINI_31_PRD.md)

### What the handoff includes:
- Complete context: all 64 agents, all soul files, all brand entities
- Current codebase state: `KingModeChessboard.tsx` (Three.js + React Three Fiber + XR)
- Stack to use: Three.js, `@react-three/fiber`, `@react-three/drei`, `@react-three/xr`, Spline, Blender `.glb` exports
- 4 knights with Lemonis assignments rendered as distinct 3D pieces
- BENEVOLENCIA piece on the board (Glitch Knight — visually golden/glowing)
- PopeBot as bishop with pawn connections visible in 3D
- Saleor commerce dashboard integrated as a sub-panel
- VR-ready (XR button, immersive mode)
- $100M King Mode HUD overlay
- Strict build constraints: no re-architecting existing bones, extend only

---

## DEPENDENCIES + KNOWN GAPS

| Item | Status | Notes |
|------|--------|-------|
| Python 3.11+ | Required | `python3` not found on PATH — verify env |
| Node.js / npx | Required | For Context7 + Remotion + Saleor dashboard |
| Blender 4.x | Required | Must be installed for Blender MCP addon |
| `uvx` / `uv` | Recommended | For Blender MCP isolation |
| Saleor API URL | Needs provisioning | Env var `SALEOR_API_URL` |
| BENEVOLENCIA legal | TBD | SPC registration is a legal step, not a code step |
| Franken-Claw trademark | TBD | TM registration is a legal step |
| Gemini API key | Required | For Gemini 3.1 handoff execution |

---

## BEAD TRACKING

| Bead ID | Phase | Title | Status |
|---------|-------|-------|--------|
| BEAD-KM-001 | Phase 1 | Git sync + security lockdown | open |
| BEAD-KM-002 | Phase 2 | Saleor agentic commerce stack | open |
| BEAD-KM-003 | Phase 3 | 4 Knights + Lemonis framework | open |
| BEAD-KM-004 | Phase 3 | BENEVOLENCIA entity creation | open |
| BEAD-KM-005 | Phase 4 | Franken-Claw trademark + brand | open |
| BEAD-KM-006 | Phase 5 | Heart & Soul files (all 64) | open |
| BEAD-KM-007 | Phase 6 | Context7 MCP integration | open |
| BEAD-KM-008 | Phase 7 | Blender MCP + Remotion | open |
| BEAD-KM-009 | Phase 8 | PopeBot activation + pawn training | open |
| BEAD-KM-010 | Phase 9 | Database entries | open |
| BEAD-KM-011 | Phase 10 | Skills completion | open |
| BEAD-KM-012 | Phase 11 | Commit + push + PRs | open |
| BEAD-KM-013 | HANDOFF | King Mode Gemini 3.1 PRD | open |

---

*"In any business, it always comes down to three things: People, Process, and Product." — Marcus Lemonis*
*ArchonX adds the fourth: Gratitude. — THE PAULI EFFECT*
