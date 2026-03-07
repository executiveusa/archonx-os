# PROJECT ECOSYSTEM MAPPING & VECTOR DB SEEDING
## Complete Inventory: 316 Repos → ARCHON-X Agents → Open Brain Vector DB

**Created:** March 6, 2026  
**Status:** Ready to ingest into Open Brain  
**Format:** CSV + JSON for bulk import  

---

## MASTER PROJECTS (Core Operational Units)

### 1. **ARCHON-X OS** (Autonomous AI Operating System)
- **Status:** Production (all 15 tests passing, 2 config items pending)
- **GitHub Repo:** `executiveusa/archonx-os`
- **Core Tech Stack:** Python, FastAPI, PostgreSQL, Docker, Coolify
- **Primary Agents:** Pauli, Synthia, Guardian Fleet (Darya, Devika, Lightning)
- **Deployment:** Coolify on Hostinger VPS
- **Key Pending:** `coolify.app_uuid`, `coolify.base_url`, `COOLIFY_API_KEY`, `ORGO_API_TOKEN`
- **Related Repos in This Group:** 15+
  - `archon-lovable-nexus` (UI)
  - `archonx-synthia` (Synthia persona microservice)
  - `orgo-agent` (Computer-use agent)
  - `VisionClaw` (Vision integration)
  - Others: OpenClaw integration, deployment tools

**Open Brain Entities:**
```json
{
  "project_id": "archonx-os-001",
  "name": "ARCHON-X OS",
  "type": "core_system",
  "status": "production_ready",
  "description": "Autonomous Zero-Touch Engineering system with 64-agent fleet",
  "agents": ["pauli", "synthia", "guardian_fleet"],
  "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker", "Coolify"],
  "deployment": {
    "platform": "Coolify",
    "host": "Hostinger VPS",
    "status": "awaiting_config"
  },
  "critical_dependencies": [
    "coolify.app_uuid",
    "coolify.base_url",
    "COOLIFY_API_KEY",
    "ORGO_API_TOKEN"
  ],
  "test_status": "15/15 passing, zero stubs",
  "github_repos": [
    "archonx-os",
    "archon-lovable-nexus",
    "archonx-synthia",
    "orgo-agent",
    "VisionClaw"
  ]
}
```

---

### 2. **Akash Engine** (Client Services Platform - $2.5K-$50K/month retainers)
- **Status:** Production with active clients
- **GitHub Repos:** 12+ (master files, versions, portfolio, orbit platform)
- **Core Tech Stack:** React/Next.js, Node.js, Stripe, Vercel (prj_LPVAL11Ktp3jTVV80thWgPlCzxIr)
- **Deployment:** Vercel multi-project
- **Primary Agents:** Synthia (client communication), Lightning (deployment)
- **Known Issues:** Auth migration to Auth0 (decision: phased rollout per budget constraints)

**Related Repos:**
```
akash-engine-2.0 (private)
akash-master-files (private)
akash-master-files-2 (private)
akash-master-files-3 (private)
akash-master.1.0 (private)
akash-master-files.2.0 (private)
akash-orbit-platform (private)
AKASHPORTFOLIO (public)
akash-last-edit (private)
```

**Open Brain Entry:**
```json
{
  "project_id": "akash-001",
  "name": "Akash Engine",
  "type": "revenue_product",
  "status": "active_production",
  "description": "Client services platform with $2.5K-$50K monthly retainers",
  "business_model": "SaaS retainers, Vegas + Seattle operations",
  "active_clients": "TBD",
  "revenue_current_month_cents": "TBD",
  "tech_stack": ["React", "Next.js", "Node.js", "Stripe", "PostgreSQL"],
  "deployment": {
    "platform": "Vercel",
    "vercel_project_id": "prj_LPVAL11Ktp3jTVV80thWgPlCzxIr",
    "environments": ["development", "staging", "production"]
  },
  "agents_assigned": ["synthia", "lightning"],
  "recent_decisions": [
    {
      "title": "Auth Migration to Auth0",
      "status": "decided",
      "approach": "phased_rollout",
      "constraint": "budget_limits",
      "timeline": "Q1-Q2 2026"
    }
  ],
  "github_repos": 12,
  "key_contacts": ["Sarah"]
}
```

