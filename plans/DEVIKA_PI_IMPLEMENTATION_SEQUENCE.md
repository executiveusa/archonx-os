# Devika on PI Implementation Sequence

## Execution Contract

- Bead format for this initiative: `BEAD-DEVIKA-PI-00x`
- Mandatory runtime loop: PLAN IMPLEMENT TEST EVALUATE PATCH REPEAT
- Mandatory verification stage: `archonx-ops doctor` plus available build and test commands
- Mandatory report output path: `ops/reports/`

## Phase A Platform Bootstrap

### A1 Install path decision and lock
- Choose managed install strategy for [`@mariozechner/pi-coding-agent`](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- Pin version in bootstrap scripts
- Add preflight checks for Node and npm

### A2 Bootstrap artifacts
- Add platform scripts under `scripts/pi/`
- Add install and verification docs under `docs/devika-pi/`
- Emit machine-readable bootstrap report under `ops/reports/devika_pi_install.json`

## Phase B Governance and Safety

### B1 Policy wrapper
- Implement wrapper entrypoint for Devika PI execution
- Enforce bead presence for code-affecting operations
- Enforce command allowlist and denylist

### B2 Compliance telemetry
- Log policy decisions and command outcomes
- Persist stage transitions for PLAN IMPLEMENT TEST EVALUATE PATCH REPEAT
- Emit `ops/reports/devika_pi_policy_report.json`

## Phase C Devika Runtime Profile

### C1 Agent identity package
- Create `agents/devika/config.json`
- Create `agents/devika/system_prompt.md`
- Create `agents/devika/pi/profile.json`

### C2 PI extension pack
- Task loop extension
- Subagent orchestration extension
- Safe command policy extension
- Status and progress extension

## Phase D Context7 MCP Integration

### D1 MCP wiring
- Add Context7 server config under `archonx/config/mcp/`
- Add Devika policy binding for docs lookup requirements

### D2 Pre-code docs contract
- Resolve library id
- Fetch docs
- Store reference metadata in run context
- Fallback behavior when unavailable

## Phase E Dashboard and API Contract

### E1 Frontend contract
- Replace hardcoded `model_id` request behavior with profile selector
- Add execution profile and governance stage status UI

### E2 Backend route
- Add PI-aware execution path
- Route profile and policy options to wrapper
- Persist profile and stage metadata in run logs

## Phase F Gap Closure and Validation

### F1 Gap closure
- Work through [`DEVIKA_PI_GAP_MATRIX.md`](./DEVIKA_PI_GAP_MATRIX.md)
- Close critical and high-severity items first

### F2 Validation gates
- Install gate
- Policy gate
- Context7 gate
- Verification and report gate

## Phase G Handoff Boundary for King Mode

### G1 Non-King completion packet
- Confirm all non-King objectives are complete
- Publish readiness report for Gemini handoff

### G2 King handoff package
- Strict build prompt
- PRD boundary
- Context bundle and interface contracts

## Release Criteria

- Devika executes via PI profile, not hardcoded model selection
- Governance wrapper blocks non-compliant operations
- Context7 docs checks are enforced and logged
- Verification and report output run at each completion boundary
- King Mode handoff package is complete and scoped for Gemini 3.1

