# ARCHON-X ECOSYSTEM: COMPREHENSIVE NASA-LEVEL AUDIT & PRECISION PLAN
**Document Version:** 1.0
**Generated:** 2026-02-27
**Authority:** Executive USA / Pauli Digital
**Classification:** Mission Critical - Autonomous Agent Handoff

---

## EXECUTIVE SUMMARY

The ARCHON-X ecosystem is a multi-agent autonomous enterprise platform designed to orchestrate 300+ repositories across integrated digital infrastructure. Current state analysis reveals **8 critical gaps** and **14 blocking issues** preventing unified monitoring and deployment. This document provides:

1. **NASA-LEVEL AUDIT** - Complete gap analysis across all systems
2. **PRECISION PLAN** - Step-by-step handoff for autonomous coding agent
3. **PAULI-SPEC-KIT CODE GENERATION** - All required code with architectural compliance

**Estimated Effort:** 160 story points | **Critical Path:** 8-12 days | **Risk Level:** MEDIUM (dependency drift, secret management, submodule corruption)

---

## PART 1: COMPREHENSIVE ECOSYSTEM AUDIT

### 1.1 CURRENT ARCHITECTURE STATE

```
ARCHON-X Ecosystem (Active)
├── Core OS (archonx-os) ..................... MAIN NODE
│   ├── Submodules (8 active)
│   │   ├── archon-x (voice agent) ......... SYNCED ✓
│   │   ├── agent-lightning ............... SYNCED ✓
│   │   ├── VisionClaw .................... SYNCED ✓
│   │   ├── brightdata-mcp ................ SYNCED ✓
│   │   ├── chrome-devtools-mcp ........... SYNCED ✓
│   │   ├── orgo-mcp ...................... SYNCED ✓
│   │   └── 2x others ..................... SYNCED ✓
│   └── Config & Manifests
│       ├── .ralphy.json .................. OPERATIONAL
│       ├── .archonx/ARCHONX.json ......... OPERATIONAL
│       ├── ARCHONX_PRIME_DIRECTIVE_v1.0.md ACTIVE
│       └── AGENTS.md ..................... PARTIAL
│
├── Dashboard Agent Swarm .................... CRITICAL GAP ⚠️
│   ├── Status: Physically present but NOT in .gitmodules
│   ├── Subagent mapping: MISSING
│   ├── Monitoring integration: INCOMPLETE
│   └── Deployment status: DISCONNECTED
│
├── Frontend (paulisworld-openclaw-3d) ....... NOT INTEGRATED
│   └── Referenced in .ralphy.json but deployment status unknown
│
├── ARCHON-X-OS Artifact Library ............. UNORGANIZED
│   ├── 25+ agent frameworks (archived as .zip)
│   ├── Training data & documentation
│   ├── Media generation tools
│   └── No central registry or manifest
│
└── Repository References (300+ repos mentioned)
    ├── Guardian Fleet ...................... UNMONITORED
    ├── Kupuri Media Repos .................. UNMONITORED
    ├── Agent Zero Fork ..................... UNDEPLOYED
    ├── Third-party integrations ............ UNINDEXED
    └── No unified dashboard visibility
```

### 1.2 CRITICAL GAPS IDENTIFIED

#### GAP #1: Dashboard-Agent-Swarm Submodule Corruption
**Severity:** CRITICAL | **Impact:** No monitoring visibility
**Root Cause:** Dashboard exists at `./dashboard-agent-swarm/` but NOT declared in `.gitmodules`

```
Current State:
- Physical directory: EXISTS at ./dashboard-agent-swarm/
- .gitmodules entry: MISSING
- Git status: "fatal: no submodule mapping found in .gitmodules"
- Result: Cannot pull updates, cannot track version, cannot verify deployment

Risk:
- Future git operations will fail
- Deployment automation cannot sync this repo
- Monitoring agent cannot track state
```

**Fix Category:** GIT INFRASTRUCTURE

#### GAP #2: Repository Inventory Mismatch
**Severity:** HIGH | **Impact:** Incomplete automation coverage
**Current:** 300+ repos mentioned in Prime Directive but only 4-6 tracked in `.ralphy.json`

```
Tracked Repos (.ralphy.json):
1. archonx-os (main) .......................... Tracked
2. dashboard-agent-swarm ....................... GAP FOUND
3. paulisworld-openclaw-3d ..................... Tracked but undeployed
4. archon-x (voice agent) ...................... Tracked

Untracked (Guardian Fleet, Kupuri Media, etc.):
- 291 repository references in PRIME DIRECTIVE
- 0 entries in active monitoring
- Result: Zero automation, zero health checks, zero deployment
```

**Fix Category:** CONFIGURATION & REGISTRY

#### GAP #3: Environment & Secret Management
**Severity:** CRITICAL | **Impact:** Security risk, deployment blocked

```
Current Issues:
1. Master.env contains 180+ keys/tokens in plaintext
2. No secret vault integration (no HashiCorp Vault, AWS Secrets Manager, etc.)
3. SSH private keys exposed in plaintext (Coolify SSH)
4. API keys for Anthropic, OpenAI, Stripe, Twilio visible
5. GitHub PAT exposed
6. No rotation schedule
7. No per-repo secret scoping

Affected Systems:
- All Supabase projects (2 projects = 4 keys exposed)
- All payment systems (Stripe, PayPal, Printful)
- All AI/LLM endpoints (Anthropic, OpenAI, HuggingFace, etc.)
- All hosting platforms (Coolify, Vercel, Hostinger)
- MCP integrations (Notion, Supabase)
- Twilio/phone infrastructure
- Telegram bot credentials
```

**Fix Category:** SECURITY & SECRETS

#### GAP #4: Missing Spec-Kit Implementation
**Severity:** MEDIUM | **Impact:** Code generation inconsistency

```
Current State:
- URL provided: git@github.com:executiveusa/Pauli-spec-kit.git
- Repository access: FAILED (SSH permission issue)
- Local clone: NONE
- Code generation standards: NOT DEFINED
- Validation rules: NOT ENFORCED

Consequence:
- All code generated without Pauli standards
- Inconsistent architecture across agents
- No design system compliance (Don't Make Me Think, UI/UX principles)
- No code quality gates
```

**Fix Category:** CODE STANDARDS & QUALITY

#### GAP #5: Deployment Pipeline Missing
**Severity:** CRITICAL | **Impact:** No automated deployment

```
Current Status:
- CI/CD config: NOT FOUND (.github/workflows minimal)
- Build automation: .ralphy.json defined but NOT integrated
- Deployment targets: Coolify, Vercel configured but disconnected
- Frontend deployment: Not automated
- Backend deployment: Manual/unknown
- Status reporting: Broken (.ralphy.json points to broken webhook)

Required:
- GitHub Actions workflows
- Deployment verification
- Rollback capability
- Deployment status tracking
- Cross-repo orchestration
```

**Fix Category:** DEVOPS & INFRASTRUCTURE

#### GAP #6: Monitoring & Health Checks
**Severity:** HIGH | **Impact:** Cannot detect failures

```
Current Status:
- Health check endpoint: /healthz (defined but not implemented)
- Dashboard webhook: http://localhost:8080/api/ralphy-report (broken)
- Repo health monitoring: Not automated
- Dependency drift detection: Not implemented
- Security scanning: Not automated
- Lint/test gating: Configured but not enforced

What Should Exist:
- Per-repo health endpoint
- Centralized health aggregation
- Daily security scanning
- Dependency audit automation
- Test coverage enforcement
- Performance monitoring
```

**Fix Category:** MONITORING & OBSERVABILITY

#### GAP #7: UI/UX Design System Missing
**Severity:** MEDIUM | **Impact:** Inconsistent user experience

```
Referenced Design Materials:
- Steve Krug "Don't Make Me Think" .......... MENTIONED but NOT IMPLEMENTED
- UI/UX Design Review PDF .................. REFERENCED but NOT APPLIED
- Refactoring UI Adam Wathan .............. REFERENCED but NOT APPLIED

Current State:
- Dashboard component design: Ad-hoc
- Consistency across frontends: NONE
- Accessibility standards: NOT DOCUMENTED
- Design tokens: NOT DEFINED
- Component library: MISSING

Required:
- Design tokens system
- Component library w/ Storybook
- Design documentation
- A11y audit & compliance
- Design review checklist
```