---

### 3. **New World Kids** (Nonprofit - Food, Water, Energy, Shelter)
- **Status:** Active with ongoing projects
- **GitHub Repos:** Culture Shock Sports, educational content, social impact tools
- **Tech Stack:** Web + mobile tools for food distribution, water access, energy solutions
- **Primary Agents:** Darya (design/brand), Devika (builds social impact tools)

**Related Repos:**
```
culture-shock-sports
culture-shock-sports-cultureshocksports
project-indigo-azul (food forest, Mexico)
new-world-kids-* (various educational tools)
```

**Open Brain Entry:**
```json
{
  "project_id": "nwk-001",
  "name": "New World Kids",
  "type": "nonprofit_social_impact",
  "status": "active",
  "description": "Seattle-based 501c3 providing food, water, energy, shelter to disadvantaged youth",
  "mission": "7-generation thinking, systemic social impact",
  "focus_areas": ["food_distribution", "water_access", "energy_solutions", "shelter"],
  "operating_regions": ["Seattle", "Puerto Vallarta"],
  "agents_assigned": ["darya", "devika"],
  "github_repos": [
    "culture-shock-sports",
    "proyecto-indigo-azul"
  ]
}
```

---

### 4. **Kupuri Media** (Ivette's Company - Web Design + Cultural Heritage)
- **Status:** Active, Wix-focused
- **Business Model:** Web design for women's empowerment, Wixárika cultural heritage focus
- **Tech Stack:** Wix, custom integrations, content management
- **Primary Agent:** Synthia (client strategy)
- **Key Context:** Wife (Ivette Bowers) is founder; birthday Feb 2, 1990; landing page gift deadline was Feb 2, 2026

**Related Repos:**
```
kupuri-* (various Kupuri projects)
agent-kupuri-template
kupuri-media-landing (birthday gift project)
```

**Open Brain Entry:**
```json
{
  "project_id": "kupuri-001",
  "name": "Kupuri Media",
  "type": "for_profit_web_design",
  "status": "active",
  "founder": "Ivette Bowers",
  "focus": ["women_empowerment", "wixarika_cultural_heritage", "web_design"],
  "business_model": "Custom web design, content strategy",
  "locations": ["Puerto Vallarta", "Mexico"],
  "agents_assigned": ["synthia"],
  "recent_projects": [
    {
      "name": "Kupuri Landing Page",
      "deadline": "2026-02-02",
      "status": "completed",
      "type": "birthday_gift"
    }
  ]
}
```

---

### 5. **The Pauli Effect** (Holding Company / AI Solutions)
- **Status:** Operating, overseeing all ventures
- **Business Model:** For-profit AI solutions, holding Akash Engine, consulting, systems design
- **Founder:** Bambu (Jeremy Bowers)
- **Tech Stack:** Cloud-agnostic, multiple stacks per project

**Open Brain Entry:**
```json
{
  "project_id": "paulieffect-001",
  "name": "The Pauli Effect",
  "type": "holding_company",
  "status": "active",
  "founder": "Jeremy Bowers (Bambu)",
  "description": "For-profit AI solutions company overseeing Akash Engine, consulting, system design",
  "subsidiaries": ["akash-engine", "pauli-systems"],
  "operating_philosophy": "7-generation thinking, autonomous systems, minimal human intervention",
  "frameworks": ["PASS (Problem-Amplification-Solution-System)", "MOSel orchestration", "YEDL ethical layer"]
}
```

---

## SECONDARY PROJECTS (Active But Non-Core)

### 6. **Culture Shock Sports** (Youth Basketball/Boxing - Seattle)
```json
{
  "name": "Culture Shock Sports",
  "type": "nonprofit",
  "focus": "Youth basketball and boxing programs in Seattle",
  "github_repos": ["culture-shock-sports"],
  "agents": ["darya"]
}
```

