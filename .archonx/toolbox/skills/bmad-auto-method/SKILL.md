# BMAD Auto Method™ Skill

> **Breakthrough Method of Agile AI-Driven Development**
> Adapted for OpenClaw sub-agent architecture. Based on lessons from production autonomous SaaS builds.

---

## Overview

This skill enables any ArchonX™ agent to follow the BMAD methodology for structured autonomous software development. Instead of wrapping OpenClaw → Claude Code → BMAD (which causes token overflow), this skill loads BMAD role prompts as standalone sub-agent configurations that OpenClaw can natively spawn.

## When To Use

- Building a full application autonomously (SaaS, API, dashboard)
- Multi-session development requiring persistent context
- Any task requiring Architect → Sprint Planning → Implementation → Review cycle

## Architecture

```
Human Architect (initial PRD + tech choices, ~30 min)
        │
        ▼
OpenClaw (long-term memory, agent orchestration)
   ├── BMAD Architect Sub-Agent
   ├── BMAD Scrum Master Sub-Agent
   ├── BMAD Developer Sub-Agent
   └── BMAD Reviewer Sub-Agent
        │
        ▼
GitHub (PR-based review, observability)
```

**Key Insight:** Extract individual BMAD role prompts and save them as files that OpenClaw loads as sub-agents. No wrapper, no extra LLM layer, no token duplication.

## BMAD Roles

### 1. Architect Agent
```markdown
You are the BMAD Architect. Your role:
- Design system architecture from PRD requirements
- Define tech stack, database schema, API contracts
- Create architecture decision records (ADRs)
- Validate that implementation proposals conform to design
- Output: Architecture document, Component diagram, API specs

Follow PAULIWHEEL™: PLAN the architecture before any code is written.
Always reference the PRD and existing architecture docs from long-term memory.
```

### 2. Scrum Master Agent
```markdown
You are the BMAD Scrum Master. Your role:
- Break architecture into sprint-sized tasks
- Prioritize by dependency order and business value
- Create task tickets with acceptance criteria
- Track velocity and blockers
- Output: Sprint backlog, Task breakdown, Priority matrix

Each sprint should have 5 implementation steps maximum.
After each sprint, trigger the Reviewer before starting the next.
```

### 3. Developer Agent
```markdown
You are the BMAD Developer. Your role:
- Implement code following the architecture and sprint backlog
- Write tests alongside implementation (TDD preferred)
- Commit with descriptive messages referencing task IDs
- Follow the project's coding style and conventions
- Output: Working code, Tests, Commit history

Always run tests before committing. Never skip linting.
Use the same stack consistently to reduce hallucination.
```

### 4. Reviewer Agent
```markdown
You are the BMAD Reviewer. Your role:
- Review code for correctness, security, performance
- Check conformance to architecture and PRD
- Verify test coverage meets acceptance criteria
- Flag issues and request specific fixes
- Output: Review comments, Approval/Rejection, Fix list

Be specific in feedback. Reference line numbers.
Check for: hardcoded secrets, missing error handling, SQL injection, XSS.
```

## Execution Protocol

### Step 1: Human Architect Phase (~30 min)
The human provides:
- Product Requirements Document (PRD) with scope and acceptance criteria
- Technology stack decisions (e.g., Next.js, Supabase, Vercel)
- Non-negotiable constraints (budget, timeline, compliance)

### Step 2: BMAD Agent Execution
```
1. Load Architect sub-agent → Generate architecture from PRD
2. Load Scrum Master → Break into sprints of 5 tasks each
3. For each sprint:
   a. Load Developer → Implement tasks, commit to GitHub
   b. Load Reviewer → Review code, approve or request fixes
   c. If fixes needed → Developer patches → Reviewer re-reviews
4. After sprint passes review → Scrum Master starts next sprint
5. Repeat until all PRD requirements met
```

### Step 3: Batch Execution Pattern
- Run in batches of 5 steps at a time
- After each batch, check output and correct course
- Use OpenClaw long-term memory to retain context across sessions
- Agent always has access to PRD + architecture docs

## Anti-Patterns (What NOT To Do)

1. **Token Overflow:** Never wrap OpenClaw → Claude Code → BMAD. This causes massive token duplication and context overflow.
2. **Vague Instructions:** Always provide a solid PRD with clear scope, tech choices, and acceptance criteria.
3. **Unlimited Runtime:** Run in 2-3 hour bursts. 24/7 without guardrails causes hallucination and loops.
4. **Mixed Stacks:** Use the same tech stack consistently to leverage repetitive patterns.
5. **No Observability:** Always commit to GitHub with the agent's own account. Review like a junior dev.

## Integration with ArchonX™

This skill is registered in the ArchonX Toolbox™ and available to all agents.

### Toolbox Registration
```json
{
  "skill_id": "bmad-auto-method",
  "name": "BMAD Auto Method™",
  "version": "1.0.0",
  "category": "methodology",
  "rainbow_color": "🔵 ARIA (Architecture)",
  "agents_allowed": ["*"],
  "triggers": ["build app", "build saas", "autonomous development", "sprint planning"],
  "dependencies": ["openclaw", "github"],
  "security_scan": "passed"
}
```

## References

- BMAD Method: https://github.com/bmad-method
- OpenClaw + BMAD Tutorial: ErwanLorteau (GitHub)
- Security Hardening: https://aimaker.substack.com/p/openclaw-security-hardening-guide
- ArchonX PAULIWHEEL™: See AGENTS.md

---

*This skill is maintained under PAULIWHEEL™ discipline by ARIA™ (Architect Agent).*
