# RALPHY LOOP - STANDARD OPERATING PROCEDURE (SOP)
## Every Build. Every Repo. Every Time.

**Version:** 1.0
**Effective:** 2026-02-24
**Enforcement:** Mandatory across all connected repositories
**Integration:** Phase 1+ all workflows

---

## What is the Ralphy Loop?

The **Ralphy Loop** is a distributed orchestration framework that ensures:
- ✅ All repos build in parallel
- ✅ Consistent execution across multi-repo systems
- ✅ Automated dependency resolution
- ✅ Unified build reports and telemetry
- ✅ Integration with ARCHONX bead loop

**Default for:** All builds, deployments, and cross-repo changes

---

## Ralphy Loop Workflow

```
┌─────────────────────────────────────────────────────┐
│ INITIATE RALPHY ORCHESTRATION                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 1. REPO DISCOVERY                                   │
│    └─ Scan connected repos (.gitmodules)            │
│    └─ Load repo configs (package.json, pyproject)  │
│    └─ Validate build dependencies                  │
│                                                     │
│ 2. WORK ITEM CREATION                               │
│    └─ Create WorkItem per repo                      │
│    └─ Assign build commands                         │
│    └─ Schedule dependencies                         │
│                                                     │
│ 3. PARALLEL EXECUTION                               │
│    └─ Execute independent repos in parallel        │
│    └─ Respect dependency ordering                  │
│    └─ Stream logs to central collector              │
│                                                     │
│ 4. CONSOLIDATED REPORTING                           │
│    └─ Merge all test/build reports                 │
│    └─ Generate unified coverage report             │
│    └─ Create failure/success matrix                │
│                                                     │
│ 5. GATE DECISION                                    │
│    └─ All pass? → Next phase                       │
│    └─ Any fail? → Rollback + report                │
│    └─ Human approval required                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Installation: Every Repo

### Primary Repo (archonx-os)
```bash
cd /c/archonx-os-main
npm install --save-dev git+https://github.com/michaelshimeles/ralphy.git
```

### Package.json Integration
```json
{
  "devDependencies": {
    "ralphy": "github:michaelshimeles/ralphy"
  },
  "scripts": {
    "build": "ralphy run build",
    "test": "ralphy run test",
    "build:parallel": "ralphy run build --parallel",
    "build:watch": "ralphy run build --watch",
    "build:report": "ralphy report --format json --output ops/reports"
  }
}
```

### All Connected Repos
- `dashboard-agent-swarm` → npm/node project
- `paulisworld-openclaw-3d` → node project (Three.js)
- `agents/devika` → Python agent (pyproject.toml)
- `agents/darya` → Python agent (pyproject.toml)
- `agents/lightning` → Bootstrap framework

---

## Ralphy Configuration (All Repos)

### File: `.ralphy.json` (in each repo root)

```json
{
  "version": "1.0",
  "project": "ARCHONX",
  "repos": [
    {
      "path": ".",
      "name": "archonx-os",
      "type": "node",
      "build_command": "npm run build",
      "test_command": "npm run test",
      "coverage_command": "npm run coverage",
      "lint_command": "npm run lint",
      "timeout_seconds": 300
    },
    {
      "path": "../dashboard-agent-swarm",
      "name": "dashboard-agent-swarm",
      "type": "node",
      "build_command": "npm run build --workspace=dashboard-agent-swarm",
      "test_command": "npm run test --workspace=dashboard-agent-swarm",
      "coverage_command": "npm run coverage --workspace=dashboard-agent-swarm",
      "timeout_seconds": 300
    },
    {
      "path": "../paulisworld-openclaw-3d",
      "name": "paulisworld-openclaw-3d",
      "type": "node",
      "build_command": "npm run build",
      "test_command": "npm run test",
      "timeout_seconds": 300
    }
  ],
  "orchestration": {
    "parallel_limit": 4,
    "fail_fast": false,
    "report_format": "json",
    "report_sink": "ops/reports/ralphy_report.json",
    "retry_on_failure": 1
  },
  "gates": {
    "min_coverage": 80,
    "fail_on_lint": true,
    "fail_on_security": true,
    "require_approval": true
  }
}
```

---

## Usage: How Agents Call Ralphy

### TypeScript/JavaScript Usage
```typescript
// agents/lightning/ralphy_executor.ts
import { Orchestrator, WorkItem } from 'ralphy';

