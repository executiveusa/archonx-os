# BEAD-P2-001 PLAN PHASE - GOVERNANCE & CONTRACTS
## Phase 2 Planning & Execution Sequencing

**Bead ID:** BEAD-P2-001
**Stage:** PLAN
**Phase:** 2 of 5 (Governance & Contract Hardening)
**Status:** ✅ IN PROGRESS
**Execution Time:** Starting 2026-02-24 17:47:00Z
**Output Target:** Two parallel workstream plans

---

## Executive Summary

Phase 2 introduces governance enforcement and contract hardening across all agent workflows.

**Two Parallel Workstreams:**
1. **WS2A: Devika-PI Integration** - Governance wrapper, policy enforcement
2. **WS2B: Workflow Contracts** - Define deterministic contracts for all workflows

**Expected Duration:** 2-3 days parallel execution
**Dependencies:** Phase 1 (Complete ✅) → Phase 2 ready to execute

---

## Workstream 2A: Devika-PI Integration & Governance

### Objective

Integrate Devika with PI coding agent framework, wrapped in PAULIWHEEL governance enforcement.

**Inputs:**
- `plans/DEVIKA_PI_INTEGRATION_PLAN.md` (Phase 1 normalized)
- `AGENTS.md` (governance baseline)
- `.ralphy.json` (build orchestration config)

**Deliverables:**
- Devika-PI governance wrapper implementation
- Policy enforcement system
- Context7 MCP integration
- Dashboard control integration

### WS2A Sub-Tasks (BEAD-P2-002A)

**Task 1: Policy Enforcement Design**
```
├─ Read: DEVIKA_PI_INTEGRATION_PLAN.md (WS2 specification)
├─ Read: AGENTS.md (compliance baseline)
├─ Design: Policy architecture for safe command execution
├─ Create: archonx/security/devika_pi_policy.py (policy rules)
└─ Output: Policy specification + test framework
```

**Task 2: Governance Wrapper**
```
├─ Design: Execution harness architecture
├─ Create: archonx/tools/devika_pi_wrapper.py (wrapper)
├─ Integrate: PAULIWHEEL bead enforcement
├─ Integrate: Approval gate checks
└─ Output: Production wrapper ready for deployment
```

**Task 3: Context7 MCP Integration**
```
├─ Design: Library documentation fetching workflow
├─ Create: Context7 MCP client
├─ Integrate: Into Devika execution pipeline
├─ Test: Context7 resolution for common libraries
└─ Output: MCP integration layer ready
```

**Task 4: Agent Configuration**
```
├─ Create: agents/devika/config.json
├─ Create: agents/devika/system_prompt.md
├─ Create: agents/devika/extensions/*.py
├─ Wire: To governance wrapper
└─ Output: Production agent config
```

**Task 5: Dashboard Integration**
```
├─ Design: Dashboard control layer for Devika
├─ Create: API endpoints for status/control
├─ Integrate: Devika telemetry to dashboard
├─ Test: Real-time status display
└─ Output: Dashboard integration ready
```

### WS2A Success Criteria

- [ ] Policy enforcement blocks unsafe commands
- [ ] Context7 MCP resolves library docs successfully
- [ ] PAULIWHEEL bead enforcement verified
- [ ] Wrapper passes security audit
- [ ] All 5 tasks integrate without errors
- [ ] Dashboard displays Devika agent status
- [ ] Approval gates enforce human control

---

## Workstream 2B: Workflow Contracts

### Objective

Define deterministic contracts for all agent workflows (trigger, payload, policy gate, telemetry, evidence).

**Inputs:**
- `plans/ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md`
- All normalized Phase 1 docs (workflow specs)
- `ops/reports/` (evidence paths)

**Deliverables:**
- Workflow contract specifications (JSON schema)
- Policy gate mappings
- Telemetry event definitions
- Evidence artifact paths

### WS2B Sub-Tasks (BEAD-P2-002B)

**Task 1: Workflow Discovery & Cataloging**
```
├─ Read: All Phase 1 docs for workflow definitions
├─ Catalog: Every workflow mentioned
├─ List: Trigger conditions, actors, outcomes
├─ Output: Complete workflow inventory
└─ Count: Expected ~40-50 workflows
```

**Task 2: Contract Schema Design**
```
├─ Design: JSON schema for workflow contracts
├─ Define: Required fields per contract
├─ Define: Policy gate requirements
├─ Define: Telemetry event format
└─ Output: Schema + examples
```

**Task 3: Contract Specification**
```
├─ For each workflow:
│  ├─ Trigger condition
│  ├─ Payload schema
│  ├─ Required approvals
│  ├─ Policy gates
│  └─ Evidence paths
├─ Create: archonx/contracts/*.json
└─ Output: 40-50 contract files
```

**Task 4: Policy Gate Mapping**
```
├─ For each workflow:
│  ├─ Map to PAULIWHEEL compliance level
│  ├─ Define escalation rules
│  ├─ Specify approval roles
│  └─ Set timeout/SLA
├─ Create: archonx/policies/*.yaml
└─ Output: Policy mappings complete
```

