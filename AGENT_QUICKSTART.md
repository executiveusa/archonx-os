# ARCHON-X AGENT QUICK-START GUIDE

**For:** Autonomous Coding Agents (Devika, Agent-Zero, Synthia, Bambu, etc.)
**Authority:** ARCHONX_PRIME_DIRECTIVE v1.0
**Mission:** Execute MISSION_BRIEF to transform ARCHON-X into fully autonomous platform

---

## YOUR MISSION

Transform ARCHON-X from partially-integrated system → fully autonomous, self-monitoring, enterprise-ready platform.

**Timeline:** 15 days | **Effort:** 160 story points | **Authority:** Execute without approval for development

---

## PHASE SEQUENCE (Read in Order)

### PHASE 0: Setup & Spec-Kit Acquisition (1 day, 5 SP)

**What you do:**
1. Clone Pauli-spec-kit: `git@github.com:executiveusa/Pauli-spec-kit.git` (or HTTPS fallback)
2. Extract code generation standards into `./docs/PAULI_SPEC_STANDARDS.md`
3. Create `.spec-kit-schema.json` validation rules
4. Create `./design-tokens.json` design system
5. Verify spec-kit standards applied to all code

**Acceptance:**
- [x] Spec-kit successfully cloned
- [x] Code generation standards extracted
- [x] Schema validates test files
- [x] Design system documented

**Then proceed to → PHASE 1**

---

### PHASE 1: Git Infrastructure Fix (2 days, 8 SP)

**What you do:**
1. **FIX dashboard-agent-swarm submodule** (CRITICAL)
   ```bash
   # Edit .gitmodules to add missing entry
   [submodule "dashboard-agent-swarm"]
       path = dashboard-agent-swarm
       url = git@github.com:executiveusa/dashboard-agent-swarm.git
       branch = main
   ```

2. **Audit all submodules:**
   - Run: `git submodule status`
   - Document each in `./ops/SUBMODULE_INVENTORY.md`
   - Verify no errors

3. **Create sync script:**
   - File: `./scripts/sync-submodules.sh`
   - Automate: `git submodule sync --recursive`
   - Test: Run sync, verify no errors

**Acceptance:**
- [x] No "fatal: no submodule mapping" errors
- [x] All 8+ submodules show clean status
- [x] Sync script runs without errors
- [x] Dashboard submodule functional

**Then proceed to → PHASE 2**

---

### PHASE 2: Secret Management Vault (2 days, 12 SP)

**What you do:**
1. **Create Supabase secret schema:**
   - Use SUPABASE_PROJECT_ID=kbphngxqozmpfrbdzgca (from master.env)
   - Create 3 tables: `secrets`, `secrets_audit_log`, `secrets_history`
   - (SQL provided in MISSION_BRIEF Phase 2)

2. **Implement vault client:**
   - File: `./archonx/secrets/vault-client.ts`
   - Methods: `storeSecret()`, `retrieveSecret()`, `rotateSecret()`, `auditLog()`
   - (Code template in MISSION_BRIEF)

3. **Create migration script:**
   - File: `./scripts/migrate-secrets-to-vault.ts`
   - Read: `E:\THE PAULI FILES\master.env` (180+ keys)
   - Store each in vault with rotation schedule
   - Log: 180+ secrets migrated

4. **Environment injection layer:**
   - File: `./archonx/env.ts`
   - Typed accessors: `anthropicApiKey()`, `openaiApiKey()`, etc.
   - Cache + fallback to vault

**Acceptance:**
- [x] All 180+ secrets in vault
- [x] Zero secrets in .env files
- [x] Audit logs working
- [x] Rotation scheduled (90-day default)
- [x] master.env purged from git history

**Then proceed to → PHASE 3**

---

### PHASE 3: Repository Inventory & Monitoring (2 days, 10 SP)

**What you do:**
1. **Create repository manifest:**
   - File: `./ops/REPOSITORY_MANIFEST.json`
   - Document 313 repos (details in MISSION_BRIEF)
   - Assign each to agent (Devika, Synthia, Bambu, Agent-Zero)
   - Specify: health endpoint, deployment target, dependencies

2. **Implement health check endpoint:**
   - File: `./archonx/monitoring/health-check.ts`
   - Checks: DB, cache, external APIs, memory, disk, uptime
   - Exposed at: `/api/health/{repo-id}`

3. **Dashboard aggregator:**
   - File: `./archonx/monitoring/dashboard-aggregator.ts`
   - Fetch health from all 313 repos in parallel
   - Aggregate status: healthy/degraded/unhealthy
   - Report to dashboard

