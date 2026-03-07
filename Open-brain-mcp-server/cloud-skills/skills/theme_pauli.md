# Pauli Theme Factory
## skill_id
`theme_pauli`

## Purpose
Extracts, standardizes, and applies design themes across all Pauli Empire outputs — web apps, landing pages, pitch decks, docs, comics, and 3D scenes. Manages 8 canonical theme presets (one per major entity/BU) plus generates custom themes on demand. Outputs design tokens in all formats needed by our stack: Tailwind config, CSS custom properties, shadcn/ui theme vars, and Figma token JSON. Acts as the single source of truth for visual consistency across 268 repos.

## When to Use
- Starting any new frontend project — get theme tokens first
- Applying consistent styling to a batch of documents or artifacts
- Creating a new BU sub-brand that needs its own theme variant
- Ensuring an Akash Engine client deliverable is on-brand
- Generating dark/light mode variants of existing themes
- Auditing existing repos for theme drift

## Inputs
```
action: "apply" | "generate" | "export" | "audit"
entity: [entity name] or "custom"
target: "web-app" | "landing-page" | "deck-doc" | "comic-avatar" | "3d-scene"
format: "tailwind" | "css-vars" | "shadcn" | "figma-tokens" | "all"
mode: "dark" | "light" | "auto"
custom_overrides: {} (optional)
```

## Outputs
- Theme token file in requested format(s)
- Applied component examples (shadcn/ui code snippets using the theme)
- Dark/light mode variants
- Figma token JSON for design handoff

## Tools & Integrations
- Tailwind config files in repos (read via jCodeMunch before generating)
- shadcn/ui theming system (CSS vars in globals.css)
- Figma MCP for export/import
- Canva MCP for quick application to social assets
- brand_pauli skill for source-of-truth brand values

## Project-Specific Guidelines
**8 Canonical Themes**:
1. `mob-noir` — Pauli Effect: black/gold, Playfair+Inter, sharp corners
2. `akash-pro` — Akash Engine: navy/blue, Inter-only, 8px radius
3. `nwkids-warm` — NW Kids: orange/green/blue, Nunito+OpenSans, 12px radius
4. `archonx-dark` — ARCHON-X: darkbg/code-blue/gold, JetBrainsMono+Inter
5. `yappyverse-pop` — Yappyverse: saturated primaries, rounded, bouncy
6. `kupuri-heritage` — Kupuri: terracotta/turquoise, cultural motifs
7. `hustle-bold` — HustleClaude: high-contrast, aggressive typography
8. `culture-energy` — Culture Shock: sports energy, bold reds/blacks

**shadcn/ui integration**: Always output `globals.css` CSS vars in addition to Tailwind config. Both are needed.
**Radius convention**: mob-noir uses 4px, akash-pro uses 8px, nwkids uses 12px+. Never mix within a single BU.

## Example Interactions
1. "Give me the Tailwind config + shadcn globals.css for the Pauli Effect website" → Both files, mob-noir theme
2. "Generate a custom theme for a new Akash Engine client in the fitness industry" → Custom theme, akash-pro base + fitness energy
3. "Apply the archonx-dark theme to this React component" → Themed component code
4. "Audit the newworldkids repo for theme drift from nwkids-warm" → Audit report with file-by-file findings
5. "Export all 8 canonical themes as Figma tokens" → 8 Figma token JSON files, one per theme
