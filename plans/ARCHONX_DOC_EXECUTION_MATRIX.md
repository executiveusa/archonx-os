# ARCHONX Documentation Execution Matrix

## Purpose

This matrix maps each planning artifact to owner role, required inputs, expected outputs, acceptance criteria, and evidence paths.

## Matrix

| Artifact | Owner Role | Inputs | Outputs | Acceptance Criteria | Evidence Path |
|---|---|---|---|---|---|
| [`ARCHONX_AUTONOMOUS_AGENCY_BLUEPRINT.md`](plans/ARCHONX_AUTONOMOUS_AGENCY_BLUEPRINT.md) | Systems Architect | org strategy, repo inventory | target architecture model | architecture components and boundaries are unambiguous | `ops/reports/blueprint_conformance.json` |
| [`ARCHONX_SOP_AND_PROMPT_SYSTEM.md`](plans/ARCHONX_SOP_AND_PROMPT_SYSTEM.md) | Governance Lead | policy baseline, team operating model | SOP and prompt standards | all SOP sections map to operational controls | `ops/reports/sop_alignment.json` |
| [`ARCHONX_HUMAN_LOOP_MINIMIZATION_MAP.md`](plans/ARCHONX_HUMAN_LOOP_MINIMIZATION_MAP.md) | Automation Strategist | current human interventions | replacement and escalation map | each manual step has automation candidate and fallback | `ops/reports/hitl_minimization.json` |
| [`ARCHONX_REALITY_MAP_AND_GAP_PLAN.md`](plans/ARCHONX_REALITY_MAP_AND_GAP_PLAN.md) | Portfolio Operator | current repo state, desired target | gap map and closure strategy | every major gap has closure action and control owner | `ops/reports/reality_gap_closure.json` |
| [`ARCHONX_SECURE_AUTOMATION_PIPELINE.md`](plans/ARCHONX_SECURE_AUTOMATION_PIPELINE.md) | Security Engineer | CI and release model | secure pipeline controls | merge gates and rollback controls explicitly defined | `ops/reports/security_pipeline_controls.json` |
| [`ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md`](plans/ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md) | Control Plane Product Owner | operator needs, agent capabilities | dashboard workflow contracts | each workflow defines trigger, payload, gate, telemetry, evidence | `ops/reports/dashboard_workflow_contracts.json` |
| [`ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md`](plans/ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md) | Documentation Architect | existing planning docs | normative patch and execution PRD | section spec and acceptance gates are fully specified | `ops/reports/doc_prd_conformance.json` |
| [`ARCHONX_PHASED_IMPLEMENTATION_ROADMAP.md`](plans/ARCHONX_PHASED_IMPLEMENTATION_ROADMAP.md) | Program Manager | all upstream planning artifacts | phased execution sequence | phase exits and compliance checkpoints are explicit | `ops/reports/phased_roadmap_readiness.json` |

## Execution Rules

1) Each artifact MUST have one accountable owner role.
2) Each acceptance criterion MUST be verifiable.
3) Every acceptance claim MUST map to a machine-readable report path under `ops/reports`.
4) Handoff to code mode requires all matrix rows marked complete.

## Handoff Packet Requirements

Each packet generated from this matrix MUST include:
- source artifact reference
- implementation objective
- constraints and policy gates
- completion criteria
- evidence report target path

## Definition of Complete Matrix

Matrix completion is achieved when all rows have:
- owner role assigned
- explicit input and output definition
- measurable acceptance criteria
- assigned evidence artifact path
