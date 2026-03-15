# Pauli Brand Guidelines
## skill_id
`brand_pauli`

## Purpose
Encodes and enforces the complete brand system for all Pauli Empire entities. Operates as the living brand bible — inferred from repo assets, CSS/Tailwind configs, marketing pages, and established brand decisions. Covers all entities: The Pauli Effect (Mob-Noir, internal/agency), Akash Engine (professional, client-facing), New World Kids (warm, nonprofit, youth), Kupuri Media (Mexican heritage, women's empowerment), Yappyverse (cartoon IP), HustleClaude (bold, marketing-forward), and ARCHON-X OS (technical, dark, gold). Prevents brand drift across 268 repos and 13 business units.

## When to Use
- Starting any design, marketing, or content task — check brand first
- Reviewing any UI component or landing page for brand compliance
- Onboarding a new Akash Engine client deliverable
- Writing copy for any external-facing property
- Generating design tokens for a new BU or sub-brand

## Inputs
```
entity: "pauli-effect" | "akash-engine" | "nwkids" | "kupuri" | "yappyverse" | "hustleclaude" | "archonx" | "culture-shock"
asset_type: "color-tokens" | "typography" | "logo-usage" | "copy-tone" | "component-patterns" | "full-brief"
format: "tailwind-config" | "css-vars" | "figma-tokens" | "markdown-brief"
```

## Outputs
- Design token file (Tailwind config, CSS custom properties, or Figma token JSON)
- Typography scale specification
- Logo usage rules (clear space, forbidden uses, minimum sizes)
- Tone-of-voice guide with do/don't examples
- Component pattern references (which shadcn/ui components, which variants)

## Tools & Integrations
- Figma MCP for exporting/importing design tokens
- Tailwind config files in repo (read via jCodeMunch before generating)
- shadcn/ui component library as the component system baseline
- Notion for storing brand decisions as living documents

## Project-Specific Guidelines

### The Pauli Effect (Mob-Noir)
- **Colors**: Black #0A0A0A, Gold #D4AF37, Charcoal #1C1C1C, Off-white #F5F5F5
- **Typography**: Playfair Display (headings), Inter (body), Courier New (code/mono)
- **Tone**: Cinematic, authoritative, mob-boss confidence. "You got sent for."
- **Forbidden**: Rounded corners >8px, pastels, sans-serif headings, stock photography

### Akash Engine (Client-Facing)
- **Colors**: Navy #1B2A4A, Electric Blue #2980B9, White, Light Grey #F8F9FA
- **Typography**: Inter (all), weight variation for hierarchy
- **Tone**: Professional, results-driven, concise. No jargon unless client's industry.

### New World Kids (Nonprofit)
- **Colors**: Warm Orange #E67E22, Forest Green #27AE60, Sky Blue #3498DB, Warm White
- **Typography**: Nunito (headings), Open Sans (body) — warm, accessible
- **Tone**: Hopeful, urgent, impact-forward. Lead with children's stories, not statistics.

### ARCHON-X OS (Technical Product)
- **Colors**: Dark #0D1117, Code Blue #58A6FF, Gold #D4AF37, Mid-grey #3D3D3D
- **Typography**: JetBrains Mono (headings/code), Inter (body)
- **Tone**: Technical precision. Every claim supported by evidence. No marketing fluff.

## Example Interactions
1. "Give me the Tailwind config for the Pauli Effect brand" → Full tailwind.config.js with all tokens
2. "What's the tone-of-voice for NW Kids grant writing?" → 2-page tone guide with before/after examples
3. "Is this Akash Engine landing page on-brand?" → Brand audit checklist with specific fixes
4. "Generate Figma tokens for Yappyverse" → Figma token JSON ready to import
5. "Write the brand brief for a new ARCHON-X marketing one-pager" → Full brand brief document
