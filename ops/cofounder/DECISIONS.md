# Decisions Log

## 2026-02-23

### D-001
- Decision: Treat `archonx-os` as the single control plane.
- Why: Reduces orchestration drift and duplicated governance.
- Impact: All repo automation routes through one policy surface.
- Revisit: 2026-03-23

### D-002
- Decision: Enforce seven-phase loop for major platform changes.
- Why: Keeps execution measurable and recoverable.
- Impact: Better reliability and fewer unbounded changes.
- Revisit: 2026-03-01

### D-003
- Decision: Keep `Pauli Effect` as a bounded subsystem, not full mission scope.
- Why: Prevents identity scope creep and preserves portfolio flexibility.
- Impact: Cleaner domain boundaries in prompt registry.
- Revisit: 2026-03-15
