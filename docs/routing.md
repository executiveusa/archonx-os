# Agent Routing Architecture

## Overview

The Routing Engine is the "nervous system" of ArchonX, mapping repositories and tasks to appropriate agent teams. It operates on dispatch plans—deterministic, reproducible JSON specifications that define exactly which agents should handle which work.

## Routing Philosophy

### Plan-Then-Execute
```
Input (repos + task)
  ↓
Router.route() → DispatchPlan (JSON)
  ↓
Review/Approval (optional)
  ↓
Execute against plan (future phase)
```

### Domain-Driven Agent Selection

Agents are recommended based on **domain type**, not ad-hoc assignment:

| Domain Type | Recommended Agents | Rationale |
|------------|-------------------|-----------|
| **SAAS** | design, backend, qa, sec, prd | Full-stack app requires all specialties |
| **TOOL** | backend, sec, prd | Dev tools focus on correctness, security, docs |
| **AGENT** | agent_ops, sec, prd | Autonomous systems need orchestration + security |
| **TEMPLATE** | prd | Templates are documentation/examples |
| **CONTENT** | prd | Content repos need clear documentation |
| **UNKNOWN** | recon, prd | Unknown type triggers classification + documentation |

## DispatchPlan Structure

```json
{
  "timestamp": "2026-03-05T12:34:56Z",
  "repo_ids": [266, 267],
  "task_name": "full_review",
  "team_id": "pauli_effect",
  "repos_metadata": [
    {
      "id": 266,
      "name": "placeholder-repo-266",
      "url": "https://github.com/executiveusa/placeholder-repo-266",
      "visibility": "public",
      "kind": "orig",
      "team_id": "pauli_effect",
      "domain_type_id": "unknown"
    }
  ],
  "preflight_steps": [
    "archonx mcp connect --profile default",
    "archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
    "archonx tokensaver enable --mode global --persist ...",
    "archonx tokens baseline start --scope session"
  ],
  "recommended_agents": [
    {
      "id": "prd_agent",
      "role": "prd_writer",
      "tools": ["repo_intel", "issue_summarizer"]
    },
    {
      "id": "recon_agent",
      "role": "classification_and_recon",
      "tools": ["playwright", "puppeteer", "repo_intel", "classifier"]
    }
  ],
  "token_tracker": {
    "enabled": true,
    "csv_path": "logs/token_savings.csv",
    "baseline_tokens": null,
    "tokensaver_tokens": null,
    "status": "pending"
  },
  "notes": "Task: full_review | Team: The Pauli Effect / BAMBU | Repos: 2 | Domains: unknown"
}
```

## Agent Profiles

Each recommended agent includes:
- **id:** Unique agent identifier (e.g., design_agent, prd_agent)
- **role:** Functional role (e.g., frontend_audit, prd_writer)
- **tools:** List of tools available to the agent

### Available Agent Profiles

#### design_agent
- **Role:** frontend_audit
- **Tools:** playwright, puppeteer, lighthouse, a11y
- **Domains:** SAAS

#### backend_agent
- **Role:** backend_audit
- **Tools:** sast, dependency_audit, api_contract, migration_check
- **Domains:** SAAS, TOOL

#### qa_agent
- **Role:** e2e_validation
- **Tools:** playwright, test_runner
- **Domains:** SAAS

#### sec_agent
- **Role:** security_review
- **Tools:** secret_scan, sast, dependency_audit
- **Domains:** SAAS, TOOL, AGENT

#### prd_agent
- **Role:** prd_writer
- **Tools:** repo_intel, issue_summarizer
- **Domains:** SAAS, TOOL, AGENT, TEMPLATE, CONTENT, UNKNOWN

#### agent_ops_agent
- **Role:** agent_orchestration
- **Tools:** mcp, github_api, agent_dispatch
- **Domains:** AGENT

#### recon_agent
- **Role:** classification_and_recon
- **Tools:** playwright, puppeteer, repo_intel, classifier
- **Domains:** UNKNOWN

## Routing API

### Core Method

