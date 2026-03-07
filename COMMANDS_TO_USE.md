# ArchonX Repository Awareness — Commands to Use

## Quick Reference

All commands run from `c:/archonx-os-main/`

### Setup

```bash
# Install dependencies (if not already installed)
pip install pyyaml pytest

# Verify module imports
python3 -c "from archonx.repos import RepoRegistry, Router; print('✓ Ready')"
```

---

## Ingest Repos Index

```bash
# Ingest the canonical YAML repository index
archonx repos ingest --file archonx/config/repos.index.yaml --mode index_only

# Output: JSON with status, repo_count, file_hash
# Stores metadata in: .archonx/repos.db (SQLite)
```

---

## List & Query Repos

```bash
# List all repos
archonx repos list

# Filter by team (pauli_effect, kupuri_media, max_digital_media, etc.)
archonx repos list --team pauli_effect

# Filter by domain type (saas, tool, agent, template, content, unknown)
archonx repos list --type saas

# Filter by visibility (public, private)
archonx repos list --vis public

# Filter by kind (orig, fork)
archonx repos list --kind orig

# Combine filters
archonx repos list --team kupuri_media --type saas --vis private
```

---

## Show Repo Details

```bash
# Show details of repo ID 80 (dashboard-agent-swarm)
archonx repos show --id 80

# Output: Repo metadata + team information
```

---

## Route Repos to Agents (Generate Dispatch Plans)

```bash
# Route single repo for full review
archonx repos route --repo-ids 80 --task full_review

# Route multiple repos
archonx repos route --repo-ids 1,2,3 --task security_audit

# Route multi-team repos
archonx repos route --repo-ids 266,267 --task full_review

# Custom task name
archonx repos route --repo-ids 1 --task custom_task_name

# Output: DispatchPlan JSON (saved to artifacts/dispatch/dispatch_plan_<timestamp>.json)
```

**Dispatch Plan includes:**
- Recommended agents (based on domain type)
- Preflight steps (MCP verify, token saver, etc.)
- Repo metadata
- Token tracker placeholder
- Notes

---

## Plan ZTE Header Installations (No Execution)

```bash
# Plan headers for specific repos (NO REMOTE WRITES)
archonx zte headers plan --repo-ids 1,2,3

# Plan headers for all repos
archonx zte headers plan --all

# Output: Plan JSON (saved to artifacts/zte/headers_plan_<timestamp>.json)
# Status: "plan_only_no_execution" — shows what WOULD be done, but doesn't do it
```

---

## MCP Preflight Verification

```bash
# Verify MCP tools are available
archonx mcp preflight --require tools:playwright,puppeteer,git,github,vault

# Output: Preflight check status (currently mock mode)
# Note: Production requires actual MCP server connection
```

---

## Run Tests

```bash
# Test RepoRegistry (ingestion, querying, database operations)
pytest tests/repos/test_registry.py -v

# Test Router (agent routing, dispatch plans)
pytest tests/repos/test_router.py -v

# Test all repo modules
pytest tests/repos/ -v

# Show coverage
pytest tests/repos/ --cov=archonx.repos
```

---

## View Artifacts Generated

```bash
# List dispatch plans
ls -la artifacts/dispatch/

# List ZTE plans
ls -la artifacts/zte/

# View a dispatch plan
cat artifacts/dispatch/dispatch_plan_<timestamp>.json | jq '.'

# View a ZTE plan
cat artifacts/zte/headers_plan_<timestamp>.json | jq '.'
```

---

## Check Database State

```bash
# Query SQLite database directly
sqlite3 .archonx/repos.db

# Inside sqlite3 prompt:
sqlite> SELECT COUNT(*) FROM repos;
sqlite> SELECT COUNT(*) FROM teams;
sqlite> SELECT * FROM ingest_history ORDER BY created_at DESC LIMIT 1;
sqlite> .quit
```

---

## Useful Combinations

### Full Audit of One Team
```bash
# See what repos pauli_effect owns
archonx repos list --team pauli_effect

# Route all team repos for full review
archonx repos route --repo-ids 1,4,5,6 --task full_review
```

