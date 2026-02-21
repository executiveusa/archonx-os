# Super Sync SOP (Read/Write Mission)

## Purpose
Create one canonical ecosystem registry that maps local project folders to correct GitHub repositories, continuously discovers newly created repositories, and routes upgrade/security opportunities to Agent Zero through OpenClaw.

## Scope (Current Phase)
- Read repository inventory from authenticated GitHub account(s).
- Write canonical repository records into `git-hub-ecosystem/`.
- Do not modify application code in this phase.
- Defer E-drive folder matching to the next phase.

## Canonical Artifacts (This Folder)
- `github_repos_raw.json` - API source snapshot.
- `github_repos_inventory.csv` - flattened inventory with visibility.
- `github_repos_numbered.txt` - numbered full list for matching sessions.
- `repos_001_050.txt` ... `repos_301_316.txt` - chunked review files.
- `repo-scout-charter.yaml` - scout assignment and duties.
- `cron-schedule-spec.md` - schedule, trigger, outputs.

## Operating Loop
1. Pull full repo inventory (public + private).
2. Normalize to canonical records with:
   - `full_name`
   - `visibility`
   - `fork`
   - `archived`
   - `updated_at`
3. Compare against prior snapshot and identify new repositories.
4. Append newly discovered repos to canonical inventory.
5. Trigger scout review cycle (security + monetization + product opportunities).
6. Deliver findings to Agent Zero via OpenClaw work item channel.

## Governance Rules
- Every agent receives OpenClaw capability before assignment.
- Universal Skills Manager is treated as mandatory skills plane for scout agents.
- Prompt-injection checks and security checks are required every run.
- Findings must include exploitation risk and business upside classification.

## Universal Skills Manager Requirement
Reference: `https://github.com/jacob-bd/universal-skills-manager.git`

Integration intent with toolbox:
- Register USM as shared skills backend.
- Mirror approved skills into toolbox contract surface.
- Require skills provenance tags for imported skills.
- Enforce denylist for untrusted/unsigned skill bundles.

## Output Contract (Per 12-hour cycle)
- `new_repos_detected`: list
- `security_findings`: list (prompt injection, auth gaps, data exposure)
- `money_upgrades`: list (feature ideas, pricing levers, growth hooks)
- `pain_signals`: list (Reddit/Product Hunt/X trend-derived opportunities)
- `agent_zero_packet`: summary payload routed through OpenClaw
