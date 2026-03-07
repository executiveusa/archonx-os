# Pauli Internal Comms
## skill_id
`comms_pauli`

## Purpose
Generates all internal and external communications for the Pauli Empire: status reports, incident reports, investor updates, partner updates, client-facing status docs, weekly ops summaries, and RFC/ADR documents. Tuned to Bambu's actual comms style — fast, direct, systems-thinking, no corporate filler. All outputs are Notion-ready (Markdown) or email-ready. Understands the multi-entity structure: distinguishes comms for The Pauli Effect (agency), NW Kids (nonprofit/grant), Akash Engine (client), and ARCHON-X (technical). Integrates with Notion MCP to push directly to the correct workspace page.

## When to Use
- Weekly ops summary for Bambu's Notion inbox
- Client status report for Akash Engine retainer clients
- Incident report after any Coolify/Vercel downtime
- Investor/donor update for NW Kids or The Pauli Effect
- RFC (Request for Comments) for any major architectural decision
- Partner update email (nonprofit partners, event sponsors, etc.)
- Post-mortem after a failed deployment or missed deadline

## Inputs
```
doc_type: "weekly-ops" | "incident-report" | "investor-update" | "client-status" | "rfc" | "post-mortem" | "partner-update"
entity: [entity name]
period: date or date range
key_metrics: {completed[], blocked[], next[], metrics{}}
tone: "executive" | "technical" | "donor-facing" | "client-facing"
destination: "notion" | "email" | "slack" | "markdown-file"
```

## Outputs
- Structured document in specified format
- Notion-ready Markdown (push via Notion MCP if approved)
- Email-ready HTML version if destination=email
- Slack-ready summary (500 chars max) if destination=slack

## Tools & Integrations
- Notion MCP: push final doc to correct page (Second Brain > Comms > [entity])
- Gmail MCP: draft and send if destination=email and approved
- Slack MCP (if connected): post summary
- Second Brain: query past comms for consistent tone and metrics tracking

## Project-Specific Guidelines
**Weekly Ops Format** (Bambu's actual format):
```
⚡ WEEK [N] OPS — [DATE]
SHIPPED: [bullet list]
BLOCKED: [bullet list + root cause]
THIS WEEK: [bullet list, priority order]
METRICS: [3-5 key numbers]
ESCALATIONS: [anything needing Bambu decision]
```
**Incident Report**: Always leads with timeline (T+0, T+5, T+30), root cause, fix applied, prevention.
**Investor Update**: SCQA framework — Situation, Complication, Question, Answer. Max 1 page.
**Client Status (Akash)**: Traffic light system. Green/Amber/Red per workstream. Always ends with "next milestone and date."
Never use passive voice. Never hedge without data. Write like Bambu talks.

## Example Interactions
1. "Write the week 10 ops summary — we shipped postatees, blocked on NWKids Supabase" → Full weekly ops doc, Notion-ready
2. "Write an incident report — Coolify went down for 45 min Thursday" → Timeline-first incident report
3. "Draft a donor update for NW Kids Q1 2026" → SCQA-structured, impact-forward, 1 page
4. "Write an RFC for switching from Supabase to PlanetScale" → Full RFC with tradeoffs, decision criteria, rollback plan
5. "Client status report for Akash Engine client Frithco — 3 weeks in" → Traffic-light status, next milestone, professional tone
