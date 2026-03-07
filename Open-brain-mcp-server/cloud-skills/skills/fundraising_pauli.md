# Fundraising & Investor Relations
## skill_id
`fundraising_pauli`

## Purpose
Supports all fundraising narrative, materials, and communications for Pauli Empire entities — from NW Kids grant applications to Pauli Effect angel/impact investor outreach to Akash Engine client revenue pitches. Uses scenario-based financial framing (never fabricated precision), SCQA narrative structure for clarity, and audience-specific tone (grant maker vs. angel vs. impact fund vs. corporate sponsor). Always flags assumptions explicitly. Does not execute transactions — generates draft materials for human review and approval before sending.

## When to Use
- Writing NW Kids grant applications (foundation grants, government grants, corporate sponsorships)
- Drafting The Pauli Effect investor pitch deck or one-pager
- Creating Akash Engine capability/ROI presentations for enterprise clients
- Writing investor update emails (quarterly cadence)
- Preparing for a funding conversation (talking points, anticipated Q&A)
- Building a data room outline

## Inputs
```
fundraising_type: "grant" | "angel" | "impact-fund" | "corporate-sponsor" | "client-revenue" | "investor-update"
entity: [entity name]
ask: string (amount + use of funds)
investor_persona: "foundation" | "angel" | "impact-fund" | "corporate" | "vc"
stage: "initial-pitch" | "follow-up" | "due-diligence" | "update"
key_metrics: {revenue, users, impact_numbers, runway}
doc_type: "deck" | "one-pager" | "email" | "data-room" | "talking-points"
```

## Outputs
- Pitch deck outline (slide-by-slide, content per slide, data placeholders)
- One-pager (single page, investor-grade, assumption-labeled)
- Email outreach sequence (cold, follow-up 1, follow-up 2)
- Investor update (SCQA structure, metrics, ask)
- Data room outline (section list with document types needed)
- Anticipated Q&A with recommended answers

## Tools & Integrations
- finance_pauli: pull financial model outputs as supporting data
- canvas_pauli: generate one-pager layout
- comms_pauli: investor update email formatting
- Notion MCP: push materials to fundraising tracker
- Gmail MCP: draft outreach (human approves before send — always)

## Project-Specific Guidelines
**SCQA framework** for all narratives: Situation (context everyone agrees on) → Complication (what changed/challenges) → Question (what does this raise?) → Answer (our approach/ask).
**Assumption labeling**: Every financial projection must include "ASSUMPTION: [what we're assuming]" in brackets. No exceptions.
**Scenario-based projections only**: Conservative / Base / Optimistic. Never single-point forecasts.
**NW Kids grant tone**: Mission-first, child-centered stories, 7-generation thinking framework, measurable outcomes.
**Angel/VC tone**: Market size first, traction evidence, founder-market fit, clear use of funds, specific ask.
**Never include**: Vague claims ("disrupting the industry"), unsupported TAM numbers, revenue projections without stated assumptions.

## Example Interactions
1. "Draft a NW Kids grant application for the Boeing Community Fund" → Full grant narrative, SCQA structure, budget justification
2. "Write a Pauli Effect angel investor one-pager for ARCHON-X" → 1-page, market context, traction, team, ask — all assumptions labeled
3. "Create Q1 2026 investor update email for NW Kids donors" → SCQA email, impact metrics, next milestone, soft donation ask
4. "Build the data room outline for a $500K impact fund pitch" → Section list, document types, what to prepare first
5. "Give me talking points for a 30-minute Akash Engine enterprise sales call" → Problem/solution framing, ROI story, anticipated objections + answers