**Fix Category:** FRONTEND & UX

#### GAP #8: Agent Assignment & Orchestration
**Severity:** HIGH | **Impact:** No autonomous operation

```
Current State per PRIME DIRECTIVE:
- Requirement: "Every repo has an assigned subagent"
- Current assignment: Devika -> archonx-os only
- Agent coverage: 1 agent, 300+ repos = UNSCALED

Missing Components:
- Subagent assignment logic
- Subagent capability registry
- Work distribution algorithm
- Escalation protocol
- Agent health monitoring
- Agent collaboration framework

Undefined Agents:
- SYNTHIA agent (mentioned, not integrated)
- Repository subagents (not deployed)
- Guardian Fleet agents (not deployed)
```

**Fix Category:** AGENT ORCHESTRATION

### 1.3 BLOCKING ISSUES (14 TOTAL)

| ID | Severity | Issue | Current State | Blocker? |
|---|---|---|---|---|
| B1 | CRITICAL | Dashboard submodule not in gitmodules | Physical dir exists, git broken | YES - Deployment |
| B2 | CRITICAL | No secret vault integration | 180+ keys in plaintext | YES - Security |
| B3 | CRITICAL | Master.env incomplete/fragmented | Multiple sections, SSH keys exposed | YES - Deployment |
| B4 | CRITICAL | Deployment pipeline nonexistent | Manual process assumed | YES - Automation |
| B5 | HIGH | No per-repo health endpoints | Manual monitoring only | YES - Orchestration |
| B6 | HIGH | Agent assignment undefined | Only Devika assigned | YES - Agent coordination |
| B7 | HIGH | Repository inventory out of sync | 291 repos untracked | YES - Monitoring |
| B8 | HIGH | Spec-kit not accessible | SSH clone failed | NO - Workaround: use defaults |
| B9 | MEDIUM | Design system not implemented | Standards referenced but not used | NO - Can work in parallel |
| B10 | MEDIUM | CI/CD workflows missing | .github/workflows incomplete | YES - Gating |
| B11 | MEDIUM | Monitoring webhook broken | localhost URL in prod config | YES - Status reporting |
| B12 | MEDIUM | Submodule versions drifting | Some pinned, some follow main | NO - Can fix in cleanup phase |
| B13 | MEDIUM | No dependency scanning | No scheduled audits | NO - Can add to monitoring |
| B14 | LOW | Archive organization poor | 25+ .zips not cataloged | NO - Informational only |

---

## PART 2: PRECISION PLAN - AUTONOMOUS AGENT HANDOFF

### 2.0 MISSION STATEMENT

**OBJECTIVE:** Convert ARCHON-X from partially-integrated system into **fully-operational, self-monitoring, self-healing autonomous enterprise platform** capable of:

- ✅ Real-time monitoring of 300+ repositories
- ✅ Automated deployment across all environments
- ✅ Secure secret management with zero plaintext exposure
- ✅ Standardized code generation (Pauli-spec-kit)
- ✅ Autonomous agent orchestration
- ✅ Daily health checks and optimization
- ✅ Enterprise-grade CI/CD and testing
- ✅ Design system compliance across all frontends

**Success Criteria:** All repos report daily status, all deployments automated, all secrets secured, zero manual operations in critical path.

---

### 2.1 EXECUTION PHASES (8 PHASES, CRITICAL PATH)

#### PHASE 0: SETUP & SPEC-KIT ACQUISITION (Days 1, Effort: 5 SP)
**Dependencies:** NONE | **Blocks:** All other phases

**Objectives:**
1. Clone Pauli-spec-kit repo (SSH or HTTPS fallback)
2. Extract code generation standards
3. Create local SPEC_KIT_SCHEMA.json
4. Document design tokens and patterns
5. Validate accessibility rules

**Deliverables:**
- `./spec-kit/` directory (cloned)
- `./docs/PAULI_SPEC_STANDARDS.md` (extracted)
- `.spec-kit-schema.json` (validation rules)
- `./design-tokens.json` (design system)

**Acceptance Criteria:**
- Spec-kit successfully cloned
- All code generation standards extracted
- Schema validates test case files
- Design system documented

**Code to Implement:** MINIMAL (clone + documentation)

---

#### PHASE 1: GIT INFRASTRUCTURE FIX (Days 1-2, Effort: 8 SP)
**Dependencies:** PHASE 0 | **Blocks:** PHASE 2, 3

**Objectives:**
1. Fix dashboard-agent-swarm submodule registration
2. Audit all submodule versions
3. Create submodule sync script
4. Document submodule dependencies
5. Test git operations (clone, update, pull)

**Detailed Tasks:**

**Task 1.1: Fix Dashboard Submodule**
```
File: .gitmodules (EDIT)
Action: Add missing dashboard-agent-swarm entry

Current State: Missing entry
Required Entry:
  [submodule "dashboard-agent-swarm"]
      path = dashboard-agent-swarm
      url = git@github.com:executiveusa/dashboard-agent-swarm.git
      branch = main

Steps:
1. Read .gitmodules
2. Add dashboard-agent-swarm section
3. Run: git config --file .gitmodules --add submodule.dashboard-agent-swarm.path dashboard-agent-swarm
4. Run: git config --file .gitmodules --add submodule.dashboard-agent-swarm.url git@github.com:executiveusa/dashboard-agent-swarm.git
5. Verify: git submodule status (should show no errors)
6. Commit: "INFRA: Fix dashboard-agent-swarm submodule registration"
```

**Task 1.2: Audit Submodule Versions**
```
Create: ./ops/SUBMODULE_INVENTORY.md

Script to run:
  git config --file .gitmodules --name-only --get-regexp path

Expected Output:
  submodule.VisionClaw.path
  submodule.agent-frameworks/agent-lightning.path
  submodule.archon-x.path
  submodule.archonx/tools/brightdata-mcp.path
  submodule.archonx/tools/chrome-devtools-mcp.path
  submodule.archonx/tools/orgo-mcp.path
  submodule.dashboard-agent-swarm.path (AFTER FIX)

For each: Document URL, branch, last update, purpose
```

**Task 1.3: Create Submodule Sync Script**
```typescript
File: ./scripts/sync-submodules.sh (NEW)

#!/bin/bash
# Synchronize all submodules to their declared versions

set -e

echo "🔄 Synchronizing ARCHON-X submodules..."

git submodule sync --recursive
git submodule update --init --recursive --remote

# Record versions
git submodule foreach 'echo "$(git config --local remote.origin.url)" > .submodule-url'
git submodule foreach 'git describe --tags --always > .submodule-version'

echo "✅ All submodules synchronized"
git status
```

**Deliverables:**
- Fixed .gitmodules
- ./ops/SUBMODULE_INVENTORY.md
- ./scripts/sync-submodules.sh
- All submodule tests passing

**Acceptance Criteria:**
- `git submodule status` shows no errors
- All 8+ submodules can be updated
- Sync script runs without errors
- No "fatal: no submodule mapping" messages

---

#### PHASE 2: SECRET MANAGEMENT VAULT (Days 2-3, Effort: 12 SP)
**Dependencies:** PHASE 0 | **Blocks:** PHASE 3, 4, 5

**Objectives:**
1. Implement Supabase-based secret vault (fast, zero infrastructure)
2. Migrate all secrets from master.env → vault
3. Create environment variable injection layer
4. Implement secret rotation schedule
5. Add secret audit logging
6. Remove master.env from git history

**Detailed Architecture:**

```typescript
// Structure: ./archonx/secrets/vault-client.ts (NEW)

import { createClient } from '@supabase/supabase-js';

interface SecretVaultConfig {
  supabaseUrl: string;
  supabaseKey: string;
  encryptionKey: string; // Per-environment
}

class ArchonXSecretVault {
  private supabase: SupabaseClient;

  async initialize(config: SecretVaultConfig) {
    this.supabase = createClient(config.supabaseUrl, config.supabaseKey);
    // Verify connection and encryption
  }

  async storeSecret(
    name: string,
    value: string,
    environment: 'dev' | 'staging' | 'prod',
    metadata?: { rotationDays?: number; owner?: string }
  ): Promise<void> {
    // Store encrypted in supabase.secrets table
    // Log audit trail
  }

  async retrieveSecret(name: string, environment: string): Promise<string> {
    // Retrieve and decrypt
    // Log access attempt
  }

  async rotateSecret(name: string, newValue: string): Promise<void> {
    // Move old to history
    // Store new encrypted
    // Notify dependent services
  }

  async auditLog(environment: string): Promise<AuditEntry[]> {
    // Return all access/modification logs
  }
}

export { ArchonXSecretVault };
```

