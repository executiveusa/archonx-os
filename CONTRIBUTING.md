# Contributing

## Local setup
- Configure required env vars (`ARCHONX_KERNEL_URL`, `ARCHONX_YAPP_URL`, `ARCHONX_TOOLBOX_URL`).
- Run checks:
  - `python -m pytest`
  - `python -m compileall core toolbox`

## Standards
- Keep privileged actions gated by grants + work item IDs.
- Emit audit events for planned and executed actions.
