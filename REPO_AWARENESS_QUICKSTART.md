# ArchonX Repository Awareness System — Quick Start Guide

## Overview

This guide demonstrates the **INDEX-ONLY, PLAN-ONLY** repo-awareness and routing system. This phase focuses on:

- ✅ Ingesting a canonical repo index (268+ repos)
- ✅ Querying repos with filters
- ✅ Generating dispatch plans (no execution)
- ✅ Planning ZTE header installations (no writes)
- ✅ MCP preflight verification

**Important:** This system does NOT clone, download, mirror, or execute any tasks. It generates plans for human review and future autonomous execution.

---

## Prerequisites

```bash
# Ensure YAML support is available
pip install pyyaml

# Optional: pytest for running tests
pip install pytest
```

---

## Step 1: Verify Installation

```bash
# Test that the repos module imports correctly
cd c:/archonx-os-main
python3 -c "from archonx.repos import RepoRegistry, Router; print('✓ Module imports OK')"
```

---

## Step 2: Ingest the Repo Index

```bash
# Ingest repos from canonical YAML index
archonx repos ingest --file archonx/config/repos.index.yaml --mode index_only
```

**Expected Output:**
```json
{
  "status": "success",
  "repo_count": 18,
  "file_hash": "sha256_hash_here",
  "errors": null,
  "ingested_at": "2026-03-05T12:34:56.789Z",
  "message": "Ingestion complete: 18 repos stored"
}
```

**What happens:**
- YAML file is parsed and validated
- Teams are stored in SQLite
- Repos are stored in SQLite (id, name, url, visibility, kind, team_id, domain_type)
- File hash is recorded for idempotency
- Database: `.archonx/repos.db`

---

## Step 3: List Repos

### List All Repos
```bash
archonx repos list
```

**Output:** JSON array with all repos, total count.

### Filter by Team
```bash
archonx repos list --team pauli_effect
```

**Output:** All repos owned by "pauli_effect" team.

### Filter by Domain Type
```bash
archonx repos list --type saas
```

**Output:** All SAAS repositories.

### Filter by Visibility
```bash
archonx repos list --vis public
```

**Output:** All public repos.

### Filter by Kind
```bash
archonx repos list --kind orig
```

**Output:** All original (non-fork) repos.

### Combine Filters
```bash
archonx repos list --team kupuri_media --type saas --vis private
```

**Output:** SAAS repos from kupuri_media team, private visibility.

---

## Step 4: Show Repo Details

```bash
archonx repos show --id 80
```

**Expected Output:**
```json
{
  "repo": {
    "id": 80,
    "name": "dashboard-agent-swarm",
    "url": "https://github.com/executiveusa/dashboard-agent-swarm",
    "visibility": "private",
    "kind": "orig",
    "team_id": "pauli_effect",
    "domain_type_id": "agent"
  },
  "team": {
    "id": "pauli_effect",
    "display": "The Pauli Effect / BAMBU",
    "owners": ["executiveusa"],
    "regions": ["US", "Global"]
  }
}
```

---

## Step 5: Route Repos for Tasks (Generate Dispatch Plans)

### Single-Repo Routing
```bash
archonx repos route --repo-ids 80 --task full_review
```

