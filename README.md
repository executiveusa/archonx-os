# ArchonX OS

ArchonX OS is the source-of-truth repository for Poly Effect security contracts, ecosystem manifests, and toolbox standards.

## Purpose
- Define canonical Access Kernel + Gastown work-item requirements.
- Publish ecosystem-wide contracts for OpenClaw reportback, toolbox, and skills.
- Provide operator bootstrap guidance (`archonxctl`) and baseline policies.

## Quickstart
```bash
./security/bin/bootstrap.sh
```

## Required environment variables
- `ARCHONX_KERNEL_URL`
- `ARCHONX_YAPP_URL`
- `ARCHONX_TOOLBOX_URL`
- `ARCHONX_WORK_ITEM_ID`
- `ARCHONX_AGENT_ID`
- `ARCHONX_REPO_SLUG`

## Test commands
```bash
python -m pytest
python -m compileall core toolbox
```

## Reporting contract
- Repo-level reportback metadata: `.archonx/reportback.json`
- Toolbox pointer metadata: `.archonx/toolbox.json`
- OpenClaw reportback contract: `ecosystem/contracts/openclaw-reporting-contract.json`
