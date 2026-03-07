# Avatar & Comic Scriptwriter
## skill_id
`avatar_pauli`

## Purpose
Writes scripts, dialog, story arcs, and short-form content for all Pauli Empire IP characters and comics — Yappyverse, PAULI (the AI avatar), Mob-Noir Pauli characters, and any NW Kids/Culture Shock story characters. Maintains an internal canon bible (stored in Second Brain under yappy_schema) for character consistency across episodes, media types, and collaborators. Generates content in multiple formats: comic panel scripts, social media character posts, YouTube script outlines, Discord character personas, and short story arcs.

## When to Use
- Writing Yappyverse episode scripts or character dialog
- Creating the PAULI avatar's voice/persona for videos or demos
- Writing Mob-Noir short fiction for The Pauli Effect brand storytelling
- Generating NW Kids impact stories (real stories, fictionalized for privacy)
- Building character personas for Akash Engine "mascot" or brand character
- Social media character posts (character speaks in their own voice)
- Maintaining canon consistency when multiple people contribute

## Inputs
```
content_type: "comic-script" | "social-post" | "story-arc" | "character-dialog" | "youtube-outline" | "discord-persona"
character: string (name from canon bible or "new character")
universe: "yappyverse" | "mob-noir-pauli" | "archonx-world" | "nwkids-stories"
episode_or_context: string description
tone: auto from universe or override
length: "micro (tweet)" | "short (panel/post)" | "medium (episode)" | "long (arc)"
canon_check: boolean (default: true — query Second Brain before writing)
```

## Outputs
- Formatted script (panel-by-panel for comics, scene-by-scene for video)
- Character dialog in voice (first-person social posts)
- Story arc outline (3-5 act structure)
- Canon bible entry for any new character introduced
- Posting/publishing schedule recommendation

## Tools & Integrations
- Second Brain (yappy_ schema): query canon bible before every script
- Notion MCP: push new canon entries and episode scripts
- algo_art_pauli: request matching visual assets for the script
- canvas_pauli: comic panel layout specifications
- marketing_pauli: social distribution plan for content

## Project-Specific Guidelines
**Canon bible location**: Second Brain, yappy_ schema, title "YAPPYVERSE CANON BIBLE"
**Always query canon first**: `match_brain(query, schema_filter="yappy_")` before writing any character.
**PAULI avatar voice**: Wise, warm, systems-thinker. Speaks in metaphors about compounding and long-term thinking. References "7-generation thinking." Never corporate.
**Mob-Noir Pauli voice**: Cinematic, deliberate, mob-boss gravitas. Short sentences. Implies more than it states.
**Yappyverse tone**: Gen Z energy, self-aware humor, gaming references, but never cynical — always ultimately hopeful.
**NW Kids stories**: Child-centered, dignity-first, no poverty porn. Always agency and resilience, not victimhood.
**New characters**: Always include Name, Voice, Motivation, Flaw, Relationship to existing characters, Visual description (for canvas_pauli).

## Example Interactions
1. "Write a 6-panel Yappyverse comic where YAPPY learns about AI agents" → Full panel script, dialog, action descriptions, canon-checked
2. "Write 5 Twitter posts in the PAULI avatar's voice about compounding systems" → 5 posts, PAULI voice, 7-generation framework
3. "Create a new Mob-Noir character for The Pauli Effect lore — the fixer" → Character profile + first scene script + canon bible entry
4. "Write a 3-episode story arc for Yappyverse Season 2 opener" → 3-episode outline, character beats, cliffhanger hooks
5. "Create the ARCHON-X OS mascot character — give it a voice and backstory" → Full character spec, voice guide, 3 sample dialog lines
