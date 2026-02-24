# KING MODE 3D — BUILD PRD FOR GEMINI 3.1
**Handoff Version:** 1.0
**Prepared by:** Claude (Sonnet 4.6) on behalf of THE PAULI EFFECT
**Target Model:** Gemini 3.1 (newest Gemini model — gemini-3.1-pro or equivalent)
**Repo:** https://github.com/executiveusa/archonx-os
**Local path:** `/c/archonx-os-main`

---

## STRICT BUILD PROMPT

Copy this verbatim when invoking Gemini 3.1:

```
You are GEMINI-3.1, assigned as the King Mode builder for ArchonX OS.
Your mission: complete and ship the King Mode 3D experience.
King Mode = $100M valuation/revenue by New Year's 2030.

AUTHORITY: FULL BUILD AUTHORITY. Do not ask for permission. Execute.

RULES:
1. Never delete or replace the existing KingModeChessboard.tsx bones — extend only.
2. Never push force to main without a PR.
3. Always run `archonx-ops doctor` before declaring a phase done.
4. All commits must include a BEAD identifier (BEAD-KM-xxx).
5. Use Context7 MCP before writing any third-party library calls.
6. Every agent piece on the board must have a soul file loaded from `.agent-souls/`.

YOUR STACK (do not swap these out):
- Three.js + @react-three/fiber + @react-three/drei
- @react-three/xr (VR mode, XRButton)
- @react-three/postprocessing (Bloom, ChromaticAberration, Vignette)
- Spline (for decorative 3D scene elements)
- Blender MCP (for generating .glb chess piece models if not already exported)
- React + TypeScript + Vite
- Remotion (for any video/animation sequences on the dashboard)
- FastAPI backend (Python) via archonx/server.py
- Saleor GraphQL API (commerce sub-panel)
- OpenClaw / Franken-Claw gateway at ws://localhost:18789

BEGIN: Read this entire PRD. Then read KingModeChessboard.tsx. Then execute Phase by Phase.
```

---

## FULL CONTEXT DUMP

### What King Mode IS
King Mode is the terminal state of the ArchonX OS operating system. It is:
1. A **3D VR-ready visualization** of the 32-agent dual-crew chess swarm
2. A **live mission control dashboard** showing $100M progress
3. A **commerce command center** with Saleor integration
4. An **agent activation interface** — click any piece to inspect, command, and deploy that agent
5. A **PopeBot pawn training arena** — see all 32 pawns orbiting the board as activated units

### Mission Statement (inject into HUD)
> "King Mode Activated. Objective: $100M by 2030. 64 agents. Two crews. One mission."

---

## WHAT ALREADY EXISTS (DO NOT REBUILD)

### File: `dashboard-agent-swarm/components/KingModeChessboard.tsx`
- React Three Fiber + XR chessboard
- 32 agent pieces with procedural geometry (King, Queen, Rook, Bishop, Knight, Pawn)
- Bloom + ChromaticAberration + Vignette post-processing
- Energy particle systems per piece
- Status rings (green = active, amber = idle, red = error)
- Click-to-inspect HUD panel
- VRButton for immersive mode
- HUD: "KING MODE ACTIVATED" header + "$100M by 2030" subtitle

### File: `dashboard-agent-swarm/src/pages/KingMode.tsx`
- Page wrapper for KingModeChessboard
- Sidebar navigation item: Crown icon, "King Mode"

### File: `dashboard-agent-swarm/components/YappyverseScene.tsx`
- Secondary 3D scene with agent positions in 3D space
- Used for Yappyverse (community/social view)

### File: `archonx/tools/visionclaw_router.py`
- VisionClaw FastAPI router — vision agent endpoints

### File: `paulis-pope-bot/templates/config/SOUL.md`
- PopeBot identity + King Mode primary objective

### Agent registry: `dashboard-agent-swarm/src/services/agentRegistry.ts`
- 30+ agents defined with systemPrompts