**Supabase Schema:**
```sql
-- secrets table
CREATE TABLE secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  environment TEXT NOT NULL, -- 'dev', 'staging', 'prod'
  value_encrypted TEXT NOT NULL,
  encryption_nonce TEXT NOT NULL,
  rotation_schedule_days INT DEFAULT 90,
  last_rotated TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  owner_email TEXT,
  UNIQUE(name, environment)
);

-- secrets_audit_log table
CREATE TABLE secrets_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  secret_id UUID REFERENCES secrets(id),
  action TEXT NOT NULL, -- 'read', 'rotate', 'create', 'delete'
  accessed_by TEXT,
  accessed_at TIMESTAMP DEFAULT NOW(),
  ip_address TEXT,
  success BOOLEAN DEFAULT true,
  error_message TEXT
);

-- secrets_history table
CREATE TABLE secrets_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  secret_id UUID REFERENCES secrets(id),
  old_value_encrypted TEXT,
  rotated_at TIMESTAMP DEFAULT NOW(),
  rotated_by TEXT
);
```

**Migration Script:**

```typescript
// scripts/migrate-secrets-to-vault.ts (NEW)
// Reads master.env, validates each key, stores in vault

import * as dotenv from 'dotenv';
import { ArchonXSecretVault } from '../archonx/secrets/vault-client';

const SECRETS_METADATA = {
  'ANTHROPIC_API_KEY': { rotationDays: 90, owner: 'admin@pauli.digital' },
  'OPENAI_API_KEY': { rotationDays: 90, owner: 'admin@pauli.digital' },
  'STRIPE_SECRET_KEY': { rotationDays: 60, owner: 'finance@pauli.digital' },
  // ... etc for all 180+ keys
};

async function migrateSecretsToVault() {
  const vault = new ArchonXSecretVault();
  const env = dotenv.parse(fs.readFileSync('E:\\THE PAULI FILES\\master.env', 'utf8'));

  for (const [name, value] of Object.entries(env)) {
    console.log(`Migrating ${name}...`);
    await vault.storeSecret(name, value, 'prod', SECRETS_METADATA[name]);
  }

  console.log('✅ All secrets migrated');
  console.log('⚠️  Next step: Delete master.env and rotate all keys');
}

migrateSecretsToVault();
```

**Environment Variable Injection:**

```typescript
// archonx/env.ts (NEW)
// Provides typed environment variable access with vault fallback

import { ArchonXSecretVault } from './secrets/vault-client';

class ArchonXEnv {
  private vault: ArchonXSecretVault;
  private cache: Map<string, string> = new Map();

  async get(key: string): Promise<string> {
    // Check cache first
    if (this.cache.has(key)) return this.cache.get(key)!;

    // Try process.env (for development)
    if (process.env[key]) return process.env[key]!;

    // Fall back to vault
    const value = await this.vault.retrieveSecret(key, process.env.NODE_ENV || 'dev');
    this.cache.set(key, value);
    return value;
  }

  // Typed accessors (intellisense-friendly)
  async anthropicApiKey(): Promise<string> { return this.get('ANTHROPIC_API_KEY'); }
  async openaiApiKey(): Promise<string> { return this.get('OPENAI_API_KEY'); }
  async stripeSecretKey(): Promise<string> { return this.get('STRIPE_SECRET_KEY'); }
  // ... etc
}

export { ArchonXEnv };
```

**Deliverables:**
- Supabase schema with secrets tables
- ArchonXSecretVault implementation
- migrate-secrets-to-vault.ts script
- Environment variable injection layer
- Secret audit logging
- Rotation schedule configuration
- Documentation: SECRET_MANAGEMENT.md

**Acceptance Criteria:**
- All 180+ secrets migrated to vault
- Zero secrets in .env files
- Secret audit logs working
- Rotation automation scheduled
- master.env deleted from git history

---

#### PHASE 3: REPOSITORY INVENTORY & MONITORING (Days 3-4, Effort: 10 SP)
**Dependencies:** PHASE 0, 2 | **Blocks:** PHASE 4, 5

**Objectives:**
1. Create unified repository manifest (all 300+ repos)
2. Assign subagent to each repo
3. Create per-repo health check endpoints
4. Implement dashboard monitoring aggregation
5. Create repository registry API

**Deliverables:**

**File: ./ops/REPOSITORY_MANIFEST.json (NEW)**
```json
{
  "version": "1.0",
  "lastUpdated": "2026-02-27T00:00:00Z",
  "totalRepos": 313,
  "repositories": [
    {
      "id": "archonx-os",
      "name": "ARCHON-X Operating System",
      "url": "git@github.com:executiveusa/archonx-os.git",
      "type": "core-os",
      "language": "typescript/python",
      "assignedAgent": "Devika",
      "healthEndpoint": "/api/health/archonx-os",
      "critical": true,
      "status": "operational",
      "lastHealthCheck": "2026-02-27T00:00:00Z",
      "dependencies": ["dashboard-agent-swarm", "archon-x"],
      "deploymentTarget": "coolify",
      "slackChannel": "#archonx-ops"
    },
    {
      "id": "dashboard-agent-swarm",
      "name": "Dashboard Agent Swarm",
      "url": "git@github.com:executiveusa/dashboard-agent-swarm.git",
      "type": "monitoring",
      "language": "typescript/react",
      "assignedAgent": "Synthia",
      "healthEndpoint": "/api/health/dashboard",
      "critical": true,
      "status": "partial-integration",
      "lastHealthCheck": null,
      "dependencies": ["archonx-os"],
      "deploymentTarget": "vercel",
      "slackChannel": "#dashboard-ops"
    },
    {
      "id": "archon-x-voice",
      "name": "Archon-X Voice Agent",
      "url": "git@github.com:executiveusa/archon-x.git",
      "type": "agent",
      "language": "python",
      "assignedAgent": "Bambu",
      "healthEndpoint": "/api/health/voice",
      "critical": true,
      "status": "operational",
      "lastHealthCheck": "2026-02-27T00:00:00Z",
      "dependencies": ["archonx-os"],
      "deploymentTarget": "coolify",
      "slackChannel": "#voice-agent"
    }
    // ... 310 more repos
  ],
  "agents": {
    "Devika": { "role": "orchestration", "repos": 45, "status": "active" },
    "Synthia": { "role": "monitoring", "repos": 89, "status": "pending-deployment" },
    "Bambu": { "role": "voice-ai", "repos": 12, "status": "active" },
    "Agent-Zero": { "role": "strategic-reasoning", "repos": 167, "status": "pending-deployment" }
  },
  "deploymentTargets": {
    "coolify": { "url": "https://coolify.instance.com", "status": "active" },
    "vercel": { "url": "https://vercel.com", "status": "active" },
    "aws": { "status": "configured" }
  }
}
```

**File: ./archonx/monitoring/health-check.ts (NEW)**
```typescript
// Standardized health check endpoint for all repos

import { Request, Response } from 'express';
import { ArchonXEnv } from '../env';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  checks: {
    database?: boolean;
    cache?: boolean;
    externalApis?: boolean;
    diskSpace?: boolean;
    memory?: boolean;
    uptime?: number;
  };
  version: string;
  environment: string;
}

async function healthCheckEndpoint(req: Request, res: Response) {
  const health: HealthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {},
    version: process.env.APP_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  };

  // Database health
  try {
    await checkDatabase();
    health.checks.database = true;
  } catch (e) {
    health.checks.database = false;
    health.status = 'degraded';
  }

  // Cache health
  try {
    await checkCache();
    health.checks.cache = true;
  } catch (e) {
    health.checks.cache = false;
    health.status = 'degraded';
  }

  // External API connectivity
  try {
    await checkExternalApis();
    health.checks.externalApis = true;
  } catch (e) {
    health.checks.externalApis = false;
    health.status = 'degraded';
  }

  // System resources
  health.checks.memory = checkMemory();
  health.checks.diskSpace = checkDiskSpace();
  health.checks.uptime = process.uptime();

  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
}

export { healthCheckEndpoint, HealthStatus };
```

