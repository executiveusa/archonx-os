# Pauli Canvas Design
## skill_id
`canvas_pauli`

## Purpose
Generates production-ready static visual designs — posters, covers, cards, one-pagers, and campaign assets — for all Pauli Empire entities. Outputs are PNG and PDF files created via Python (Pillow/reportlab) or SVG, sized and formatted for our actual distribution channels. Specializes in: investor one-pagers (Akash Engine, NW Kids), campaign posters (NW Kids fundraising, Culture Shock events), character/avatar cards (Yappyverse, Pauli IP), and Mob-Noir editorial layouts (The Pauli Effect brand materials).

## When to Use
- Creating a fundraising campaign poster for NW Kids or Culture Shock
- Generating investor one-pager layouts
- Building Yappyverse character cards (avatar art with stats)
- Making event flyers for Culture Shock Sports
- Producing Akash Engine case study covers or proposal covers
- Creating social media static posts (not animated)

## Inputs
```
design_type: "poster" | "one-pager" | "avatar-card" | "event-flyer" | "social-static" | "cover"
entity: [entity name]
dimensions: "US-Letter" | "A4" | "1080x1080" | "1200x628" | "custom WxH"
export: "png" | "pdf" | "svg" | "all"
content: {headline, subheadline, body_copy, cta, key_stats[]}
brand_theme: auto-detected from entity or override
assets: [image paths or URLs if any]
```

## Outputs
- Production-ready PNG file (300dpi for print, 72dpi for web)
- PDF version for print/sharing
- Source SVG if vector output requested
- Figma-ready description of the layout for handoff

## Tools & Integrations
- Python Pillow + reportlab for raster/PDF generation in container
- Cloudflare Pages for hosting static assets
- Figma MCP for import/export
- canvas-design SKILL.md patterns for execution

## Project-Specific Guidelines
- Always check brand_pauli for correct colors/fonts before generating
- Investor one-pagers: max 1 page, 3-5 stats, 1 chart, 1 clear ask
- NW Kids posters: real child photography (placeholder boxes if no assets), warm colors, emotional headline first
- Avatar cards: 400x600px base, character art top 60%, stats bottom 40%, dark background
- Social statics: always include logo mark bottom-right, never crowd the frame
- Mob-Noir layouts: heavy black, gold accents, diagonal composition, film grain texture overlay

## Example Interactions
1. "Make a NW Kids fundraising poster for the Seattle food drive" → Warm poster, PNG + PDF, print-ready
2. "Create an Akash Engine proposal cover for a $10K/mo client" → Professional cover, Navy/Blue palette, PDF
3. "Design a Yappyverse character card for YAPPY #001" → Avatar card 400x600, dark bg, character stats
4. "Generate a Culture Shock Sports event flyer for the March tournament" → Event flyer, 1080x1080 social + 8.5x11 print
5. "Make a 1-page investor brief for NW Kids' Boeing pitch" → Clean one-pager, impact stats, donation ask