### Classify Unknown Domains
```bash
# Find all unknown repos
archonx repos list --type unknown

# Route for classification (triggers recon_agent + prd_agent)
archonx repos route --repo-ids 266,267 --task full_review
```

### Security Audit
```bash
# Find all public SaaS repos (highest risk)
archonx repos list --type saas --vis public

# Route for security audit
archonx repos route --repo-ids <ids> --task security_audit
```

### Review All Tools
```bash
# Find all tool repos
archonx repos list --type tool

# Route for code review
archonx repos route --repo-ids <ids> --task code_review
```

---

## Environment Variables

```bash
# Optional: Set custom database location
export ARCHONX_REPOS_DB=/path/to/custom/repos.db

# Optional: Set custom artifacts directory
export ARCHONX_ARTIFACTS_DIR=./custom_artifacts/
```

---

## Expected Output Examples

### repos ingest
```json
{
  "status": "success",
  "repo_count": 18,
  "file_hash": "sha256hash...",
  "errors": null,
  "ingested_at": "2026-03-05T12:34:56.789Z",
  "message": "Ingestion complete: 18 repos stored"
}
```

### repos list --team pauli_effect
```json
{
  "total": 15,
  "filters": {
    "team": "pauli_effect",
    "type": null,
    "visibility": null,
    "kind": null
  },
  "repos": [
    {
      "id": 1,
      "name": "-e-commerce-remix",
      "url": "https://github.com/executiveusa/-e-commerce-remix",
      "visibility": "public",
      "kind": "fork",
      "team_id": "pauli_effect",
      "domain_type_id": "tool"
    },
    ...
  ]
}
```

### repos route --repo-ids 266,267 --task full_review
```json
{
  "status": "success",
  "dispatch_plan": {
    "timestamp": "2026-03-05T12:34:56.789Z",
    "repo_ids": [266, 267],
    "task_name": "full_review",
    "team_id": "multi_team",
    "preflight_steps": [
      "archonx mcp connect --profile default",
      "archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
      "archonx tokensaver enable --mode global --persist ...",
      "archonx tokens baseline start --scope session"
    ],
    "recommended_agents": [
      {
        "id": "recon_agent",
        "role": "classification_and_recon",
        "tools": ["playwright", "puppeteer", "repo_intel", "classifier"]
      },
      {
        "id": "prd_agent",
        "role": "prd_writer",
        "tools": ["repo_intel", "issue_summarizer"]
      }
    ],
    "token_tracker": {
      "enabled": true,
      "csv_path": "logs/token_savings.csv",
      "baseline_tokens": null,
      "tokensaver_tokens": null,
      "status": "pending"
    },
    "notes": "Task: full_review | Team: multi_team (triage_unknown) | Repos: 2 | Domains: unknown"
  },
  "artifact_saved": "artifacts/dispatch/dispatch_plan_20260305_123456.json"
}
```

### zte headers plan --repo-ids 1,2,3
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
  "artifact_saved": "artifacts/zte/headers_plan_20260305_123456.json"
}
```

---

## Documentation References

| Topic | File |
|-------|------|
| Complete system guide | `docs/repo-awareness.md` |
| Routing architecture | `docs/routing.md` |
| Quick start (step-by-step) | `REPO_AWARENESS_QUICKSTART.md` |
| Implementation summary | `IMPLEMENTATION_SUMMARY.md` |
| This reference | `COMMANDS_TO_USE.md` |

---

## Key Points

🔒 **INDEX-ONLY:** No cloning, downloading, or mirroring repos
🤖 **DETERMINISTIC:** Same input → same output (except timestamps)
📋 **PLAN-ONLY:** Generates dispatch plans without execution (Phase 2+)
✅ **MCP-FIRST:** Preflight verification required before operations
📊 **ARTIFACT-BASED:** All outputs saved for audit and review

---

**Last Updated:** 2026-03-05
**Status:** ✅ COMPLETE
**Mode:** INDEX-ONLY, PLAN-ONLY, MCP-FIRST
