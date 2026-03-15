# ARCHON-X OS — CLOUD SKILLS SUITE
## Master Index & Flow Library
**Version 1.0 · March 2026 · The Pauli Effect**
**Stack: Python · Next.js · Tailwind · shadcn/ui · Coolify · Vercel · Supabase · Cloudflare**

---

## SYSTEM MAP

### Products & Services
| Entity | Type | Platform | Schema |
|--------|------|----------|--------|
| The Pauli Effect | AI Solutions Agency | Coolify + Cloudflare | pauli_ |
| ARCHON-X OS | AI Operating System (product) | Coolify + GitHub | archonx_ |
| Akash Engine | Client Services Brand | Vercel + Resell | akash_ |
| New World Kids | 501c3 Nonprofit | Cloudflare Pages | nwkids_ |
| Culture Shock Sports | Youth Sports Nonprofit | Cloudflare Pages | culture_ |
| Kupuri Media | Web Design (Ivette) | Vercel + CF Pages | kupuri_ |
| Yappyverse | IP/Media | Coolify | yappy_ |
| HustleClaude | Revenue/Marketing | Coolify | hustle_ |
| PostaTees Studio | AI T-Shirt Design SaaS | Vercel | posta_ |
| Veronika | Smart Sites Agent | Vercel | saas_ |

### Key Feedback Loops
1. **Deploy Loop**: Code → ZTE Pipeline → Coolify → Health Check → Second Brain log → Lightning RL training
2. **Content Loop**: Create → Publish → Engagement signal → Lightning APO → Better next prompt
3. **Grant Loop**: NWKids outreach → Response rate → SCQA refinement → Higher conversion
4. **Client Loop**: Akash delivers → Retainer renews → Case study → New client acquisition

---

## SKILL REGISTRY

### Baseline (Customized from Anthropic)
| skill_id | Display Name | File |
|----------|-------------|------|
| algo_art_pauli | Pauli Algorithmic Art | skills/algo_art_pauli.md |
| brand_pauli | Pauli Brand Guidelines | skills/brand_pauli.md |
| canvas_pauli | Pauli Canvas Design | skills/canvas_pauli.md |
| comms_pauli | Pauli Internal Comms | skills/comms_pauli.md |
| mcp_builder_pauli | Pauli MCP Builder | skills/mcp_builder_pauli.md |
| skill_creator_pauli | Pauli Skill Creator | skills/skill_creator_pauli.md |
| gif_pauli | Pauli GIF & Animation | skills/gif_pauli.md |
| theme_pauli | Pauli Theme Factory | skills/theme_pauli.md |
| web_artifacts_pauli | Pauli Web Artifacts Builder++ | skills/web_artifacts_pauli.md |

### Net-New Custom Skills
| skill_id | Display Name | File |
|----------|-------------|------|
| ux_pauli | UI/UX Design | skills/ux_pauli.md |
| devops_pauli | Deployment & DevOps | skills/devops_pauli.md |
| marketing_pauli | Marketing & Growth | skills/marketing_pauli.md |
| fundraising_pauli | Fundraising & Investor Relations | skills/fundraising_pauli.md |
| avatar_pauli | Avatar & Comic Scriptwriter | skills/avatar_pauli.md |
| finance_pauli | Finance & Ops | skills/finance_pauli.md |
| crypto_pauli | Crypto & Web3 Strategy | skills/crypto_pauli.md |
| gratitude_pauli | Gratitude Department | skills/gratitude_pauli.md |

---

## FLOW LIBRARY

### Flow 01 — New Feature Launch
**Trigger**: Bambu says "ship [feature]"
**Sequence**:
1. `ux_pauli` → wireframe + acceptance criteria
2. `web_artifacts_pauli` → UI components + landing page
3. `devops_pauli` → Coolify/Vercel deploy config
4. `comms_pauli` → internal RFC + status update to Notion
5. `marketing_pauli` → launch post series + email sequence
**Human gate**: PR review before merge · First deploy approval
**Fully auto after gate**: deploy, smoke test, Notion update, social posts queued

### Flow 02 — Fundraising Push
**Trigger**: Grant deadline or investor outreach cycle
**Sequence**:
1. `finance_pauli` → runway model + metrics snapshot
2. `fundraising_pauli` → pitch deck + one-pager + data room outline
3. `comms_pauli` → investor update email
4. `marketing_pauli` → social proof content (impact stats)
5. `gratitude_pauli` → thank-you sequence for past donors
**Human gate**: All financial figures reviewed before send · Bambu approves outreach list

### Flow 03 — Content & Community Week
**Trigger**: Weekly Monday cadence
**Sequence**:
1. `avatar_pauli` → 3 comic panels / character dialog scripts
2. `algo_art_pauli` → generative visual assets for social
3. `theme_pauli` → apply consistent theme across all outputs
4. `marketing_pauli` → post schedule + captions + CTAs
5. `gratitude_pauli` → weekly shoutouts + community recognition
**Human gate**: Optional — Bambu can approve or auto-publish if configured
**Fully auto**: scheduling, formatting, cross-platform adaptation

### Flow 04 — Client Delivery (Akash Engine)
**Trigger**: New Akash client onboarded
**Sequence**:
1. `ux_pauli` → product audit + UX recommendations
2. `web_artifacts_pauli` → prototype / mockup artifacts
3. `devops_pauli` → hosting setup on Resell, Coolify, or Vercel
4. `comms_pauli` → client status report template
5. `marketing_pauli` → client's launch strategy (if in scope)
**Human gate**: Client approval gates at UX spec and live deploy

### Flow 05 — Weekly Self-Improvement Cycle (ARCHON-X Internal)
**Trigger**: Every Friday 11pm (cron)
**Sequence**:
1. `devops_pauli` GC Agent → health check all 268 repos
2. Agent Lightning training run → optimize prompts from week's trajectories
3. Second Brain ingestion → embed new Notion pages + GitHub commits
4. `comms_pauli` → weekly summary report to Bambu's Notion inbox
**Human gate**: Lightning training approval (optional — can be fully auto)

### Flow 06 — New BU Activation
**Trigger**: New business unit or product line spun up
**Sequence**:
1. `brand_pauli` → apply brand guidelines, generate asset kit
2. `theme_pauli` → create BU-specific theme variant
3. `devops_pauli` → provision subdomain + Coolify/Vercel project
4. `mcp_builder_pauli` → build MCP server if new external API needed
5. `skill_creator_pauli` → create BU-specific skill if recurring workflows emerge
**Human gate**: Domain registration · First deploy

### Flow 07 — Crisis / Incident Response
**Trigger**: Downtime alert or Coolify health check failure
**Sequence**:
1. `devops_pauli` → incident runbook execution (auto-rollback attempt)
2. `comms_pauli` → incident report drafted
3. Second Brain → query for similar past incidents
4. `devops_pauli` → post-mortem document
**Human gate**: Rollback confirmation if auto-rollback fails · Post-mortem sign-off

---

## INSTALLATION

### Claude Desktop (Skills folder)
```
Windows: C:\Users\<you>\AppData\Roaming\Claude\skills\user\
Mac:     ~/Library/Application Support/Claude/skills/user/
```
Drop each `.md` file from `/skills/` into that folder. Restart Claude Desktop.

### Claude Code (ARCHON-X repo)
```bash
# In ARCHON-X2.0 repo root:
mkdir -p .claude/skills
cp skills/*.md .claude/skills/
# Claude Code auto-reads .claude/ directory
```

### Notion (Second Brain)
Push via Notion MCP — each skill becomes a sub-page under PAULI Second Brain.
