# ARCHONX End-to-End Execution PRD
## Production-Ready Implementation with Beads Loop + Ralphy + Human Governance Gates

**Version:** 1.0
**Date:** 2026-02-24
**Orchestration:** Beads + Ralphy + PAULIWHEEL
**Execution Model:** Agent-driven with human approval gates at phase boundaries
**Target State:** Full autonomous agency orchestration with human control dashboard

---

## Executive Summary

This PRD operationalizes the ARCHONX architecture into an executable, production-ready implementation sequence. It combines:

- **Beads Loop** (PLAN → IMPLEMENT → TEST → EVALUATE → PATCH → REPEAT) for deterministic execution
- **Ralphy** multi-repo orchestration for parallel agent coordination
- **Human Approval Gates** at phase boundaries (not removed, automated through)
- **Build/Test Checkpoints** mandatory at each phase
- **Dashboard Control** for real-time monitoring and decision-making
- **Master.env Integration** for credential/config management
- **Subagent Deployment** (agents build → merge to main via automated PR + human-approval-gated merge)

---

## Implementation Phases

### Phase Structure

Each phase follows this pattern:

```
[Phase Gate / Approval]
  ↓
[PLAN Bead] → [IMPLEMENT Bead] → [TEST Bead] → [EVALUATE Bead]
  ↓
[Build Checkpoint]
  ↓
[Automated PR to Main]
  ↓
[Human Approval Required]
  ↓
[Merge to Main]
  ↓
[Telemetry + Report Emission]
  ↓
[Next Phase Gate]
```

---

## PHASE 0: Baseline Audit & Readiness

**Owner:** Audit Agent
**Duration:** Async continuous
**Approval Gate:** Baseline report review

### Bead: PLAN_BASELINE
```yaml
bead_id: BEAD-P0-001
title: "Plan baseline audit"
stage: PLAN
tasks:
  - inventory_plans_artifacts
  - map_repository_cross_references
  - identify_conformance_gaps
  - generate_baseline_report
output: ops/reports/baseline_audit.json
```

### Bead: IMPLEMENT_BASELINE
```yaml
bead_id: BEAD-P0-002
title: "Implement baseline tooling"
stage: IMPLEMENT
tasks:
  - create_audit_scripts
  - integrate_with_ops_doctor
  - bootstrap_reporting_pipeline
output:
  - scripts/audit/archonx-audit.py
  - archonx/tools/baseline_reporter.py
```

### Bead: TEST_BASELINE
```yaml
bead_id: BEAD-P0-003
title: "Test baseline audit"
stage: TEST
tasks:
  - run_audit_on_archonx_os
  - verify_report_json_schema
  - confirm_all_repos_listed
  - check_cross_reference_completeness
success_criteria:
  - report_generated: true
  - all_plans_inventoried: true
  - zero_unresolved_refs: true
```

### Build Checkpoint P0
```bash
# Automated checks
npm run lint --workspace=archonx
python -m pytest archonx/tools/test_baseline_reporter.py -v
python scripts/audit/archonx-audit.py --verify-schema
```

### Phase 0 Deliverables
- ✅ `ops/reports/baseline_audit.json` (machine-readable inventory)
- ✅ `ops/reports/P0_CONFORMANCE_REPORT.md` (human summary)
- ✅ `PHASE_0_GATE_APPROVAL.md` (human sign-off template)

### Human Approval Gate: Phase 0 → Phase 1
**Required Sign-off:**
```
[ ] All plans artifacts inventoried
[ ] Repository cross-references verified
[ ] Baseline report accurate
[ ] Zero unresolved referential gaps
Approver: _______________  Date: _______________
```

---

## PHASE 1: Documentation Normalization

**Owner:** Documentation Agent
**Depends On:** Phase 0 Gate Approval
**Duration:** Parallel implementation per workstream
**Approval Gate:** Conformance report + schema validation

### Bead: PLAN_DOC_NORMALIZATION
```yaml
bead_id: BEAD-P1-001
title: "Plan documentation normalization"
stage: PLAN
tasks:
  - read_spec_driven_doc_prd
  - map_conformance_failures
  - generate_patch_list
  - identify_blocking_issues
output: ops/reports/P1_normalization_plan.json
```

