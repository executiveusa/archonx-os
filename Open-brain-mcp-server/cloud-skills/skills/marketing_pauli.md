# Marketing & Growth
## skill_id
`marketing_pauli`

## Purpose
Plans and executes full-funnel marketing campaigns for all Pauli Empire entities — from strategy through copy, landing pages, email sequences, social post series, and ad concepts. Audience-aware: NW Kids reaches donors and grant makers, Akash Engine reaches founders and CTOs, Yappyverse reaches Gen Z gaming community, HustleClaude reaches entrepreneurs. Proposes metrics and experiments tied to our actual analytics stack (inferred from repos). Generates Notion-ready campaign briefs and MCP-ready outputs for direct publishing via connected tools.

## When to Use
- Planning a product launch campaign (ARCHON-X public release, new Akash service)
- NW Kids fundraising push or grant application marketing
- HustleClaude content strategy and post series
- Yappyverse community growth (Discord, TikTok, Twitter)
- Akash Engine lead generation (LinkedIn, cold outreach, SEO)
- Culture Shock Sports event promotion
- Any A/B test planning for landing page or email

## Inputs
```
campaign_type: "product-launch" | "fundraising" | "community-growth" | "lead-gen" | "event-promo" | "content-series"
entity: [entity name]
audience: string description
goal: string (e.g., "100 donors", "50 signups", "$10K raised")
budget: "zero" | "low (<$500)" | "medium (<$5K)" | "paid"
channels: ["email", "twitter", "instagram", "linkedin", "discord", "tiktok"]
timeline: string
existing_assets: [URLs or descriptions]
```

## Outputs
- Full-funnel campaign strategy (1-2 pages, Notion-ready)
- Landing page copy (all sections, CTA variants)
- Email sequence (3-7 emails, subject lines + body)
- Social post series (platform-specific, with hashtags, posting schedule)
- Ad concept copy (headline + body + CTA for 3 variants)
- Success metrics dashboard spec (which metrics, which tools, which thresholds)

## Tools & Integrations
- web_artifacts_pauli: hand off landing page specs for implementation
- Gmail MCP: draft and schedule email sequences
- Canva MCP: social asset generation
- Notion MCP: push campaign brief to campaign tracker
- algo_art_pauli: generate visual assets for campaigns
- Second Brain: query past campaign performance for benchmarks

## Project-Specific Guidelines
**Channel-audience matrix**:
- NW Kids donors → Email first, Instagram second, local press third
- Akash Engine clients → LinkedIn first, direct outreach second, content marketing third
- Yappyverse community → Discord first, TikTok second, Twitter third
- HustleClaude → Twitter/X first, YouTube second, newsletter third
- ARCHON-X developers → Twitter/X, Hacker News, Dev.to, GitHub

**Copy rules**: Lead with the reader's problem, not our product. Every piece of copy must answer "so what?" before the reader asks. CTAs are specific actions, not generic asks.
**Zero-budget playbook**: Organic Twitter threads, GitHub README marketing, Reddit community posts, Discord cross-promotion. Maximum leverage from existing audience before paid.
**Analytics**: Always propose 3 metrics: a vanity metric (impressions), an engagement metric (clicks/replies), and a conversion metric (signups/donations).

## Example Interactions
1. "Plan the ARCHON-X v1.0 public launch campaign — zero budget, developer audience" → Full launch strategy, Twitter thread series, GitHub README optimization, HN Show post
2. "Write a 5-email fundraising sequence for NW Kids spring campaign" → 5 emails, subject lines, plain-text + HTML
3. "Create 30 days of HustleClaude Twitter content" → 30 posts, variety of formats, posting schedule
4. "Plan Yappyverse Discord growth from 0 to 1K members" → Community growth playbook, content calendar, engagement tactics
5. "Write 3 LinkedIn ad variants for Akash Engine targeting startup CTOs" → 3 ad copy sets, audience targeting notes
