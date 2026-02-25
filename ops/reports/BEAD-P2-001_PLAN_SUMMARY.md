# PHASE 2 PLAN SUMMARY
## Governance & Contract Hardening - Complete Planning

**Date:** 2026-02-24 17:50:00Z
**Bead ID:** BEAD-P2-001
**Phase:** 2 of 5
**Status:** ✅ PLAN PHASE COMPLETE
**Duration:** 1 hour 3 minutes
**Output:** Two parallel workstream plans

---

## Executive Summary

Phase 2 planning is complete. Two parallel workstreams sequenced and ready for implementation:

- **WS2A (Devika-PI Governance):** 5 implementation tasks, 7-10 hours execution
- **WS2B (Workflow Contracts):** 42 workflow contracts, 8-12 hours execution

**Combined:** 2-3 days parallel execution, Ralphy orchestration active

---

## Workstream 2A: Devika-PI Integration & Governance

### Objective
Integrate Devika coding agent with PI framework, wrapped in PAULIWHEEL governance enforcement and policy gates.

### Execution Plan: 5 Tasks

#### Task 2A-1: Policy Enforcement Framework
**Duration:** ~2 hours
**Deliverables:**
- `archonx/security/devika_pi_policy.py` (policy engine)
- `archonx/config/devika_pi_policy.yaml` (policy rules)
- Policy enforcement tests

**What it does:**
- Defines safe command allowlist
- Blocks dangerous operations (file deletion, network calls without approval)
- Enforces PAULIWHEEL bead requirements
- Requires approval gate for elevated operations

**Success Criteria:**
- [ ] Policy engine blocks 100% of unsafe test commands
- [ ] Allowlist enforces command set
- [ ] Audit logging for all operations
- [ ] Tests pass: 10/10 security checks

#### Task 2A-2: Governance Wrapper
**Duration:** ~2 hours
**Deliverables:**
- `archonx/tools/devika_pi_wrapper.py` (execution harness)
- Integration with PAULIWHEEL bead loop
- Approval gate integration

**What it does:**
- Wraps all Devika operations
- Enforces PLAN→IMPLEMENT→TEST→EVALUATE cycle
- Requires bead_id for code-affecting operations
- Integrates with approval gate system

**Success Criteria:**
- [ ] Wrapper enforces bead requirements
- [ ] Execution halts on missing bead_id
- [ ] Reports emitted for all operations
- [ ] Rollback procedures functional

#### Task 2A-3: Context7 MCP Integration
**Duration:** ~1.5 hours
**Deliverables:**
- Context7 MCP client initialization
- Integration into Devika execution pipeline
- Fallback modes if MCP unavailable

**What it does:**
- Before any code generation, resolves library documentation
- Fetches official API reference from Context7
- Caches docs in execution context
- Prevents hallucinated API usage

**Success Criteria:**
- [ ] Context7 resolves library IDs correctly
- [ ] Docs fetched for React, Three.js, FastAPI, etc.
- [ ] Fallback mode works if Context7 unavailable
- [ ] Integration tests pass: 8/8

#### Task 2A-4: Devika Agent Configuration
**Duration:** ~2 hours
**Deliverables:**
- `agents/devika/config.json` (agent config)
- `agents/devika/system_prompt.md` (behavior spec)
- `agents/devika/extensions/` (subagent extensions)
  - task_loop.py
  - safe_commands.py
  - subagent_orchestration.py

**What it does:**
- Configures Devika as production agent
- Defines system behavior and constraints
- Sets up subagent spawning capability
- Integrates all governance layers

**Success Criteria:**
- [ ] Config valid JSON with all required fields
- [ ] Agent spins up without errors
- [ ] Extensions load and initialize
- [ ] Dashboard can discover and control agent

#### Task 2A-5: Dashboard Integration
**Duration:** ~2 hours
**Deliverables:**
- API endpoint: GET /api/agents/devika/status
- API endpoint: POST /api/agents/devika/execute
- Dashboard UI for Devika control
- Real-time telemetry display

**What it does:**
- Allows dashboard to view Devika operational status
- Allows dashboard to trigger Devika execution (with approval)
- Streams telemetry and log output to dashboard
- Displays policy gate decisions in real-time