### Bead: IMPLEMENT_DOC_NORMALIZATION
```yaml
bead_id: BEAD-P1-002
title: "Normalize documentation"
stage: IMPLEMENT
tasks:
  - apply_section_spec_patches
  - resolve_terminology_inconsistencies
  - standardize_heading_levels
  - update_cross_references
  - validate_internal_links
patched_files:
  - plans/*.md
  - docs/*.md
  - agents/*/system_prompt.md
output_pr_branch: feature/P1-doc-normalization
```

### Bead: TEST_DOC_NORMALIZATION
```yaml
bead_id: BEAD-P1-003
title: "Test normalized documentation"
stage: TEST
tasks:
  - validate_markdown_schema
  - check_section_ordering
  - verify_internal_links
  - confirm_terminology_consistency
  - run_spell_check
success_criteria:
  - all_files_conform_to_spec: true
  - no_broken_links: true
  - terminology_consistency_score: "99%"
```

### Build Checkpoint P1
```bash
# Markdown validation
npm run lint:markdown plans/ docs/
# Link validation
python scripts/validate/check_links.py
# Schema validation
python scripts/validate/check_doc_schema.py ops/reports/P0_CONFORMANCE_REPORT.md
```

### Bead: PATCH_DOC_NORMALIZATION
```yaml
bead_id: BEAD-P1-004
title: "Patch and iterate on documentation"
stage: PATCH
tasks:
  - review_test_failures
  - apply_fixes
  - re-run_tests
  - emit_final_conformance_report
```

### Phase 1 Deliverables
- ✅ `plans/` directory fully normalized
- ✅ `docs/` directory fully normalized
- ✅ `ops/reports/P1_CONFORMANCE_REPORT.md`
- ✅ PR `feature/P1-doc-normalization` ready for merge

### Human Approval Gate: Phase 1 → Phase 2
```
[ ] All documentation normalized
[ ] Conformance report green
[ ] Schema validation passed
[ ] Internal links verified
[ ] Terminology consistent
Approver: _______________  Date: _______________
```

---

## PHASE 2: Governance & Contract Hardening

**Owner:** Governance Agent + Devika PI Agent
**Depends On:** Phase 1 Gate Approval
**Duration:** 2-3 parallel workstreams
**Approval Gate:** Contract completeness + policy testing

### Parallel Workstream 2A: DEVIKA-PI Integration

#### Bead: PLAN_DEVIKA_PI_WS2
```yaml
bead_id: BEAD-P2-WS2A-001
title: "Plan Devika-PI integration and governance wrapper"
stage: PLAN
tasks:
  - read_devika_pi_integration_plan
  - map_gap_matrix
  - sequence_implementation
  - generate_task_packets
output: ops/reports/P2_devika_pi_plan.json
dependencies:
  - BEAD-P1-004  # Doc normalization patched
```

#### Bead: IMPLEMENT_DEVIKA_PI_GOVERNANCE
```yaml
bead_id: BEAD-P2-WS2A-002
title: "Implement Devika-PI governance wrapper + policy"
stage: IMPLEMENT
tasks:
  - create_archonx/security/devika_pi_policy.py
  - create_archonx/tools/devika_pi_wrapper.py
  - create_agents/devika/config.json
  - create_agents/devika/system_prompt.md
  - create_agents/devika/extensions/*.py
  - wire_context7_mcp
  - integrate_pauliwheel_gate
new_files:
  - archonx/security/devika_pi_policy.py
  - archonx/tools/devika_pi_wrapper.py
  - agents/devika/config.json
  - agents/devika/system_prompt.md
  - agents/devika/extensions/task_loop.py
  - agents/devika/extensions/safe_commands.py
  - agents/devika/extensions/subagents.py
  - agents/devika/registry.json
output_pr_branch: feature/P2-devika-pi-governance
```

#### Bead: TEST_DEVIKA_PI
```yaml
bead_id: BEAD-P2-WS2A-003
title: "Test Devika-PI governance wrapper"
stage: TEST
tasks:
  - verify_policy_blocks_unsafe_commands
  - test_context7_mcp_resolution
  - verify_bead_id_requirement
  - test_loop_stage_enforcement
  - verify_report_emission
  - test_fallback_modes
success_criteria:
  - unsafe_commands_blocked: true
  - context7_integration_working: true
  - pauliwheel_gates_enforced: true
  - reports_emitted_correctly: true
```

