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
