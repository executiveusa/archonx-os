# Rainbow Protocol™ — Code & Agent Color Index

> Maps every agent, directory, task outcome, and skill to its assigned Rainbow Protocol™ color.
> Reference: [archonx-synthia/docs/TRADEMARK_REGISTRY.md](archonx-synthia/docs/TRADEMARK_REGISTRY.md)

---

## Agent → Color Mapping

| Color | Agent | Crew | Domain | Primary Directories |
|-------|-------|------|--------|-------------------|
| 🟣 Purple | **SYNTHIA™** | White | Core logic, code gen | `archonx-synthia/`, `archonx/core/` |
| 🔵 Blue | **ARIA™** | White | System design, schemas | `archonx-synthia/packages/core/`, architecture docs |
| 🟢 Green | **NEXUS™** | White | Multi-agent orchestration | `archonx/crews/`, `archonx/meetings/` |
| 🟡 Gold | **ORACLE™** | White | Metrics, signals, reports | `archonx/core/metrics.py`, `ops/reports/` |
| ⚫ Black | **PHANTOM™** | Black | Scraping, data extraction | `archonx/tools/`, `archonx/security/anti_scraping.py` |
| 🔴 Red | **CIPHER™** | Black | Security, credentials | `archonx/security/`, `.gitignore`, secrets |
| 🟠 Orange | **VECTOR™** | Black | CI/CD, Vercel/Coolify | `archonx/deploy/`, `archonx-synthia/Dockerfile*` |
| 🌈 Rainbow | **PRISM™** | Black | Content, SEO, docs | `docs/`, `public/blog/`, `README.md` |
| 🩵 Cyan | **ECHO™** | Specialized | Discord/Telegram hooks | `archonx/openclaw/channels.py` |
| 📘 Navy | **ATLAS™** | Specialized | Research, documentation | `files/`, `01-main/docs/` |
| ⭐ Star White | **NOVA™** | Specialized | R&D, experiments | `agent-frameworks/` |
| 🌊 Ocean Blue | **DARYA™** | Specialized | Computer-use, Orgo, OpenClaw | `agents/darya/`, `Darya-designs-main/` |

---

## Task Outcome Colors

| Color | Outcome | PAULIWHEEL™ Stage | Bead Tag |
|-------|---------|------------------|----------|
| 🟢 Green | Pass / Success | TEST ✓ | `status:pass` |
| 🔴 Red | Fail / Blocked | TEST ✗ | `status:fail` |
| 🟡 Yellow | Partial / Needs Review | EVALUATE | `status:partial` |
| 🔵 Blue | In Progress | IMPLEMENT | `status:wip` |
| 🟣 Purple | Planned / Not Started | PLAN | `status:planned` |
| 🟠 Orange | Patching / Hotfix | PATCH | `status:patching` |

---

## Skill → Color Mapping

| Color | Skill | Category | Toolbox Path |
|-------|-------|----------|-------------|
| 🔵 Blue | BMAD Auto Method™ | Methodology | `.archonx/toolbox/skills/bmad-auto-method/` |
| 🔴 Red | USM (Universal Skills Manager) | Security / Install | `.archonx/toolbox/skills/universal-skills-manager/` |
| 🟣 Purple | Agent Lightning™ | Bootstrap | `agent-frameworks/agent-lightning/` |
| 🌈 Rainbow | Rainbow Protocol™ | Organization | This file |
| ⚫ Black | ACIP v1.3 | Prompt Injection Defense | Planned (P7) |
| 🟠 Orange | Deployment Pipeline | CI/CD | `archonx/deploy/` |

---

## Directory → Color Quick Reference

```
c:\archonx-os-main\
├── 🟣 archonx-synthia/          SYNTHIA — Platform core
│   ├── 🔵 packages/core/        ARIA — Architecture
│   ├── 🟠 Dockerfile*           VECTOR — Deployment
│   └── 🌈 docs/                 PRISM — Documentation
├── 🟣 archonx/                  SYNTHIA — Python modules
│   ├── 🟢 crews/                NEXUS — Multi-agent
│   ├── 🟡 core/metrics.py       ORACLE — Metrics
│   ├── 🔴 security/             CIPHER — Security
│   ├── 🟠 deploy/               VECTOR — Deployment
│   ├── ⚫ tools/                PHANTOM — Tools
│   └── 🩵 openclaw/             ECHO — Communications
├── 🌊 agents/darya/             DARYA — Computer-use
├── 🌊 Darya-designs-main/       DARYA — OpenHands fork
├── ⭐ agent-frameworks/          NOVA — R&D
├── 📘 files/                    ATLAS — Knowledge
├── 🟡 ops/reports/              ORACLE — Reports
├── 🔴 .gitignore                CIPHER — Secret gates
└── 🌈 public/                   PRISM — Content
```

---

*Maintained under PAULIWHEEL™ discipline. Updated whenever agents or skills change.*