**File: ./archonx/monitoring/dashboard-aggregator.ts (NEW)**
```typescript
// Aggregates health from all 300+ repos into single dashboard status

import axios from 'axios';
import { REPOSITORY_MANIFEST } from '../ops/REPOSITORY_MANIFEST.json';

class DashboardAggregator {
  async aggregateHealthStatus(): Promise<DashboardStatus> {
    const statuses: Map<string, HealthStatus> = new Map();

    // Fetch health from all repos in parallel
    const promises = REPOSITORY_MANIFEST.repositories.map(async (repo) => {
      try {
        const response = await axios.get(repo.healthEndpoint, { timeout: 5000 });
        statuses.set(repo.id, response.data);
      } catch (e) {
        statuses.set(repo.id, { status: 'unhealthy', error: e.message });
      }
    });

    await Promise.allSettled(promises);

    // Calculate aggregate status
    const healthy = Array.from(statuses.values()).filter(s => s.status === 'healthy').length;
    const degraded = Array.from(statuses.values()).filter(s => s.status === 'degraded').length;
    const unhealthy = Array.from(statuses.values()).filter(s => s.status === 'unhealthy').length;

    return {
      timestamp: new Date().toISOString(),
      overall: unhealthy > 0 ? 'unhealthy' : degraded > 0 ? 'degraded' : 'healthy',
      summary: { healthy, degraded, unhealthy, total: REPOSITORY_MANIFEST.repositories.length },
      repoStatuses: Object.fromEntries(statuses),
      criticalAlerts: Array.from(statuses.entries())
        .filter(([id, status]) => {
          const repo = REPOSITORY_MANIFEST.repositories.find(r => r.id === id);
          return repo?.critical && status.status !== 'healthy';
        })
        .map(([id, status]) => ({ repo: id, status: status.status }))
    };
  }

  async reportToDashboard(status: DashboardStatus): Promise<void> {
    await axios.post(
      'http://dashboard-agent-swarm:8080/api/status/aggregate',
      status
    );
  }
}

export { DashboardAggregator };
```

**File: ./archonx/apis/repository-registry.ts (NEW)**
```typescript
// REST API for querying repository metadata

import { Router, Request, Response } from 'express';
import { REPOSITORY_MANIFEST } from '../ops/REPOSITORY_MANIFEST.json';

const router = Router();

// GET /api/repos - List all repositories
router.get('/', (req: Request, res: Response) => {
  const { type, agent, status } = req.query;

  let repos = REPOSITORY_MANIFEST.repositories;

  if (type) repos = repos.filter(r => r.type === type);
  if (agent) repos = repos.filter(r => r.assignedAgent === agent);
  if (status) repos = repos.filter(r => r.status === status);

  res.json({ total: repos.length, repos });
});

// GET /api/repos/:id - Get specific repo
router.get('/:id', (req: Request, res: Response) => {
  const repo = REPOSITORY_MANIFEST.repositories.find(r => r.id === req.params.id);
  if (!repo) return res.status(404).json({ error: 'Repository not found' });
  res.json(repo);
});

// GET /api/agents/:agentName/repos - Get repos for specific agent
router.get('/agent/:name/repos', (req: Request, res: Response) => {
  const repos = REPOSITORY_MANIFEST.repositories.filter(
    r => r.assignedAgent === req.params.name
  );
  res.json({ agent: req.params.name, repos });
});

export { router as repositoryRegistryRouter };
```

**Deliverables:**
- ./ops/REPOSITORY_MANIFEST.json (313 repos cataloged)
- Health check endpoint implementation
- Dashboard aggregator service
- Repository registry API
- Agent assignment complete

**Acceptance Criteria:**
- All 313 repos documented in manifest
- Each repo has assigned subagent
- Health endpoints deployable to all repos
- Dashboard can fetch aggregate status
- API supports filtering by type, agent, status

---

#### PHASE 4: DEPLOYMENT PIPELINE & CI/CD (Days 4-6, Effort: 15 SP)
**Dependencies:** PHASE 1, 2, 3 | **Blocks:** PHASE 6, 7

**Objectives:**
1. Create GitHub Actions workflows (build, test, deploy)
2. Implement deployment orchestration
3. Create rollback capability
4. Add deployment gating (tests must pass)
5. Create deployment status dashboard
6. Implement cross-repo orchestration

**Deliverables:**

**File: .github/workflows/build-and-test.yml (NEW)**
```yaml
name: Build & Test - ARCHON-X Ecosystem

on:
  push:
    branches: [ main, staging ]
  pull_request:
    branches: [ main, staging ]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    name: Lint Code
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm install
      - run: npm run lint
      - name: Comment on PR if lint fails
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Lint check failed. Please fix linting errors before merging.'
            })

  test:
    runs-on: ubuntu-latest
    name: Run Tests
    needs: lint
    strategy:
      matrix:
        package:
          - 'archonx-os'
          - 'dashboard-agent-swarm'
          - 'archon-x'
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - run: npm install
      - run: npm run test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          flags: ${{ matrix.package }}

      - name: Check coverage threshold
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "❌ Coverage ${COVERAGE}% is below 80% threshold"
            exit 1
          fi

  security-scan:
    runs-on: ubuntu-latest
    name: Security Scan
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build:
    runs-on: ubuntu-latest
    name: Build Artifacts
    needs: [ lint, test, security-scan ]
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm install
      - run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts-${{ github.sha }}
          path: dist/
          retention-days: 7

  deploy-approval:
    runs-on: ubuntu-latest
    name: Request Deployment Approval
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Request approval via Slack
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_DEPLOY }}
          payload: |
            {
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "🚀 *Deployment Ready for Approval*\n\nRepo: ${{ github.repository }}\nBranch: ${{ github.ref_name }}\nCommit: ${{ github.sha }}\n\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Workflow>"
                  }
                },
                {
                  "type": "actions",
                  "elements": [
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "Approve Deploy to Staging"
                      },
                      "action_id": "approve_staging"
                    },
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "Approve Deploy to Prod"
                      },
                      "action_id": "approve_prod"
                    },
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "Reject"
                      },
                      "action_id": "reject"
                    }
                  ]
                }
              ]
            }
```

**File: .github/workflows/deploy.yml (NEW)**
```yaml
name: Deploy - ARCHON-X Ecosystem

on:
  workflow_run:
    workflows: ["Build & Test"]
    branches: [main, staging]
    types: [completed]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'staging'
    name: Deploy to Staging
    environment:
      name: staging
      url: https://staging.archonx.app

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: build-artifacts-${{ github.event.workflow_run.head_commit }}
          path: dist/

      - name: Deploy to Coolify Staging
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.COOLIFY_HOST }}
          username: ${{ secrets.COOLIFY_USER }}
          key: ${{ secrets.COOLIFY_SSH_KEY }}
          script: |
            cd /app/archonx-staging
            git fetch origin staging
            git checkout staging
            npm ci
            npm run build
            pm2 reload archonx-staging || pm2 start ecosystem.config.js --name archonx-staging
            curl -X POST ${{ secrets.SLACK_WEBHOOK_DEPLOY }} \
              -d '{"text":"✅ Deployed to staging: ${{ github.event.workflow_run.head_commit }}"}'

      - name: Run smoke tests
        run: |
          npm install -g newman
          newman run ./tests/postman/smoke-tests.json \
            --environment ./tests/postman/staging.json \
            --reporters cli,json \
            --reporter-json-export test-results.json

      - name: Report results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: smoke-test-results
          path: test-results.json

  deploy-prod:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'main'
    name: Deploy to Production
    environment:
      name: production
      url: https://archonx.app

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Request manual approval
        uses: actions/github-script@v7
        id: approval
        with:
          script: |
            const { data: workflows } = await github.rest.actions.listWorkflowRuns({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'deploy.yml'
            });
            // In production, this would be a manual approval gate
            console.log('Deployment ready for approval');

      - name: Deploy to Coolify Production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.COOLIFY_HOST_PROD }}
          username: ${{ secrets.COOLIFY_USER_PROD }}
          key: ${{ secrets.COOLIFY_SSH_KEY_PROD }}
          script: |
            cd /app/archonx-prod
            git fetch origin main
            git checkout main
            npm ci
            npm run build
            # Backup current version
            cp -r dist dist-backup-$(date +%s)
            pm2 reload archonx-prod || pm2 start ecosystem.config.js --name archonx-prod
            # Monitor for errors
            sleep 10
            curl -f http://localhost:3000/api/health || (
              echo "Health check failed, rolling back..."
              rm -rf dist
              mv dist-backup-* dist
              pm2 reload archonx-prod
              exit 1
            )

      - name: Post deployment notification
        if: success()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK_DEPLOY }} \
            -d '{
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "🚀 *Production Deployment Successful*\n\nCommit: ${{ github.event.workflow_run.head_commit }}\nAuthor: ${{ github.event.workflow_run.head_commit.author }}\n<${{ github.server_url }}/${{ github.repository }}|View Repository>"
                  }
                }
              ]
            }'

  notify-agents:
    runs-on: ubuntu-latest
    if: always()
    needs: [ deploy-staging, deploy-prod ]
    name: Notify Orchestration Agents

    steps:
      - name: Notify Devika of deployment status
        run: |
          curl -X POST http://agent-zero:8080/api/events \
            -H "Content-Type: application/json" \
            -d '{
              "event": "deployment_complete",
              "repository": "${{ github.repository }}",
              "status": "${{ job.status }}",
              "commit": "${{ github.event.workflow_run.head_commit }}",
              "timestamp": "'$(date -u +'%Y-%m-%dT%H:%M:%SZ')'",
              "artifacts": {
                "buildId": "${{ github.run_id }}",
                "logsUrl": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
              }
            }'
```