class RalphyBuildExecutor {
  private ralphy: Orchestrator;

  constructor() {
    this.ralphy = new Orchestrator('.ralphy.json');
  }

  async executePhase(phase: number, beads: string[]): Promise<RalphyReport> {
    const workItems: WorkItem[] = beads.map(bead => ({
      bead_id: bead,
      repo: this.determineRepo(bead),
      branch: `feature/${bead}`,
      commands: [
        'npm run lint',
        'npm run build',
        'npm run test -- --coverage',
        `npm run report -- --phase ${phase}`
      ],
      timeout: 300,
      retry: 1
    }));

    // Execute all repos in parallel
    const results = await this.ralphy.executeParallel(workItems);

    // Consolidate reports
    return this.consolidateReports(results);
  }

  async waitForApprovalGate(report: RalphyReport): Promise<boolean> {
    const approved = await this.postToDashboard('/api/approval-gate', {
      report,
      phase: report.phase,
      build_status: report.status,
      coverage: report.coverage,
      test_results: report.test_results
    });
    return approved;
  }
}
```

### Python Usage (agents/devika)
```python
# agents/devika/ralphy_orchestrator.py
from ralphy import Orchestrator, WorkItem

class PythonRalphyBridge:
    def __init__(self, config_path: str = '.ralphy.json'):
        self.ralphy = Orchestrator(config_path)

    def run_phase(self, phase: int, beads: list[str]) -> dict:
        """Execute all beads in a phase."""
        work_items = [
            WorkItem(
                bead_id=bead,
                repo=self._get_repo(bead),
                branch=f"feature/{bead}",
                commands=[
                    "npm run lint",
                    "npm run build",
                    "npm run test --coverage",
                ]
            )
            for bead in beads
        ]

        # Parallel execution
        results = self.ralphy.execute_parallel(work_items)

        # Generate unified report
        report = {
            'phase': phase,
            'beads': beads,
            'results': [r.to_dict() for r in results],
            'consolidated': self._consolidate(results)
        }

        return report
```

---

## Mandatory Build Workflow

### Every Time Code Changes in Any Repo

```bash
# 1. Developer commits to feature branch
git checkout -b feature/BEAD-P1-002

# 2. Make changes
[edit files]

# 3. Run Ralphy locally (before push)
npm run build:parallel
# OR
ralphy run build --parallel

# 4. Check results
# Output: ./ops/reports/ralphy_report.json
# Shows: all repos' build status, coverage %, test results

# 5. If all pass → push to GitHub
git push origin feature/BEAD-P1-002