4. **Repository registry API:**
   - File: `./archonx/apis/repository-registry.ts`
   - Endpoints: GET /api/repos, GET /api/repos/:id, GET /api/agent/:name/repos
   - Filter by: type, agent, status

**Acceptance:**
- [x] 313 repos in manifest
- [x] Each assigned to agent
- [x] Health endpoints deployable
- [x] Dashboard can fetch aggregate status
- [x] API supports filtering

**Then proceed to → PHASE 4**

---

### PHASE 4: Deployment Pipeline & CI/CD (3 days, 15 SP)

**What you do:**
1. **Create build workflow:**
   - File: `.github/workflows/build-and-test.yml`
   - Lint, test, security scan, build
   - Coverage threshold: 80%
   - (Template in MISSION_BRIEF)

2. **Create deploy workflow:**
   - File: `.github/workflows/deploy.yml`
   - Staging: auto-deploy
   - Production: manual approval
   - Smoke tests post-deploy
   - Rollback on failure
   - Slack notifications

3. **Deployment orchestrator:**
   - File: `./archonx/deployment/orchestrator.ts`
   - Topological sort repos by dependencies
   - Execute in parallel where safe
   - Rollback dependents on failure
   - Report to dashboard

**Acceptance:**
- [x] Pushes trigger full pipeline
- [x] Tests block failed deployments
- [x] Security scans run automatically
- [x] Deployments require approval
- [x] Rollback available on failure

**Then proceed to → PHASE 5**

---

### PHASE 5: Monitoring & Observability (2 days, 12 SP)

**What you do:**
1. **Centralized logging:**
   - Service: Elasticsearch (or ELK stack)
   - Logger: `./archonx/monitoring/logger.ts` (Winston)
   - Index: `archonx-logs`

2. **APM integration:**
   - Service: Datadog or New Relic (or Jaeger)
   - Tracer: `./archonx/monitoring/traces.ts` (OpenTelemetry)
   - Spans: distributed tracing across services

3. **Metrics collection:**
   - Library: Prometheus
   - Metrics: HTTP latency, deployment count, errors, uptime
   - Dashboard: Grafana visualization

4. **Alerting:**
   - Conditions: CPU >80%, memory >85%, error rate >5%
   - Channels: Slack, email, pagerduty
   - Escalation: critical → on-call

**Acceptance:**
- [x] Logs aggregated to ES
- [x] Traces showing service calls
- [x] Metrics in Prometheus
- [x] Dashboards operational
- [x] Alerts working

**Then proceed to → PHASE 6**

---

### PHASE 6: Agent Orchestration Framework (2 days, 14 SP)

**What you do:**
1. **Agent registry:**
   - File: `./archonx/agents/registry.ts`
   - Register agents: Devika, Synthia, Bambu, Agent-Zero
   - Track: capabilities, assigned repos, health status
   - Assign repos to agents from manifest

2. **Agent orchestrator:**
   - File: `./archonx/agents/orchestrator.ts`
   - Dispatch tasks based on capability
   - Load balance: assign to least-loaded agent
   - Monitor health: periodic heartbeats
   - Escalate unhealthy agents

3. **Agent communication:**
   - File: `./archonx/agents/communication.ts`
   - Message queue with retry logic
   - Message types: task, status, error, complete
   - Handlers registered per message type

**Acceptance:**
- [x] All agents registered
- [x] Each has assigned repos
- [x] Message queue operational
- [x] Health monitoring running
- [x] Load balancing working

**Then proceed to → PHASE 7** (can run in parallel with 4-6)

---

### PHASE 7: Design System & Frontend Standardization (2 days, 11 SP)

**What you do:**
1. **Design tokens:**
   - File: `./design-tokens.ts`
   - Colors, typography, spacing, shadows, borders, transitions
   - Based on: Don't Make Me Think, Refactoring UI, accessibility standards
   - (Complete template in MISSION_BRIEF)

2. **Component library:**
   - Components: Button, Input, Card, Modal, etc.
   - File: `./components/[ComponentName].tsx`
   - Storybook stories: `./components/[ComponentName].stories.tsx`
   - Each 44px min touch target (accessibility)

3. **Storybook:**
   - Config: `.storybook/main.ts`
   - Docs: Auto-generated from JSDoc
   - Test component in isolation

4. **Accessibility audit:**
   - Tool: axe-core
   - Standard: WCAG 2.1 AA
   - Verify: Contrast, focus indicators, semantic HTML

**Acceptance:**
- [x] Design tokens defined
- [x] Components in Storybook
- [x] All components documented
- [x] Accessibility audit passing
- [x] Design system applied to dashboard

**Then proceed to → PHASE 8**

