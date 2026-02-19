
# Pauli Agent Directory

## Agents
1. **Pauli (The Truth Teller)**: The face of the brand. Handles the live brainstorming and script tone.
2. **Researcher**: Ingests news from RSS and searches for automation pain points.
3. **Producer**: Manages the Veo render queue and scene assembly.
4. **Fixer (Self-Heal Agent)**: Monitors logs and attempts patches on failed automation runs.

## Workflows
- **Daily Content Loop**: Research -> Script -> Voice -> Render -> Publish.
- **Lead Capture**: UGC Ad -> Landing Page -> Supabase -> CRM Webhook.
- **Niche Detection**: Scans repo structure and docs to classify the business niche.

## Integration Patterns
- **n8n library**: Used as a pattern library for Python equivalents.
- **Supabase**: Primary data store for lead metrics and logs.
- **Google Search Grounding**: Ensures script facts are valid.
