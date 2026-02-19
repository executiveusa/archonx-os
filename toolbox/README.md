# ArchonX Toolbox

Canonical toolbox used by ArchonX ecosystem agents.

## Usage
1. Repos should include `.archonx/toolbox.json` as a pointer only.
2. Agents read `ARCHONX_TOOLBOX_URL` and pull `toolbox/toolbox.json`.
3. All toolbox actions require grant + work item ID.

## Current access mode
- **Git pull (default)** for simplicity in early rollout.
- Future enterprise upgrade path is tracked in `future-upgrades/TOOLBOX_HTTP_SERVICE_TODO.md`.

## Layout
- `skills/`: declarative skill manifests.
- `workflows/`: reusable playbooks.
- `tools/`: lightweight wrappers for grant + audit actions.
- `remotion/`: templates and renderer integration for video generation.