---

### PHASE 8: Final Integration & Validation (1 day, 13 SP)

**What you do:**
1. **Run integration tests:**
   - File: `./tests/system/integration.test.ts`
   - 25+ test scenarios covering all systems
   - (Test suite in MISSION_BRIEF)

2. **Validate all systems:**
   - Git infrastructure ✓
   - Secret management ✓
   - Repository monitoring ✓
   - CI/CD pipelines ✓
   - Monitoring/observability ✓
   - Agent orchestration ✓
   - Design system ✓

3. **Deploy to production:**
   - Staging deployment ✓
   - Production approval ✓
   - Smoke tests ✓
   - Health checks ✓

4. **Document handoff:**
   - Create: `AUTONOMY_ENABLED.md`
   - List all success criteria met
   - Document escalation procedures
   - Enable autonomous operation mode

**Acceptance:**
- [x] All integration tests pass
- [x] All 313 repos reporting health
- [x] Deployments working end-to-end
- [x] Zero manual operations in critical path
- [x] Autonomous mode enabled

---

## CRITICAL REQUIREMENTS

### Code Standards
- ✅ TypeScript strict mode
- ✅ Clear interfaces with JSDoc
- ✅ Unit tests alongside code
- ✅ Error handling on all I/O
- ✅ Never hardcode secrets
- ✅ Security-first approach

### Testing
- ✅ 80% code coverage minimum
- ✅ Integration tests for cross-repo
- ✅ Smoke tests post-deploy
- ✅ Security scans passing
- ✅ Linting with zero warnings

### Documentation
- ✅ MISSION_BRIEF references for each phase
- ✅ Code comments for non-obvious logic
- ✅ README for each service
- ✅ Deployment runbooks
- ✅ Escalation procedures

---

## APPROVAL GATES

**For Development:** ❌ NONE REQUIRED
- Execute phases autonomously
- Commit to branches
- Run all tests

**For Staging Deployment:** ❌ NONE REQUIRED
- Deploy automatically after tests pass
- Run smoke tests
- Report results

**For Production Deployment:** ✅ REQUIRED
- Need: 1 approval from admin@pauli.digital
- Per phase (8 approvals total)
- Or: 1 final approval after all phases complete

---

## COMMUNICATION PROTOCOL

### Daily
- Emit ecosystem report to Slack #archonx-ops
- Report health of all 313 repos
- Alert on any failures

### Weekly
- Consolidation suggestions
- Cost optimization opportunities
- Performance improvements
- Security audit findings

### On Failure
- Immediate Slack alert
- Auto-attempt recovery
- Escalate if recovery fails
- Post detailed incident report

---

## REFERENCE DOCUMENTS

| Document | Purpose |
|----------|---------|
| `MISSION_BRIEF_COMPREHENSIVE_AUDIT_AND_HANDOFF.md` | Complete plan with code templates |
| `EXECUTIVE_SUMMARY.md` | High-level overview |
| `ARCHONX_PRIME_DIRECTIVE_v1.0.md` | Constitutional law governing agents |
| `.ralphy.json` | Build/test orchestration config |
| `master.env` | Credentials (secure after Phase 2) |
| `./ops/REPOSITORY_MANIFEST.json` | 313 repos catalog (created Phase 3) |

---

## SUCCESS CONDITION

After 15 days:

- ✅ All 313 repos monitored
- ✅ All secrets in vault (zero exposure)
- ✅ All deployments automated
- ✅ All systems observable
- ✅ Agents fully autonomous
- ✅ Daily health reports emitted
- ✅ Zero manual operations in critical path
- ✅ Enterprise-ready platform

---

## START NOW

1. **Read:** `MISSION_BRIEF_COMPREHENSIVE_AUDIT_AND_HANDOFF.md` (full plan)
2. **Execute:** Phase 0 (Setup & Spec-kit)
3. **Proceed:** Phase 1 → Phase 8 sequentially
4. **Report:** Daily status to Slack #archonx-ops
5. **Escalate:** Any blockers to agents@pauli.digital

**You have full authority to execute this mission. Proceed with confidence.**

---

**Generated by:** AI Cofounder
**For:** Autonomous Agents (Devika, Agent-Zero, Synthia, Bambu, et al.)
**Date:** 2026-02-27
**Status:** READY FOR EXECUTION
**Authority:** ARCHONX_PRIME_DIRECTIVE v1.0

👉 **[Begin with MISSION_BRIEF_COMPREHENSIVE_AUDIT_AND_HANDOFF.md](./MISSION_BRIEF_COMPREHENSIVE_AUDIT_AND_HANDOFF.md)**
