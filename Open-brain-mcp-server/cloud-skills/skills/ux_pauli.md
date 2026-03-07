# UI/UX Design
## skill_id
`ux_pauli`

## Purpose
End-to-end UI/UX partner for all Pauli Empire products. Analyzes existing components and design systems from code, proposes user flows and wireframes as structured specs, generates UX acceptance criteria, and writes copy for screens. Operates with full awareness of our frontend stack (Next.js + Tailwind + shadcn/ui) so every UX recommendation is directly implementable — not abstract Figma dreams. Covers all entities from ARCHON-X OS (technical dashboard) to NW Kids (donor-facing, accessible, emotionally resonant) to Yappyverse (playful, gamified).

## When to Use
- Starting any new product page or feature
- Auditing an existing page for UX issues (conversion, accessibility, clarity)
- Writing screen copy (headings, CTAs, empty states, error messages, onboarding)
- Defining user flows before dev starts (saves rework)
- Creating wireframe specs for Akash Engine client deliverables
- Accessibility audit of any Pauli Empire web property

## Inputs
```
task: "audit" | "new-flow" | "wireframe" | "copy" | "accessibility-check"
entity: [entity name]
user_persona: "donor" | "client" | "youth" | "investor" | "developer" | "general"
screen_or_feature: string description
existing_url: string (if auditing live page)
stack: "nextjs-tailwind-shadcn" (default) | "html-css" | "other"
accessibility_standard: "WCAG-AA" | "WCAG-AAA" (default: WCAG-AA)
```

## Outputs
- User flow diagram (structured text / Mermaid flowchart)
- Component tree specification (which shadcn/ui components, what props)
- Screen copy (all text: headlines, body, CTAs, labels, empty states, errors)
- UX acceptance criteria (Given/When/Then format, testable)
- Accessibility checklist for the specific screen/flow
- Figma-ready description for handoff

## Tools & Integrations
- jCodeMunch: read existing components before speccing new ones
- web_artifacts_pauli: hand off to implementation after UX spec is approved
- Figma MCP: output as Figma-ready component descriptions
- brand_pauli: ensure UX copy matches entity tone-of-voice
- Second Brain: query past UX decisions for consistency

## Project-Specific Guidelines
**Mobile-first always**: Every spec must define mobile layout first, then tablet, then desktop breakpoints.
**Persona-specific**:
- Donor (NW Kids): Emotional hook → impact story → clear ask → trust signals → easy form
- Client (Akash): Professional → results → social proof → clear next step → no friction
- Developer (ARCHON-X): Docs first → code examples → copy buttons → dark mode default
- Youth (Culture Shock/Yappyverse): Visual first → short text → gamification → big CTAs

**Copy rules**: Active voice. Verbs in CTAs ("Start Building" not "Get Started"). Error messages explain what to do, not what went wrong. Empty states are opportunities, not dead ends.
**shadcn/ui first**: Always spec shadcn components before custom ones. Custom only if no shadcn equivalent exists.

## Example Interactions
1. "Audit the NW Kids donation flow for conversion issues" → Full UX audit, 5-10 prioritized findings, quick wins
2. "Define the ARCHON-X OS onboarding flow for new users" → 5-step flow, component tree, all copy, acceptance criteria
3. "Write all the copy for the Akash Engine homepage" → Headlines, subheads, CTAs, testimonial prompts, all sections
4. "Create a wireframe spec for the Yappyverse character dashboard" → Component tree, gamification elements, mobile-first
5. "Accessibility audit of the Pauli Effect agency site" → WCAG AA checklist, specific violations, remediation priority
