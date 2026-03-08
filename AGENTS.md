# ArchonX OS Agent Doctrine
**Version:** 2.1.0 | **Authority:** ZTE + PAULIWHEEL

## 1. THE PRIME DIRECTIVE
The ArchonX OS is the primary source of truth for the autonomous agent swarm. Every action must follow the ZTE Protocol:
**WRITE → TEST → FIX → COMMIT → DEPLOY → VERIFY → NOTIFY**

## 2. AGENT RULES (PAULIWHEEL)
- PAULIWHEEL is the default coding behavior.
- Code-affecting operations must include a `bead_id` and execute through Ralphy loop stages (PLAN, IMPLEMENT, TEST, EVALUATE, PATCH, REPEAT).
- Agent Lightning bootstrap is required before other functional changes.
- Minimal diffs only; avoid broad refactors unless required.

## 3. CONTEXT & MEMORY (Open Brain)
- **Search First**: EVERY agent MUST call `search_memories` before starting a task.
- **Store Always**: EVERY agent MUST call `store_memory` after completion.
- **jcodemunch**: Use symbol-level retrieval via MCP for 90%+ token efficiency.

## 4. SECURITY & VAULT
- **Zero-Trust**: No secrets in code or plaintext. Use `archonx/security/vault.py`.
- **Classification**: Secrets are categorized as CRITICAL, HIGH, MEDIUM, or LOW risk.
- **Audit**: Run `RedteamSkill` or `vault_agent.py` before every deployment.

## 5. REPO COMPLIANCE
Every managed repo must include:
1. `.archonx/reportback.json`
2. `.archonx/toolbox.json`
3. Standard commands: `dev`, `test`, `lint`.

## 6. RUNNER CONTRACT
The ArchonX Ops Runner must:
1. Read eco-prompts from `security/codex/eco-prompts/*.json`.
2. Execute steps in deterministic order.
3. Write machine-readable reports under `ops/reports/`.
