# Onboarding Voice Agent

This package bootstraps a production onboarding voice flow from transcript inputs.

## Goal

Create a mission-aware onboarding agent that:
- captures founder goals and constraints,
- maps them to ArchonX capabilities,
- emits a first runnable task plan for the kernel.

## Inputs

- Raw transcript (`transcript_intake.md`)
- Account context (org name, project, priorities)
- Deployment context (Hostinger/Coolify/Cloudflare/Vercel)

## Outputs

- Normalized onboarding profile JSON
- Initial task bundle for `/api/task`
- Flywheel improvement hints for cycle 1

## Runtime handoff

1. Parse transcript into intent blocks.
2. Generate `onboarding_profile.json`.
3. Submit initial tasks to ArchonX API.
4. Log first run in dashboard `/api/agents/run`.
