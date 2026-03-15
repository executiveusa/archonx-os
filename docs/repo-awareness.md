# Repository Awareness System

## Overview

The Repository Awareness System is a core component of ArchonX that maintains an index of 268+ repositories across the Guardian Fleet without cloning or mirroring them. It serves as the "consciousness" of the system, enabling intelligent agent routing, audit scheduling, and operational awareness.

## Key Principles

### INDEX-ONLY
- **Never clone, download, or mirror** any repository
- Maintain metadata-only in SQLite registry
- All operations route through GitHub API for live data when needed

### MCP-FIRST
- Require MCP (Multi-Context Protocol) handshake before any operational tasks
- Preflight verification is non-negotiable for code execution or git operations
- All operations must pass security gates

### PLANNING-ONLY (This Phase)
- Generate dispatch plans without executing tasks
- Separate "plan" from "execute" phases
- Enable review and approval workflows

## Architecture

### Core Components

#### RepoRegistry (SQLite)
- **Location:** `c:/archonx-os-main/archonx/repos/registry.py`
- **Database:** `c:/archonx-os-main/.archonx/repos.db`
- **Tables:**
  - `teams`: Team metadata (id, display, owners, regions)
  - `domain_types`: Domain classification (saas, tool, agent, template, content, unknown)
  - `repos`: Repository metadata (id, name, url, visibility, kind, team_id, domain_type_id)
  - `ingest_history`: Ingest tracking (file_hash, repo_count, status, error)

#### Router
- **Location:** `c:/archonx-os-main/archonx/repos/router.py`
- **Function:** Maps repos + tasks to agent dispatch plans
- **Output:** `DispatchPlan` JSON with preflight steps, recommended agents, metadata

#### Models
- **Location:** `c:/archonx-os-main/archonx/repos/models.py`
- **Classes:** Team, Repo, DomainType, DispatchPlan, IngestHistory

### Index File

**Source:** `c:/archonx-os-main/archonx/config/repos.index.yaml`

Schema:
```yaml
archonx_repo_index_spec:
  version: "1.0.0"
  mode: "index_only"
  do_not_clone: true
  do_not_vendor: true
  do_not_mirror: true

  teams:
    - id: team_id
      display: "Team Name"
      owners: [user1, user2]
      regions: [region1, region2]

  domain_types:
    - id: saas | tool | agent | template | content | unknown
      description: "Description"

  repos:
    - id: 1
      name: "repo-name"
      url: "https://github.com/owner/repo"
      vis: public | private
      kind: orig | fork
      team_id: "team_id"
      domain_type_id: "domain_type"
```

## CLI Commands

### Ingestion

```bash
archonx repos ingest --file archonx/config/repos.index.yaml --mode index_only
```

**Output:** JSON with ingest results, repo_count, file_hash, errors.

### List Repositories

```bash
# List all repos
archonx repos list

# Filter by team
archonx repos list --team pauli_effect

# Filter by domain type
archonx repos list --type saas

# Filter by visibility
archonx repos list --vis public

# Filter by kind
archonx repos list --kind orig

# Combine filters
archonx repos list --team kupuri_media --type saas --vis private
```

**Output:** JSON array of repos with metadata.

### Show Repo Details

```bash
archonx repos show --id 80
```

**Output:** JSON with repo metadata and team information.

### Route Repos to Agents

```bash
archonx repos route --repo-ids 1,2,3 --task "full_review"
archonx repos route --repo-ids 266,267 --task "security_audit"
```

**Output:** JSON dispatch plan saved to `artifacts/dispatch/dispatch_plan_<timestamp>.json`

Dispatch Plan includes:
- Preflight steps (MCP verification, token saver activation)
- Recommended agents based on domain type
- Repo metadata
- Token tracking placeholder
- Notes

## Agent Routing Logic

Based on domain type, the router recommends:

