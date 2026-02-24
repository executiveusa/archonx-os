# Devika on PI Install Standard

## Purpose

Provide a deterministic installation path for PI to run Devika workflows consistently across ArchonX operator machines.

## Package

- PI package: `@mariozechner/pi-coding-agent`
- Install mode: pinned version via managed script

## Preflight

1. Node.js LTS installed
2. npm available
3. repo root is current working directory
4. operator has access to required environment secrets

## Standard Install Path

1. Run managed install script
2. Verify PI version
3. Verify Devika PI profile files exist
4. Emit setup report into `ops/reports/`

## Proposed Script Contract

- `scripts/pi/install-devika-pi.ps1`
- `scripts/pi/install-devika-pi.sh`
- `scripts/pi/check-devika-pi.ps1`
- `scripts/pi/check-devika-pi.sh`

Each script should:
- validate node and npm versions
- install pinned PI version
- verify CLI command availability
- print machine-readable output and write report JSON

## Security and Governance Requirements

- PI execution must route through Devika wrapper policy
- no direct unrestricted shell from UI path
- bead id required for code-affecting operations
- verification stage must run before completion signal

## Example Report Schema

```json
{
  "tool": "devika-pi-install",
  "status": "ok",
  "pi_version": "x.y.z",
  "node_version": "vXX",
  "npm_version": "X",
  "timestamp": "ISO-8601"
}
```

## Acceptance

- Install script succeeds on target machine profiles
- Check script confirms expected version and profile wiring
- Setup report generated under `ops/reports/`