**Expected Output:**
```json
{
  "status": "success",
  "dispatch_plan": {
    "timestamp": "2026-03-05T12:34:56.789Z",
    "repo_ids": [80],
    "task_name": "full_review",
    "team_id": "pauli_effect",
    "repos_metadata": [
      {
        "id": 80,
        "name": "dashboard-agent-swarm",
        "url": "...",
        "visibility": "private",
        "kind": "orig",
        "team_id": "pauli_effect",
        "domain_type_id": "agent"
      }
    ],
    "preflight_steps": [
      "archonx mcp connect --profile default",
      "archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
      "archonx tokensaver enable --mode global --persist --compression smart --dedupe prompts --minify context",
      "archonx tokens baseline start --scope session"
    ],
    "recommended_agents": [
      {
        "id": "agent_ops_agent",
        "role": "agent_orchestration",
        "tools": ["mcp", "github_api", "agent_dispatch"]
      },
      {
        "id": "prd_agent",
        "role": "prd_writer",
        "tools": ["repo_intel", "issue_summarizer"]
      },
      {
        "id": "sec_agent",
        "role": "security_review",
        "tools": ["secret_scan", "sast", "dependency_audit"]
      }
    ],
    "token_tracker": {
      "enabled": true,
      "csv_path": "logs/token_savings.csv",
      "baseline_tokens": null,
      "tokensaver_tokens": null,
      "status": "pending"
    },
    "notes": "Task: full_review | Team: The Pauli Effect / BAMBU | Repos: 1 | Domains: agent"
  },
  "artifact_saved": "/path/to/artifacts/dispatch/dispatch_plan_20260305_123456.json"
}
```

**What it means:**
- **preflight_steps:** Commands that MUST run before execution
- **recommended_agents:** Agents suited for this domain type
- **token_tracker:** Placeholder for token optimization metrics
- **artifact_saved:** Plan is saved for review/audit

### Multi-Repo Routing
```bash
archonx repos route --repo-ids 266,267 --task full_review
```

**Output:** Dispatch plan for both repos (domains: unknown) includes recon_agent + prd_agent.

### Multi-Team Routing
```bash
archonx repos route --repo-ids 1,9 --task audit
```

**Output:**
- Repo 1 is pauli_effect + SAAS
- Repo 9 is kupuri_media + AGENT
- Result: team_id = "multi_team", union of all recommended agents

---

## Step 6: Plan ZTE Header Installations (No Execution)

```bash
# Plan headers for specific repos
archonx zte headers plan --repo-ids 1,2,3
```

**Expected Output:**
```json
{
  "status": "success",
  "plan": {
    "status": "plan_only_no_execution",
    "timestamp": "2026-03-05T12:34:56.789Z",
    "repos_count": 3,
    "modifications": [
      {
        "repo_id": 1,
        "repo_name": "-e-commerce-remix",
        "file_to_modify_or_create": "agent.md or AGENTS.md or agents.md",
        "action": "create or update",
        "header_lines": 3,
        "remote_write": false,
        "status": "planned_no_execution"
      },
      ...
    ],
    "universal_header_lines": [
      "archonx mcp connect --profile default && archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
      "archonx zte run --task \"$ARCHON_TASK\" --repo \"$ARCHON_REPO\" --id \"$ARCHON_REPO_ID\" --no-human --autofix --open-pr",
      "archonx tokens report --task \"$ARCHON_TASK\" --repo \"$ARCHON_REPO\" --compare baseline,token_saver --append logs/token_savings.csv"
    ],
    "next_step": "Review plan above. When ready, run: archonx zte headers install --artifact <path>"
  },
  "artifact_saved": "/path/to/artifacts/zte/headers_plan_20260305_123456.json"
}
```

### Plan Headers for All Repos
```bash
archonx zte headers plan --all
```

**Output:** Same structure, but for all 268 repos.

**Important:** No remote writes occur. This is a PLAN only.

---

## Step 7: MCP Preflight Verification

```bash
archonx mcp preflight --require tools:playwright,puppeteer,git,github,vault
```

**Expected Output (Mock Mode):**
```json
{
  "status": "mock_success",
  "message": "Preflight verification (mock mode) — would require actual MCP server",
  "required_tools": ["tools:playwright", "tools:puppeteer", "tools:git", "tools:github", "tools:vault"],
  "verified_tools": ["tools:playwright", "tools:puppeteer", "tools:git", "tools:github", "tools:vault"],
  "next_step": "Run: archonx mcp connect --profile default"
}
```

**Note:** This is currently in mock mode. Production requires an actual MCP server connection.

---

## Step 8: Run Tests

```bash
# Test RepoRegistry
pytest tests/repos/test_registry.py -v

# Test Router
pytest tests/repos/test_router.py -v

# Test all repo modules
pytest tests/repos/ -v
```

