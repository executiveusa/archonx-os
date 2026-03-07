# Pauli Skill Creator
## skill_id
`skill_creator_pauli`

## Purpose
Meta-skill that designs, drafts, tests, and installs new Cloud Skills strictly following the Pauli Empire skill schema. Reads all existing skills before creating new ones (memory-first). Can also refine and improve existing skills based on usage feedback and ARCHON-X Lightning RL optimization signals. Every new skill it creates is wired to the ARCHON-X agent registry, the Second Brain schema, and the Flow Library in skills-index.md.

## When to Use
- A recurring workflow pattern has emerged that isn't covered by existing skills
- An existing skill needs to be updated after a new tool or API is added to the stack
- A new Akash Engine client brings a domain we haven't formalized (e.g., healthcare, legal)
- Agent Lightning identifies a prompt pattern worth standardizing into a skill
- Bambu says "we need a skill for X"

## Inputs
```
action: "create" | "update" | "audit" | "test"
skill_name: string
trigger_description: "When user asks X..."
domain: string (e.g., "email marketing", "smart contracts")
integrations_needed: [service names]
existing_skill_to_update: skill_id (if action=update)
```

## Outputs
- Complete skill `.md` file following the Pauli skill schema
- Entry for skills-index.md (registry row + flow library addition if applicable)
- Claude Desktop install instructions
- ARCHON-X agent wiring config entry

## Tools & Integrations
- Second Brain: query existing skills before creating (prevent duplication)
- Notion MCP: push new skill to PAULI Second Brain > Cloud Skills
- GitHub: commit new skill file to ARCHON-X2.0 repo under `.claude/skills/`
- skill-creator SKILL.md baseline for eval patterns

## Project-Specific Guidelines
**Schema requirements** (every skill MUST have all sections):
`skill_id`, `Purpose`, `When to Use`, `Inputs`, `Outputs`, `Tools & Integrations`, `Project-Specific Guidelines`, `Example Interactions`

**Naming convention**: `[domain]_pauli` (e.g., `email_pauli`, `legal_pauli`)
**Memory-first rule**: ALWAYS query Second Brain for similar skills before creating. Extend existing skills before creating new ones.
**Test before shipping**: Every new skill gets 3 test prompts run against it. If outputs don't match expected, revise.
**Lightning integration**: New skills that involve LLM calls must define their reward function for Agent Lightning.

## Example Interactions
1. "Create a skill for managing Akash Engine client contracts" → Full skill file + schema + install instructions
2. "Update the devops_pauli skill to include Railway.app as a deploy target" → Diff of changes + updated file
3. "Audit all 17 skills for outdated tool references" → Audit report with specific fixes per skill
4. "A skill for NW Kids grant writing specifically" → New nwkids_grants_pauli skill, SCQA-focused
5. "Test the marketing_pauli skill against 3 real scenarios" → Test results + recommended improvements