### 7. **Proyecto Indigo Azul** (Food Forest - Puerto Vallarta)
```json
{
  "name": "Proyecto Indigo Azul",
  "type": "nonprofit",
  "focus": "Regenerative food forest providing food security",
  "location": "Puerto Vallarta, Mexico",
  "github_repos": ["project-indigo-azul"],
  "agents": ["devika"]
}
```

### 8. **PAULI (Persistent Autonomous Universal Learning Intelligence)**
- **Status:** Long-term vision, foundational work in progress
- **Description:** Voice-controlled AI avatar embodying complete knowledge base for future generations
- **Tech Stack:** LiteLLM, LibreChat, Coolify self-hosted
- **Related Repos:** pauli-ecosystem (32M), PAULI-AI-Tower

---

## GITHUB REPOS CLASSIFICATION & AGENT ASSIGNMENTS

### CRITICAL/ACTIVE (Mapped to ARCHON-X Agents)

#### Pauli (Analytical Brain - Data, Analysis, Logic)
```csv
repo_name,status,category,priority,assigned_agent,notes
archonx-os,active,core_system,p1,pauli,Zero-Touch Engineering orchestration
pauli-brain-persona,active,agent_system,p1,pauli,Self-aware analytical persona
pauli-ecosystem,active,knowledge_system,p1,pauli,32M knowledge base
PAULI-AI-Tower,planning,infrastructure,p1,pauli,Self-hosted LiteLLM + LibreChat
```

#### Synthia (Creative Brain - Communication, Synthesis, Design)
```csv
repo_name,status,category,priority,assigned_agent,notes
archonx-synthia,active,agent_system,p1,synthia,Microservice for Synthia persona
kupuri-media-landing,completed,client_project,p0,synthia,Birthday gift for Ivette
darya-design-throne,active,design_system,p2,synthia,Design collaboration with Darya
```

#### Guardian Fleet (Specialized Agents)

**Darya (Design & Brand):**
```csv
repo_name,status,category,priority,assigned_agent,notes
Darya-designs,active,design_system,p1,darya,Design assets and brand systems
darya-design-throne,active,design_system,p1,darya,Advanced design workspace
artist-fold-gallery,planning,design_product,p3,darya,Artist portfolio platform
```

**Devika (Code & Building):**
```csv
repo_name,status,category,priority,assigned_agent,notes
devika-agent,active,agent_system,p1,devika,Autonomous coding agent
devika-pi-governance,active,governance,p2,devika,Constitutional AI governance
GPT-Agent-im-ready-main,review,agent_system,p2,devika,Agent framework evaluation
```

**Lightning (Deployment & Automation):**
```csv
repo_name,status,category,priority,assigned_agent,notes
agent-lightning,active,agent_system,p1,lightning,Deployment automation agent
agent-lightning-memory,active,memory_system,p1,lightning,Context for rapid iteration
akash-engine-deployment,active,infrastructure,p1,lightning,Client platform deployment
```

---

## FULL REPO INVENTORY (All 316 - Summarized by Category)

### Category: AI/Agent Systems (45 repos)
```
ARCHON-X related: archonx-os, ARCHON-X2.0, archon-lovable-nexus, archonx-synthia, archon-ghl-automator
Agent frameworks: agent-zero-Fork, agent-lightning, devika-agent, agent-kupuri-template
Memory/RAG: -lightning-claude-memory-agent, coding_agent_session_search, coding_agent_usage_tracker
OpenClaw/Computer Use: ai-sdk-computer-use, clawdbot-Whatsapp-agent, openclaw-integration
Other agents: darya-design-agent, vibe-coding-suite
```

### Category: Web/SaaS Applications (80+ repos)
```
Client platforms: akash-engine-2.0, akash-master-files (multiple versions), AKASHPORTFOLIO
E-commerce: -e-commerce-remix, auto-shop-turkey, base-stack-vite
Design/Creative: artist-fold-gallery, darya-next-js-landing-page, cinematicsmart-funnels
Social/Community: CLONELY-FANZ, cult-directory-template, ECO-TOUR-DIRECTORY
```