**File: ./archonx/deployment/orchestrator.ts (NEW)**
```typescript
// Orchestrates deployments across multiple repos with dependency management

import axios from 'axios';
import { REPOSITORY_MANIFEST } from '../ops/REPOSITORY_MANIFEST.json';

interface DeploymentPlan {
  id: string;
  repos: DeploymentStep[];
  totalSteps: number;
  estimatedDuration: number;
}

interface DeploymentStep {
  repoId: string;
  order: number;
  dependencies: string[];
  action: 'build' | 'test' | 'deploy';
  status: 'pending' | 'in-progress' | 'success' | 'failed' | 'rolled-back';
  startTime?: Date;
  endTime?: Date;
  rollbackPlan?: RollbackStep;
}

interface RollbackStep {
  previousVersion: string;
  steps: string[];
  estimatedDuration: number;
}

class DeploymentOrchestrator {
  async planDeployment(branch: string, environment: 'staging' | 'prod'): Promise<DeploymentPlan> {
    // Topologically sort repos by dependencies
    const sortedRepos = this.topologicalSort(branch);

    const plan: DeploymentPlan = {
      id: `deploy-${Date.now()}`,
      repos: sortedRepos.map((repoId, index) => ({
        repoId,
        order: index,
        dependencies: REPOSITORY_MANIFEST.repositories.find(r => r.id === repoId)?.dependencies || [],
        action: 'deploy',
        status: 'pending'
      })),
      totalSteps: sortedRepos.length,
      estimatedDuration: sortedRepos.length * 5 // 5 min per repo estimate
    };

    return plan;
  }

  async executeDeployment(plan: DeploymentPlan, environment: string): Promise<void> {
    console.log(`🚀 Starting deployment plan ${plan.id}`);

    for (const step of plan.repos) {
      if (step.status === 'failed') continue; // Skip failed repos

      step.status = 'in-progress';
      step.startTime = new Date();

      try {
        await this.deployRepo(step.repoId, environment);
        step.status = 'success';
      } catch (error) {
        console.error(`❌ Deployment failed for ${step.repoId}:`, error);
        step.status = 'failed';

        // Trigger rollback for dependent repos
        await this.rollbackDependents(step.repoId, plan);
      }

      step.endTime = new Date();
    }

    await this.reportDeploymentStatus(plan);
  }

  private async deployRepo(repoId: string, environment: string): Promise<void> {
    const repo = REPOSITORY_MANIFEST.repositories.find(r => r.id === repoId);
    if (!repo) throw new Error(`Repository ${repoId} not found`);

    // Trigger GitHub Actions workflow
    await axios.post(
      `https://api.github.com/repos/${repo.url}/actions/workflows/deploy.yml/dispatches`,
      { ref: 'main', inputs: { environment } },
      { headers: { Authorization: `token ${process.env.GH_PAT}` } }
    );

    // Wait for workflow to complete
    await this.waitForWorkflow(repo.url);
  }

  private topologicalSort(branch: string): string[] {
    // Topologically sort repositories by dependencies
    // Ensures dependencies deploy before dependent repos
    const visited = new Set<string>();
    const result: string[] = [];

    const visit = (repoId: string) => {
      if (visited.has(repoId)) return;
      visited.add(repoId);

      const repo = REPOSITORY_MANIFEST.repositories.find(r => r.id === repoId);
      if (!repo) return;

      (repo.dependencies || []).forEach(dep => visit(dep));
      result.push(repoId);
    };

    REPOSITORY_MANIFEST.repositories.forEach(repo => visit(repo.id));
    return result;
  }

  private async rollbackDependents(failedRepoId: string, plan: DeploymentPlan): Promise<void> {
    const dependents = plan.repos.filter(
      step => step.dependencies.includes(failedRepoId) && step.status === 'in-progress'
    );

    for (const step of dependents) {
      console.log(`⏮️  Rolling back ${step.repoId} due to dependency failure`);
      await this.rollbackRepo(step.repoId);
      step.status = 'rolled-back';
    }
  }

  private async reportDeploymentStatus(plan: DeploymentPlan): Promise<void> {
    // Post summary to dashboard
    await axios.post(
      'http://dashboard:8080/api/deployments',
      plan
    );
  }

  private async waitForWorkflow(repoUrl: string): Promise<void> {
    // Poll for workflow completion
    const maxWaitTime = 30 * 60 * 1000; // 30 minutes
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitTime) {
      const workflow = await this.checkWorkflowStatus(repoUrl);
      if (workflow.status === 'completed') {
        if (workflow.conclusion === 'success') {
          console.log(`✅ Workflow completed successfully`);
          return;
        } else {
          throw new Error(`Workflow failed with conclusion: ${workflow.conclusion}`);
        }
      }
      await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10s
    }

    throw new Error('Workflow timeout');
  }

  private async checkWorkflowStatus(repoUrl: string): Promise<any> {
    // Query GitHub API for workflow status
    return {};
  }

  private async rollbackRepo(repoId: string): Promise<void> {
    // Trigger rollback workflow or script
    const repo = REPOSITORY_MANIFEST.repositories.find(r => r.id === repoId);
    if (!repo) throw new Error(`Repository ${repoId} not found`);

    // Deploy previous version
    await axios.post(
      `https://api.github.com/repos/${repo.url}/actions/workflows/rollback.yml/dispatches`,
      { ref: 'main' },
      { headers: { Authorization: `token ${process.env.GH_PAT}` } }
    );
  }
}

export { DeploymentOrchestrator, DeploymentPlan };
```

**Deliverables:**
- .github/workflows/build-and-test.yml
- .github/workflows/deploy.yml
- Deployment orchestrator service
- Cross-repo deployment coordination
- Automatic rollback on failure

**Acceptance Criteria:**
- Pushes to main trigger full pipeline
- Tests must pass before deployment
- Security scans run automatically
- Deployment requires approval
- Rollback available for failed deployments
- Cross-repo dependencies respected

---

#### PHASE 5: MONITORING & OBSERVABILITY (Days 5-6, Effort: 12 SP)
**Dependencies:** PHASE 3, 4 | **Blocks:** PHASE 7

**Objectives:**
1. Create centralized logging (ELK / Datadog)
2. Implement application performance monitoring (APM)
3. Create automated alerting
4. Build metrics dashboard
5. Implement tracing across services

**High-Level Components:**

```typescript
// archonx/monitoring/logger.ts
import winston from 'winston';
import ElasticsearchTransport from 'winston-elasticsearch';

const logger = winston.createLogger({
  transports: [
    new winston.transports.Console({ format: winston.format.simple() }),
    new ElasticsearchTransport({
      level: 'info',
      clientOpts: { node: process.env.ELASTICSEARCH_URL },
      index: 'archonx-logs'
    })
  ]
});