#### Build Checkpoint P2-WS2A
```bash
# Python tests
python -m pytest archonx/tools/test_devika_pi_wrapper.py -v
python -m pytest archonx/security/test_devika_pi_policy.py -v
# Integration test
python scripts/test/devika_pi_integration_test.py
# Config validation
python scripts/validate/validate_devika_config.py agents/devika/config.json
```

### Parallel Workstream 2B: Workflow Contracts

#### Bead: PLAN_WORKFLOW_CONTRACTS
```yaml
bead_id: BEAD-P2-WS2B-001
title: "Plan workflow contract specifications"
stage: PLAN
tasks:
  - read_dashboard_control_workflows
  - map_all_agent_workflows
  - define_contract_schema
  - generate_contract_templates
output: ops/reports/P2_workflow_contracts_plan.json
```

#### Bead: IMPLEMENT_WORKFLOW_CONTRACTS
```yaml
bead_id: BEAD-P2-WS2B-002
title: "Implement workflow contracts"
stage: IMPLEMENT
tasks:
  - create_archonx/contracts/*.json (all workflows)
  - document_trigger_conditions
  - define_payload_schemas
  - map_policy_gates
  - define_telemetry_events
  - specify_evidence_paths
new_files:
  - archonx/contracts/workflow_*.json
  - docs/contracts/WORKFLOW_REFERENCE.md
output_pr_branch: feature/P2-workflow-contracts
```

#### Bead: TEST_WORKFLOW_CONTRACTS
```yaml
bead_id: BEAD-P2-WS2B-003
title: "Test workflow contracts"
stage: TEST
tasks:
  - validate_contract_json_schema
  - verify_all_workflows_documented
  - test_contract_parsing
  - verify_policy_gate_mappings
success_criteria:
  - all_contracts_valid_json: true
  - zero_missing_workflows: true
  - policy_mappings_complete: true
```

#### Build Checkpoint P2-WS2B
```bash
# Schema validation
python scripts/validate/validate_contracts.py archonx/contracts/
# Coverage check
python scripts/validate/check_contract_coverage.py
```

### Phase 2 Deliverables
- ✅ `agents/devika/` fully configured with governance wrapper
- ✅ `archonx/security/devika_pi_policy.py` enforcing safe commands
- ✅ `archonx/contracts/` all workflows documented
- ✅ `ops/reports/P2_GOVERNANCE_REPORT.md`
- ✅ PR `feature/P2-devika-pi-governance` ready for merge
- ✅ PR `feature/P2-workflow-contracts` ready for merge

### Human Approval Gate: Phase 2 → Phase 3
```
[ ] Devika-PI governance wrapper tested
[ ] Policy enforcement verified
[ ] Workflow contracts complete
[ ] Context7 MCP integrated
[ ] All tests passing
[ ] Reports emitted
Approver: _______________  Date: _______________
```

---

## PHASE 3: Control Plane & Dashboard Wiring

**Owner:** Dashboard Orchestration Agent
**Depends On:** Phase 2 Gate Approval
**Duration:** Frontend + Backend parallel workstreams
**Approval Gate:** Dashboard smoke tests + control flow verification

### Workstream 3A: Dashboard Frontend Control

#### Bead: IMPLEMENT_DASHBOARD_CONTROLS
```yaml
bead_id: BEAD-P3-WS3A-001
title: "Implement dashboard control UI"
stage: IMPLEMENT
tasks:
  - create_ExecutionControl component (React)
  - create_PhaseGateApproval component
  - create_RepoStatus component
  - create_MasterEnvViewer component
  - create_AlertPanel component
  - integrate_agent_telemetry_display
  - wire_credential_management_ui
new_components:
  - dashboard-agent-swarm/src/components/ExecutionControl.tsx
  - dashboard-agent-swarm/src/components/PhaseGateApproval.tsx
  - dashboard-agent-swarm/src/components/RepoStatus.tsx
  - dashboard-agent-swarm/src/components/MasterEnvViewer.tsx
  - dashboard-agent-swarm/src/pages/ControlDashboard.tsx
output_pr_branch: feature/P3-dashboard-frontend
```

