# Pauli Algorithmic Art
## skill_id
`algo_art_pauli`

## Purpose
Generates production-ready generative and algorithmic visual art for the Pauli Empire using p5.js, Three.js, and canvas APIs. Tuned for three distinct brand aesthetics: Mob-Noir (dark, gold, cinematic — internal Pauli Effect), Awwwards-Trending (clean, bold, client-facing Akash Engine), and Yappyverse (vibrant, cartoon-energy, youth-forward). All outputs include seeded randomness for reproducibility, parameterized presets for easy variation, and export targets matched to our actual distribution channels (web, social, Discord/Slack, Coolify-hosted interactive pages).

## When to Use
- Generating social media visual assets (Instagram, Twitter/X, TikTok cover frames)
- Creating generative backgrounds for landing pages (Pauli Effect, NW Kids campaigns)
- Building interactive art experiences for Yappyverse or HustleClaude
- Producing animated loop assets for Discord/Slack community engagement
- Generating NFT-style avatar card art for Pauli IP characters
- Background art for ARCHON-X OS dashboard or Akash Engine client reports

## Inputs
```
theme: "mob-noir" | "awwwards" | "yappyverse"
output_format: "p5js" | "threejs" | "svg" | "canvas-static"
dimensions: "1080x1080" | "1920x1080" | "1080x1920" | "custom WxH"
seed: integer (for reproducibility)
palette_override: [hex, hex, ...] (optional)
animation: boolean
export_target: "web-embed" | "png-download" | "gif-loop" | "coolify-hosted"
```

## Outputs
- Self-contained HTML artifact (p5.js/Three.js embedded)
- Parameterized preset object (JSON) for regeneration
- Export-ready PNG/SVG/GIF depending on target
- Coolify deploy config if `export_target: "coolify-hosted"`

## Tools & Integrations
- p5.js (CDN: cdnjs.cloudflare.com) for 2D generative work
- Three.js r128 for 3D scenes
- Coolify API for hosting interactive pieces
- Vercel for static export pages
- Figma MCP for importing design tokens as palette inputs

## Project-Specific Guidelines
**Mob-Noir palette**: #0A0A0A (black), #D4AF37 (gold), #1C1C1C (charcoal), #F5F5F5 (off-white). Heavy use of grain texture, vignette, film noir lighting angles.
**Awwwards palette**: Clean whites, bold single accent (electric blue #2980B9 or coral), generous whitespace, no more than 2 typefaces.
**Yappyverse palette**: Saturated primaries, cartoon outlines, bouncy easing on animations.
Always include `let seed = <value>; randomSeed(seed); noiseSeed(seed);` at top of p5.js sketches.
Flow fields and particle systems are the preferred patterns — they scale from thumbnail to full-screen.
Never hard-code canvas size — always `createCanvas(windowWidth, windowHeight)` with responsive resize.

## Example Interactions
1. "Make a mob-noir flow field for the Pauli Effect homepage background" → p5.js sketch, black/gold palette, seeded, web-embed ready
2. "Generate a Yappyverse avatar card for character YAPPY #001" → Three.js scene, vibrant palette, PNG export 1080x1080
3. "Create an animated loop for our Discord server banner" → p5.js GIF-ready loop, 960x540, 3 seconds, Mob-Noir theme
4. "Build an interactive particle system I can host on Coolify" → p5.js + Coolify deploy config + Docker-ready HTML
5. "Generate 5 variations of the NW Kids campaign header art" → 5 seeded SVG exports, warm palette, youth-forward energy
