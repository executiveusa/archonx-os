# Blender MCP — ArchonX Integration
**BEAD-KM-008** | Owner: PATCH KNIGHT (Process Dept)

## What This Is

Blender MCP enables AI agents to control Blender 3D for generating chess piece models, scene exports, and visual assets for the King Mode 3D experience.

- **Upstream:** https://github.com/ahujasid/blender-mcp
- **Protocol:** MCP server ↔ TCP socket ↔ Blender addon (port 9000)
- **MCP config key:** `blender`

## Installation

### Step 1: Install MCP server
```bash
# Recommended (isolated environment)
uvx blender-mcp

# Or via pip
pip install blender-mcp
```

### Step 2: Install Blender addon
1. Download addon from https://github.com/ahujasid/blender-mcp
2. Blender → Edit → Preferences → Add-ons → Install from Disk
3. Select the addon `.zip` or `.py` file
4. Enable the addon via its checkbox
5. In the sidebar (N panel): click **"Start MCP Server"**

### Step 3: MCP settings (already configured)
`mcp_settings.json` already has:
```json
{
  "blender": {
    "command": "uvx",
    "args": ["blender-mcp"]
  }
}
```

## What Agents Can Do

- Generate chess piece 3D models (King, Queen, Rook, Bishop, Knight, Pawn) as `.glb`
- Apply PBR materials: white marble (white crew) / obsidian steel (black crew)
- Export scenes for Three.js / React Three Fiber consumption
- Render preview images for agent profile cards
- Create animated sequences for the King Mode intro

## Workflow: Chess Piece → Three.js

```
Agent calls Blender MCP tools
  → create_object / execute_blender_code (build piece geometry)
  → set_material (PBR marble or obsidian)
  → export .glb to dashboard-agent-swarm/public/models/chess/
  → Three.js loads via useGLTF('/models/chess/knight.glb')
  → KingModeChessboard.tsx renders piece in 3D scene
```

## Output Paths

| Asset | Path |
|-------|------|
| White crew pieces | `dashboard-agent-swarm/public/models/chess/white/` |
| Black crew pieces | `dashboard-agent-swarm/public/models/chess/black/` |
| Scene exports | `services/blender/scenes/` |
| Preview renders | `ops/reports/blender_previews/` |

## Requirements

- Blender 4.0+
- Python 3.10+ (for blender-mcp server)
- Node.js (for consuming in Three.js)
- `uvx` or `pip` for installing blender-mcp

## Troubleshooting

**"Connection refused on port 9000"** → Blender addon is not started. Open Blender → N panel → Start MCP Server.

**"uvx not found"** → Install `uv`: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Large .glb files** → Use Draco compression in Blender export settings or via `gltf-pipeline`.