```python
from archonx.repos import Router, RepoRegistry

registry = RepoRegistry()
router = Router(registry)

# Generate dispatch plan
plan = router.route(
    repo_ids=[266, 267],
    task_name="full_review"
)

# Plan is deterministic and reproducible
dispatch_json = plan.to_dict()
```

### Properties

- **Deterministic:** Same input → same output (except timestamps)
- **Reproducible:** Can be re-generated from repo IDs + task name
- **Stateless:** Router doesn't modify registry or any external state
- **Versioned:** Includes timestamp for traceability

## Preflight Gate

All dispatch plans include preflight steps that MUST execute before task execution:

```bash
# Step 1: Connect to MCP
archonx mcp connect --profile default

# Step 2: Verify required tools
archonx mcp verify --require tools:playwright,puppeteer,git,github,vault

# Step 3: Enable token optimization
archonx tokensaver enable \
  --mode global \
  --persist \
  --compression smart \
  --dedupe prompts \
  --minify context

# Step 4: Start token tracking
archonx tokens baseline start --scope session
```

**Non-negotiable:** No code execution or git operations proceed without all preflight steps passing.

## Multi-Team Routing

When a dispatch plan spans multiple teams:
- **team_id:** Set to "multi_team"
- **notes:** List all team IDs (e.g., "Teams: pauli_effect, kupuri_media")
- **Agents:** Union of all team-specific agents

Example:
```json
{
  "team_id": "multi_team",
  "notes": "Task: audit | Team: multi_team (agent_ops, pauli_effect) | Repos: 2 | Domains: agent, tool",
  "recommended_agents": [
    {"id": "agent_ops_agent", ...},
    {"id": "sec_agent", ...},
    {"id": "prd_agent", ...},
    {"id": "backend_agent", ...}
  ]
}
```

## Token Tracking Integration

Each dispatch plan includes a placeholder for token tracking:

```json
"token_tracker": {
  "enabled": true,
  "csv_path": "logs/token_savings.csv",
  "baseline_tokens": null,
  "tokensaver_tokens": null,
  "status": "pending"
}
```

After task execution:
- **baseline_tokens:** Original prompt size (before optimization)
- **tokensaver_tokens:** Optimized prompt size (after CodeMunch)
- **status:** "success" or "error"
- **percent_saved:** (baseline - optimized) / baseline * 100

## Example Workflows

### Single-Repo Security Audit

```bash
# Route repo 80 (dashboard-agent-swarm) for security audit
archonx repos route --repo-ids 80 --task security_audit

# Output: DispatchPlan with sec_agent, prd_agent
```

### Multi-Repo Full Review

```bash
# Route repos 1,2,3 for comprehensive review
archonx repos route --repo-ids 1,2,3 --task full_review

# Output: DispatchPlan with design, backend, qa, sec, prd agents
```

### Unknown Domain Classification

```bash
# Route unknown repos for classification
archonx repos route --repo-ids 266,267 --task full_review

# Output: DispatchPlan with recon_agent, prd_agent (+ classification_required flag)
```

## Future Enhancements

### Custom Agent Routing Rules
- Domain-specific preferences (e.g., "always include DevOps agent for infrastructure repos")
- Team-based agent overrides
- Task-specific agent customization

### Cron-Based Dispatch
- Daily audits via scheduled dispatch plans
- Automated classification of unknown domains
- Periodic security sweeps

### Approval Workflows
- Plan generation → Review queue
- Approval gates before execution
- Audit trails for all dispatched work

---

## Implementation Notes

### Idempotency
Routing is fully idempotent:
```python
plan_a = router.route([1,2,3], "audit")
plan_b = router.route([1,2,3], "audit")

# plan_a.to_dict() == plan_b.to_dict() (except timestamps)
```

### Testability
All routing logic is pure functions with no side effects:
```python
# Easy to unit test
assert len(router._recommend_agents({"saas"})) == 5  # All 5 agents
assert len(router._recommend_agents({"unknown"})) == 2  # recon + prd
```

### Performance
Router is O(n) where n = number of repos requested:
- Fetch repo metadata: O(n)
- Determine domain types: O(n)
- Recommend agents: O(domain_types) ≈ O(1)
- Build dispatch plan: O(n)

Suitable for large-scale routing (100+ repos in <1s).
