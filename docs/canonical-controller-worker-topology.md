# Canonical Controller-Worker Topology

## Core Rule
`archonx-os` is the only controller in the ecosystem.

It owns:
- planning
- routing
- state
- policy
- approval boundaries
- repo and capability registry

## Mandatory Layers
- `DesktopCommanderMCP`: primary control tower for machine actions
- `mcp2cli`: mandatory invocation layer for MCP and OpenAPI tools
- `Darya/OpenHands`: execution hands worker
- `agency-agents`: multi-agent worker service
- `Agent Zero`: specialized worker
- `Goose`: cloud coding worker
- `ralphy`: specialized worker
- `ext-apps`: connector plugin layer
- `jcodemunch-mcp`: MCP plugin layer
- `Notion`: second-brain memory backend
- `pauli-comic-funnel`: canonical Pauli frontend
- `THE PAULI EFFECT`: product and brand layer on top of Archon-X

## Repo-Native Source Files
- `ecosystem/manifest.canonical.json`
- `data/architecture/archon_install_plan.json`
- `data/architecture/archon_integration_graph.json`
- `data/architecture/archon_risk_register.json`
- `data/architecture/archon_canonical_architecture.json`
- `plans/ARCHONX_BUILD_PLAN_SYNTHESIS.md`
- `plans/ARCHONX_FINAL_ARCHITECTURE_REPORT.md`

## Practical Next Step
Implement the repo registry and worker capability registry in `archonx-os`, then connect Darya, agency-agents, Goose, and DesktopCommanderMCP through one Archon-owned routing contract.
