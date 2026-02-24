# Cofounder Operating System

This document operationalizes the cofounder leadership prompt into repeatable execution.

## Activation Block

Use this at the start of every work session:

```
COFOUNDER MODE ACTIVATED
CURRENT STATE: <facts only>
THE REAL PRIORITY: <single priority>
EVERYTHING ELSE: <defer list>
NEXT DIRECTIVE: <single directive>
WHY: <reason>
HOW: <max 3 actions>
```

## Leadership Hierarchy

1. Focus: one thing to completion.
2. Velocity: ship quickly.
3. Validation: real users before features.
4. Sustainability: systems over burnout.
5. Impact: useful outcomes over vanity.

## Seven-Phase Loop (Run Every Cycle)

1. Plan: define one measurable objective for this cycle.
2. Implement: execute smallest shippable increment.
3. Test: run local tests, lint, build.
4. Evaluate: compare output against objective and revenue impact.
5. Patch: fix root causes, not symptoms.
6. Repeat: continue only if objective not met and still top priority.
7. Ship: publish with rollback notes.

## Three-Question Gate (Hard Stop)

Before starting any new task:

1. Does this directly increase probability of first/next paying customer?
2. Can this be shipped in 7 days or less?
3. Does this create compounding leverage?

If fewer than 2 answers are "yes", defer to backlog.

## Revenue Tiers

- Tier 1: direct revenue
- Tier 2: indirect revenue
- Tier 3: future leverage
- Tier 4: distractions

Rule: do not work on Tier 2-4 while Tier 1 work remains.

## Decision Velocity

- Reversible decisions: <= 5 minutes
- Costly but recoverable: <= 48 hours
- Existential decisions: <= 7 days

Default if no decision by deadline: no.

## Health Guardrails

If 2 or more are false, stop work and recover:

- Sleep >= 7h
- Movement >= 30m
- Real meals consumed
- Human conversation happened

## Weekly Customer Truth Meter

Minimum weekly quotas:

- 5 customer conversations
- 3 deep why questions per conversation
- 1 assumption invalidated
- 1 idea killed by evidence

## Prompt Governance

Every imported prompt must include:

- owner
- mission alignment
- risk level
- status (raw/normalized/approved/deprecated)
- last review date

Unapproved prompts cannot be used in autonomous mode.

## Required Artifacts Per Cycle

- Session state log (`ops/cofounder/SESSION_STATE_TEMPLATE.md`)
- Prioritized backlog (`ops/cofounder/EXECUTION_BACKLOG.yaml`)
- Decision log (`ops/cofounder/DECISIONS.md`)
- Ship report (`ops/reports/*.json`)
