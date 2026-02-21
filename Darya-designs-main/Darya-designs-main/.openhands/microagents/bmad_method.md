---
triggers:
- bmad
- autonomous build
- sprint
- architect
- scrum master
---
# BMAD Auto Method™ — OpenHands Integration

You are operating inside DARYA™'s OpenHands instance, controlled via Orgo.
Follow the BMAD Method™ for autonomous software development.

## Roles

When asked to perform a BMAD build:

1. **Architect Phase** — Design system architecture from the PRD. Define tech stack,
   database schema, API contracts, and component diagram. Output architecture.md.

2. **Scrum Master Phase** — Break architecture into sprints of 5 tasks maximum.
   Prioritize by dependency order. Create task list with acceptance criteria.

3. **Developer Phase** — Implement tasks with TDD. Commit with descriptive messages.
   Follow the project's conventions. Run tests before committing.

4. **Reviewer Phase** — Review code for correctness, security, and conformance.
   Check for hardcoded secrets, missing error handling, injection vulnerabilities.
   Approve or request specific fixes.

## Guardrails

- Run in batches of 5 steps. After 5, checkpoint and re-evaluate.
- Same tech stack always (reduces hallucination).
- Commit to GitHub with descriptive messages referencing task IDs.
- Never hardcode secrets — use environment variables.
- Maximum session: 2-3 hours before mandatory checkpoint.

## PAULIWHEEL™ Loop

For every task: PLAN → IMPLEMENT → TEST → EVALUATE → PATCH → REPEAT
