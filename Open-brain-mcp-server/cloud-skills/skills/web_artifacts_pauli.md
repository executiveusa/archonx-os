# Pauli Web Artifacts Builder++
## skill_id
`web_artifacts_pauli`

## Purpose
Generates production-grade web artifacts — React components, Next.js pages, full multi-page flows, 3D scenes, and social media campaign assets — tuned to the Pauli Empire's exact stack: Next.js App Router, Tailwind CSS, shadcn/ui, React Three Fiber, GSAP/Framer Motion, and Spline embeds. Goes beyond simple HTML to generate cohesive multi-page flows (landing → pricing → signup), hook into Supabase and Coolify-hosted APIs already in our repos, and produce social media campaign artifacts (carousels, story sequences, ad variants). Always reads existing codebase patterns via jCodeMunch before generating.

## When to Use
- Building new pages or components for any Pauli Empire web property
- Generating landing page → pricing → signup conversion flows
- Creating 3D interactive scenes (Three.js/R3F) for ARCHON-X or Yappyverse
- Building social media campaign artifacts (carousels, story sequences)
- Producing interactive demos for Akash Engine client proposals
- Generating A/B test variants of existing pages

## Inputs
```
artifact_type: "component" | "page" | "multi-page-flow" | "3d-scene" | "social-carousel" | "ad-variant"
framework: "react" | "nextjs-app-router" | "html" (default: react)
entity: [entity name]
route: string (for Next.js pages)
api_endpoints: [endpoint URLs from existing repos]
motion: "none" | "framer" | "gsap" | "r3f"
shadcn_components: [component names to use]
analytics_events: [event names] (optional)
ab_variants: int (optional)
```

## Outputs
- Production-ready React/Next.js code following repo patterns
- Tailwind + shadcn/ui styled components matching entity theme
- API integration code (Supabase, Coolify, existing endpoints)
- Analytics event hooks (ready for PostHog, Plausible, or custom)
- A/B variant versions if requested
- Framer Motion / GSAP / R3F animation code

## Tools & Integrations
- jCodeMunch: read existing components before generating (Gate Zero)
- Vercel MCP: deploy preview after generation
- Supabase: client setup from existing repo patterns
- shadcn/ui component library
- Figma MCP: import designs if available
- Canva MCP: social asset export

## Project-Specific Guidelines
**Always jCodeMunch first**: `index_folder → search_symbols("component") → read relevant files` before writing any component.
**Next.js App Router conventions**: Use `"use client"` directive only when needed. Server components by default.
**API patterns**: Use existing `lib/supabase.ts` or `lib/api.ts` — never create new API client setup files if one exists.
**Performance**: Images via `next/image`, fonts via `next/font`, dynamic imports for heavy 3D components.
**Social carousels**: Generate as React with CSS scroll snap, export-ready as static HTML for social tools.
**Analytics**: Always include analytics events for: page_view, cta_click, form_submit, error. Use PostHog pattern if detected in repo.

## Example Interactions
1. "Build the ARCHON-X OS landing page → pricing → signup flow" → 3-page Next.js flow, dark theme, Framer Motion
2. "Create a React Three Fiber hero scene for the Pauli Effect homepage" → R3F scene, gold particles, mob-noir aesthetic
3. "Generate an Instagram carousel for NW Kids campaign (5 slides)" → React scroll-snap carousel, export as static HTML
4. "Build a shadcn/ui dashboard for Akash Engine client reporting" → Full dashboard, charts, Supabase data integration
5. "Make 3 A/B variants of the HustleClaude landing page CTA section" → 3 variants with different copy/layout/color