**Success Criteria:**
- [ ] Status endpoint returns agent telemetry
- [ ] Execute endpoint respects approval gates
- [ ] Dashboard displays live status and logs
- [ ] All integration tests pass: 6/6

### WS2A Summary
```
Tasks: 5
Total Duration: ~2+2+1.5+2+2 = 9.5 hours (estimated 8-12 with testing)
New Files: 8 (py files + config + extensions)
Dependencies: Phase 1 docs, Context7 availability
Success Rate Target: 100% (all gates must pass)
```

---

## Workstream 2B: Workflow Contracts

### Objective
Define deterministic contracts for all agent workflows with explicit trigger conditions, payloads, policy gates, telemetry, and evidence paths.

### Workflow Inventory: 42 Workflows Identified

**Category 1: Control Plane Workflows (12)**
1. Phase Gate Approval (human decision)
2. Phase Gate Rejection (with reason)
3. Bead Execution Start
4. Bead Status Report
5. Build Checkpoint Validation
6. Test Suite Execution
7. Coverage Report Generation
8. Rollback Trigger
9. Emergency Pause
10. Agent Telemetry Collection
11. Dashboard Update
12. Alert Dispatch

**Category 2: Devika-PI Workflows (8)**
1. Devika Task Reception
2. Library Documentation Fetch (Context7)
3. Code Generation
4. Test Execution
5. Build Validation
6. Approval Gate Check
7. Merge to Main
8. Execution Report

**Category 3: Orchestration Workflows (10)**
1. Subagent Spawn
2. Subagent Status Check
3. Multi-Repo Coordination (Ralphy)
4. Dependency Resolution
5. Parallel Execution
6. Result Consolidation
7. Error Handling
8. Retry Logic
9. Timeout Management
10. Agent Communication

**Category 4: Dashboard Workflows (7)**
1. Approval Gate Display
2. Status Dashboard Refresh
3. Real-time Telemetry Update
4. Manual Intervention Request
5. Configuration Change
6. Credential Update (Master.env)
7. Report Generation

**Category 5: System Operations (5)**
1. Health Check
2. Monitoring Alert
3. Log Aggregation
4. Compliance Audit
5. Archive & Cleanup

### Contract Schema Structure

```json
{
  "workflow_id": "WF-001",
  "name": "Phase Gate Approval",
  "category": "Control Plane",
  "version": "1.0",
  "trigger": {
    "event": "phase_complete",
    "condition": "all_tests_pass && all_gates_pass",
    "actor": "human_approver",
    "required_context": ["phase_number", "test_results", "reports"]
  },
  "payload_schema": {
    "type": "object",
    "required": ["phase", "approved", "reason"],
    "properties": {
      "phase": {"type": "integer", "minimum": 0, "maximum": 5},
      "approved": {"type": "boolean"},
      "reason": {"type": "string"}
    }
  },
  "policy_gates": {
    "required_role": "approver",
    "compliance_level": "PAULIWHEEL_CRITICAL",
    "approval_required": true,
    "escalation_path": ["tech_lead", "engineering_manager"]
  },
  "telemetry": {
    "event_name": "phase_gate_decision",
    "fields": ["phase", "decision", "timestamp", "approver_id"]
  },
  "evidence_path": "ops/reports/phase_{phase}_approval.json",
  "success_criteria": [
    "Approval timestamp recorded",
    "Report written to evidence path",
    "Next phase triggered if approved"
  ],
  "timeout_seconds": 3600
}
```

### Contract Specifications: 42 Contracts Ready

**All 42 contracts will be created per schema above**

Breakdown by effort:
- High-complexity (need design decisions): 8 contracts → 4 hours
- Medium-complexity (standard patterns): 16 contracts → 8 hours
- Low-complexity (standard templates): 18 contracts → 6 hours

Total: 42 contracts in ~18 hours effort (will parallelize)

### WS2B Deliverables

**Files to Create:**
- `archonx/contracts/workflow_*.json` (42 files)
- `docs/contracts/WORKFLOW_REFERENCE.md` (index)
- `ops/reports/P2_CONTRACT_COMPLETENESS.json` (audit)

