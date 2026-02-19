# OpenClaw Reportback Contract

OpenClaw-connected repos must report to ArchonX OS kernel and YAPP control tower.

## Required env vars
- `ARCHONX_KERNEL_URL`
- `ARCHONX_YAPP_URL`
- `ARCHONX_WORK_ITEM_ID`
- `ARCHONX_AGENT_ID`
- `ARCHONX_REPO_SLUG`

## Required payloads
- Agent register: `/v1/agents/register`
- Heartbeat every 15s: `/v1/agents/heartbeat`
- Audit event: `/v1/audit`
- Work item link: `/v1/workitems/link`

## Deny defaults
- Missing work item ID => deny with `missing_work_item_id` and audit event.
- Kernel unreachable => deny unless `ARCHONX_KERNEL_PROVIDER=mock`.
