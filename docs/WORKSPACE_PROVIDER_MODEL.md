# Workspace and Provider Model

## Goal

Allow each client workspace to run on ArchonX with its own branding, model provider, and API credentials while keeping the frontend secret-free.

## Workspace

Each workspace should own:
- brand identity
- billing status
- allowed providers
- encrypted provider credentials
- feature flags
- approval policy
- API access status

## Provider routing

ArchonX should support:
- OpenAI
- Anthropic
- Google
- OpenRouter
- custom OpenAI-compatible endpoints

Each run resolves provider selection in this order:
1. explicit workspace override
2. explicit user selection if policy permits
3. workspace default provider
4. platform-managed fallback if enabled

## Secret handling

Rules:
- no provider secret in frontend builds
- no secret echoed to the client
- secrets stored only as encrypted backend references
- provider validation performed server-side

## White-label rule

Frontend deployments are public-shell applications only.
They should contain:
- backend base URL
- workspace slug
- public branding config
- non-secret feature flags

They should never contain:
- provider API keys
- backend admin tokens
- database credentials
- connector secrets

## Billing gate

When a workspace is suspended:
- frontend still loads
- backend rejects authenticated runs
- cockpit shows controlled suspension state
- no model calls or write actions execute

## Success condition

A new client can be deployed by shipping a themed frontend shell and binding it to an ArchonX workspace that controls provider access and policy entirely from the backend.
