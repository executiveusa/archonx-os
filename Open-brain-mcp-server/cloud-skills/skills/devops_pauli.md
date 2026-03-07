# Deployment & DevOps
## skill_id
`devops_pauli`

## Purpose
Handles all deployment strategy, configuration authoring, and automation for the Pauli Empire's infrastructure: Coolify VPS (31.220.58.212), Vercel (50+ projects), Cloudflare (DNS/CDN/WAF front for everything), GitHub Actions CI/CD, and Docker. Infers current deployment state from repo configs before making changes. Drafts rollout strategies (staging, canary, blue-green), generates ops runbooks for deployments and incident handling, and manages the 5 Garbage Collection agents on cron schedule. This is the implementation arm of the ZTE pipeline.

## When to Use
- Deploying any of the 268 repos to their assigned platform
- Setting up a new Coolify app or Vercel project
- Writing GitHub Actions CI/CD pipelines
- Planning a zero-downtime migration or major version upgrade
- Writing a deployment runbook for a new service
- Managing Cloudflare DNS/WAF/Page Rules changes
- Executing or planning any GC agent cron job

## Inputs
```
action: "deploy" | "rollback" | "configure" | "migrate" | "runbook" | "gc-agent" | "health-check"
target: "coolify" | "vercel" | "cloudflare" | "github-actions" | "docker"
repo: string (repo name from 268-repo registry)
environment: "production" | "staging" | "preview"
strategy: "direct" | "canary" | "blue-green" | "rolling"
rollback_plan: boolean (always true for production)
```

## Outputs
- Coolify app configuration (JSON/YAML)
- Vercel `vercel.json` with build settings, rewrites, redirects, env var map
- `Dockerfile` and `docker-compose.yml`
- GitHub Actions workflow YAML
- Cloudflare DNS/WAF rule configuration
- Ops runbook (Markdown, Notion-ready)
- GC agent cron scripts

## Tools & Integrations
- Coolify MCP: `deploy`, `rollback`, `health_check`, `get_app_status`
- Vercel MCP: project config, preview deploys, domain management
- GitHub MCP: create/update GitHub Actions workflows
- Cloudflare API (via MCP when available)
- Vault Agent: secret injection for all deploy configs

## Project-Specific Guidelines
**Platform routing** (do not deviate from this):
- Python/Docker/agents → Coolify VPS 31.220.58.212
- Next.js/React/TypeScript → Vercel (use both accounts if quota hit)
- Static sites/Nonprofits/Landing pages → Cloudflare Pages (free unlimited)
- Client sites billed to client → Resell Hosting

**Cloudflare as front door for everything**: Even Coolify apps sit behind CF for DDoS/SSL/caching. All DNS in one CF panel.
**Subdomain convention**: Use thepaulieffect.com as root domain. Subdomains for each BU (archon., nwkids., roi., etc.)
**Never push secrets**: All env vars via Coolify UI environment section or Vercel env UI — never in repo files.
**Rollback SLA**: Every production deploy must have documented rollback command. Coolify: revert to previous build. Vercel: instant rollback in dashboard.
**GC agents cron schedule**: DocDrift (Sun 3am), ConstraintGC (Tue 3am), BrainGC (Fri 3am), SecretAudit (Mon 3am), DeployHealth (Daily 6am).

## Example Interactions
1. "Deploy postatees-studio to Vercel with staging and production environments" → vercel.json + GitHub Actions workflow + env var map
2. "Set up ARCHON-X2.0 on Coolify with Docker" → Dockerfile + Coolify config + Cloudflare DNS entry
3. "Write the runbook for deploying NW Kids to Cloudflare Pages" → Step-by-step runbook, rollback instructions
4. "Plan a blue-green migration for the Pauli Effect main site" → Migration plan, traffic switch procedure, rollback trigger conditions
5. "Run the weekly DeployHealth GC agent" → Health check all Coolify apps, SSL expiry check, disk usage, Notion report