#### Bead: TEST_DASHBOARD_FRONTEND
```yaml
bead_id: BEAD-P3-WS3A-002
title: "Test dashboard frontend"
stage: TEST
tasks:
  - run_component_tests
  - verify_control_interactions
  - test_real_time_telemetry_updates
  - check_accessibility
  - run_e2e_dashboard_flow
success_criteria:
  - all_components_render: true
  - controls_respond_to_actions: true
  - telemetry_updates_live: true
  - no_console_errors: true
```

#### Build Checkpoint P3-WS3A
```bash
# Build frontend
npm run build --workspace=dashboard-agent-swarm
# Component tests
npm run test --workspace=dashboard-agent-swarm -- "ControlDashboard"
# E2E tests (if available)
npm run test:e2e --workspace=dashboard-agent-swarm
```

### Workstream 3B: Backend Control Plane

#### Bead: IMPLEMENT_CONTROL_BACKEND
```yaml
bead_id: BEAD-P3-WS3B-001
title: "Implement control plane backend"
stage: IMPLEMENT
tasks:
  - create_phase_gate_approval_endpoint
  - create_master_env_credential_loader
  - create_repo_status_aggregator
  - create_agent_telemetry_sink
  - integrate_ralphy_orchestrator
  - wire_build_test_pipelines
new_routes:
  - POST /api/phases/{phase}/approve (with audit trail)
  - POST /api/phases/{phase}/reject (with reason)
  - GET /api/repos/status
  - GET /api/agent-telemetry
  - POST /api/execution/start-phase
  - GET /api/master-env/summary (safe non-secret view)
output_pr_branch: feature/P3-control-backend
```

#### Bead: TEST_CONTROL_BACKEND
```yaml
bead_id: BEAD-P3-WS3B-002
title: "Test control plane backend"
stage: TEST
tasks:
  - test_phase_gate_endpoints
  - verify_credential_loading
  - test_repo_status_aggregation
  - verify_audit_logging
  - test_orchestration_triggering
success_criteria:
  - endpoints_respond_correctly: true
  - credentials_loaded_safely: true
  - audit_trail_complete: true
  - orchestration_triggers_work: true
```

#### Build Checkpoint P3-WS3B
```bash
# Build backend
npm run build --workspace=dashboard-agent-swarm
# Backend tests
npm run test --workspace=dashboard-agent-swarm -- "server/routes"
# Lint
npm run lint --workspace=dashboard-agent-swarm
```

### Phase 3 Deliverables
- ✅ `dashboard-agent-swarm/src/pages/ControlDashboard.tsx` with full controls
- ✅ Control plane backend endpoints deployed
- ✅ Real-time telemetry dashboard working
- ✅ Phase gate approval UI functional
- ✅ Master.env viewer (safe, non-secrets)
- ✅ `ops/reports/P3_DASHBOARD_VERIFICATION.md`
- ✅ PR `feature/P3-dashboard-frontend` ready for merge
- ✅ PR `feature/P3-control-backend` ready for merge

### Human Approval Gate: Phase 3 → Phase 4
```
[ ] Dashboard frontend built and tested
[ ] Control plane backend functional
[ ] Phase gate approval working
[ ] Telemetry display live
[ ] Audit logging verified
[ ] No security vulnerabilities in credential handling
Approver: _______________  Date: _______________
```

---

## PHASE 4: Automation Rollout & Safe Execution

**Owner:** Agent Lightning Bootstrap Agent (Always-On)
**Depends On:** Phase 3 Gate Approval
**Duration:** Multi-phase executable sequence
**Approval Gate:** Successful dry-run + rollback plan verification

### Bead: PLAN_AUTOMATION_ROLLOUT
```yaml
bead_id: BEAD-P4-001
title: "Plan automation rollout"
stage: PLAN
tasks:
  - sequence_all_implementation_packets
  - define_rollback_controls
  - generate_deployment_matrix
  - identify_blocking_dependencies
output: ops/reports/P4_automation_plan.json
```

### Bead: IMPLEMENT_AGENT_BOOTSTRAP
```yaml
bead_id: BEAD-P4-002
title: "Implement Agent Lightning bootstrap automation"
stage: IMPLEMENT
tasks:
  - create_agent_lightning_launcher.py
  - create_subagent_pool_manager.py
  - create_bead_executor.py
  - create_ralphy_orchestrator_integration.py
  - wire_approval_gate_checks
  - implement_rollback_triggers
new_files:
  - agents/lightning/launcher.py
  - agents/lightning/subagent_pool.py
  - agents/lightning/bead_executor.py
  - archonx/tools/ralphy_orchestrator.py
  - ops/scripts/rollback_procedures.sh
output_pr_branch: feature/P4-agent-bootstrap
```

