# Franken-Claw™ — Divergence Changelog

**Tracking every point where Franken-Claw departs from upstream OpenClaw**

All entries are relative to the OpenClaw upstream baseline at the time of the fork. This changelog does not track OpenClaw's own upstream changes — it tracks Franken-Claw's divergence from that baseline.

---

## v1.4 — Franken-Claw™ Trademark + Brand Identity

**Date:** 2026-02-23
**Type:** Trademark / Brand
**Status:** Active

### Changes

- Formally established **Franken-Claw™** as a registered trademark of THE PAULI EFFECT
- Created brand identity document (`BRAND.md`) defining visual identity, voice, colors, and usage rules
- Primary color: Electric Green (`#00FF88`) + Dark Steel (`#1A1A2E`)
- Tagline established: "OpenClaw had 56 tools. We gave it a brain, a badge, and a conscience."
- Icon concept finalized: stitched-together claw with brain/badge/conscience motifs
- Trademark disambiguation: Franken-Claw™ is distinct from BENEVOLENCIA™, Frankenstack, and upstream OpenClaw

### Rationale

As Franken-Claw continues to diverge from upstream OpenClaw, establishing a clear trademark and brand identity prevents confusion with the upstream project and positions Franken-Claw as a distinct, ArchonX-native tool gateway with its own identity.

---

## v1.3 — Agent Heartbeat Protocol (agent-fleet-v1)

**Date:** 2026-02-20
**Type:** Protocol Addition
**Status:** Active

### Changes

- Added `agent-fleet-v1` heartbeat protocol to the Franken-Claw WebSocket gateway
- Agents send heartbeat payloads every **30 seconds** containing: `agent_id`, `timestamp`, `status`, `current_bead`, `crew`
- Gateway acknowledges each heartbeat with `{"ack": true, "timestamp": "<ISO-8601>"}`
- Fleet health state maintained in-memory; exposed via HTTP port 18790 at `/fleet/status`
- Dead agent detection: agent marked inactive after 2 missed heartbeat intervals (60 seconds)
- Crew-level aggregation: black crew and white crew health tracked separately
- King Mode dashboard integration: fleet status panel reads from `/fleet/status`

### Divergence from OpenClaw

OpenClaw has no agent heartbeat or fleet monitoring concept. This is a purely Franken-Claw addition.

### Files Added/Modified

- `services/franken-claw/heartbeat/` — heartbeat handler and fleet state manager
- `archonx/agents/base_agent.py` — added heartbeat emission loop

---

## v1.2 — Franken-Claw Skill Registry (archonx/skills/ Auto-Discovery)

**Date:** 2026-02-15
**Type:** Feature Addition
**Status:** Active

### Changes

- Added skill auto-discovery: at startup, Franken-Claw scans `archonx/skills/` for modules exposing a `SKILL_MANIFEST` object
- Discovered skills are registered as first-class tools in the tool registry alongside the OpenClaw base tools
- Skill manifest schema defined: `skill_id`, `description`, `input_schema`, `output_schema`, `crew_permissions`, `cost_class`
- Skill registry endpoint added at HTTP port 18790: `/skills/list` and `/skills/{skill_id}`
- Total tool count: 56+ (OpenClaw base) + variable ArchonX skills (grows as `archonx/skills/` expands)

### Divergence from OpenClaw

OpenClaw's tool registry is static at startup. Franken-Claw's registry is extended at startup via auto-discovery, making it dynamically extensible without modifying the gateway core.

### Files Added/Modified

- `services/franken-claw/registry/` — skill auto-discovery scanner and registry manager
- `archonx/skills/` — directory created for ArchonX-native skill modules

---

## v1.1 — PAULIWHEEL Bead Compliance Routing

**Date:** 2026-02-10
**Type:** Compliance Layer Addition
**Status:** Active

### Changes

- Added PAULIWHEEL compliance routing layer between IronClaw and the tool execution runtime
- Every tool call that passes IronClaw is logged to PAULIWHEEL before and after execution
- Log entry schema: `bead_id`, `agent_id`, `tool_name`, `input_schema_hash`, `execution_status`, `duration_ms`, `cost`, `timestamp`
- Bead identifiers sourced from `.beads/` issue tracking system — every tool action is traceable to a work item
- PAULIWHEEL logs written to `ops/reports/pauliwheel_YYYY-MM-DD.jsonl`
- Cost attribution enabled: per-bead tool costs aggregated for King Mode financial reporting
- Audit endpoint: HTTP port 18790 at `/pauliwheel/audit?bead_id=<id>`

### Divergence from OpenClaw

OpenClaw has no compliance logging, bead tracking, or cost attribution. PAULIWHEEL is entirely Franken-Claw native.

### Files Added/Modified

- `services/franken-claw/pauliwheel/` — compliance routing handler and log writer
- `archonx/kernel.py` — bead ID injection into tool call context

---

## v1.0 — IronClaw Security Layer

**Date:** 2026-02-05
**Type:** Security Layer Addition
**Status:** Active

### Changes

Added the IronClaw security layer — 7 modules — between the agent WebSocket connection and the OpenClaw tool execution runtime. All tool calls must pass all 7 IronClaw modules before reaching the execution runtime.

| Module          | File                                  | What It Does                                                          |
|-----------------|---------------------------------------|-----------------------------------------------------------------------|
| Tool Gating     | `archonx/security/tool_gating.py`     | Allow/deny tool calls based on agent identity and crew permissions    |
| Sandbox Policy  | `archonx/security/sandbox_policy.py`  | Enforce execution sandboxing for filesystem, network, subprocess tools |
| Safety Layer    | `archonx/security/safety_layer.py`    | Block tool calls matching known unsafe patterns                       |
| Leak Detector   | `archonx/security/leak_detector.py`   | Detect and block exfiltration of secrets, credentials, sensitive data |
| Env Scrubber    | `archonx/security/env_scrubber.py`    | Scrub environment variables from tool outputs before returning results |
| Cost Guard      | `archonx/security/cost_guard.py`      | Enforce per-agent and per-session cost limits                         |
| Command Guard   | `archonx/security/command_guard.py`   | Block dangerous shell commands; enforce command allowlist/blocklist   |

IronClaw modules execute in sequence. A block at any module aborts the tool call and returns a structured error to the calling agent. No module is optional.

### Divergence from OpenClaw

OpenClaw has no security enforcement layer. All security in stock OpenClaw relies on the calling application. IronClaw moves security enforcement into the gateway, making it impossible for any agent in the ArchonX ecosystem to bypass regardless of how the agent is implemented.

### Files Added/Modified

- `archonx/security/tool_gating.py` — new
- `archonx/security/sandbox_policy.py` — new
- `archonx/security/safety_layer.py` — new
- `archonx/security/leak_detector.py` — new
- `archonx/security/env_scrubber.py` — new
- `archonx/security/cost_guard.py` — new
- `archonx/security/command_guard.py` — new
- `services/franken-claw/ironclaw/` — IronClaw orchestrator

---

## Upstream Baseline

**OpenClaw version forked:** Latest stable at time of fork (2026-02-05)

OpenClaw upstream continues to evolve independently. Franken-Claw does not automatically merge upstream changes. Upstream changes are reviewed quarterly; security patches are merged on an expedited basis.

Any upstream OpenClaw changes that conflict with IronClaw, PAULIWHEEL, the skill registry, or the heartbeat protocol are rejected in favor of Franken-Claw's implementations.