### Category: Design & Brand (30+ repos)
```
Darya's work: Darya-designs, darya-design-throne, darya-design-agent
Brand assets: arkan-os-branding, ARCHON-X branding materials
Design tools: codex-craft-forge, artist-fold-gallery, visual-design-studio
```

### Category: Content & Funnels (25+ repos)
```
Video/Media: AI-Youtube-Shorts-Generator, pauli-comic-funnel, StoryToolkitAI
Sales funnels: cinematic-smart-funnels-launchpad, CHEGGIE-AI-Trader
Content platforms: botanical-memories, digital-odyssey-scroll
```

### Category: Business/Revenue (20+ repos)
```
Stripe/Billing: theater-billing, stripe-minions-architecture
Analytics: analytics-dashboard, PAULI-analytics-engine
Finance: cheggie-lifestyle-finance, CHEGGIE-AI-Trader
```

### Category: Education/Learning (15+ repos)
```
Learning platforms: amentislibrary, animeta-roblox-craft, learn-*
Knowledge tools: knowledge-extractor, -yt-knowledge-extractor
```

### Category: Social Impact (10+ repos)
```
Nonprofits: culture-shock-sports, new-world-kids-*, proyecto-indigo-azul
Sustainability: eco-tour-*, breatheinternational
```

### Category: Experimental/Exploration (50+ repos)
```
Forks & experiments: BMAD-METHOD, black-mirror, botanical-memories, balldontlie
Prototypes: AionUi-cowork, AVATAR, crystal-memory-cube
Early stage: ani-maze, animeta-roblox-craft, apify-studiobuilder
```

### Category: Archived/Low Priority (100+ repos)
```
Status: archived or stale (>6 months no commits)
Examples: airbnbauto, aiwear-trend-hub, allweatherroofs, blockerbuiltautosales
Action: Review quarterly, clean up or reactivate
```

---

## VECTOR DB SEEDING SCRIPT

### Import All Repos & Projects

```sql
-- Seed github_repos table from inventory
INSERT INTO github_repos (
  repo_name, repo_url, owner, is_private, is_fork, 
  status, priority, associated_projects, description
)
VALUES
-- ARCHON-X Core
('archonx-os', 'https://github.com/executiveusa/archonx-os', 'executiveusa', false, false, 'active', 1, ARRAY['ARCHON-X OS'], 'Zero-Touch Engineering OS'),
('archonx-synthia', 'https://github.com/executiveusa/archonx-synthia', 'executiveusa', false, false, 'active', 1, ARRAY['ARCHON-X OS'], 'Synthia persona microservice'),
('orgo-agent', 'https://github.com/executiveusa/orgo-agent', 'executiveusa', false, false, 'active', 1, ARRAY['ARCHON-X OS'], 'Computer-use agent'),

-- Akash Engine
('akash-engine-2.0', 'https://github.com/executiveusa/akash-engine-2.0', 'executiveusa', true, false, 'active', 1, ARRAY['Akash Engine'], 'Client services platform v2'),
('AKASHPORTFOLIO', 'https://github.com/executiveusa/AKASHPORTFOLIO', 'executiveusa', false, false, 'active', 2, ARRAY['Akash Engine'], 'Portfolio showcase'),

-- Darya Design
('Darya-designs', 'https://github.com/executiveusa/Darya-designs', 'executiveusa', false, true, 'active', 1, ARRAY['Kupuri Media'], 'Design system assets'),
('darya-design-throne', 'https://github.com/executiveusa/darya-design-throne', 'executiveusa', true, false, 'active', 2, ARRAY['Kupuri Media'], 'Advanced design workspace'),

-- Agents
('agent-lightning', 'https://github.com/executiveusa/agent-lightning', 'executiveusa', false, true, 'active', 1, ARRAY['ARCHON-X OS'], 'Deployment automation'),
('devika-agent', 'https://github.com/executiveusa/devika-agent', 'executiveusa', false, true, 'active', 1, ARRAY['ARCHON-X OS'], 'Autonomous coding'),
-- ... (310 more rows for all repos)
ON CONFLICT (repo_name) DO UPDATE SET status = EXCLUDED.status;

-- Seed projects table
INSERT INTO projects (
  name, status, owner, team, description, 
  github_repos, deployment_status, budget_cents
)
VALUES
('ARCHON-X OS', 'active', 'Bambu', ARRAY['Pauli', 'Synthia'], 'Autonomous zero-touch engineering system', 
 ARRAY['archonx-os', 'archonx-synthia', 'orgo-agent'], 'production_pending_config', 0),

('Akash Engine', 'active', 'Bambu', ARRAY['Synthia', 'Lightning'], 'Client services platform', 
 ARRAY['akash-engine-2.0', 'AKASHPORTFOLIO'], 'production', 250000),

('Kupuri Media', 'active', 'Ivette', ARRAY['Darya', 'Synthia'], 'Web design for cultural heritage',
 ARRAY['Darya-designs', 'kupuri-media-landing'], 'production', 0),

('New World Kids', 'active', 'Bambu', ARRAY['Devika'], 'Food security and shelter for disadvantaged youth',
 ARRAY['culture-shock-sports'], 'development', 0)
ON CONFLICT (name) DO UPDATE SET last_updated = NOW();
```

