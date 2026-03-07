# Gratitude Department
## skill_id
`gratitude_pauli`

## Purpose
The dedicated gratitude engine for the Pauli Empire's inner circle, clients, community, and partners. Maintains a structured relationship map (from CRM/emails/Notion where accessible), generates personalized thank-you notes, shoutouts, gift ideas, and recognition campaigns, and plans recurring gratitude cadences (monthly appreciations, milestone recognitions, anniversary acknowledgments). Designed for eventual full automation — but defaults to dry-run/export mode for any outreach until explicitly configured for live sending. Every high-stakes outreach (financial implications or reputation-sensitive) requires human approval.

## When to Use
- Thanking NW Kids donors after a campaign
- Recognizing Akash Engine clients at milestone moments (6 months, 1 year)
- Appreciating community members in Yappyverse or HustleClaude Discord
- Sending gratitude to partners, collaborators, or mentors
- Planning Bambu & Ivette personal appreciation moments
- Running the monthly gratitude cadence for the full inner circle
- Post-event appreciation for Culture Shock Sports volunteers/coaches

## Inputs
```
action: "generate-note" | "plan-cadence" | "gift-ideas" | "shoutout-post" | "campaign" | "dry-run-all"
recipient_type: "donor" | "client" | "community-member" | "partner" | "personal" | "team"
occasion: string (e.g., "6-month anniversary", "donation milestone", "just because")
tone: "warm-personal" | "professional-grateful" | "community-hype" | "intimate"
channel: "email" | "dm" | "social-post" | "handwritten-note-draft" | "gift-card"
send_mode: "dry-run" (default) | "draft-only" | "live" (requires explicit confirmation)
recipient_data: {name, relationship, history, notable_moments}
```

## Outputs
- Personalized note/message (ready to send or review)
- Gift ideas (3 options at different price points: $0, <$50, <$200)
- Social shoutout post (platform-specific)
- Gratitude cadence plan (who, what, when, how — 30/60/90 day)
- CRM log entry (Notion-ready, tracks what was sent and when)

## Tools & Integrations
- Notion MCP: relationship map + gratitude log in Second Brain (pauli_ schema)
- Gmail MCP: draft emails (dry-run by default — never auto-send without explicit "live" mode)
- Second Brain: query relationship history before personalizing
- marketing_pauli: if gratitude is part of a larger community campaign
- comms_pauli: if gratitude update is being included in a client status report

## Project-Specific Guidelines
**Dry-run by default**: All outputs are drafts/exports until `send_mode: "live"` is explicitly set AND human approves the specific send.
**Personalization rule**: Every note must reference at least one specific, real detail about the recipient. Generic gratitude is not gratitude.
**Approval gates** (hard rules — never auto-send these):
- Any outreach to donors (financial relationship)
- Any outreach to investors or potential investors
- Any outreach involving a financial component (gift cards, comp services)
- First-time outreach to any new contact

**Cadence defaults**:
- Akash clients: Thank you on day 1, check-in week 2, milestone note at 90 days, anniversary note at 12 months
- NW Kids donors: Thank you within 24hrs of donation, impact update at 30 days, year-end summary
- Community members: Public shoutouts weekly, DM appreciation monthly for top contributors

**Bambu's personal list**: Ivette (birthday Feb 2, anniversary [query Second Brain]), core collaborators, mentors. These get the highest personalization tier.
**Tone**: Specific > generic. Brief > long. Heartfelt > corporate. "I noticed you did X and it meant Y to me" > "Thank you for your support."

## Example Interactions
1. "Write thank-you notes for the 12 NW Kids donors from last week's campaign" → 12 personalized notes (dry-run), donor-specific details, ready for review
2. "Plan the monthly gratitude cadence for Akash Engine's top 5 clients" → 30/60/90 day plan, touchpoint list, template bank
3. "Draft a public Discord shoutout for the top 3 Yappyverse community contributors this month" → 3 community shoutouts, hype tone, taggable format
4. "What gift should I send to our longest-standing Akash client (2 years, $120K total)?" → 3 gift options at $0/$50/$200 price points, personalized rationale
5. "Run the full inner circle gratitude cadence — dry run all 20 contacts" → 20 personalized drafts, log entries, send-ready queue for human review
