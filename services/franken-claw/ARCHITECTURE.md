# Franken-Claw™ — Technical Architecture

**How Franken-Claw differs from upstream OpenClaw**

---

## Overview

Franken-Claw™ is a fork of OpenClaw. It preserves the OpenClaw tool execution runtime and network interface while extending it with four major proprietary layers. This document defines the full architecture of Franken-Claw as deployed in the ArchonX ecosystem.

---

## Layer 0: OpenClaw Upstream (Preserved)

These components are inherited directly from upstream OpenClaw and are preserved without modification unless noted.

| Component              | Description                                                        |
|------------------------|--------------------------------------------------------------------|
| WebSocket gateway      | Port **18789** — primary agent connection interface                |
| HTTP interface         | Port **18790** — REST-style tool invocation and status endpoint    |
| Tool execution runtime | Stateless tool execution with structured input/output              |
| Base tool registry     | 56+ tools covering filesystem, web, code, search, and more        |
| Tool schema system     | JSON-schema based tool definitions with input validation           |

All ArchonX agents connect to the Franken-Claw WebSocket gateway at:

```
ws://localhost:18789
```

No agent should connect directly to a raw upstream OpenClaw instance. If you see an agent connecting to any other OpenClaw endpoint, it is a misconfiguration.

---

## Layer 1: IronClaw Security Layer

IronClaw is Franken-Claw's proprietary security enforcement layer. It sits between the agent connection and the tool execution runtime, intercepting all tool calls for policy evaluation before execution.

All IronClaw modules are located in `archonx/security/`.

### Modules

| Module                | File                                  | Responsibility                                                                 |
|-----------------------|---------------------------------------|--------------------------------------------------------------------------------|
| Tool Gating           | `archonx/security/tool_gating.py`     | Allow/deny tool calls based on agent identity and crew permissions             |
| Sandbox Policy        | `archonx/security/sandbox_policy.py`  | Enforce execution sandboxing for filesystem, network, and subprocess tools     |
| Safety Layer          | `archonx/security/safety_layer.py`    | Block tool calls that match known unsafe patterns                              |
| Leak Detector         | `archonx/security/leak_detector.py`   | Detect and block exfiltration of secrets, credentials, and sensitive data      |
| Env Scrubber          | `archonx/security/env_scrubber.py`    | Scrub environment variables from tool outputs before returning to agents       |
| Cost Guard            | `archonx/security/cost_guard.py`      | Enforce per-agent and per-session cost limits on expensive tool operations     |
| Command Guard         | `archonx/security/command_guard.py`   | Block dangerous shell commands; enforce command allowlist/blocklist            |

### IronClaw Execution Flow

```
Agent -> WebSocket (18789) -> IronClaw [tool_gating -> safety_layer -> leak_detector
         -> env_scrubber -> cost_guard -> command_guard -> sandbox_policy]
         -> Tool Execution Runtime -> Response -> [env_scrubber] -> Agent
```

All seven IronClaw modules are applied in sequence. A block at any module aborts the tool call and returns a structured error to the agent. No module is optional.

---

## Layer 2: PAULIWHEEL Compliance Routing

PAULIWHEEL is Franken-Claw's compliance logging layer. Every tool call that passes IronClaw is logged to PAULIWHEEL before and after execution.

### What PAULIWHEEL Logs

Every tool call generates a PAULIWHEEL entry containing:

- **Bead identifier** — the unique ID of the agent action (from `.beads/`)
- **Agent ID** — which agent made the call
- **Tool name** — which tool was invoked
- **Input schema hash** — a hash of the tool inputs (not the raw inputs, for security)
- **Execution status** — success / error / blocked
- **Duration** — wall-clock execution time in milliseconds
- **Cost** — estimated cost if applicable (LLM calls, API calls)
- **Timestamp** — ISO-8601

### Why Bead Identifiers

PAULIWHEEL uses bead identifiers (from the `.beads/` issue tracking system) to link every tool call to a work item. This means:

- Every tool action is traceable to a specific task or issue
- Compliance audits can reconstruct what was done for any given bead
- Cost attribution is accurate at the task level
- King Mode reporting can tie infrastructure costs to specific work streams

---

## Layer 3: Franken-Claw Skill Registry

The Franken-Claw skill registry extends the OpenClaw base tool registry with ArchonX-native skills discovered from `archonx/skills/`.

### Auto-Discovery

At startup, Franken-Claw scans `archonx/skills/` for Python modules that expose a `SKILL_MANIFEST` object. Discovered skills are registered as first-class tools alongside the OpenClaw base tools.

Skills are registered with:
- A unique skill ID (e.g., `archonx.skills.pauliwheel_log`)
- A JSON schema for inputs and outputs
- Crew/agent permission requirements
- Cost classification (cheap / moderate / expensive)

### Registry Composition

| Source                  | Tool Count  | Notes                                           |
|-------------------------|-------------|-------------------------------------------------|
| OpenClaw upstream       | 56+         | All original OpenClaw tools                     |
| ArchonX skills registry | Variable    | Grows as new skills are added to `archonx/skills/` |
| Total                   | 56+ (growing) | Live count at runtime                         |

---

## Layer 4: Agent Heartbeat Protocol

The agent heartbeat protocol (`agent-fleet-v1`) is a Franken-Claw native protocol that enables fleet-wide agent health monitoring.

### Protocol

- **Name:** `agent-fleet-v1`
- **Interval:** Every 30 seconds
- **Direction:** Agent -> Franken-Claw gateway
- **Payload:**

```json
{
  "protocol": "agent-fleet-v1",
  "agent_id": "<agent_identifier>",
  "timestamp": "<ISO-8601>",
  "status": "active | idle | error",
  "current_bead": "<bead_id or null>",
  "crew": "black | white | null"
}
```

- **Gateway response:** `{"ack": true, "timestamp": "<ISO-8601>"}`

### What Heartbeats Enable

- Real-time agent fleet status on the King Mode dashboard
- Automatic detection of stalled or dead agents
- Crew-level health monitoring (black crew vs white crew)
- Bead-level work-in-progress tracking across the fleet

---

## Full Stack Diagram

```
ArchonX Agents (black crew / white crew)
         |
         | ws://localhost:18789
         |
+--------v----------------------------------------------------------+
|                     FRANKEN-CLAW™                                 |
|                                                                   |
|  +--Layer 0: OpenClaw Upstream (WebSocket/HTTP, 56+ tools)----+  |
|  |                                                             |  |
|  |  +--Layer 1: IronClaw Security (7 modules)---------------+ |  |
|  |  |  tool_gating | sandbox_policy | safety_layer           | |  |
|  |  |  leak_detector | env_scrubber | cost_guard             | |  |
|  |  |  command_guard                                         | |  |
|  |  +-------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  +--Layer 2: PAULIWHEEL Compliance Routing---------------+ |  |
|  |  |  Bead ID logging | agent ID | tool name | cost        | |  |
|  |  +-------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  +--Layer 3: Franken-Claw Skill Registry-----------------+ |  |
|  |  |  OpenClaw base (56+) + archonx/skills/ auto-discovery | |  |
|  |  +-------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  +--Layer 4: Agent Heartbeat Protocol (agent-fleet-v1)---+ |  |
|  |  |  30s intervals | fleet health | bead tracking          | |  |
|  |  +-------------------------------------------------------+ |  |
|  +-------------------------------------------------------------+  |
+-------------------------------------------------------------------+
         |
         | HTTP port 18790
         |
+--------v------------------+
|  King Mode Dashboard /    |
|  PAULIWHEEL Audit UI      |
+---------------------------+
```
