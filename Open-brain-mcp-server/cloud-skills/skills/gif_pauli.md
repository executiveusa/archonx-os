# Pauli GIF & Animation
## skill_id
`gif_pauli`

## Purpose
Creates optimized animated GIFs and short video loops for Slack, Discord, social media, and web embed use across the Pauli Empire. Tuned for our actual internal culture: Mob-Noir cinematic energy for The Pauli Effect, hype/reaction GIFs for the Yappyverse community, clean motion for Akash Engine client deliverables. All outputs respect platform constraints (Slack: <2MB, Discord: <8MB, Twitter: <5MB) and are generated via Python (Pillow/imageio) or wrapped canvas animations.

## When to Use
- Internal Slack/Discord reaction GIFs (mob-noir memes, ARCHON-X status indicators)
- Yappyverse character animation loops for community
- Social media animated posts (Instagram stories, Twitter loops)
- Loading/progress animations for ARCHON-X dashboard
- Campaign launch countdown animations
- Akash Engine client presentation animations

## Inputs
```
type: "reaction-gif" | "logo-animation" | "text-animation" | "character-loop" | "progress-indicator" | "countdown"
theme: "mob-noir" | "yappyverse" | "akash-clean" | "nwkids-warm"
platform: "slack" | "discord" | "twitter" | "instagram-story" | "web-embed"
duration_sec: 1-10
text_overlay: string (optional)
fps: 12 | 24 | 30
```

## Outputs
- Optimized GIF file at correct dimensions and file size for target platform
- MP4 loop version (for platforms that prefer video)
- Embed code if web-embed target
- Usage instructions (correct Slack upload method, Discord emoji upload vs. message)

## Tools & Integrations
- Python Pillow + imageio for GIF generation in container
- p5.js canvas-to-GIF for generative animations
- Cloudflare Pages for hosting web-embed versions
- slack-gif-creator SKILL.md patterns for Slack-specific constraints

## Project-Specific Guidelines
**Slack constraints**: Max 2MB, 128x128 for emoji, 400x300 max for message GIFs. Always test file size.
**Discord constraints**: Max 8MB for standard, 50MB for Nitro. Emoji must be exactly 128x128.
**Loop quality**: Last frame must match first frame within 5% visual difference for seamless loop.
**Mob-Noir style**: Black bg, gold text/elements, slow-burn timing (ease-in-out, not bouncy).
**Yappyverse style**: Bright colors, bouncy easing (cubic-bezier overshoot), 24fps minimum.
Never use Comic Sans or Impact as text fonts. Use brand fonts from brand_pauli.

## Example Interactions
1. "Make a Slack GIF of the ARCHON-X logo powering up" → 400x300, <2MB, dark/gold, seamless loop
2. "Create a 'SHIPPED' reaction GIF in Mob-Noir style for our Slack" → 128x128 emoji, gold text, cinematic
3. "Build a loading spinner for the ARCHON-X dashboard" → Web-embed GIF, CSS animation code, dark theme
4. "Make a hype GIF for Yappyverse Discord when someone joins" → Vibrant, bouncy, character elements, <8MB
5. "Animated countdown for NW Kids 24-hour fundraising push" → 3-day countdown, warm palette, Instagram story size