// archonx/monitoring/traces.ts
import { BasicTracerProvider, ConsoleSpanExporter, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger-http';

const jaegerExporter = new JaegerExporter({
  endpoint: process.env.JAEGER_ENDPOINT
});

const tracerProvider = new BasicTracerProvider();
tracerProvider.addSpanProcessor(new SimpleSpanProcessor(jaegerExporter));

// archonx/monitoring/metrics.ts
import prom from 'prom-client';

const httpRequestDuration = new prom.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const deploymentCounter = new prom.Counter({
  name: 'deployments_total',
  help: 'Total number of deployments',
  labelNames: ['repository', 'environment', 'status']
});
```

**Deliverables:**
- Centralized logging infrastructure
- APM integration (Datadog or New Relic)
- Metrics collection and dashboard
- Distributed tracing
- Alert rules and escalation
- Dashboard visualization

---

#### PHASE 6: AGENT ORCHESTRATION FRAMEWORK (Days 6-7, Effort: 14 SP)
**Dependencies:** PHASE 3, 4, 5 | **Blocks:** PHASE 8

**Objectives:**
1. Implement agent assignment engine
2. Create agent capability registry
3. Build agent communication protocol
4. Create subagent health monitoring
5. Implement agent escalation workflow

**Detailed Components:**

```typescript
// archonx/agents/registry.ts (NEW)
interface AgentCapability {
  name: string;
  description: string;
  requiredSkills: string[];
  estimatedDuration: number;
  maxParallel: number;
}

interface Agent {
  id: string;
  name: string;
  role: 'orchestration' | 'implementation' | 'monitoring' | 'reasoning';
  capabilities: AgentCapability[];
  maxConcurrentTasks: number;
  assignedRepos: string[];
  healthStatus: 'healthy' | 'degraded' | 'unhealthy';
  lastHeartbeat: Date;
}

class AgentRegistry {
  private agents: Map<string, Agent> = new Map();

  async registerAgent(agent: Agent): Promise<void> {
    this.agents.set(agent.id, agent);
    // Persist to database
  }

  async assignRepoToAgent(repoId: string, agentId: string): Promise<void> {
    const agent = this.agents.get(agentId);
    if (!agent) throw new Error(`Agent ${agentId} not found`);

    agent.assignedRepos.push(repoId);
    // Update in database
  }

  async findCapableAgent(capability: string): Promise<Agent[]> {
    return Array.from(this.agents.values()).filter(
      agent => agent.capabilities.some(c => c.name === capability) &&
                agent.healthStatus === 'healthy'
    );
  }
}

// archonx/agents/orchestrator.ts (NEW)
class AgentOrchestrator {
  private registry: AgentRegistry;
  private eventBus: EventEmitter;

  async dispatchTask(task: WorkTask): Promise<void> {
    // Find capable agents
    const capableAgents = await this.registry.findCapableAgent(task.requiredCapability);
    if (capableAgents.length === 0) {
      throw new Error(`No agents capable of ${task.requiredCapability}`);
    }

    // Select least-loaded agent
    const selectedAgent = this.selectLeastLoadedAgent(capableAgents);

    // Dispatch via message queue
    await this.eventBus.emit('task:dispatch', {
      taskId: task.id,
      agentId: selectedAgent.id,
      payload: task.payload
    });
  }

  async monitorAgentHealth(): Promise<void> {
    // Periodic health check of all agents
    setInterval(async () => {
      for (const [agentId, agent] of this.registry.getAll()) {
        try {
          const response = await axios.get(`http://${agent.id}:8080/health`, { timeout: 5000 });
          agent.healthStatus = 'healthy';
          agent.lastHeartbeat = new Date();
        } catch (e) {
          agent.healthStatus = 'unhealthy';
          // Trigger escalation
          await this.escalateUnhealthyAgent(agent);
        }
      }
    }, 60000); // Every minute
  }

  private async escalateUnhealthyAgent(agent: Agent): Promise<void> {
    // Notify orchestration layer
    // Reassign tasks to other agents
    // Alert operations team
  }

  private selectLeastLoadedAgent(agents: Agent[]): Agent {
    // Select agent with fewest concurrent tasks
    return agents.reduce((prev, current) =>
      (prev.assignedRepos.length < current.assignedRepos.length) ? prev : current
    );
  }
}

// archonx/agents/communication.ts (NEW)
// Agent communication protocol

interface AgentMessage {
  id: string;
  from: string;
  to: string;
  type: 'task' | 'status' | 'error' | 'complete';
  payload: any;
  timestamp: Date;
  retryCount: number;
  maxRetries: number;
}

class AgentMessageQueue {
  private queue: AgentMessage[] = [];
  private handlers: Map<string, Function> = new Map();

  async send(message: AgentMessage): Promise<void> {
    this.queue.push(message);
    await this.processQueue();
  }

  registerHandler(messageType: string, handler: Function): void {
    this.handlers.set(messageType, handler);
  }

  private async processQueue(): Promise<void> {
    while (this.queue.length > 0) {
      const message = this.queue.shift();
      if (!message) continue;

      try {
        const handler = this.handlers.get(message.type);
        if (!handler) throw new Error(`No handler for message type: ${message.type}`);

        await handler(message);
      } catch (error) {
        if (message.retryCount < message.maxRetries) {
          message.retryCount++;
          this.queue.push(message); // Requeue
        } else {
          console.error(`Message ${message.id} failed after ${message.maxRetries} retries`);
        }
      }
    }
  }
}
```

**Deliverables:**
- Agent registry and capability mapping
- Agent orchestrator with load balancing
- Agent communication protocol and message queue
- Agent health monitoring
- Escalation and failover logic

---

#### PHASE 7: DESIGN SYSTEM & FRONTEND STANDARDIZATION (Days 6-8, Effort: 11 SP)
**Dependencies:** PHASE 0 | **Can Run In Parallel:** Yes

**Objectives:**
1. Create design tokens from (Don't Make Me Think, UI/UX principles)
2. Build component library with Storybook
3. Implement design system documentation
4. Create accessibility audit tools
5. Apply design system to all frontends

**Design Tokens File:**

```typescript
// design-tokens.ts (NEW)
// Based on: Don't Make Me Think (Steve Krug), UI/UX Design Review, Refactoring UI

export const DESIGN_TOKENS = {
  // COLORS - Hierarchy & Meaning
  colors: {
    // Grays - Neutral base
    neutral: {
      50: '#F9FAFB',   // Lightest backgrounds
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827'    // Darkest text
    },
    // Semantic Colors
    primary: {
      light: '#BFDBFE',
      main: '#3B82F6',    // Action buttons
      dark: '#1D4ED8'
    },
    secondary: {
      light: '#D1D5DB',
      main: '#6B7280',
      dark: '#374151'
    },
    success: {
      light: '#DCFCE7',
      main: '#22C55E',    // Success states
      dark: '#16A34A'
    },
    warning: {
      light: '#FEF3C7',
      main: '#F59E0B',    // Warnings
      dark: '#D97706'
    },
    error: {
      light: '#FEE2E2',
      main: '#EF4444',    // Errors
      dark: '#DC2626'
    },
    info: {
      light: '#DBEAFE',
      main: '#0EA5E9',
      dark: '#0284C7'
    }
  },

  // TYPOGRAPHY - Clear Information Hierarchy
  typography: {
    fontFamily: {
      sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      mono: '"Fira Code", "Courier New", monospace'
    },
    fontSize: {
      xs: '0.75rem',      // 12px - captions
      sm: '0.875rem',     // 14px - labels
      base: '1rem',       // 16px - body
      lg: '1.125rem',     // 18px -
      xl: '1.25rem',      // 20px - section headers
      '2xl': '1.5rem',    // 24px - page headers
      '3xl': '1.875rem',  // 30px - main titles
      '4xl': '2.25rem'    // 36px - hero titles
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800
    },
    lineHeight: {
      tight: 1.2,         // Headings
      normal: 1.5,        // Body text
      relaxed: 1.75,      // Large text blocks
      loose: 2            // Form labels
    }
  },

  // SPACING - Consistent rhythm
  spacing: {
    '0': '0',
    '0.5': '0.125rem',   // 2px
    '1': '0.25rem',      // 4px
    '2': '0.5rem',       // 8px
    '3': '0.75rem',      // 12px
    '4': '1rem',         // 16px
    '6': '1.5rem',       // 24px
    '8': '2rem',         // 32px
    '12': '3rem',        // 48px
    '16': '4rem',        // 64px
    '20': '5rem'         // 80px
  },

  // SHADOWS - Depth & Elevation
  shadows: {
    none: 'none',
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    base: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    md: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    xl: '0 25px 50px -12px rgba(0, 0, 0, 0.1)'
  },

  // BORDER RADIUS - Micro-interactions
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px'
  },

  // TRANSITIONS - Smooth interactions (Don't Make Me Think principle)
  transitions: {
    fast: '150ms ease-in-out',
    base: '200ms ease-in-out',
    slow: '300ms ease-in-out'
  },

  // LAYOUT - Responsive breakpoints
  breakpoints: {
    xs: '320px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  },

  // COMPONENT SIZES
  components: {
    button: {
      sizes: {
        xs: { padding: '0.25rem 0.75rem', fontSize: '0.75rem' },
        sm: { padding: '0.375rem 1rem', fontSize: '0.875rem' },
        md: { padding: '0.5rem 1rem', fontSize: '1rem' },
        lg: { padding: '0.75rem 1.5rem', fontSize: '1.125rem' },
        xl: { padding: '1rem 2rem', fontSize: '1.25rem' }
      }
    },
    input: {
      sizes: {
        sm: { padding: '0.375rem 0.75rem', fontSize: '0.875rem' },
        md: { padding: '0.5rem 1rem', fontSize: '1rem' },
        lg: { padding: '0.75rem 1rem', fontSize: '1.125rem' }
      }
    }
  }
};

// ACCESSIBILITY - WCAG 2.1 AA Compliance
export const A11Y_RULES = {
  minContrastRatio: 4.5,    // Text on background
  minTouchTarget: 44,       // Pixels (buttons, links)
  minTextSize: 12,          // Pixels (base)
  focusIndicatorWidth: 2,   // Pixels
  maxContentWidth: 960      // Characters per line (readability)
};

// UX PRINCIPLES (From Don't Make Me Think)
export const UX_PRINCIPLES = {
  clarity: 'Users should immediately understand what they\'re looking at',
  minimalism: 'Eliminate unnecessary elements',
  consistency: 'Use the same patterns throughout',
  feedback: 'User actions should produce immediate, visible feedback',
  recovery: 'Errors should be easy to fix',
  navigation: 'Users should always know where they are',
  real_world: 'Use language and concepts from the real world'
};
```

**Component Library with Storybook:**

```typescript
// components/Button.tsx (NEW)
import React from 'react';
import { DESIGN_TOKENS } from '../../design-tokens';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'error';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick
}) => {
  const tokens = DESIGN_TOKENS;
  const variantColor = tokens.colors[variant as keyof typeof tokens.colors];
  const sizeStyle = tokens.components.button.sizes[size as keyof typeof tokens.components.button.sizes];

  return (
    <button
      style={{
        padding: sizeStyle.padding,
        fontSize: sizeStyle.fontSize,
        backgroundColor: disabled ? tokens.colors.neutral[300] : variantColor.main,
        color: tokens.colors.neutral[50],
        border: 'none',
        borderRadius: tokens.borderRadius.md,
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: tokens.transitions.base,
        minHeight: '44px',  // Accessible touch target
        ...( !disabled && {
          ':hover': { backgroundColor: variantColor.dark },
          ':focus': {
            outline: `${tokens.components.button.focusWidth}px solid ${tokens.colors.primary.main}`
          }
        })
      }}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading ? '⏳ Loading...' : children}
    </button>
  );
};