### Bead: TEST_AGENT_BOOTSTRAP
```yaml
bead_id: BEAD-P4-003
title: "Test agent bootstrap and automation"
stage: TEST
tasks:
  - dry_run_phase_4_execution
  - verify_subagent_spinning
  - test_bead_execution_loop
  - verify_approval_gate_checks
  - test_rollback_procedures
  - verify_report_emission
success_criteria:
  - bootstrap_completes_without_errors: true
  - subagents_spawn_correctly: true
  - approval_gates_enforced: true
  - rollback_procedures_work: true
```

#### Build Checkpoint P4
```bash
# Python tests
python -m pytest agents/lightning/test_launcher.py -v
python -m pytest agents/lightning/test_subagent_pool.py -v
# Integration test
python scripts/test/bootstrap_integration_test.py --dry-run
# Deployment plan validation
python scripts/validate/validate_deployment_matrix.py ops/reports/P4_automation_plan.json
```

### Bead: PATCH_BOOTSTRAP_ITERATIONS
```yaml
bead_id: BEAD-P4-004
title: "Patch and iterate bootstrap"
stage: PATCH
tasks:
  - review_dry_run_failures
  - apply_fixes
  - re_run_tests
  - verify_rollback_procedures
  - emit_final_readiness_report
```

### Subagent Deployment Strategy

**For each implementation packet:**

1. **Subagent Assigned** → Creates feature branch
2. **Development Loop** → PLAN/IMPLEMENT/TEST/PATCH cycle
3. **Build Passes** → Automated checks run
4. **PR Created** → Automated PR to `main` with:
   - Build status badge
   - Test coverage report
   - Dependency graph
   - Rollback instructions
5. **Human Approval Gate** → Dashboard shows approval UI
6. **Merge Decision** → If approved → merge to main
7. **Deployment** → Agent performs merge + emits telemetry

**Approval Gate Template (embedded in PR):**
```markdown
## Approval Gate Requirements

- [ ] Build passed
- [ ] Tests passed (>80% coverage)
- [ ] No merge conflicts
- [ ] Rollback tested
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Security review (if applicable)

**Approver:** _______________
**Timestamp:** _______________
**Reason (if rejected):** _______________
```

### Phase 4 Deliverables
- ✅ `agents/lightning/launcher.py` with always-on bootstrap
- ✅ Subagent pool manager operational
- ✅ Bead executor loop working
- ✅ Ralphy orchestration integrated
- ✅ `ops/scripts/rollback_procedures.sh` tested
- ✅ `ops/reports/P4_AUTOMATION_READINESS.md`
- ✅ PR `feature/P4-agent-bootstrap` ready for merge

### Human Approval Gate: Phase 4 → Phase 5
```
[ ] Agent bootstrap tested in dry-run
[ ] Subagent pool verified
[ ] Bead executor loop working
[ ] Rollback procedures tested
[ ] Approval gate enforcement confirmed
[ ] No production safety concerns
Approver: _______________  Date: _______________
```

---

## PHASE 5: Validation, Reporting & Handoff

**Owner:** Validation & Reporting Agent
**Depends On:** Phase 4 Gate Approval
**Duration:** Consolidation + final verification
**Approval Gate:** All production criteria met

### Bead: EVALUATE_COMPLETE
```yaml
bead_id: BEAD-P5-001
title: "Evaluate complete implementation"
stage: EVALUATE
tasks:
  - consolidate_all_evidence_artifacts
  - verify_production_readiness_checklist
  - generate_execution_matrix
  - generate_patch_ledger
  - produce_final_handoff_brief
output:
  - ops/reports/EXECUTION_MATRIX.json
  - ops/reports/PATCH_LEDGER.md
  - plans/FINAL_HANDOFF_BRIEF.md
```

### Final Production Checklist