# 6. GitHub CI runs same Ralphy build (automated)
# 7. PR auto-created if build passes
# 8. Human approves PR
# 9. Merge to main
```

---

## Report Format: Unified Output

After every Ralphy execution, generated report at `ops/reports/ralphy_report.json`:

```json
{
  "timestamp": "2026-02-24T16:45:30Z",
  "phase": 1,
  "execution_id": "exec-P1-001-20260224",
  "repos": {
    "archonx-os": {
      "status": "passed",
      "build_time_seconds": 45,
      "test_results": {
        "passed": 234,
        "failed": 0,
        "skipped": 2
      },
      "coverage": 87.3,
      "lint_status": "passed"
    },
    "dashboard-agent-swarm": {
      "status": "passed",
      "build_time_seconds": 52,
      "test_results": {
        "passed": 156,
        "failed": 0,
        "skipped": 0
      },
      "coverage": 82.1,
      "lint_status": "passed"
    },
    "paulisworld-openclaw-3d": {
      "status": "passed",
      "build_time_seconds": 38,
      "test_results": {
        "passed": 78,
        "failed": 0,
        "skipped": 1
      },
      "coverage": 75.2,
      "lint_status": "passed"
    }
  },
  "consolidated": {
    "overall_status": "passed",
    "total_time_seconds": 52,
    "total_tests": 468,
    "total_failures": 0,
    "average_coverage": 81.5,
    "gate_decisions": {
      "coverage_gate": "passed (81.5% >= 80%)",
      "lint_gate": "passed",
      "test_gate": "passed"
    }
  }
}
```

---

## Gate Decisions: When Build Fails

### Scenario: One Repo Fails Tests

```json
{
  "consolidated": {
    "overall_status": "FAILED",
    "gate_decisions": {
      "test_gate": "FAILED - paulisworld-openclaw-3d: 2 failed tests"
    },
    "failed_repos": [
      {
        "name": "paulisworld-openclaw-3d",
        "failed_tests": [
          "3D world agent meeting initialization",
          "Voice command parsing timeout"
        ]
      }
    ]
  },
  "action": "ROLLBACK",
  "next_steps": [
    "Revert feature branch",
    "Alert agent: paulisworld-openclaw-3d tests failing",
    "Emit rollback report to dashboard",
    "Wait for agent to fix + re-submit"
  ]
}
```

---

## Dashboard Integration

### Real-Time Ralphy Status Display

```
╔════════ RALPHY BUILD STATUS ════════╗
║                                     ║
║ Execution: exec-P1-001-20260224     ║
║ Status: IN PROGRESS                 ║
║ Time Elapsed: 35s / 52s max         ║
║                                     ║
║ [████░░░░░] 67% Complete            ║
║                                     ║
║ Repos:                              ║
║  ✅ archonx-os (45s)                ║
║  🔷 dashboard-agent-swarm (35s)     ║
║  ⏳ paulisworld-openclaw-3d (started) ║
║                                     ║
║ Coverage So Far: 85.1%              ║
║ Tests Passed: 390 / 468             ║
║                                     ║
╚═════════════════════════════════════╝
```

---

## Terminal Output (Live)

```
[RALPHY] Orchestrating Phase 1 Build
[RALPHY] Loading config from .ralphy.json
[RALPHY] Discovered 3 repositories
[RALPHY] Starting parallel execution...

[archonx-os] Building...
[archonx-os] npm run build ✓
[archonx-os] npm run test ✓ (234 passed, 87.3% coverage)

[dashboard-agent-swarm] Building...
[dashboard-agent-swarm] npm run build ✓
[dashboard-agent-swarm] npm run test ✓ (156 passed, 82.1% coverage)

[paulisworld-openclaw-3d] Building...
[paulisworld-openclaw-3d] npm run build ✓
[paulisworld-openclaw-3d] npm run test ✓ (78 passed, 75.2% coverage)

[RALPHY] All repositories passed gates
[RALPHY] Report: ./ops/reports/ralphy_report.json
[RALPHY] Coverage average: 81.5% ✓
[RALPHY] Ready for human approval
```

---

## Failure Handling: Auto-Rollback

If any repo fails build/test:

```bash
#!/usr/bin/env bash
# Auto-triggered by Ralphy on gate failure

# 1. Identify failed repo
FAILED_REPO=$(jq -r '.consolidated.failed_repos[0].name' ops/reports/ralphy_report.json)

# 2. Revert feature branch
git checkout main
git branch -D feature/BEAD-P1-*

# 3. Alert agent
curl -X POST http://localhost:8080/api/agent/alert \
  -d '{
    "agent": "documentation-agent",
    "status": "revert",
    "reason": "'$FAILED_REPO' tests failed",
    "report": "ops/reports/ralphy_report.json"
  }'

# 4. Dashboard notification
echo "ROLLBACK: Phase 1 failed - $FAILED_REPO tests"
echo "Agent re-attempting fixes..."
```

---

## Integrating with Beads Loop

### Every IMPLEMENT Bead Requires Ralphy

```yaml
bead_id: BEAD-P1-002
title: "Normalize documentation"
stage: IMPLEMENT