---

## AGENT-TO-PROJECT MATRIX

```
Agent              | Primary Projects           | Secondary Projects          | Specialization
---|---|---|---
Pauli              | ARCHON-X OS, Pauli        | All (data, analysis)       | Analytics, logic, diagnostics
Synthia            | Akash Engine, Kupuri      | New World Kids             | Communication, synthesis
Darya              | Kupuri Media              | Pauli Ecosystem            | Design, branding, aesthetics
Devika             | ARCHON-X OS              | New World Kids             | Code, infrastructure, automation
Lightning          | Akash Engine              | ARCHON-X OS                | Deployment, CI/CD, DevOps
Guardian Fleet     | All (rotating)            | Emergency response         | Coordination, governance
```

---

## DEPLOYMENT READINESS CHECKLIST

### ARCHON-X OS
- [x] Core system built and tested (15/15 tests passing)
- [ ] `coolify.app_uuid` configured
- [ ] `coolify.base_url` set
- [ ] `COOLIFY_API_KEY` added to environment
- [ ] `ORGO_API_TOKEN` added to environment
- [ ] Vault master.env rotated (12 critical keys flagged)
- [ ] All 64 agents initialized and heartbeat verified

### Akash Engine
- [x] Production code stable
- [x] Vercel deployment configured
- [ ] Auth0 migration Phase 1 approved by Sarah
- [ ] Budget allocation approved
- [ ] Client onboarding docs updated

### Kupuri Media
- [x] Landing page completed (birthday gift delivered)
- [ ] Wix integration scripts deployed
- [ ] Content management pipeline established

---

## NEXT STEPS FOR OPEN BRAIN

1. **Today:**
   - Export this mapping as CSV
   - Import all repos into `github_repos` table
   - Seed all projects into `projects` table

2. **This week:**
   - Run Notion sync script to bring in all decisions & project metadata
   - Generate embeddings for all 316 repos
   - Start capturing daily thoughts in Slack

3. **Next week:**
   - Wire all agents to Open Brain MCP server
   - Test semantic search across repos & projects
   - Document key findings

4. **Ongoing:**
   - Maintain weekly sync from Notion
   - Keep GitHub repos inventory updated
   - Capture decisions as they're made

---

## CONTACT & CONTEXT REFERENCES

**Founder:** Bambu (Jeremy Bowers)  
**Key Contacts:**
- Ivette Bowers (wife, Kupuri Media founder) - Birthday: Feb 2, 1990
- Sarah (Akash Engine stakeholder, budget constraints)
- Meish (legal defense case - separate legal dashboard in Cloudflare D1)

**Infrastructure Locations:**
- Seattle (primary operations)
- Puerto Vallarta, Mexico (secondary operations with Ivette)
- Cloud: Vercel (50+ projects), Coolify/Hostinger VPS, Railway, GitHub (200+ repos)

---

**This mapping is your foundation for Open Brain. Everything connects through the vector database.**