```yaml
Production Readiness Checklist:
  Phase 0:
    - [ ] Baseline audit complete and report accurate
    - [ ] All repos inventoried
  Phase 1:
    - [ ] All documentation normalized
    - [ ] Schema validation passing
  Phase 2:
    - [ ] Devika-PI governance wrapper tested
    - [ ] Workflow contracts complete
    - [ ] Security policies enforces
  Phase 3:
    - [ ] Dashboard control UI functional
    - [ ] Control plane backend operational
    - [ ] Master.env integration working
    - [ ] Telemetry display live
  Phase 4:
    - [ ] Agent bootstrap automation operational
    - [ ] Subagent pool manager working
    - [ ] Bead executor loop functioning
    - [ ] Rollback procedures tested
  Phase 5:
    - [ ] All deliverables merged to main
    - [ ] Zero critical issues in reports
    - [ ] Monitoring and alerting live
    - [ ] Handoff documentation complete
```

### Execution Matrix

**Generated as JSON:**
```json
{
  "project": "ARCHONX End-to-End Implementation",
  "phases": {
    "phase_0": {
      "name": "Baseline Audit",
      "beads": ["BEAD-P0-001", "BEAD-P0-002", "BEAD-P0-003"],
      "status": "completed",
      "evidence": "ops/reports/baseline_audit.json",
      "human_approval_timestamp": "2026-02-24T14:30:00Z"
    },
    "phase_1": {
      "name": "Documentation Normalization",
      "status": "in_progress",
      "pr": "feature/P1-doc-normalization"
    }
    ...
  },
  "deployment_status": {
    "merged_to_main": 12,
    "pending_approval": 3,
    "in_development": 5
  }
}
```

### Patch Ledger

**Generated as Markdown:**
```markdown
# ARCHONX Patch Ledger

## Phase 0: Baseline Audit
- **Patch:** BEAD-P0-001 → Created audit baseline
- **Status:** ✅ Merged
- **Files:** ops/reports/baseline_audit.json

## Phase 1: Documentation Normalization
- **Patch:** BEAD-P1-002 → Normalized all plans/ and docs/
- **Files Modified:** 47 files
- **Status:** ✅ Merged

...

## Deployment Summary
- **Total Patches:** 32
- **Merged:** 28
- **Pending:** 4
- **Failed/Rolled Back:** 0
- **Deployment Date:** 2026-02-24
```

### Handoff Brief

**Key sections:**
1. Implementation summary
2. Architecture overview
3. Known limitations
4. Production support procedures
5. Monitoring & alerting
6. Escalation contacts

### Phase 5 Deliverables
- ✅ `ops/reports/EXECUTION_MATRIX.json`
- ✅ `ops/reports/PATCH_LEDGER.md`
- ✅ `plans/FINAL_HANDOFF_BRIEF.md`
- ✅ All 32+ beads executed and reported
- ✅ All PRs merged to `main`
- ✅ Production monitoring live

### Final Human Approval Gate: Production Release
```
PRODUCTION RELEASE SIGN-OFF

[ ] All phases completed
[ ] All human approval gates satisfied
[ ] Zero critical issues
[ ] Monitoring live
[ ] Rollback procedures tested
[ ] Support team trained
[ ] Documentation complete

Authorized Release Approver: _______________
Date/Time: _______________
```

---

## Master.env Integration

### Credential Management Strategy

**Location:** `E:\THE PAULI FILES\master.env` (referenced, not in repo)

**Dashboard Safe View (NO SECRETS EXPOSED):**
```
✅ DATABASE_CONNECTION_POOL_SIZE: 20
✅ CACHE_ENABLED: true
✅ LOG_LEVEL: info
❌ ANTHROPIC_API_KEY: [REDACTED]
❌ GITHUB_TOKEN: [REDACTED]
```

**Credential Loading in Phase 4:**

```python
# agents/lightning/secrets_loader.py
import os
from pathlib import Path

def load_master_env_safe():
    """Load master.env with safety guards."""
    env_path = Path("E:/THE PAULI FILES/master.env")

    if not env_path.exists():
        raise FileNotFoundError(f"master.env not found at {env_path}")

    # Load into os.environ (isolated process)
    with open(env_path) as f:
        for line in f:
            if line.startswith("SECRET_"):
                # Secrets never logged or displayed
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
            elif not line.startswith("#"):
                # Non-secrets safe to log for debugging
                os.environ[line.split("=")[0]] = line.split("=")[1]
```