**For Each Contract:**
- Trigger specification
- Payload schema
- Policy gate requirements
- Telemetry event definition
- Evidence artifact path
- Success criteria
- Timeout/SLA

### WS2B Summary
```
Workflows: 42 identified and cataloged
Contracts: 42 specifications to create
Total Duration: ~18 hours (estimated 12-20 with review/iteration)
New Files: 42 JSON + 1 reference doc
Dependencies: Phase 1 workflow definitions
Success Rate Target: 100% (all contracts must validate)
```

---

## Combined Phase 2 Execution

### Parallel Workstream Timeline

```
Start: 2026-02-25 (next business day)

DAY 1:
├─ WS2A Task 1-2 (4 hours): Policy + Wrapper
├─ WS2B Tasks 1-2 (6 hours): Inventory + Schema
└─ Status: On track

DAY 2:
├─ WS2A Task 3-4 (4 hours): Context7 + Config
├─ WS2B Task 3 (8 hours): Contract specs
└─ Status: Halfway through

DAY 3:
├─ WS2A Task 5 + Testing (4 hours): Dashboard + validation
├─ WS2B Task 4-5 + Review (6 hours): Policy mapping + evidence
└─ Status: Both complete

Ralphy Build Checkpoints:
├─ After WS2A Task 4: Build all new code
├─ After WS2B Task 3: Validate contracts
└─ Full validation: All tests pass

Total Phase 2: 2.5-3 days parallel execution
```

### Build & Test Integration

**After WS2A Implementation:**
```bash
npm run build:parallel --phase 2
# Tests:
- Policy enforcement: 10 tests
- Wrapper functionality: 8 tests
- Context7 integration: 8 tests
- Config validation: 5 tests
- Dashboard API: 6 tests
# Expected: 100% pass
```

**After WS2B Implementation:**
```bash
npm run test:contracts --phase 2
# Validates:
- Contract JSON schema: 42 contracts
- Consistency: All workflows covered
- No conflicts or duplicates
- Evidence paths valid
# Expected: 100% compliance
```

---

## Risk Assessment

### WS2A Risks

| Risk | Probability | Mitigation |
|------|------------|-----------|
| Context7 API unavailable | Low | Fallback mode, local cache |
| Policy too restrictive | Medium | Iterative testing, refinement |
| Devika integration breaking | Low | Comprehensive test suite |

### WS2B Risks

| Risk | Probability | Mitigation |
|------|------------|-----------|
| Missing workflows | Low | Systematic inventory from docs |
| Contract ambiguity | Medium | Schema validation + review |
| Workflow conflicts | Low | Dependency analysis |

**Overall Risk Level:** ✅ **LOW** - Both workstreams have clear specifications

---

## Phase 2 → Phase 3 Prerequisite

Before Phase 3 (Dashboard Control Plane) can begin:

- ✅ Devika-PI fully integrated and tested
- ✅ All 42 workflow contracts specified
- ✅ Policy gates enforcing PAULIWHEEL compliance
- ✅ Build passed, tests passed, validation complete

---

## Next Step: Human Approval for Phase 2

### Phase 2 PLAN: ✅ COMPLETE

**Both workstreams planned and sequenced:**
- WS2A: Devika-PI Governance (5 tasks, ~9.5 hours)
- WS2B: Workflow Contracts (42 contracts, ~18 hours)
- **Combined:** 2-3 days parallel execution

### Approval Required

**Do you approve Phase 2 execution with this plan?**

**Options:**

A) **APPROVE** → Proceed to IMPLEMENT immediately
   - Agents activate today
   - Parallel workstreams begin
   - Estimated complete: 2-3 days

B) **REVIEW** → Questions about approach?
   - I'll clarify any aspect
   - Modify plan as needed

C) **HOLD** → Defer Phase 2
   - System pauses at Phase 1
   - Awaits further approval

---

**BEAD-P2-001 (PLAN): ✅ COMPLETE**

Awaiting human approval to proceed to BEAD-P2-002 (IMPLEMENT)

---

**Generated by:** Governance & Contracts Planning Agent (Autonomous)
**For:** ARCHONX Phase 2 Implementation
**Date:** 2026-02-24 17:50:00Z
**Next:** Await approval → IMPLEMENT phase begins
