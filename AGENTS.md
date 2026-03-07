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

## Open Brain MCP — Agent Memory Protocol

### Memory System Overview
All agents have access to a shared pgvector-backed memory layer via the Open Brain MCP server. This enables persistent, searchable memory across agent lifespans and coordination.

### Memory Architecture
- **Thoughts**: Raw memories, notes, insights (searchable by embedding)
- **Entities**: Named concepts (people, places, projects)
- **Repositories**: Linked GitHub repos with descriptions
- **Telemetry**: Event logging and token usage tracking
- **Lightning Events**: Agent lifecycle events

### Mandatory Memory Protocol

**EVERY agent MUST:**

1. **Before starting ANY task** → Call `search_memories` with task context
   ```
   search_memories(
     agent_id="<your_agent_id>",
     query="<task_context>",
     limit=5
   )
   ```
   This retrieves relevant prior context and decisions.

2. **After completing ANY task** → Call `store_memory` with results
   ```
   store_memory(
     agent_id="<your_agent_id>",
     content="<task_result>",
     memory_type="decision|insight|note",
     metadata={...}
   )
   ```
   This ensures continuity and avoids duplicate work.

3. **On agent startup** → Log lightning event
   ```
   log_lightning_event(
     agent_id="<your_agent_id>",
     event_type="agent_start",
     event_data={"version": "1.0", "mode": "production"}
   )
   ```

4. **On significant decisions** → Store as decision memory
   ```
   store_memory(
     agent_id="<your_agent_id>",
     content="<decision>",
     memory_type="decision",
     metadata={"rationale": "...", "impact": "..."}
   )
   ```

### Memory Types
- `note` — General information, observations
- `decision` — Important choices, trade-offs considered
- `insight` — Lessons learned, patterns discovered
- `meeting` — Meeting notes, attendees, action items
- `person` — Person-specific information (contacts, roles)
- `project` — Project context, status, deliverables

### jcodemunch Integration (Token Efficiency)
When enabled (default), Open Brain uses jcodemunch for symbol-level code retrieval instead of full-file reads, achieving 80-99% token savings.

**Agents should NOT directly read large files.** Instead:
1. Use memory search to find prior code analysis
2. If new analysis needed, use jcodemunch symbol retrieval (via MCP)
3. Store findings in memory for future reuse

### Configuration
All agents automatically have access to Open Brain via MCP. Enable in `archonx-config.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "enabled": true,
      "command": "python",
      "args": ["Open-brain-mcp-server/open_brain_mcp_server.py"],
      "env": {
        "SUPABASE_HOST": "31.220.58.212",
        "JCODEMUNCH_ENABLED": "true"
      }
    }
  }
}
```

### Compliance & Violations
- **Not searching memory before task** = redundant work, wasted tokens ✗
- **Not storing results** = knowledge lost, other agents reinvent wheel ✗
- **Direct file reads instead of jcodemunch** = token waste, overruns budget ✗
- **Leaving out task context in memory** = reduced searchability ✗

Violating memory protocol incurs token penalties and may trigger cost guard alerts.