tasks:
  - apply_doc_patches
  - normalize_headings
  - update_cross_refs

# NEW: Ralphy integration mandatory
ralphy_build_required: true
ralphy_config: .ralphy.json
ralphy_gates:
  - coverage_minimum: 80
  - lint_required: true
  - test_timeout: 300

execution:
  1. Make changes to docs
  2. Run: npm run build:parallel    # ← Ralphy orchestration
  3. Check: ops/reports/ralphy_report.json
  4. If pass: git push → PR created
  5. If fail: Auto-rollback → agent re-attempts

```

---

## Setup Checklist: All Repos

For each connected repo:

- [ ] Clone repo locally
- [ ] `npm install ralphy` (or pin it in deps)
- [ ] Create `.ralphy.json` in repo root (copy template)
- [ ] Update `package.json` scripts section
- [ ] Test locally: `npm run build:parallel`
- [ ] Verify `ops/reports/ralphy_report.json` generates
- [ ] Commit `.ralphy.json` to git
- [ ] Add `.ralphy.json` to GitHub workflow files

---

## GitHub Workflow CI Integration

### File: `.github/workflows/ralphy-build.yml` (all repos)

```yaml
name: Ralphy Orchestrated Build

on:
  pull_request:
    branches: ["main", "develop"]

jobs:
  ralphy-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Ralphy
        run: npm install

      - name: Run Ralphy Orchestration
        run: npm run build:parallel
        timeout-minutes: 10

      - name: Upload Ralphy Report
        uses: actions/upload-artifact@v3
        with:
          name: ralphy-report
          path: ops/reports/ralphy_report.json

      - name: Check Coverage Gate
        run: |
          COVERAGE=$(jq '.consolidated.average_coverage' ops/reports/ralphy_report.json)
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% below 80% threshold"
            exit 1
          fi

      - name: Post Build Status Comment
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('ops/reports/ralphy_report.json', 'utf8')
            );
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Ralphy Build Report

Status: **${report.consolidated.overall_status}**
Tests: ${report.consolidated.total_tests} passed
Coverage: ${report.consolidated.average_coverage}%`
            });
```

---

## Emergency: Manual Override

If Ralphy fails and you need emergency deployment:

```bash
# Override approval gate (requires human signature)
export RALPHY_OVERRIDE=true
export RALPHY_OVERRIDE_REASON="Emergency security patch"
export RALPHY_OVERRIDE_APPROVAL_TICKET="SECURITY-2026-001"

npm run deploy:emergency
# ↑ This still requires human decision, just flags it as emergency
```

---

## Monitoring & Alerts

### Slack Integration (Phase 4)

```
When Ralphy Build Fails:
  → Sends alert to #archonx-alerts
  → Includes: Failed repo, error details, rollback status
  → Mentions: Assigned agent

When Coverage Drops:
  → Sends warning to #archonx-metrics
  → Includes: Previous vs current coverage
  → Recommends: areas to improve
```

---

## SOP Enforcement

**Mandatory across all repos:**

All builds MUST use Ralphy loop by default. No exceptions.

```bash
# ✅ CORRECT: Uses Ralphy
npm run build

# ❌ WRONG: Bypasses Ralphy
npm run build -- --no-ralphy
npm build  # Fails if not defined

# ✅ CORRECT: Ralphy parallel execution
npm run build:parallel

# ❌ WRONG: Individual repo build
cd agents/devika && python build.py
```

---

## Success Criteria

Ralphy loop is working when:

- ✅ All 3+ repos build in parallel
- ✅ Unified coverage report generated
- ✅ All tests pass or fail clearly reported
- ✅ Gate decisions automatic (no manual intervention needed)
- ✅ Any failure triggers automatic rollback
- ✅ Human approves consolidated result, not individual repos
- ✅ Report visible in dashboard in real-time
- ✅ Slack/email notifications working

---

**END OF RALPHY SOP**

This SOP is now mandatory for all Phase 1+ work. Every agent must follow these procedures. Every build must use Ralphy orchestration.

Next: Initializing Phase 1 bead execution...