**Task 5: Evidence Path Documentation**
```
├─ For each workflow:
│  ├─ Define evidence output location
│  ├─ Specify telemetry format
│  ├─ Create: ops/reports/ paths
│  └─ Document: audit trail expectations
└─ Output: Evidence documentation complete
```

### WS2B Success Criteria

- [ ] All workflows cataloged
- [ ] 40-50 contract specifications complete
- [ ] Schema validation passes
- [ ] Policy gates mapped to compliance levels
- [ ] Evidence paths documented
- [ ] No ambiguity in contract definitions
- [ ] Ready for implementation in Phase 3

---

## PLAN Phase Execution

### Current Status: In Progress ✅

**Agent:** Governance and Contracts Planning Agent
**Start Time:** 2026-02-24 17:47:00Z
**Status:** Reading specifications and designing architecture

### Phase 1: Specification Analysis (Now)

```
Reading:
├─ DEVIKA_PI_INTEGRATION_PLAN.md (WS2A spec)
├─ ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md (WS2B spec)
├─ AGENTS.md (governance baseline)
├─ All Phase 1 normalized docs (workflow context)
└─ ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md

Building:
├─ WS2A architecture: Wrapper design + policy framework
├─ WS2B catalog: 40-50 workflow inventory
├─ Contract schema: JSON structure definition
└─ Implementation sequence: Task dependencies
```

### Phase 2: Plan Generation (Next 30 min)

```
Generating:
├─ WS2A detailed plan (tasks + success criteria)
├─ WS2B detailed plan (workflow contracts + schemas)
├─ Cross-workstream dependencies
├─ Risk assessment for each workstream
└─ Consolidated PLAN summary report
```

### Phase 3: Human Review (Then)

```
Output files:
├─ ops/reports/BEAD-P2-001_PLAN_SUMMARY.md
├─ ops/reports/P2_WS2A_PLAN.md (Devika-PI detail)
├─ ops/reports/P2_WS2B_PLAN.md (Contracts detail)
└─ ops/reports/BEAD-P2-001_PLAN_APPROVAL.md (gate document)

Human action required:
├─ Review: WS2A approach (Devika-PI governance)
├─ Review: WS2B approach (workflow contracts)
├─ Decision: Approve plan → Proceed to IMPLEMENT
```

---

## Parallel Workstream Dependencies

```
PLAN Phase (BEAD-P2-001)
├─ WS2A PLAN: Devika-PI governance (parallel)
└─ WS2B PLAN: Workflow contracts (parallel)
   └─ Both complete → Human approval
      ↓
IMPLEMENT Phase (BEAD-P2-002A & 2B)
├─ WS2A IMPLEMENT: Governance wrapper (parallel)
└─ WS2B IMPLEMENT: Contract specs (parallel)
   └─ Both pass Ralphy build → Human approval
      ↓
TEST Phase (BEAD-P2-003A & 2B)
├─ WS2A TEST: Policy enforcement verification
└─ WS2B TEST: Contract validation
   └─ Both 100% pass → EVALUATE
```

---

## Deliverables Expected

### From BEAD-P2-001 (PLAN)

**Report Files:**
- ✅ `ops/reports/BEAD-P2-001_PLAN_SUMMARY.md`
- ✅ `ops/reports/P2_DEVIKA_PI_PLAN.md` (WS2A details)
- ✅ `ops/reports/P2_WORKFLOW_CONTRACTS_PLAN.md` (WS2B details)
- ✅ `ops/reports/BEAD-P2-001_PLAN_APPROVAL.md` (gate)

**Planning Artifacts:**
- ✅ WS2A task breakdown (5 tasks)
- ✅ WS2B workflow inventory (40-50 workflows)
- ✅ Parallel execution sequence
- ✅ Success criteria for each workstream
- ✅ Risk assessment

---

## Implementation Timeline (Expected)

```
PLAN Phase:       ~1 hour (BEAD-P2-001, concurrent planning)
IMPLEMENT Phase: ~8 hours (BEAD-P2-002A & 2B, parallel execution)
TEST Phase:      ~4 hours (BEAD-P2-003A & 2B, concurrent validation)
EVALUATE:        ~1 hour (final reports, gate approval)
────────────────────────────────────────────────
PHASE 2 TOTAL:   ~14 hours (over 2-3 days)
```

---

## Current Status: PLAN Phase Active

**Agent:** Planning Agent (Governance & Contracts)
**Start Time:** 2026-02-24 17:47:00Z
**Expected Completion:** 2026-02-24 18:50:00Z (approx 1 hour)

**Next Output:** `ops/reports/BEAD-P2-001_PLAN_SUMMARY.md`

**Then:** Human reviews plan → Approves → IMPLEMENT begins

---

**BEAD-P2-001: PLANNING PHASE IN PROGRESS**

Awaiting: Plan summary generation and human approval
Next: BEAD-P2-002 (IMPLEMENT Phase)

