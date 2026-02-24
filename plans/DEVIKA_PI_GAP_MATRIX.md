# Devika on PI Gap Matrix

## Baseline

- Devika UI endpoint wiring exists in [`DevikaAgent.tsx`](../dashboard-agent-swarm/src/pages/DevikaAgent.tsx)
- Generic runtime route exists in [`agents.ts`](../dashboard-agent-swarm/server/routes/agents.ts)
- Darya has rich agent identity and prompt files under [`agents/darya`](../agents/darya)
- King Mode handoff PRD exists in [`KING_MODE_GEMINI_31_PRD.md`](./KING_MODE_GEMINI_31_PRD.md)

## Gap Table

| ID | Area | Current State | Target State | Severity | Owner | Closure Criteria |
|---|---|---|---|---|---|---|
| GAP-PI-001 | Install | No standardized PI bootstrap in repo | Reproducible install scripts and version checks | High | Platform | Install scripts pass and produce report |
| GAP-PI-002 | Runtime Contract | UI hardcodes model id | UI sends execution profile | High | Dashboard | `executionProfile` used end to end |
| GAP-PI-003 | API Route | Generic route, no PI profile routing | PI-aware route with wrapper invocation | High | Backend | Route dispatches profile to PI wrapper |
| GAP-PI-004 | Agent Identity | Devika not codified like Darya | `agents/devika` identity, config, prompt, PI profile | High | Agent Ops | Devika config and prompt files present |
| GAP-PI-005 | Governance | No PI command policy gate | PAULIWHEEL and bead guard wrapper | Critical | Security | Unsafe command blocked and logged |
| GAP-PI-006 | Observability | No PI-specific telemetry phases | PI stage telemetry and machine-readable reports | High | Observability | Reports emitted under `ops/reports` |
| GAP-PI-007 | Context7 | No mandatory pre-code docs resolution | Context7 resolve and docs retrieval in loop | High | Tooling | Context7 calls visible in logs |
| GAP-PI-008 | Extension Pack | No Devika PI extension bundle | Task loop, subagents, status widget, safe commands | Medium | Agent Runtime | Extension pack loaded and tested |
| GAP-PI-009 | Verification | `archonx-ops doctor` not integrated in Devika path | Verification gate integrated before completion | High | Platform | Verification stage blocks on failure |
| GAP-PI-010 | Rollback | No PI cutover rollback plan | Documented fallback to existing runtime | Medium | Release | Rollback steps tested in staging |

## Priority Order

1. GAP-PI-005 Governance
2. GAP-PI-001 Install
3. GAP-PI-002 Contract
4. GAP-PI-003 API routing
5. GAP-PI-004 Devika identity
6. GAP-PI-006 Observability
7. GAP-PI-007 Context7
8. GAP-PI-008 Extension pack
9. GAP-PI-009 Verification
10. GAP-PI-010 Rollback

## Acceptance Checklist

- [ ] PI install is deterministic on target machines
- [ ] Devika executes by profile, not hardcoded model
- [ ] Bead id is mandatory for code-affecting operations
- [ ] Unsafe shell commands are denied with structured errors
- [ ] Context7 docs checks occur before third-party API calls
- [ ] `archonx-ops doctor` stage is included in completion gate
- [ ] Reports are emitted to `ops/reports/`
- [ ] Rollback route is validated

