# Universal Skills Manager (USM)™ Integration Skill

> Search, scan, install, and sync AI skills securely across all agent tools.
> Based on: https://github.com/jacob-bd/universal-skills-manager

---

## Overview

The USM is a security-first skill manager that acts as the "NPM for LLMs." It searches three skill marketplaces, runs 20+ security checks on every skill before installation, and syncs skills across 10+ AI tools automatically.

## When To Use

- Installing any third-party AI skill
- Scanning existing skills for prompt injection, credential theft, or shell exploits
- Syncing a skill across Claude, Cursor, Gemini, OpenClaw, and other tools
- Auditing the skill inventory on your system

## Supported Marketplaces

| Marketplace | Skills | API Key Required |
|-------------|--------|-----------------|
| **SkillsMP** | 200,000+ | Optional (free) |
| **SkillHub** | 187,000+ | No |
| **ClawHub** | Growing | No |

## Supported Tools (10+)

Claude Desktop, Claude Code, Cursor, VS Code Copilot, Gemini, OpenClaw, Windsurf, Cline, and more.

## Installation

### One-Command Install (all tools)
```bash
npx universal-skills-manager install
```

### Install for specific tool
```bash
npx universal-skills-manager install --tools claude-code
```

### Optional: Set SkillsMP API key
Generate free key at https://skillsmp.com → API → Generate Key
```bash
npx universal-skills-manager config --set-api-key YOUR_KEY
```

## Security Scanning (20+ checks)

Every skill is scanned for:
- **Prompt injection** — Attempts to override system instructions
- **Credential theft** — Patterns that exfiltrate env vars, API keys, tokens
- **Shell exploits** — Commands that could execute arbitrary code
- **File system access** — Unauthorized read/write to sensitive paths
- **Network exfiltration** — Unauthorized outbound connections
- **Privilege escalation** — Attempts to gain elevated permissions
- **Structure validation** — Proper SKILL.md format (required for Claude Desktop)

## Usage Commands

### Search for a skill
```
Search SkillsMP for "humanizer" skill
```

### Download and install
```
Download the humanizer skill by villa7 for Claude Desktop
```

### Scan existing skills
```
Scan all installed skills for security issues
```

### Sync across tools
```
Deploy the humanizer skill across all available applications
```

### List top skills
```
Show top 10 skills on SkillHub
Show top 5 skills on ClawHub
```

## Claude Desktop Skill Fix

USM can automatically fix skills that don't conform to Claude Desktop's strict SKILL.md structure requirements:
1. Downloads original skill
2. Detects structure errors
3. Creates fixed version (Claude Desktop ready)
4. Creates zip package for upload
5. Both versions saved to downloads folder

## Integration with ArchonX™

### Toolbox Registration
```json
{
  "skill_id": "universal-skills-manager",
  "name": "Universal Skills Manager™",
  "version": "1.0.0",
  "category": "security",
  "rainbow_color": "🔴 CIPHER (Security)",
  "agents_allowed": ["CIPHER", "DARYA", "SYNTHIA"],
  "triggers": ["install skill", "scan skill", "search skill", "sync skill", "skill marketplace"],
  "dependencies": ["npx"],
  "security_scan": "self-protected"
}
```

### CIPHER™ Agent Workflow
1. Before any skill installation, CIPHER runs USM scan
2. Skills failing security scan are quarantined in `.archonx/quarantine/`
3. Approved skills are installed to `.archonx/toolbox/skills/`
4. Sync triggers update across all configured tools

## Anti-Patterns

1. **Never install skills without scanning** — ClawHub has had malware incidents (VirusTotal partnership was a response)
2. **Don't trust star counts** — Stars may be for the parent repo, not the individual skill
3. **Don't skip Claude Desktop validation** — Skills need strict MD structure or they'll be rejected
4. **Don't expose marketplace API keys** — Store in env vars, not in configs

## References

- USM Repo: https://github.com/jacob-bd/universal-skills-manager
- NotebookLM Overview: See USM video transcript
- SkillsMP: https://skillsmp.com/
- SkillHub: https://skills.palebluedot.live/
- ClawHub: https://clawhub.ai/

---

*This skill is maintained under PAULIWHEEL™ discipline by CIPHER™ (Security Agent).*
