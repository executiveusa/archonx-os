# ArchonX Ops Runner

`archonx_ops_runner.py` provides local ArchonX automation for eco-prompt execution, enrollment, meetings, and operational health checks.

## Entrypoints
- `archonx-ops run --eco-prompt <name> [--dry-run] [--report-only]`
- `archonx-ops sync --all`
- `archonx-ops enroll --agent-id <id>`
- `archonx-ops meeting`
- `archonx-ops doctor`

## Report Outputs
Reports are emitted under `ops/reports/`:
- `PAULIWHEEL_SYNC_REPORT_<timestamp>.json`
- `PAULIWHEEL_COMPLIANCE_MATRIX_<timestamp>.json`
- `pauliwheel_meeting_<timestamp>.json`
- `FINAL_ECO_PROMPT_REPORT.json`