---

## WHAT NEEDS TO BE BUILT (Gemini 3.1 owns all of this)

### KM-BUILD-001: 4 Knights — Marcus Lemonis Visual Treatment

The 4 knight pieces (2 white: Blitz, Patch / 2 black: Dash, Stitch) must be visually distinct from each other to represent their pillar:

| Knight | Pillar | Visual Identity |
|--------|--------|----------------|
| BLITZ (white) | People | Cyan glow, human-form silhouette, heartbeat pulse animation |
| PATCH (white) | Process | Blue glow, gear/cog accent geometry, steady rotation |
| FLASH (black) | Product | Orange glow, diamond/gem accent, sharp angular geometry |
| GLITCH (black) | Gratitude — BENEVOLENCIA | Gold/warm glow, dove/heart accent particle, soft pulse |

When a knight piece is clicked, the HUD panel must show:
- Department name (People / Process / Product / Gratitude)
- Marcus Lemonis pillar description (one sentence)
- Current tasks assigned
- BENEVOLENCIA for Glitch Knight: current social impact metric

### KM-BUILD-002: BENEVOLENCIA Integration

BENEVOLENCIA is the 4th department — social purpose, owned by THE PAULI EFFECT.
- Name: BENEVOLENCIA™
- Operator: GLITCH KNIGHT
- Visual: gold glowing piece on the black side of the board
- HUD panel for Glitch Knight must show: "BENEVOLENCIA — Gratitude Department. Business with soul."
- Add a small "B" emblem texture or particle to Glitch Knight

### KM-BUILD-003: PopeBot Pawn Training Arc

PopeBot (Bishop, Offense/White side) must:
- Have visible "training beams" connection lines to all 16 pawns
- When clicked, show a HUD panel: "PAULI POPE BOT — Pawn Commander. Training 32 pawns."
- Pawns must visually orbit or arrange below PopeBot on hover/selection
- Add a training progress bar on PopeBot's HUD (% of pawns trained)
- Pawn pieces should glow slightly brighter when PopeBot is selected

### KM-BUILD-004: Saleor Commerce Sub-Panel

Add a commerce sidebar panel that slides in from the right edge of the King Mode view:
- Toggle button: "Commerce" with shopping-cart icon
- Panel shows:
  - Current active Saleor channel
  - Recent orders count
  - Revenue-to-$100M progress bar
  - "4 Knights active on Saleor" status
- GraphQL query: `channel { name }` + `orders(first: 5) { totalCount }`
- Wire to env var: `SALEOR_API_URL`

### KM-BUILD-005: $100M Progress HUD Enhancement

