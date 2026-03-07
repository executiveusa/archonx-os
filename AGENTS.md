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

## Vault Agent + AI Advisor Protocol (MANDATORY)

### Purpose
Every agent and deployment must implement automated secret management, rotation auditing, and AI-powered security recommendations. This prevents credential leaks, ensures compliance with rotation policies, and provides intelligent guidance for secret handling.

### Vault Agent Core Functions
The `vault_agent.py` tool provides:
1. **Secret Discovery** — Recursively find all `.env*` files across the repo
2. **Risk Classification** — Categorize secrets by type and assign risk levels:
   - **CRITICAL**: Cryptographic keys, database credentials, API keys with `sk-` prefix
   - **HIGH**: Auth tokens (JWT, GitHub, etc.), passwords without length validation
   - **MEDIUM**: Webhook URLs, generic secrets, encoded tokens
   - **LOW**: Configuration variables, version info, non-sensitive identifiers
3. **Audit Reporting** — Generate JSON reports with full inventory and findings
4. **Rotation Checklists** — Prioritized lists grouped by risk level for manual rotation
5. **Safe Templates** — Generate `.env` templates with `[REPLACE_TYPE]` placeholders
6. **Infisical Export** — Create import-ready JSON for HashiCorp Vault, Infisical, or similar tools

### AI Advisor Integration
The `ai_advisor.py` tool provides multi-backend recommendations:
- **Primary**: HuggingFace Inference API (Mistral-7B) via `HF_API_KEY`
- **Fallback 1**: Groq API (Mixtral-8x7b) via `GROQ_API_KEY`
- **Fallback 2**: Google Gemini API via `GOOGLE_API_KEY`
- **Fallback 3**: Offline mode (always available) with rule-based recommendations

**Environment Setup**:
```bash
export HF_API_KEY=hf_xxxxxxxxxxxxxx         # Optional: HuggingFace token
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx    # Optional: Groq token
export GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxx  # Optional: Gemini token
```

### Full Orchestration
The `run_full.py` orchestrator runs both systems in sequence:
1. **Stage 1**: Execute vault agent audit → generates vault_audit.json
2. **Stage 2**: Load audit, run AI advisor on critical secrets → generates ai_recommendations.json
3. **Stage 3**: Merge both outputs → generates integrated_report.json

**Run command**:
```bash
python3 run_full.py
```

### Mandatory Execution Points
- **On every PAULIWHEEL sync meeting** → Run `vault_agent.py --path .` and store findings in Open Brain memory
- **Before any deployment** → Run `run_full.py` and review ai_recommendations.json
- **Daily automated** → Cron job at 3:00 AM (configured by setup.sh) stores reports under `ops/reports/`
- **On secret rotation** → Update AGENTS.md with last rotation date and use AI advisor to guide new secret generation

### Report Locations
```
ops/reports/
├── vault_audit.json              # Complete audit with classifications
├── ai_recommendations.json        # AI-generated guidance (top critical secrets)
├── integrated_report.json         # Merged findings and recommendations
├── rotation_checklist.md          # Markdown checklist by risk level
├── safe_template.env             # Template with [REPLACE_*] placeholders
├── infisical_import.json         # Vault import format
└── cron.log                       # Automated daily run logs
```

### Integration with Open Brain Memory
After every vault audit, store findings in Open Brain:
```python
store_memory(
  agent_id="<your_agent_id>",
  content="Vault audit: 24 secrets, 8 critical, rotation due for API_SECRET_KEY, MONGO_CONNECTION",
  memory_type="insight",
  metadata={
    "audit_timestamp": "2026-03-07T07:59:13Z",
    "total_secrets": 24,
    "critical_count": 8,
    "report_path": "ops/reports/integrated_report.json"
  }
)
```

### Compliance & Violations
- **Skipping vault audit before deployment** = security breach risk ✗
- **Not implementing AI advisor feedback** = missed rotation deadlines, compromised secrets ✗
- **Leaving secrets in code instead of .env** = exposure to Git history ✗
- **Ignoring CRITICAL-level findings** = grounds for `restricted` status ✗

Violations trigger immediate audit escalation and cost guard alerts.
