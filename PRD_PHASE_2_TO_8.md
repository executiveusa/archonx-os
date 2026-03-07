# ARCHON-X OS: PHASE 2-8 PRODUCT REQUIREMENTS DOCUMENT (PRD)

## 1. VISION & MISSION
The objective is to evolve the ARCHON-X ecosystem from a set of disconnected repositories into a **fully-operational, self-monitoring, and self-healing autonomous enterprise platform**. The system will orchestrate a 64-agent swarm to manage 300+ repositories, ensuring technical excellence and ethical alignment.

## 2. KEY PHASES

### PHASE 2: SECRET VAULT REFACTOR (CRITICAL)
- **Problem**: 180+ API keys and credentials are currently stored in plaintext `master.env` and `kilo-code-secrets.json`.
- **Solution**:
  - Implement a Supabase-backed encrypted vault.
  - Create a `ArchonXVault` client for on-demand secret retrieval.
  - Automate secret rotation using n8n or internal cron jobs.
  - Clean git history of all previous secret exposure.

### PHASE 3: EXECUTION LAYER & SUBAGENT LIFECYCLE
- **Problem**: Repos are indexed/planned, but actions are manual.
- **Solution**:
  - Implement the `ExecutionEngine` to run planned tasks.
  - Map specific subagents (from the 64-agent fleet) to specialized repository types.
  - Store results, logs, and artifacts back into the Repository Registry (SQLite/Postgres).

### PHASE 4: CI/CD & AUTOMATED DEPLOYMENT
- **Problem**: No unified deployment pipeline.
- **Solution**:
  - Integrate Github Actions to trigger builds on PR/Commit.
  - Wire deployments to Coolify (for backends) and Vercel (for frontends).
  - Implement a `RollbackProtocol` for failed deployments.

### PHASE 5: MONITORING & HEALTH REGISTRY
- **Problem**: No real-time visibility into repo health.
- **Solution**:
  - Implement `/healthz` endpoints across all core services.
  - Aggregate status in the `MonitoringService`.
  - Send alerts to Slack/Telegram on service degradation.

### PHASE 6: UNIFIED UX & DASHBOARD
- **Problem**: Fractionalized UI (Mission Console vs. Dashboard Swarm).
- **Solution**:
  - **Public Frontend**: High-frequency "Archon X Hero" with interactive mission signals.
  - **Internal Dashboard**: Integrated `dashboard-agent-swarm` for agent management, logs, and task control.
  - **Security**: Implement JWT/OAuth login for the internal dashboard.

### PHASE 7: OPTIMIZATION (TOKEN & PERFORMANCE)
- **Problem**: High LLM token costs for large codebase analysis.
- **Solution**:
  - Integrate **jCodeMunch MCP** for symbol-based code retrieval (cutting costs by ~90%).
  - Use **Ralphy** for automated PRD-to-Implementation loops.

### PHASE 8: SELF-HEALING & AUTONOMOUS MAINTENANCE
- **Problem**: System depends on human developer for bug fixes.
- **Solution**:
  - Enable agents to detect health failures and autonomously attempt a "fix-and-redeploy" cycle.
  - Implement a Governance Board (King/Queen agents) for final approval of critical fixes.

## 3. SUCCESS METRICS
- **Security**: Zero plaintext credentials in code or history.
- **Uptime**: 99.9% health reporting for core 313 repositories.
- **Efficiency**: 80% reduction in token usage for code-reading tasks.
- **Autonomy**: 70% of routine maintenance tasks handled without human intervention.
