# ArchonX OS Agent Doctrine

ArchonX OS is the primary source of truth for the Poly Effect ecosystem.

## Operating Doctrine

`PAULIWHEEL + RALPHY + BEADS`

1. Use `bead_id` for all milestones and include `bead_id` in every commit message.
2. Run the loop: `PLAN -> IMPLEMENT -> TEST -> EVALUATE -> PATCH -> REPEAT` until gates are green.
3. Integrate Agent Lightning first in any repo change, or install a compiling stub plus smoke test.
4. No destructive git operations (`reset --hard`, force push, history rewrites).
5. Minimal diffs only; avoid broad refactors unless required by acceptance criteria.
6. Never commit secrets, API keys, tokens, or credentials.

## Compliance Requirements

Every managed repo must include:

1. `.archonx/reportback.json`
2. `.archonx/toolbox.json`
3. An `AGENTS.md` shim that references this file.
4. Standard commands available via scripts or make targets: `dev`, `test`, `lint`.

## Runner Contract

The ArchonX Ops Runner (`ops/runner/main.py`) must:

1. Read eco-prompts from `security/codex/eco-prompts/*.json`.
2. Execute steps in deterministic order.
3. Support `--dry-run` and `--report-only`.
4. Write reports under `ops/reports/`.

## Priority Order

1. Agent Lightning bootstrap
2. Repo compliance scan
3. Bead tracking sync
4. Verification and reportback