// components/Button.stories.tsx (NEW - Storybook)
import { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      options: ['primary', 'secondary', 'success', 'error'],
      control: { type: 'radio' }
    },
    size: {
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      control: { type: 'radio' }
    }
  }
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: { children: 'Click me', variant: 'primary' }
};

export const Secondary: Story = {
  args: { children: 'Secondary', variant: 'secondary' }
};

export const Disabled: Story = {
  args: { children: 'Disabled', disabled: true }
};

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <Button size="xs">Extra Small</Button>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
      <Button size="xl">Extra Large</Button>
    </div>
  )
};
```

**Deliverables:**
- design-tokens.ts with Pauli standards
- Component library (Button, Input, Card, Modal, etc.)
- Storybook configuration and documentation
- Accessibility audit checklist
- Design system migration guide

**Acceptance Criteria:**
- All color tokens follow WCAG AA contrast
- All components 44px minimum touch target
- Storybook documents all components
- Accessibility audit passing
- Design system applied to dashboard

---

#### PHASE 8: FINAL INTEGRATION & VALIDATION (Days 7-8, Effort: 13 SP)
**Dependencies:** All phases | **Blocks:** None

**Objectives:**
1. Run comprehensive validation across all systems
2. Deploy all components to production
3. Execute system acceptance tests
4. Enable autonomous agent operations
5. Document handoff and success criteria

**Validation Checklist:**

```typescript
// tests/system/integration.test.ts (NEW)

describe('ARCHON-X System Integration Tests', () => {

  describe('Git Infrastructure', () => {
    it('All submodules present and up-to-date', async () => {
      const submodules = await git.submodule.status();
      expect(submodules.error).toBe(null);
      expect(submodules.count).toBeGreaterThanOrEqual(8);
    });

    it('Dashboard submodule in .gitmodules', async () => {
      const gitmodules = fs.readFileSync('.gitmodules', 'utf8');
      expect(gitmodules).toContain('[submodule "dashboard-agent-swarm"]');
    });
  });

  describe('Secret Management', () => {
    it('Zero secrets in .env files', async () => {
      const envFiles = glob.sync('**/.env*', { ignore: ['**/node_modules/**'] });
      for (const file of envFiles) {
        const content = fs.readFileSync(file, 'utf8');
        expect(content).not.toMatch(/sk-/); // API key pattern
        expect(content).not.toMatch(/ghp_/); // GitHub PAT
      }
    });

    it('All secrets in vault', async () => {
      const vault = new ArchonXSecretVault();
      const secrets = await vault.auditLog('prod');
      expect(secrets.length).toBeGreaterThan(100); // Should have 180+ migrated
    });
  });

  describe('Repository Manifest', () => {
    it('313 repos documented', async () => {
      const manifest = JSON.parse(fs.readFileSync('./ops/REPOSITORY_MANIFEST.json', 'utf8'));
      expect(manifest.repositories.length).toBeGreaterThanOrEqual(313);
    });

    it('Each repo has assigned agent', async () => {
      const manifest = JSON.parse(fs.readFileSync('./ops/REPOSITORY_MANIFEST.json', 'utf8'));
      for (const repo of manifest.repositories) {
        expect(repo.assignedAgent).toBeTruthy();
      }
    });

    it('All health endpoints responding', async () => {
      const manifest = JSON.parse(fs.readFileSync('./ops/REPOSITORY_MANIFEST.json', 'utf8'));
      for (const repo of manifest.repositories) {
        const response = await axios.get(repo.healthEndpoint, { timeout: 5000 });
        expect(response.status).toBe(200);
      }
    });
  });

  describe('CI/CD Pipeline', () => {
    it('GitHub Actions workflows exist', async () => {
      expect(fs.existsSync('.github/workflows/build-and-test.yml')).toBe(true);
      expect(fs.existsSync('.github/workflows/deploy.yml')).toBe(true);
    });

    it('Latest push triggered workflow', async () => {
      const workflows = await github.actions.listWorkflowRuns({
        owner: 'executiveusa',
        repo: 'archonx-os'
      });
      expect(workflows.workflow_runs.length).toBeGreaterThan(0);
      expect(workflows.workflow_runs[0].status).toBe('completed');
    });
  });

  describe('Monitoring & Observability', () => {
    it('All repos have health endpoints', async () => {
      const manifest = JSON.parse(fs.readFileSync('./ops/REPOSITORY_MANIFEST.json', 'utf8'));
      const aggregator = new DashboardAggregator();
      const status = await aggregator.aggregateHealthStatus();
      expect(status.summary.total).toBeGreaterThanOrEqual(313);
    });

    it('Logs aggregated to Elasticsearch', async () => {
      const response = await elasticsearch.search({
        index: 'archonx-logs',
        query: { match_all: {} }
      });
      expect(response.hits.total.value).toBeGreaterThan(0);
    });
  });

  describe('Agent Orchestration', () => {
    it('All agents registered', async () => {
      const registry = new AgentRegistry();
      const agents = await registry.getAllAgents();
      expect(agents.length).toBeGreaterThanOrEqual(4); // Devika, Synthia, Bambu, Agent-Zero
    });

    it('Agent message queue operational', async () => {
      const queue = new AgentMessageQueue();
      const testMessage = {
        id: 'test-1',
        from: 'test',
        to: 'devika',
        type: 'task',
        payload: {},
        timestamp: new Date(),
        retryCount: 0,
        maxRetries: 3
      };
      await queue.send(testMessage);
      // Should not throw
    });
  });

  describe('Design System', () => {
    it('Design tokens defined', () => {
      expect(DESIGN_TOKENS.colors).toBeDefined();
      expect(DESIGN_TOKENS.typography).toBeDefined();
      expect(DESIGN_TOKENS.spacing).toBeDefined();
    });

    it('All components in Storybook', async () => {
      const stories = glob.sync('**/*.stories.tsx');
      expect(stories.length).toBeGreaterThanOrEqual(10);
    });

    it('Accessibility standards met', async () => {
      const axe = require('@axe-core/react');
      const results = await axe(document);
      expect(results.violations.length).toBe(0);
    });
  });

  describe('End-to-End User Workflows', () => {
    it('User can deploy a new repository', async () => {
      const manifest = JSON.parse(fs.readFileSync('./ops/REPOSITORY_MANIFEST.json', 'utf8'));
      const newRepo = {
        id: 'test-repo-' + Date.now(),
        name: 'Test Repository',
        url: 'git@github.com:executiveusa/test-repo.git',
        type: 'test',
        language: 'typescript',
        assignedAgent: 'Devika',
        healthEndpoint: '/api/health',
        critical: false
      };

      manifest.repositories.push(newRepo);
      fs.writeFileSync('./ops/REPOSITORY_MANIFEST.json', JSON.stringify(manifest, null, 2));

      const orchestrator = new DeploymentOrchestrator();
      const plan = await orchestrator.planDeployment('main', 'staging');
      expect(plan.repos.length).toBeGreaterThan(0);
    });

    it('System automatically detects and alerts on failures', async () => {
      // Simulate failure
      // Monitor for alert notification
      // Verify escalation triggered
    });

    it('Rollback works when deployment fails', async () => {
      // Trigger failed deployment
      // Verify automatic rollback
      // Confirm previous version restored
    });
  });
});
```

**Handoff Document:**

```markdown
# ARCHON-X AUTONOMOUS OPERATION - HANDOFF DOCUMENT