**Dashboard safely displays config state without exposing values:**
```tsx
// dashboard-agent-swarm/src/components/MasterEnvViewer.tsx
export function MasterEnvViewer() {
  const [envState, setEnvState] = useState<Record<string, string>>({});

  useEffect(() => {
    fetch('/api/master-env/summary')
      .then(r => r.json())
      .then(data => {
        // Server returns {key: "REDACTED" | "true" | "20" | etc}
        // NO SECRET VALUES EVER SENT TO CLIENT
        setEnvState(data);
      });
  }, []);

  return (
    <table>
      {Object.entries(envState).map(([k, v]) => (
        <tr key={k}>
          <td>{k}</td>
          <td>{v}</td>
        </tr>
      ))}
    </table>
  );
}
```

---

## Ralphy Orchestration Integration

### Ralphy Wrapper

```python
# archonx/tools/ralphy_orchestrator.py

from ralphy import Orchestrator, WorkItem

class ArchonXRalphyBridge:
    """Bridge beads loop to Ralphy multi-repo orchestration."""

    def __init__(self, master_env_path: str):
        self.ralphy = Orchestrator(
            repos=[
                "archonx-os",
                "dashboard-agent-swarm",
                "paulisworld-openclaw-3d",
                # + all connected repos
            ]
        )
        self.master_env = self._load_master_env(master_env_path)

    def execute_phase(self, phase_num: int, beads: list[str]):
        """Execute all beads in a phase across repos."""
        work_items = [
            WorkItem(
                bead_id=bead,
                repo=self._determine_repo(bead),
                branch=f"feature/{bead}",
                commands=[
                    f"python agents/lightning/bead_executor.py {bead}",
                ]
            )
            for bead in beads
        ]

        results = self.ralphy.execute_parallel(work_items)

        # Collect reports
        reports = [r.get_report() for r in results]
        return self._consolidate_reports(reports)

    def wait_for_approval_gate(self, phase_num: int):
        """Block until human approves via dashboard."""
        while True:
            status = self._fetch_dashboard_approval_status(phase_num)
            if status == "approved":
                return True
            elif status == "rejected":
                return False
            time.sleep(5)
```

---

## Automated Build/Test Pipeline

### Phase Build Template

```yaml
# Every phase has this build config
name: Phase-X-Build
on: [pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build

      - name: Unit Tests
        run: npm run test -- --coverage

      - name: Integration Tests
        run: npm run test:integration

      - name: Generate Coverage Report
        run: npm run coverage:report

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: coverage/

  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate PR
        run: |
          python scripts/validate/pr_requirements.py \
            --approval-gate \
            --rollback-plan \
            --coverage-threshold 80
```

---

## Agent Logging & Telemetry

### Bead Execution Logging

```json
{
  "timestamp": "2026-02-24T15:30:45Z",
  "bead_id": "BEAD-P2-WS2A-002",
  "phase": 2,
  "stage": "IMPLEMENT",
  "agent": "devika-pi-governance-agent",
  "status": "completed",
  "files_created": 8,
  "files_modified": 12,
  "execution_time_seconds": 245,
  "output_branch": "feature/P2-devika-pi-governance",
  "next_stage": "TEST",
  "evidence_path": "ops/reports/BEAD-P2-WS2A-002.log"
}
```

### Dashboard Telemetry

```tsx
// Real-time agent activity displayed on dashboard
{
  "agents": [
    {
      "name": "Devika-PI Agent",
      "status": "executing",
      "current_bead": "BEAD-P2-WS2A-002",
      "progress": "65%",
      "last_heartbeat": "2026-02-24T15:30:45Z",
      "health": "healthy"
    },
    {
      "name": "Documentation Agent",
      "status": "waiting",
      "current_bead": "BEAD-P1-004",
      "blocked_by": "BEAD-P1-003",
      "health": "healthy"
    }
  ],
  "phase_gate_pending": {
    "phase": 1,
    "approval_required_by": "human",
    "initiated_at": "2026-02-24T14:30:00Z",
    "status": "waiting_approval"
  }
}
```

---

## Success Criteria & Exit Gates

### Per-Phase Success Criteria

