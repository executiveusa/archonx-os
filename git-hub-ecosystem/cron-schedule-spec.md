# Super Sync Cron Design

## Schedule
Run twice daily:
- 12:00 AM local
- 12:00 PM local

Cron expression:
- `0 0,12 * * *`

## Runbook Per Trigger
1. Refresh authenticated GitHub repo inventory (public + private).
2. Diff against previous snapshot.
3. Add newly discovered repos to canonical list.
4. Trigger White + Black scout sweep.
5. Emit combined report to Agent Zero over OpenClaw.

## Required Outputs
- `github_repos_raw.json` (snapshot)
- `github_repos_inventory.csv` (normalized)
- `new_repos_<timestamp>.txt` (delta)
- `scout_report_<timestamp>.md` (security + monetization)
- `agent_zero_packet_<timestamp>.json` (routing payload)

## Reliability Rules
- If GitHub auth fails: mark cycle as `degraded` and retry in 15 minutes.
- If diff fails: preserve previous canonical list and emit warning.
- Never delete repos from canonical list without explicit archival decision.