- **SAAS:** design_agent, backend_agent, qa_agent, sec_agent, prd_agent
- **TOOL:** backend_agent, sec_agent, prd_agent
- **AGENT:** agent_ops_agent, sec_agent, prd_agent
- **TEMPLATE/CONTENT:** prd_agent
- **UNKNOWN:** recon_agent, prd_agent (+ classification_required flag)

## Zero-Touch Engineer (ZTE) Headers

### Plan Header Installations

```bash
# Plan for specific repos
archonx zte headers plan --repo-ids 1,2,3

# Plan for all repos
archonx zte headers plan --all
```

**Output:** JSON plan saved to `artifacts/zte/headers_plan_<timestamp>.json`

Plan includes:
- List of repos to modify
- Files to create/edit (agent.md, AGENTS.md, agents.md)
- Universal header commands (MCP + ZTE run + token tracking)
- Status: "plan_only_no_execution"

**Note:** This task does NOT write to remote repos. It only generates a plan for review.

## Token Savings Tracking

### Foundation Setup

The system includes a placeholder for token tracking:

```python
from archonx.repos.registry import RepoRegistry
from archonx.repos.models import TokenTracker

tracker = TokenTracker()
tracker.start(task="full_review", repo_id=80)
# ... perform work ...
tracker.finish(status="success", baseline_tokens=5000, tokensaver_tokens=3500)
```

### CSV Format

**File:** `logs/token_savings.csv`

```
repo_id,repo_name,task,baseline_tokens,tokensaver_tokens,tokens_saved,percent_saved,started_utc,ended_utc,status
80,dashboard-agent-swarm,full_review,5000,3500,1500,30%,2026-03-05T10:00:00Z,2026-03-05T10:15:00Z,success
```

## MCP Preflight Gate

```bash
archonx mcp preflight --require tools:playwright,puppeteer,git,github,vault
```

**Required before:**
- Code execution
- Git operations
- PR creation/updates
- Any GitHub API calls

## Testing

Unit tests are located in `tests/repos/`:

```bash
pytest tests/repos/test_registry.py
pytest tests/repos/test_router.py
pytest tests/repos/test_yaml_schema.py
```

## Safety & Constraints

### Hard Rules
1. **DO NOT clone repos** — ever. Index-only mode enforced.
2. **MCP-FIRST** — all operations require preflight verification
3. **NO SECRETS IN OUTPUT** — all secrets routed through vault agent
4. **SAFE CHANGES** — additive, backward compatible only

### Validation
- YAML schema validation (strict)
- Deterministic file hash (sha256) for ingest tracking
- Database schema with foreign key constraints
- Idempotent upsert operations

## Integration with Other Systems

### GraphBrain
- Receives dispatch plans from Router
- Executes planned work orders
- Reports results back to ArchonX

### Agent Zero
- Consumes dispatch plans
- Routes work to specialist crews
- Tracks execution metrics

### Token Saver (CodeMunch)
- Receives baseline + optimized token counts
- Appends to `logs/token_savings.csv`
- Calculates percent savings

## Future Enhancements (Phase 2)

1. **Daily Cron Recon:** Automated UI/backend audits at 03:00 UTC
2. **Playwright Audits:** E2E testing + UI validation
3. **Security Scanning:** Secret detection, SAST, dependency audit
4. **PRD Generation:** Automated problem statement + recommended improvements
5. **PR Creation:** Auto-open PRs with fixes (subject to approval policy)

---

## Quick Start

1. **Ingest the index:**
   ```bash
   archonx repos ingest --file archonx/config/repos.index.yaml --mode index_only
   ```

2. **List repos by team:**
   ```bash
   archonx repos list --team pauli_effect | jq '.repos | length'
   ```

3. **Route repos for review:**
   ```bash
   archonx repos route --repo-ids 266,267 --task full_review
   ```

4. **Plan ZTE headers (no execution):**
   ```bash
   archonx zte headers plan --repo-ids 1,2,3
   ```
