# Franken-Claw™

**ArchonX's proprietary fork and evolution of the OpenClaw tool gateway**

---

## What Is Franken-Claw?

Franken-Claw™ is what you get when you take the best open-source tool gateway ever built — **OpenClaw** — and graft on your own security layer, your own compliance routing, your own skill registry, and your own agent heartbeat protocol.

We took OpenClaw's backbone: 56+ tools, a WebSocket gateway at port 18789, an HTTP interface at port 18790, and a rock-solid tool-execution runtime. Then we animated it with our own DNA.

> "We took the best parts of OpenClaw and animated them with our own DNA — hence: Franken-Claw."

The result is not a wrapper. It is a fork. A living, growing, ArchonX-native tool gateway that will continue to diverge from upstream as our requirements evolve.

**Trademark: Franken-Claw™, owned by THE PAULI EFFECT.**

---

## Why Fork OpenClaw?

OpenClaw is an excellent general-purpose tool gateway. It was not built for:

- Multi-agent crew architectures (black crew / white crew)
- Bead-level compliance logging (PAULIWHEEL)
- IronClaw security enforcement (7 modules)
- ArchonX skill auto-discovery
- Agent heartbeat protocols at fleet scale

We needed all of those things. Forking was the right call.

---

## Core Inheritance from OpenClaw

Franken-Claw inherits and preserves:

| Component           | OpenClaw Origin                        | Status in Franken-Claw          |
|---------------------|----------------------------------------|---------------------------------|
| Tool gateway runtime | OpenClaw core                         | Preserved, extended             |
| WebSocket port 18789 | OpenClaw standard                     | Preserved                       |
| HTTP port 18790      | OpenClaw standard                     | Preserved                       |
| 56+ base tools       | OpenClaw tool registry                | Preserved, extended             |
| Tool execution model | OpenClaw                              | Preserved                       |

---

## What We Added

| Layer                    | Description                                                              |
|--------------------------|--------------------------------------------------------------------------|
| IronClaw Security Layer  | 7-module security enforcement (see `ARCHITECTURE.md`)                   |
| PAULIWHEEL Routing       | Bead-level compliance logging on every tool call                         |
| Skill Registry           | Auto-discovery of `archonx/skills/` extending base tool count            |
| Agent Heartbeat Protocol | `agent-fleet-v1`, 30-second intervals, fleet-wide agent health tracking  |

---

## Agent Connection

All ArchonX agents connect to Franken-Claw instead of raw OpenClaw. No agent in the ArchonX ecosystem should connect directly to an upstream OpenClaw instance.

**Connection endpoint:**

```
ws://localhost:18789
```

---

## Trademark

**Franken-Claw™** is a registered trademark of THE PAULI EFFECT.

Not to be confused with:
- **BENEVOLENCIA™** — the ArchonX social purpose company (different entity, different function)
- **Frankenstack** — a different agent in the ecosystem
- **OpenClaw** — the upstream open-source project Franken-Claw forked from

---

## Key Documents

| File              | Purpose                                              |
|-------------------|------------------------------------------------------|
| `BRAND.md`        | Visual identity, voice, and trademark rules          |
| `ARCHITECTURE.md` | Technical diff from upstream OpenClaw                |
| `CHANGELOG.md`    | Version history of Franken-Claw divergence from OpenClaw |
