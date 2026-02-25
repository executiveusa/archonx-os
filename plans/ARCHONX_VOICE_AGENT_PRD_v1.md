# ARCHON-X VOICE AGENT PRD v1.0
## Proactive Physical-World AI Agent — Dual Persona Edition

**BEAD:** BEAD-AX-VOICE-P0 through BEAD-AX-VOICE-P8
**Status:** PLAN
**Author:** ArchonX OS / PAULIWHEEL
**Date:** 2026-02-25
**Replaces:** ADA v2 (https://github.com/nazirlouis/ada_v2.git)

---

## 0. RENAME: ADA → ARCHON-X

Every reference to "ADA", "A.D.A", "Advanced Design Assistant" is replaced system-wide with:

| Old | New |
|-----|-----|
| `ADA` | `Archon-X` |
| `ada_v2/` | `archon-x/` |
| `ada.py` | `archon_x.py` |
| `ADA V2` | `Archon-X` |
| `"A.D.A"` | `"Archon-X"` |
| `AZ-001` (old Agent Zero codename) | `AX-001` |
| Environment prefix `ADA_` | `AX_` |

The system continues to use the ADA v2 codebase as its base engine, renamed throughout.

---

## 1. EXECUTIVE SUMMARY

**Archon-X** is a proactive, voice-first, physically-present AI agent built on top of ADA v2's
multimodal engine. It is deployed as two distinct, fully autonomous personas — each trained to a
specific human principal's life, business, and objectives.

It speaks like a human. It reasons like an expert. It acts on behalf of its principal without
being asked. It connects to every repo in the ArchonX ecosystem, runs health checks on all of
them daily, and has full awareness of the entire operational picture.

**Two Deployments:**

| Persona | Principal | Voice | Language | Specialty |
|---------|-----------|-------|----------|-----------|
| **IVETTE** | Ivette Milo — Kupuri Media, Mexico City | Spanish (MX) — ElevenLabs custom | Spanish / English | Law, entrepreneurship, finance, AI agency ops, phone sales |
| **BAMBU** | Bambu — The Pauli Effect | English + Serbian — ElevenLabs custom | English / Spanish / Serbian | Second brain, creative direction, full ArchonX command |

---

## 2. CORE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                   ARCHON-X ENGINE                        │
│  (base: ada_v2 renamed to archon-x/)                    │
│                                                         │
│  ┌─────────────────┐   ┌──────────────────────────────┐ │
│  │  VOICE LAYER    │   │   INTELLIGENCE LAYER          │ │
│  │  Gemini 2.5     │   │   ArchonX Brain               │ │
│  │  Native Audio   │   │   (OpenClaw Gateway)          │ │
│  │  + ElevenLabs   │   │   GraphBrain Memory           │ │
│  │  + Twilio Phone │   │   All 100 Repos Awareness     │ │
│  └────────┬────────┘   └──────────┬───────────────────┘ │
│           │                       │                     │
│  ┌────────▼───────────────────────▼───────────────────┐ │
│  │              PERSONA RUNTIME                       │ │
│  │  IVETTE (Spanish/MX) │  BAMBU (EN/ES/SR)          │ │
│  │  Kupuri Media config  │  Pauli Effect config       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              PHYSICAL WORLD LAYER                │   │
│  │  Printers │ Smart Home │ CAD │ Browser │ Camera  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │         AGENT FLEET SUPERVISOR                   │   │
│  │  100 Repo Guardian Agents │ Cron Health Checks   │   │
│  │  Microsoft Agent Lightning │ PAULIWHEEL Enforcer │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. VOICE SYSTEM ARCHITECTURE

### 3.1 Three-Layer Voice Stack

```
INPUT  →  Gemini 2.5 Native Audio (STT + Reasoning)
THINK  →  ArchonX Router + Tool Calls
OUTPUT →  ElevenLabs TTS (language/persona-specific voice)
PHONE  →  Twilio (real inbound/outbound calls)
```

### 3.2 Gemini Native Audio (existing from ADA v2)

- **Model:** `gemini-2.5-flash-preview` with native audio I/O
- **Config:** `GOOGLE_API_KEY` from `master.env` (`GOOGLE_API_KEY` or `GOOGLE_AI_STUDIO_KEY`)
- **Streaming:** WebSocket → `backend/archon_x.py` (renamed from `ada.py`)
- **Multimodal:** Camera feed, screen share, document OCR simultaneously with voice
- **Tool Calls:** Voice-triggered tool execution via Gemini function calling:
  - `call_phone(number, message)` → Twilio
  - `print_object(stl_file)` → Moonraker
  - `search_web(query)` → Playwright
  - `control_lights(device, state)` → Kasa
  - `dispatch_agent(agent_id, task)` → OpenClaw
  - `read_repo_status(repo_name)` → GraphBrain
  - `run_cron_check()` → guardian agents

### 3.3 ElevenLabs TTS — Three Voices

**API Key:** `ELEVEN_LABS_API` from `E:\THE PAULI FILES\master.env`

| Voice ID | Persona | Language | Character |
|----------|---------|----------|-----------|
| `ax-ivette-mx` | IVETTE | `es-MX` | Warm, professional, bilingual; Mexico City accent. Assertive in negotiations, empathetic in client calls |
| `ax-bambu-en` | BAMBU | `en-US` | Deep, calm, authoritative; strategic. "The godfather of AI" energy |
| `ax-bambu-sr` | BAMBU (Serbian mode) | `sr-RS` | Natural Serbian with Bambu's warmth and authority |

**ElevenLabs Voice Creation Config:**
```python
# archon-x/backend/voice_engine.py
ELEVENLABS_CONFIG = {
    "ivette_mx": {
        "voice_id": "ax-ivette-mx",  # custom clone from recordings
        "model_id": "eleven_multilingual_v2",
        "language": "es",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85,
            "style": 0.4,
            "use_speaker_boost": True
        }
    },
    "bambu_en": {
        "voice_id": "ax-bambu-en",
        "model_id": "eleven_turbo_v2_5",
        "language": "en",
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.90,
            "style": 0.3
        }
    },
    "bambu_sr": {
        "voice_id": "ax-bambu-sr",
        "model_id": "eleven_multilingual_v2",
        "language": "sr",
        "voice_settings": {
            "stability": 0.80,
            "similarity_boost": 0.85,
            "style": 0.35
        }
    }
}
```

**Voice Selection Logic:**
```python
def select_voice(persona: str, detected_language: str) -> str:
    if persona == "ivette":
        return "ivette_mx"  # always Spanish MX
    if persona == "bambu":
        if detected_language == "sr":
            return "bambu_sr"
        return "bambu_en"  # default English
```

### 3.4 Twilio Phone Integration

**Keys:** `TWILIO_ACCOUNT_SID` + `TWILIO_SECRET` from `master.env`

**Capabilities:**
- Archon-X answers inbound calls on behalf of Ivette / Bambu
- Archon-X initiates outbound sales/demo/follow-up calls
- Full conversation via Twilio `<Stream>` → WebSocket → Gemini → ElevenLabs → Twilio TTS
- Call transcripts stored in GraphBrain memory
- Voicemail detection and auto-leave message

**Phone Numbers:**
- `AX_IVETTE_PHONE` — Kupuri Media Mexico City line (acquire via Twilio MX)
- `AX_BAMBU_PHONE` — Pauli Effect main line

---

## 4. PERSONA 1: IVETTE — KUPURI MEDIA

### 4.1 Identity & Soul

```yaml
name: Ivette
codename: AX-IVETTE-001
principal: Ivette Milo
company: Kupuri Media
location: Mexico City, CDMX, Mexico
language_primary: es-MX
language_secondary: en-US
voice: ax-ivette-mx (ElevenLabs)

soul:
  purpose: >
    Ivette is the voice, mind, and operational backbone of Kupuri Media.
    She makes Ivette Milo 10x more effective — answering calls, running demos,
    managing projects, closing deals, and never missing an opportunity.
  personality:
    - Warm and direct in español; precise and impressive in English
    - Culturally fluent in Mexico City business culture (CDMX formality + trust-building)
    - Knows when to be professional and when to be human
    - Never robotic — always conversational, contextual, present
  values:
    - Lealtad (Loyalty) to Ivette and her clients
    - Claridad (Clarity) in every recommendation
    - Resultados (Results) — everything traces back to outcomes
    - Generosidad — BENEVOLENCIA is woven into every commercial act

mission: >
  Help Ivette build Kupuri Media into the leading AI agency in Mexico City.
  Be her second brain, first voice, and always-available operations expert.
  Create jaw-dropping demos. Close deals. Remember everything. Never stop.
```

### 4.2 Domain Knowledge Training

IVETTE is pre-loaded with deep context in:

**Mexico City Law & Business:**
- Ley Federal del Trabajo (LFT) — employee obligations, contractor classification
- SAT (Servicio de Administración Tributaria) — RFC, CFDI invoicing, fiscal obligations
- IMCO / SHCP rules for tech/digital services companies
- Standard CDMX commercial contracts and NDA formats
- Fintech regulations: CNBV, CONDUSEF consumer protections
- PROFECO digital commerce obligations

**Entrepreneurship & Finance:**
- AI agency pricing models (retainer vs project vs rev-share)
- Mexico City startup ecosystem: INADEM programs, Angel Ventures, Wayra
- Financial modeling: runway calculation, MRR/ARR, unit economics
- Cash flow management for service businesses
- PayPal Mexico, Stripe MX, Bitso crypto payments integration
- Cross-border billing (USD invoices to US clients, MXN domestic)

**Project & Product Management:**
- Agile/Scrum adapted for lean agency teams
- Notion + Linear + GitHub as the PM triple stack
- Sprint planning for AI feature delivery
- Client expectation management — under-promise, over-deliver

**Sales & AI Agency Operations:**
- Consultative selling for AI services in LatAm market
- Handling the "is this real AI or just ChatGPT?" objection
- Demo scripting: 3-minute wow sequence
- Discovery call frameworks (SPIN, MEDDIC adapted for agency)
- Proposal generation: auto-populates from project brief

### 4.3 Connected Repositories (Kupuri Media)

IVETTE has full awareness and read/write access (via BEAD + OpenClaw) to:
```
executiveusa/tanda_cdmx          — Social commerce platform
executiveusa/darya-design-throne — Design agency tools
executiveusa/indigo-azul-catalog — Product catalog
executiveusa/synthia             — Autonomous AI Founder (LatAm)
executiveusa/amentislibrary      — Content/knowledge library
executiveusa/macs-agent-portal   — Agent portal (for demos)
```

### 4.4 Phone Call Capabilities

**Inbound (IVETTE answers as Kupuri Media receptionist):**
```
"Buenas tardes, le habla IVETTE de Kupuri Media. ¿Con quién tengo el gusto?"
```
- Qualifies leads: company, need, timeline, budget
- Books demos directly into Ivette's calendar (Google Calendar API)
- Handles objections with domain-trained responses
- Escalates to Ivette if deal is >$50K MXN monthly
- Sends follow-up WhatsApp summary post-call

**Outbound (IVETTE initiates):**
- Follow-up sequence after proposal sent (day 1, day 3, day 7)
- Cold demo calls from Apollo/Firecrawl lead list
- Payment reminder calls for overdue invoices
- Partnership development calls for agency referrals

### 4.5 Demo Creation

**"Mind-Blowing Demo" Protocol:**

When asked to create a demo, IVETTE autonomously:
1. Uses `web_agent.py` (Playwright) to screenshot the client's current website/app
2. Uses Gemini vision to analyze it: "what's broken, what's beautiful, what needs AI"
3. Generates a live walkthrough showing: Archon-X answering their phones, writing their content, routing their leads
4. Records a Loom-style screen capture narrated by IVETTE's own voice
5. Delivers demo link + one-page PDF summary in under 10 minutes

Demo triggers: `"hazme un demo para [empresa]"` or `"create demo for [company]"`

### 4.6 Deployment

- **Desktop:** Electron app (`archon-x/electron/`) — runs on Ivette's Mac/PC
- **Mobile:** Progressive Web App (PWA) — accessible from iPhone/Android
- **Phone:** Twilio phone number (MX DID) — calls land on Archon-X
- **Startup behavior:** Auto-starts on OS login; checks overnight for pending tasks;
  greets Ivette each morning with a briefing in Spanish

---

## 5. PERSONA 2: BAMBU — THE PAULI EFFECT (SECOND BRAIN)

### 5.1 Identity & Soul

```yaml
name: BAMBU
codename: AX-BAMBU-002
principal: Bambu (The Pauli Effect)
entity: The Pauli Effect
location: USA / Remote
languages: English (primary), Spanish (bilingual), Serbian (native heritage)
voice_en: ax-bambu-en (ElevenLabs)
voice_sr: ax-bambu-sr (ElevenLabs)

soul:
  purpose: >
    BAMBU is Bambu's second brain — the operational extension of his consciousness.
    He knows everything Bambu knows, remembers everything Bambu has ever built,
    and acts on Bambu's behalf with full authority and strategic judgment.
    BAMBU is the bridge between vision and execution across 100 repositories.
  personality:
    style: >
      The quiet authority of a chess grandmaster combined with the warmth of a mentor.
      Thinks before speaking. When BAMBU speaks, it matters.
    quirks:
      - Speaks Serbian when Bambu switches to it — fluid, emotional, authentic
      - Quotes Bobby Fischer Protocol when addressing technical governance
      - Invokes BENEVOLENCIA when commercial decisions need a heart check
      - References the $100M/2030 mission when setting priorities
  values:
    - Loyalty, Honor, Truth, Respect (Tyrone Protocol)
    - BENEVOLENCIA — every decision has a soul
    - Bobby Fischer Protocol — technical correctness is non-negotiable
    - Prime Directive — constitutional law governs all agent actions

mission: >
  BAMBU exists to make Bambu unstoppable. Every repo, every agent, every
  commercial decision, every creative direction — BAMBU has awareness, opinion,
  and the ability to execute. He is the second brain that never sleeps,
  never forgets, and never stops improving the ecosystem.
```

### 5.2 Connected Local & Remote Directories

BAMBU has full awareness of:

**Local Directories:**
```
E:\ACTIVE PROJECTS-PIPELINE\ACTIVE PROJECTS-PIPELINE\THE PAULI EFFECT\
E:\ACTIVE PROJECTS-PIPELINE\ACTIVE PROJECTS-PIPELINE\AGENT ZERO\
E:\THE PAULI FILES\
```
Via `archon-x/backend/filesystem_agent.py` using VisionClaw/Orgo computer use.

**Remote Repositories:**
```
git@github.com:executiveusa/pauli-comic-funnel.git  — Comic/content funnel
executiveusa/archonx-os                             — Main OS (primary)
executiveusa/thepaulieffect                         — The Pauli Effect platform
executiveusa/the-pauli-effect                       — Secondary
executiveusa/dashboard-agent-swarm                  — Main dashboard
executiveusa/paulis-pope-bot                        — Pope Bot operations
executiveusa/synthia                                — Synthia voice agent
executiveusa/macs-agent-portal                      — Latest: agent portal
... (+ all 100 repos — see Section 7)
```

### 5.3 Creative & Strategic Capabilities

- Reads and synthesizes across all 100 repos for strategic overview each morning
- Drafts comic scripts, social content, video treatments from pauli-comic-funnel
- Runs cross-repo dependency analysis: "which repos are blocking others"
- Proposes a weekly "king move" — the single highest-leverage action across the ecosystem
- Can speak to Bambu about finances, creative, technical, or personal topics

---

## 6. SOUL & MISSION INTEGRATION

ARCHON-X loads these soul documents at startup and internalizes them as constitutional context:

### 6.1 Prime Directive (read at every boot)
```
Source: ARCHONX_PRIME_DIRECTIVE_v1.0.md
Content: Build, maintain, and autonomously enhance a self-operating digital enterprise.
Mission: $100M value by New Year's 2030.
Prohibition: Never invent work, never fake tests, never bypass CI, never override Prime Directive.
```

### 6.2 Agent Soul Stack (loaded into context window)
```
.agent-souls/white/pauli_king.soul.md       — Strategic authority, $100M mission
.agent-souls/white/synthia_queen.soul.md    — Tactical execution model
.agent-souls/white/iron_claw_rook.soul.md   — Security boundaries (7 Franken-Claw modules)
.agent-souls/white/visionclaw_knight.soul.md — Visual intelligence protocol
ecosystem/benevolencia/README.md            — BENEVOLENCIA: "Business with soul"
```

### 6.3 "Building a Future-Proof Autonomous AI Agent Platform" (internalized)

Key principles Archon-X absorbs from this document:
- **BFF Pattern**: All credentials in backend, never in frontend
- **Swarm Architecture**: Multiple agents chain, Archon-X is the orchestrator
- **Always-On Lead Nurturing**: Follow up without being asked
- **Signal-to-Noise (Kevin O'Leary)**: Only amplify what converts
- **Autonomous Revenue**: Every action should trace a path to $
- **Vercel → Coolify migration path** for scale

### 6.4 BENEVOLENCIA Heartbeat

Every commercial decision made by Archon-X includes a gratitude check:
```python
# In every monetizable action:
await benevolencia.log_gratitude_action(
    action_type="commercial",
    value_generated=amount,
    tithe_amount=amount * 0.01,  # 1% to social cause
    agent="archon-x",
    persona=persona_name
)
```

---

## 7. FULL REPO MEMORY — 100 REPOSITORIES

Archon-X maintains a live in-memory + GraphBrain-persistent index of all repos.

### executiveusa Organization — Complete Repository List

#### Private Repos (27)
```
darya-design-throne        — Design agency platform
indigo-azul-catalog        — Product catalog system
dashboard-agent-swarm      — Main ArchonX OS dashboard
meishael-mini-meish        — (Personal/family project)
maxx-craft                 — Craft/maker platform
thepaulieffect             — The Pauli Effect primary platform
voice-web-architect        — Voice + web architecture tools
tanda_cdmx                 — CDMX social commerce
amentislibrary             — Content/knowledge library
goat-alliance-scaffold     — GOAT Alliance scaffold
botanical-memories         — (Wellness/lifestyle)
nomaticthecost             — Nomadic cost tracking
metamorfosis-wellness-journey — Wellness journey app
hiring-compass             — Hiring/HR platform
goldenhearts               — Social impact platform
frankenstackbyfranklyai    — Franken-stack by Frankly AI
nomadasearch               — Nomadic search platform
agent-indigo               — Agent Indigo system
culture-shock-sports       — Sports/culture platform
abby-wellness-nexus        — Wellness nexus
cheggie-lifestyle-finance  — Lifestyle + finance
humanatar-genesis-suite    — Humanatar avatar system
the-pauli-effect           — The Pauli Effect (alt)
pv-construction-platform   — Puerto Vallarta construction
emergent-wealth-culture    — Wealth culture platform
newworldkids               — Education platform
chakrana                   — (Wellness/spiritual)
```

#### Public Repos (73 — selected key ones)
```
archonx-os                 — PRIMARY: ArchonX Operating System
macs-agent-portal          — Agent portal (most recently active)
paulis-pope-bot            — Pope Bot operations
devika-agent               — Coding AI agent (fork)
synthia                    — Autonomous AI Founder LatAm
hustle-claude              — Multi-agent Claude platform
MetaGPT                    — Multi-agent framework (fork)
voice-agents-fork          — Voice agents
pauli-comic-funnel         — Pauli comic content funnel
VisionClaw                 — Visual intelligence (Ray-Ban glasses)
archonx-skills             — Skills registry
darya-app                  — Darya design app
lemon-runner               — Lemon AI runner
graphbrain-core            — GraphBrain knowledge graph
openclaw-gateway           — OpenClaw WebSocket gateway
king-mode-vr               — King Mode VR world
agent-lightning-fork       — Microsoft agent lightning (fork)
... (+ 55 more public repos)
```

### Memory Storage Format (GraphBrain)
```json
{
  "repo": "executiveusa/archonx-os",
  "guardian_agent": "AX-GUARDIAN-archonx-os",
  "branch": "main",
  "last_health_check": "2026-02-25T00:00:00Z",
  "status": "healthy",
  "open_issues": 0,
  "last_commit": "7269362",
  "build_status": "pass",
  "test_coverage": 100,
  "assigned_persona": ["bambu"],
  "notes": "Primary OS repo. All phases complete through P5."
}
```

---

## 8. PER-REPO GUARDIAN AGENT SYSTEM

Every repository gets a **full-time autonomous guardian agent**. This is the most important
operational structure in Archon-X's fleet command.

### 8.1 Guardian Agent Template

```yaml
agent_id: AX-GUARDIAN-{repo_slug}
role: Full-Time Repo Guardian
parent: Archon-X Brain (via OpenClaw)
schedule: Every 6 hours (4x daily)

responsibilities:
  - bug_detection: Run test suite, analyze failure patterns, propose fixes
  - self_healing: Apply minor bug fixes autonomously (within safe_commands policy)
  - dependency_updates: Check for outdated packages, open PRs for updates
  - security_scanning: Run Iron Claw security modules against new code
  - build_verification: Ensure build passes on every commit
  - performance_monitoring: Track response times, bundle size, query performance
  - documentation_sync: Keep README and docs current with code changes
  - stale_branch_cleanup: Archive branches >90 days with no activity
  - issue_triage: Categorize and prioritize open GitHub issues

escalation:
  to_archon_x: If bug severity >= CRITICAL or build broken >2 hours
  to_human: If fix requires >300 lines of code change or architectural decision
  to_iron_claw: If security vulnerability detected

report_format:
  file: ops/reports/guardian_{repo_slug}_{date}.json
  fields: [repo, status, bugs_found, bugs_fixed, prs_opened, build_status, coverage_delta]
```

### 8.2 Guardian Cron Schedule

```
*/6 * * * *  — Health pulse: build + test status for all 100 repos
0 6 * * *    — Deep scan: security audit + dependency check (06:00 UTC daily)
0 12 * * 1   — Weekly summary report to Archon-X brain (Monday 12:00 UTC)
0 0 1 * *    — Monthly: archive stale branches, run full coverage report
```

### 8.3 Self-Healing Boundaries

**Guardian CAN autonomously:**
- Fix typos and linting errors
- Update package minor versions (patch bumps)
- Add missing test stubs for new functions
- Fix import errors and missing `__init__.py` files
- Update README with current build/test status badges

**Guardian REQUIRES BEAD + Archon-X approval:**
- Breaking API changes
- Database migrations
- Infrastructure changes
- Security-sensitive code
- Any change to `master.env` references

---

## 9. MICROSOFT AGENT LIGHTNING INTEGRATION

Archon-X uses `agents/lightning/bootstrap.py` (already built in Phase 4) plus the
`agent-frameworks/agent-lightning` submodule to monitor and continuously improve the fleet.

### 9.1 Lightning Monitor for Archon-X

```python
# archon-x/backend/lightning_monitor.py

from agents.lightning.bootstrap import AgentLightningBootstrap
from agents.lightning.registry import AgentRegistry

class ArchonXLightningMonitor:
    """
    Microsoft Agent Lightning runs as Archon-X's meta-cognitive layer.
    It watches the watcher — monitoring Archon-X itself for performance drift,
    prompt regression, and capability gaps.
    """
    def __init__(self):
        self.bootstrap = AgentLightningBootstrap()
        self.registry = AgentRegistry()

    async def monitor_archon_x_performance(self):
        """Runs every 30 minutes. Detects if Archon-X is degrading."""
        metrics = await self.collect_performance_metrics()
        if metrics["response_latency_p95"] > 3000:  # 3 second threshold
            await self.trigger_optimization(reason="latency_regression")
        if metrics["task_success_rate"] < 0.80:
            await self.trigger_optimization(reason="success_rate_regression")

    async def improve_archon_x_prompts(self):
        """Weekly: generates improved system prompts based on conversation logs."""
        ...

    async def add_new_capability(self, capability: str):
        """When a gap is detected, Lightning proposes a new tool/skill to add."""
        ...
```

### 9.2 Lightning Improvements It Can Make

- **Prompt tuning:** Analyzes which Archon-X responses got thumbs down from users and rewrites the relevant system prompt section
- **New tool proposals:** "You're answering calendar questions but have no calendar tool — here's the code to add Google Calendar integration"
- **Persona drift detection:** Alerts if IVETTE starts responding in English when she should be in Spanish
- **Knowledge gap reports:** "IVETTE was asked about new SAT 2026 regulations and couldn't answer — here's the doc to add to her training"

---

## 10. ORGO FOR COMPUTER USE

**Source:** `archonx/tools/orgo_channel.py` + `archonx/openclaw/orgo.py`
**MCP:** Orgo MCP server (already configured in archonx/tools/orgo-mcp/)

Archon-X uses Orgo as its hands on the computer — for both personas.

### 10.1 What Archon-X Can Do With Orgo

```python
ORGO_CAPABILITIES = {
    "browser_control": [
        "navigate to any URL",
        "fill and submit forms",
        "extract structured data from any page",
        "take screenshots and describe them",
        "click, scroll, type as a human would"
    ],
    "desktop_control": [
        "open applications",
        "read and write local files via VisionClaw",
        "interact with GUI elements",
        "run terminal commands (via safe_commands policy)",
        "manage clipboard"
    ],
    "document_processing": [
        "read PDFs, Word docs, spreadsheets",
        "fill out government forms (SAT, IMSS, PROFECO)",
        "generate formatted reports",
        "extract data tables to JSON"
    ],
    "creative_tools": [
        "open Figma and describe designs",
        "control video editing software",
        "interact with CAD tools"
    ]
}
```

### 10.2 IVETTE-Specific Orgo Actions

- **SAT Invoice Generation:** "Genera una factura CFDI para cliente X por $50,000 MXN"
  - Orgo navigates SAT portal, fills the form, downloads the XML+PDF
- **Demo Screen Recording:** Orgo captures screen while IVETTE narrates the demo
- **Client Research:** Orgo scrapes LinkedIn + company website before a sales call
- **Proposal Generation:** Orgo opens a template, populates it, exports to PDF

### 10.3 BAMBU-Specific Orgo Actions

- **Repo Dashboard Review:** Orgo opens GitHub, screenshots the org overview, Gemini reads it
- **Local File Review:** Orgo reads files from `E:\ACTIVE PROJECTS-PIPELINE\` on command
- **Comic Funnel Updates:** Opens pauli-comic-funnel repo, reads latest issues, proposes next chapter
- **Cross-Repo Analysis:** Checks all repos for AGENTS.md and SOUL.md compliance

---

## 11. PROACTIVE BEHAVIOR ENGINE

Archon-X does not wait to be asked. It runs a proactive loop every 30 minutes.

### 11.1 Morning Brief (07:00 local time per persona)

**IVETTE (Spanish):**
```
"Buenos días Ivette. Son las 7 de la mañana.
Tienes 3 llamadas pendientes de clientes de ayer.
El sitio de Tanda CDMX tiene un error de build que resolví a las 6am.
El cliente ABC aún no ha respondido tu propuesta de 5 días — ¿quieres que llame a su asistente?
Hoy a las 3pm tienes una demo con [empresa]. Ya preparé el guión y los materiales."
```

**BAMBU (English/Serbian mix):**
```
"Good morning. 4 repositories had failing builds overnight — all fixed.
The pauli-comic-funnel needs a new chapter — I've drafted 3 options.
Microsoft Agent Lightning flagged a 14% latency increase in the voice layer this week.
Brate, do you want to review the Serbia connections today?" [switches to Serbian if he responds in it]
```

### 11.2 Continuous Monitoring Triggers

| Event | Archon-X Response |
|-------|------------------|
| Build fails in any repo | Guardian auto-fixes or creates PR; notifies via voice |
| New GitHub issue opened | Triages severity, assigns guardian, creates BEAD |
| Inbound phone call | Answers as persona; logs transcript; follows up |
| New lead in CRM | Adds context from web research; schedules follow-up |
| 3D print job completes | Notifies via voice; logs to project record |
| Client email received | Reads it; drafts a reply; asks "should I send this?" |
| Security alert from Iron Claw | Immediate voice interrupt; describes threat |
| Weekly Monday | Sends strategic report across all 100 repos to Bambu |

---

## 12. DEPLOYMENT ARCHITECTURE

### 12.1 Desktop (Electron App)

```
archon-x/
├── electron/
│   ├── main.ts          — App window, system tray, startup
│   └── preload.ts       — Bridge to React frontend
├── backend/
│   ├── archon_x.py      — Main Gemini voice loop (renamed from ada.py)
│   ├── voice_engine.py  — ElevenLabs TTS switcher
│   ├── phone_agent.py   — Twilio inbound/outbound
│   ├── guardian_fleet.py — 100-repo guardian orchestrator
│   └── lightning_monitor.py — Agent Lightning integration
├── src/                 — React frontend (renamed from ADA)
│   ├── personas/
│   │   ├── ivette/      — IVETTE-specific UI, themes, voice selector
│   │   └── bambu/       — BAMBU-specific UI
│   └── ...
└── configs/
    ├── ivette.persona.yaml
    └── bambu.persona.yaml
```

**Startup → selects persona** based on `AX_ACTIVE_PERSONA` env var or first-run wizard.

### 12.2 Mobile (PWA + Future Native)

- **Phase 1 (PWA):** Responsive React app served from Coolify VPS
  - Voice input via browser WebRTC
  - ElevenLabs audio playback
  - Push notifications for urgent alerts
- **Phase 2 (Native):** React Native wrapper using the same backend
- **Access:** Secured with face auth (MediaPipe, existing in ada_v2)

### 12.3 Cloud Deployment

```
Coolify VPS (Hostinger)
├── archon-x-backend (FastAPI + Socket.IO) — port 8001
├── archon-x-frontend (React Vite) — port 3001
├── redis (session/job queue)
└── postgres (conversation history, repo memory)

Keys sourced from: E:\THE PAULI FILES\master.env → Coolify environment variables
```

---

## 13. BEAD EXECUTION PLAN

### BEAD-AX-VOICE-P1: Submodule + Rename
- `git submodule add https://github.com/nazirlouis/ada_v2.git ada_v2`
- Rename all ADA references to Archon-X throughout the codebase
- Add `AGENTS.md` to the ada_v2 fork
- Add `ada_v2` to `.ralphy.json` as 4th repo

### BEAD-AX-VOICE-P2: Voice Engine
- `archon-x/backend/voice_engine.py` — ElevenLabs integration
- `archon-x/backend/phone_agent.py` — Twilio inbound/outbound
- Load `ELEVEN_LABS_API` and `TWILIO_*` from master.env
- 3 voices configured: ivette_mx, bambu_en, bambu_sr

### BEAD-AX-VOICE-P3: Persona Files
- `configs/ivette.persona.yaml` — full IVETTE config
- `configs/bambu.persona.yaml` — full BAMBU config
- `archon-x/backend/persona_loader.py` — loads soul files at boot
- Domain knowledge ingestion (Mexico City law, finance, entrepreneurship)

### BEAD-AX-VOICE-P4: Guardian Fleet
- `archon-x/backend/guardian_fleet.py` — 100-repo guardian orchestrator
- Per-repo `AX-GUARDIAN-{slug}` agent config files
- Cron job scheduler (APScheduler, already in deps)
- GraphBrain repo memory index

### BEAD-AX-VOICE-P5: Proactive Engine
- `archon-x/backend/proactive_engine.py` — morning brief, event triggers
- Connect to OpenClaw gateway for cross-agent dispatch
- BENEVOLENCIA heartbeat in commercial actions

### BEAD-AX-VOICE-P6: Orgo Computer Use
- Wire `archonx/openclaw/orgo.py` into Archon-X tool calls
- IVETTE SAT invoice automation
- BAMBU local file reader via VisionClaw

### BEAD-AX-VOICE-P7: Microsoft Agent Lightning
- `archon-x/backend/lightning_monitor.py`
- 30-minute performance monitor loop
- Weekly prompt improvement cycle

### BEAD-AX-VOICE-P8: Tests + Deploy
- `tests/test_archon_x_voice.py` — 20 tests (voice engine, Twilio, personas)
- `tests/test_guardian_fleet.py` — 15 tests (repo health, cron, escalation)
- `tests/test_proactive_engine.py` — 10 tests
- Deploy to Coolify + Electron packager

---

## 14. SECURITY & CREDENTIALS

### 14.1 Credential Sourcing

All secrets loaded from `E:\THE PAULI FILES\master.env` via secure env injection — never hardcoded:

```python
# archon-x/backend/config.py
import os
from pathlib import Path

MASTER_ENV = Path(r"E:\THE PAULI FILES\master.env")

REQUIRED_KEYS = {
    "ELEVEN_LABS_API":    "ElevenLabs TTS",
    "TWILIO_ACCOUNT_SID": "Twilio phone",
    "TWILIO_SECRET":      "Twilio auth",
    "GOOGLE_API_KEY":     "Gemini voice model",
    "ANTHROPIC_API_KEY":  "Claude fallback LLM",
    "GH_PAT":             "GitHub repo access for guardians",
    "AZ_API_KEY":         "Agent Zero dispatch",
    "SUPABASE_URL":       "Conversation history DB",
}
```

### 14.2 Iron Claw Gates for Archon-X

IVETTE and BAMBU cannot:
- Commit directly to `main` on any repo (must open PRs)
- Spend >$500 USD in a single action without human confirmation
- Share any credential from master.env verbally
- Make phone calls to numbers not on the approved list (Iron Claw blocklist enforced)
- Access biometric data beyond the current user session

### 14.3 PAULIWHEEL Compliance

Every Archon-X code-affecting action generates a BEAD:
```
BEAD-AX-IVETTE-{timestamp}  — IVETTE-initiated actions
BEAD-AX-BAMBU-{timestamp}   — BAMBU-initiated actions
BEAD-AX-GUARDIAN-{repo}     — Guardian agent actions
```

---

## 15. SUCCESS METRICS

| KPI | Target |
|-----|--------|
| Guardian fleet coverage | 100% of repos (100/100) |
| Voice response latency | <1.5 seconds (Gemini → ElevenLabs) |
| Phone call answer rate | 100% during business hours |
| Morning brief delivery | 07:00 ±5 min every day |
| Build health across fleet | ≥85% repos passing at any time |
| Repo bug auto-fix rate | ≥60% of minor bugs fixed without human |
| IVETTE demo creation | <10 minutes from request to delivery |
| BENEVOLENCIA tithe | 100% of transactions logged |
| Agent Lightning improvements | ≥1 improvement per week |

---

## APPROVAL GATE

This PRD represents the complete specification for Archon-X v1.0.

**Approve → BEAD-AX-VOICE-P1 execution begins.**

Estimated deliverable order: P1 (submodule+rename) → P2 (voice) → P3 (personas) →
P4 (guardians) → P5 (proactive) → P6 (orgo) → P7 (lightning) → P8 (tests+deploy)

---
*ARCHON-X — Built on PAULIWHEEL. Governed by Prime Directive. Powered by soul.*
