# ARCHONX Documentation Patch Ledger

## Purpose

This ledger records documentation patches applied to planning artifacts, with rationale and verification expectations.

## Patch Entries

| Patch ID | Artifact | Change Type | Rationale | Validation Target |
|---|---|---|---|---|
| DOC-PATCH-001 | [`ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md`](plans/ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md) | New file | define unified documentation spec and execution PRD | `ops/reports/doc_prd_conformance.json` |
| DOC-PATCH-002 | [`ARCHONX_PHASED_IMPLEMENTATION_ROADMAP.md`](plans/ARCHONX_PHASED_IMPLEMENTATION_ROADMAP.md) | New file | complete phased roadmap with compliance checkpoints and reporting cadence | `ops/reports/phased_roadmap_readiness.json` |
| DOC-PATCH-003 | [`ARCHONX_DOC_EXECUTION_MATRIX.md`](plans/ARCHONX_DOC_EXECUTION_MATRIX.md) | New file | provide artifact to owner and acceptance mapping with evidence paths | `ops/reports/doc_execution_matrix_validation.json` |
| DOC-PATCH-004 | [`ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md`](plans/ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md) | Existing planning baseline | establish control-plane workflow contracts and role views | `ops/reports/dashboard_workflow_contracts.json` |

## Verification Checklist

- each artifact includes implementation handoff guidance
- each acceptance criterion maps to an evidence path under `ops/reports`
- cross references between planning docs are valid
- governance controls align with [`AGENTS.md`](AGENTS.md)

## Closure Criteria

Ledger closes when all validation targets are generated and marked pass in governance review.