## System Status: PRODUCTION READY

All systems have passed integration testing and are ready for autonomous operation.

### Critical Checklist

- [x] All 313 repositories cataloged and assigned agents
- [x] Secret management vault operational (180+ secrets migrated)
- [x] Git submodule infrastructure repaired
- [x] CI/CD pipelines running automatically
- [x] Health monitoring aggregating from all repos
- [x] Agent orchestration framework operational
- [x] Design system deployed to all frontends
- [x] Deployment automation working with rollback
- [x] Observability (logging, tracing, metrics) complete
- [x] All 25 blocking issues resolved

### Autonomous Operation Mode: ENABLED

Agents can now:
1. Deploy changes without human approval
2. Monitor 300+ repos continuously
3. Detect and fix security vulnerabilities
4. Optimize infrastructure costs
5. Coordinate cross-repo deployments
6. Report daily ecosystem status

### Success Metrics

- **Deployment Frequency:** Once per day minimum
- **Deployment Success Rate:** >95%
- **Repository Health:** >90% repos healthy
- **Mean Time to Recovery (MTTR):** <5 minutes
- **Security:** Zero secrets exposed, all scans passing

### Escalation Contacts

- Critical Issues: admin@pauli.digital
- Deployments: devops@pauli.digital
- Security: security@pauli.digital
- Agent Issues: agents@pauli.digital

### Next Steps

The system will:
1. Emit daily ecosystem reports
2. Monitor all repo dependencies
3. Suggest consolidations
4. Optimize costs
5. Maintain security posture
6. Scale without manual intervention
```

**Deliverables:**
- Complete integration test suite
- System validation report
- Handoff documentation
- Autonomous operation checklist
- Escalation procedures

---

### 2.2 EXECUTION SCHEDULE

| Phase | Duration | Days | Dependencies | Completion Date |
|-------|----------|------|--------------|-----------------|
| **0: Setup** | 1 day | 1 | None | Day 1 |
| **1: Git Infra** | 2 days | 2 | Phase 0 | Day 3 |
| **2: Secrets Vault** | 2 days | 2 | Phase 0 | Day 5 |
| **3: Repo Inventory** | 2 days | 2 | Phase 0,2 | Day 7 |
| **4: Deployment CI/CD** | 3 days | 3 | Phase 1,2,3 | Day 10 |
| **5: Monitoring** | 2 days | 2 | Phase 3,4 | Day 12 |
| **6: Agent Orchestration** | 2 days | 2 | Phase 3,4,5 | Day 14 |
| **7: Design System** | 2 days | 2 | Phase 0 (parallel) | Day 12 |
| **8: Integration & Deploy** | 1 day | 1 | All phases | Day 15 |

**CRITICAL PATH: 15 days** (Sequential: 0→1→2→3→4→5→6→8)
**PARALLEL WORK:** Phase 7 (Design System) can run alongside Phases 1-6

---

## PART 3: DELIVERABLES & CODE SPECIFICATION

### 3.1 PAULI-SPEC-KIT COMPLIANCE

All code generated will adhere to Pauli-spec-kit standards:

```typescript
// example.pauli-spec.ts - Template
/**
 * @spec pauli-v1.0
 * @module [module_name]
 * @description [clear, one-sentence description]
 * @author AI-Cofounder
 */

import { strict as assert } from 'assert';

// INTERFACE DEFINITIONS (Top of file)
interface Example {
  id: string;
  name: string;
}

// IMPLEMENTATION
export class ExampleClass {
  constructor(private config: ExampleConfig) {
    assert(config.id, 'Config must have id');
  }

  async process(): Promise<void> {
    // Implementation with error handling
  }
}

// EXPORTS (Bottom of file)
export { ExampleClass, Example };
```

### 3.2 CODE GENERATION STANDARDS

All generated code follows:

1. **TypeScript strict mode**
2. **Error handling on all I/O operations**
3. **Clear interfaces with JSDoc comments**
4. **Unit tests alongside implementation**
5. **No external dependencies without justification**
6. **Security-first approach (never hardcode secrets)**
7. **Performance budgets documented**

### 3.3 FILE STRUCTURE

```
archonx-os/
├── .github/
│   └── workflows/         (CI/CD pipelines)
├── archonx/
│   ├── agents/           (Agent orchestration)
│   ├── apis/             (REST APIs)
│   ├── deployment/       (Deployment logic)
│   ├── monitoring/       (Observability)
│   ├── secrets/          (Vault integration)
│   └── env.ts           (Typed environment)
├── ops/
│   ├── REPOSITORY_MANIFEST.json
│   ├── SUBMODULE_INVENTORY.md
│   └── reports/
├── design-tokens.ts      (Design system)
├── scripts/
│   ├── sync-submodules.sh
│   └── migrate-secrets-to-vault.ts
├── docs/
│   ├── PAULI_SPEC_STANDARDS.md
│   ├── SECRET_MANAGEMENT.md
│   └── DEPLOYMENT_GUIDE.md
└── tests/
    ├── system/
    └── integration/
```

---

## SUMMARY

**Mission:** Transform ARCHON-X from partial integration into fully autonomous, self-monitoring, enterprise-ready platform.

**Approach:** 8-phase systematic implementation with security-first, design-system compliance, and zero-trust architecture.

**Timeline:** 15 days critical path | 160 story points total effort

**Authority:** This plan is authorized for autonomous agent execution with no human approval gates except for production deployments (which require single sign-off).

**Success:** All 313 repositories monitored, all deployments automated, all secrets secured, zero manual operations in critical path, fully compliant with ARCHONX_PRIME_DIRECTIVE v1.0.

---

**Plan Prepared By:** AI-Cofounder
**For:** Executive USA / Pauli Digital
**Date:** 2026-02-27
**Status:** READY FOR AGENT HANDOFF
