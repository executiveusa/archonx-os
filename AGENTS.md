# ArchonX OS Agent Rules

## PAULIWHEEL Default
- PAULIWHEEL is the default coding behavior for every coding agent operating in this repository.
- Code-affecting operations must include a bead identifier and execute through beads + Ralphy loop stages (PLAN, IMPLEMENT, TEST, EVALUATE, PATCH, REPEAT).
- Agent Lightning bootstrap is required before other functional changes in any touched repository.

## Compliance Gates
- Agents must ACK the latest eco-prompt, toolbox version, and contracts hash during scheduled sync meetings.
- Non-ACKed agents are `restricted` and may only heartbeat, request grants, and join meetings.

## Operational Cadence
- Run PAULIWHEEL sync meetings at least 3 times per day.
- Every run must execute verification (build/test where available + `archonx-ops doctor`) and emit machine-readable reports under `ops/reports/`.