| Phase | Build Passes | Tests Pass | Reports Generated | Gate Approval |
|-------|--------------|------------|--------------------|---------------|
| P0 | ✅ | ✅ | ✅ Baseline audit | Human sign-off |
| P1 | ✅ | ✅ | ✅ Conformance | Human sign-off |
| P2 | ✅ | ✅ | ✅ Governance | Human sign-off |
| P3 | ✅ | ✅ | ✅ Dashboard verification | Human sign-off |
| P4 | ✅ | ✅ | ✅ Automation readiness | Human sign-off |
| P5 | ✅ | ✅ | ✅ Final handoff brief | Production release |

### Overall Success Criteria (Production Release)

```yaml
Production_Release_Gate:
  all_phases_completed: true
  human_approval_gates_satisfied: true
  zero_critical_issues: true
  build_test_passing: true
  monitoring_live: true
  rollback_tested: true
  documentation_complete: true
  support_training_complete: true
  artifact_preservation: true
```

---

## Timeline & Scheduling

### Recommended Execution Windows

- **Phase 0 (Baseline):** Immediate (async continuous)
- **Phase 1 (Docs):** Post-P0 approval (2-3 days parallel)
- **Phase 2 (Governance):** Post-P1 approval (3-5 days parallel workstreams)
- **Phase 3 (Dashboard):** Post-P2 approval (3-5 days parallel)
- **Phase 4 (Automation):** Post-P3 approval (2-3 days + dry-run)
- **Phase 5 (Handoff):** Post-P4 approval (1-2 days consolidation)

### Human Touch Points

1. **Phase Gate Approval**: ~15 min review + decision
2. **Dashboard Monitoring**: Passive (telemetry updates live)
3. **Emergency Rollback**: Instant (if issues detected)
4. **Config Updates**: Via master.env changes (triggers Phase X restart)

---

## Emergency Procedures

### Rollback Chain

```bash
# If Phase X fails tests:
./ops/scripts/rollback_procedures.sh --phase X --revert-to-previous

# This will:
# 1. Revert feature branch
# 2. Reset main to last stable commit
# 3. Alert approver
# 4. Emit failure report
# 5. Await human decision
```

### Approval Rejection Flow

```
Human Rejects PR
  ↓
Agent receives rejection reason
  ↓
Agent creates analysis report
  ↓
Issues reassigned to same agent with corrections needed
  ↓
New PR generated with fixes
  ↓
Human reviews revised PR
```

---

## Repository Integration Map

**All connected repos orchestrated via Ralphy:**

```
archonx-os (CONTROL PLANE)
├── Devika-PI Governance (Phase 2)
├── Dashboard Control (Phase 3)
└── Agent Bootstrap (Phase 4)

dashboard-agent-swarm (ORCHESTRATION)
├── Frontend Controls (Phase 3)
└── Backend API (Phase 3)

paulisworld-openclaw-3d (3D VENUE)
└── Agent Meeting Integration (Future)

paulis-pope-bot (IDENTITY)
└── Persona Integration (Future)

[Submodules via git]
├── agent-lightning (Launch control)
├── VisionClaw (Visual processing)
└── [Other supportive tools]
```

---

## Success Definition

**You will know this is successful when:**

1. ✅ Phase 0: Baseline report shows all repos connected and accounted for
2. ✅ Phase 1: Dashboard shows all documentation conformant
3. ✅ Phase 2: Security policies enforcing safe command execution
4. ✅ Phase 3: Human can control execution through dashboard, see real-time telemetry
5. ✅ Phase 4: Agents autonomously execute beads loops with human approval gates
6. ✅ Phase 5: Full system operational with centralized control, automated deployments, zero manual merges

**The Big Picture:**
- Humans make high-level decisions (approve phase gates)
- Agents execute all other work autonomously
- Dashboard provides complete visibility
- All code changes traced in execution matrix
- Production safety maintained via approval boundaries

---

## Sign-Off Template

```
PROJECT: ARCHONX End-to-End Implementation
PRD VERSION: 1.0
APPROVAL DATE: _______________
APPROVED BY: _______________

This implementation plan is approved for execution per the 5-phase beads+Ralphy loop
with mandatory human approval gates at each phase boundary.

Execution may begin upon Phase 0 Gate Approval.

Authorized by: _______________
```

---

**END OF PRD**

Next: Human approval to proceed with Phase 0 baseline audit.