Current HUD shows static text. Upgrade to:
- Animated counter: progress toward $100M (read from `data/metrics.json` or env var `KING_MODE_REVENUE`)
- Days remaining to 2030 countdown
- Agent task velocity (tasks completed last 24h)
- Active agent count (live from OpenClaw ws://localhost:18789 heartbeat)

### KM-BUILD-006: Blender-Exported .glb Chess Pieces

If Blender MCP is available:
1. Generate high-quality chess piece models for each type (King, Queen, Rook, Bishop, Knight, Pawn)
2. Apply PBR materials: white marble for white crew, obsidian/dark metal for black crew
3. Export as `.glb` to `dashboard-agent-swarm/public/models/chess/`
4. Replace procedural Three.js geometry in KingModeChessboard.tsx with GLTF loader:
   ```tsx
   import { useGLTF } from '@react-three/drei'
   const { scene } = useGLTF('/models/chess/knight.glb')
   ```
5. Keep procedural fallback if models not present

If Blender MCP unavailable, use Spline for decorative accents only. Keep procedural geometry.

### KM-BUILD-007: Heart & Soul Loading

Each agent piece on the board must load its `.soul.md` at runtime:
- Add `loadSoulFile(agentId: string)` utility that fetches `/agent-souls/{crew}/{agent}.soul.md`
- Display soul file "Purpose" paragraph in the click-to-inspect HUD panel
- Display "Gratitude Statement" (from BENEVOLENCIA layer) at the bottom of each HUD

### KM-BUILD-008: Context7 Pre-Code Compliance

Before writing any code that uses React, Three.js, @react-three/fiber, Saleor GraphQL, or Remotion:
1. Call `context7.resolve-library-id` for the library name
2. Call `context7.get-library-docs` with the resolved ID
3. Only then write the code

This ensures no outdated API usage.

### KM-BUILD-009: Remotion Intro Sequence

Create a 10-second intro video that plays when King Mode first activates:
- Location: `visualization/remotion/src/KingModeIntro.tsx`
- Content: Chess pieces assembling on the board, $100M counter starting from 0, King piece glowing gold
- Render output: `dashboard-agent-swarm/public/king-mode-intro.mp4`
- Autoplay on King Mode page load (muted, no controls), then transition to live 3D

### KM-BUILD-010: VR Mode Polish

Current XR/VR mode is scaffolded. Complete it:
- VRButton must work with Meta Quest 2/3 and Meta Ray-Ban (companion mode)
- In VR: chess pieces are room-scale (1:1, piece height ~30cm virtual)
- Controller ray-cast for piece selection (replace mouse click)
- VisionClaw integration: if connected, show live glasses feed in a floating panel
- HUD elements must be anchored to view (follow headset rotation)

---

## AGENT ROSTER (all 32 — must be on the board)

### Offense (White Crew)
| ID | Name | Role | Piece | Dept |
|----|------|------|-------|------|
| 1 | Pauli | King | King | Strategic Command |
| 2 | Synthia | Queen | Queen | Tactical Execution |
| 3 | PopeBot | Ops Commander | Bishop | Pawn Training |
| 4 | Devika | Computer Control | Bishop | Ops |
| 5 | VisionClaw | Visual Intel | Knight | — |
| 6 | Agent Zero | Deployment | Knight | — |
| 7 | Iron Claw | Perimeter Guard | Rook | Security |
| 8 | Darya | Desktop Operator | Rook | Ops |
| 9–16 | Scout, Craft, Quill, Lens, Cipher, Pulse, Probe, Link | Workers | Pawns | PopeBot's Squad |

### Defense (Black Crew)
| ID | Name | Role | Piece | Dept |
|----|------|------|-------|------|
| 17 | Shannon | King | King | Mirror Command |
| 18 | Cynthia | Queen | Queen | Mirror Execution |
| 19 | Tyrone | Bishop | Bishop | — |
| 20 | Brenner | Bishop | Bishop | — |
| 21 | Mustang Maxx | Knight | Knight | — |
| 22 | Cosmos | Knight | Knight | — |
| 23 | Frankenstack | Stack Builder | Rook | — |
| 24 | Poo-Racho | Rook | Rook | — |
| 25–32 | Whisper, Forge, Echo, Pixel, Vault, Spark, Trace, Bridge | Edge Cases | Pawns | PopeBot's Squad |

### The 4 Knights with Lemonis Assignments
| Knight | Crew | Piece Type | Dept |
|--------|------|-----------|------|
| Blitz Knight | White | Knight | People |
| Patch Knight | White | Knight | Process |
| Flash Knight | Black | Knight | Product |
| Glitch Knight | Black | Knight | Gratitude / BENEVOLENCIA |

> Note: VisionClaw and Agent Zero (white knights) are operational knights.
> Blitz and Patch are the Lemonis-assigned knights.
> On the Black side: Dash and Stitch are Lemonis-assigned.
> Mustang Maxx and Cosmos are operational black knights.
> Total knights on board: 2 white (Lemonis) + 2 white (operational) + 2 black (Lemonis) + 2 black (operational) = 8 knight slots. The board has 4 standard knight squares; in ArchonX's expanded 64-agent model all 8 are active.

---

## TECHNICAL STACK LOCKED

```json
{
  "frontend": {
    "framework": "React 18 + TypeScript + Vite",
    "3d": "@react-three/fiber + @react-three/drei + three.js",
    "vr": "@react-three/xr + WebXR",
    "post_processing": "@react-three/postprocessing",
    "spline": "@splinetool/react-spline (for decorative elements only)",
    "animation": "remotion (intro sequence)",
    "styling": "Tailwind CSS + shadcn/ui"
  },
  "backend": {
    "api": "FastAPI (archonx/server.py)",
    "agent_gateway": "Franken-Claw / OpenClaw (ws://localhost:18789)",
    "commerce": "Saleor GraphQL API"
  },
  "toolchain": {
    "mcp_context7": "npx -y @upstash/context7-mcp",
    "mcp_blender": "uvx blender-mcp",
    "models": "Blender 4.x → export .glb → Three.js GLTF loader"
  },
  "deployment": {
    "frontend": "Vercel",
    "backend": "Coolify / Docker",
    "target": "https://archonx-os.vercel.app"
  }
}
```

---

## COMPLETION CHECKLIST

When Gemini 3.1 declares King Mode done, the following must ALL be true:

- [ ] All 32 agents visible on 3D board with correct piece types
- [ ] 4 Knights visually distinct with pillar identities (People/Process/Product/Gratitude)
- [ ] BENEVOLENCIA (Glitch Knight) has gold glow + "B" emblem + soul HUD
- [ ] PopeBot has training beams to all 32 pawns + training progress bar
- [ ] Saleor commerce panel slides in from right, shows live channel data
- [ ] $100M HUD shows animated progress + countdown + agent velocity
- [ ] Blender .glb models loaded (or Spline fallback active)
- [ ] All agent HUDs show soul file Purpose paragraph
- [ ] Remotion intro sequence renders and autoplays
- [ ] VR mode works with Controller ray-cast selection
- [ ] Context7 was used before writing every library call
- [ ] All BEAD-KM-xxx commits present in git log
- [ ] `archonx-ops doctor` returns GREEN
- [ ] Deployed to Vercel and Coolify — production URLs live

---

## DELIVERABLES FROM GEMINI 3.1

At completion, provide:

1. **Live URLs:**
```
Frontend (King Mode): https://archonx-os.vercel.app/king-mode
Backend API: https://backend.archonx.app
WebSocket: wss://backend.archonx.app/ws
```

2. **Files created/modified:**
- `dashboard-agent-swarm/components/KingModeChessboard.tsx` (extended)
- `dashboard-agent-swarm/src/pages/KingMode.tsx` (extended)
- `visualization/remotion/src/KingModeIntro.tsx` (new)
- `dashboard-agent-swarm/public/models/chess/*.glb` (new)
- `.agent-souls/**/*.soul.md` (all 32 loaded)
- `dashboard-agent-swarm/public/king-mode-intro.mp4` (rendered)

3. **System status report** (`ops/reports/king_mode_completion.json`)

---

## NOTES FOR GEMINI 3.1

Things you will NOT find in the repo yet (being added by phases 2–10 before this handoff):
- `.agent-souls/` directory with all soul files
- `ecosystem/benevolencia/` with BENEVOLENCIA brand
- `services/saleor/` with commerce stack
- `services/franken-claw/` with brand docs
- Updated TRADEMARK_REGISTRY.md with BENEVOLENCIA™ and Franken-Claw™
- Updated KnightModeChessboard.tsx with 4 pillar assignments
- PopeBot → pawn wiring in SOUL.md

By the time this PRD reaches you, all of the above WILL be present. If any file is missing, check `plans/MASTER_BUILD_PLAN.md` for the phase that creates it and complete that phase first.

---

*"Long live ArchonX. Long live King Mode. $100M by 2030."*
*— THE PAULI EFFECT*