**Expected:** All tests pass.

---

## Understanding Agent Routing

The system recommends agents based on **domain type**:

| Domain | Recommended Agents | Rationale |
|--------|-------------------|-----------|
| **SAAS** | design, backend, qa, sec, prd | Full-stack app = all specialties |
| **TOOL** | backend, sec, prd | Dev tools: correctness, security, docs |
| **AGENT** | agent_ops, sec, prd | Autonomous systems: orchestration + security |
| **TEMPLATE** | prd | Templates: documentation |
| **CONTENT** | prd | Content: documentation |
| **UNKNOWN** | recon, prd | Unknown: classify + document |

---

## Database Schema

**Location:** `.archonx/repos.db` (SQLite)

### teams
```sql
CREATE TABLE teams (
  id TEXT PRIMARY KEY,
  display TEXT NOT NULL,
  owners_json TEXT,
  regions_json TEXT,
  created_at TEXT
);
```

### repos
```sql
CREATE TABLE repos (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL UNIQUE,
  visibility TEXT NOT NULL,
  kind TEXT NOT NULL,
  team_id TEXT NOT NULL,
  domain_type_id TEXT NOT NULL,
  created_at TEXT,
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (domain_type_id) REFERENCES domain_types(id)
);
```

### ingest_history
```sql
CREATE TABLE ingest_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ingested_at_utc TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  repo_count INTEGER NOT NULL,
  status TEXT NOT NULL,
  error TEXT,
  created_at TEXT
);
```

---

## Artifacts Generated

All outputs are saved as JSON artifacts for audit and future use:

- **Dispatch Plans:** `artifacts/dispatch/dispatch_plan_<timestamp>.json`
- **ZTE Header Plans:** `artifacts/zte/headers_plan_<timestamp>.json`

---

## Safety Guarantees

### Hard Rules (Enforced)
✅ **INDEX-ONLY:** No cloning, downloading, or mirroring
✅ **MCP-FIRST:** Preflight verification required
✅ **NO SECRETS:** No credentials in output
✅ **SAFE CHANGES:** Additive, backward compatible
✅ **PLANNING:** No execution (except future phases)

### Validation
✅ YAML schema validation
✅ Deterministic file hash (sha256)
✅ Database FK constraints
✅ Idempotent operations

---

## Next Steps (Future Phases)

### Phase 2: Execution
- Implement `archonx repos execute --artifact <path>`
- Run agents from dispatch plans
- Track execution results

### Phase 3: Automation
- Daily cron recon at 03:00 UTC
- Playwright UI audits
- Security scanning + SAST
- Auto-generate PRDs + recommendations

### Phase 4: Integration
- Agent Zero orchestration
- Slack notifications
- Dashboard updates
- PR creation with approval gates

---

## Troubleshooting

### YAML Parse Error
```
ERROR: Invalid YAML: mapping values are not allowed here
```
**Fix:** Check repos.index.yaml syntax (YAML is whitespace-sensitive)

### Repo Not Found
```
ERROR: Repo 999 not found in registry
```
**Fix:** Verify repo ID exists. Run `archonx repos list` to see all.

### Database Locked
```
ERROR: database is locked
```
**Fix:** Close other connections to `.archonx/repos.db`

### Module Import Error
```
ERROR: ModuleNotFoundError: No module named 'yaml'
```
**Fix:** `pip install pyyaml`

---

## Documentation

- **Detailed Docs:** See `docs/repo-awareness.md` and `docs/routing.md`
- **API Docs:** Python docstrings in `archonx/repos/`
- **Schema:** `archonx/config/repos.index.schema.json`
- **Tests:** `tests/repos/test_registry.py`, `tests/repos/test_router.py`

---

## Support

For issues or questions:
1. Check the documentation files
2. Review test cases for examples
3. Inspect the JSON artifacts generated by commands
4. Run tests to verify the system is working correctly

---

**Last Updated:** 2026-03-05
**System Version:** 1.0.0
**Mode:** INDEX-ONLY, PLAN-ONLY
