# Archon-X Build Plan

## Executive Direction
Archon-X should be the controller, planner, router, and state layer for the ecosystem. Darya/OpenHands, agency-agents, Agent Zero, Goose, ralphy, and similar systems should operate as workers under Archon control. DesktopCommanderMCP should serve as the primary control tower for local machine operations, while mcp2cli should sit in front of MCP and OpenAPI invocations to reduce token overhead and normalize tool usage.

## What Archon-X Is Supposed To Be
Archon-X is the operating system and orchestration brain for the ecosystem. It should own planning, task routing, state and memory references, policy and approval boundaries, repo and capability registry, worker selection, and deployment and edge exposure decisions.

## Recommended Architecture
- Brain: `archonx-os`
- Control tower: `DesktopCommanderMCP`
- Invocation layer: `mcp2cli`
- Worker plane: `Darya/OpenHands`, `agency-agents`, `Agent Zero`, `Goose`, `ralphy`
- Plugin and integration plane: `ext-apps`, `jcodemunch-mcp`, `Cloudflare Tunnel`
- Memory plane: `Notion`, normalized Pauli repo family
- Frontend and product plane: `pauli-comic-funnel`, `THE PAULI EFFECT`

## Placement Recommendations
- `archonx-os`: core dependency and single controller
- `Darya/OpenHands`: worker service behind Archon job contracts
- `agency-agents`: worker service behind Archon routing
- `mcp2cli`: mandatory invocation sidecar
- `DesktopCommanderMCP`: primary control-tower sidecar
- `Goose`: cloud coding worker, repo-aware and extension-aware
- `ext-apps`: plugin layer for external connectors
- `ralphy`: specialized worker service
- `jcodemunch-mcp`: MCP plugin exposed through mcp2cli
- `pauli-comic-funnel`: canonical frontend layer
- `THE PAULI EFFECT`: product and brand layer on top of Archon-X
- `pauli-repo-family`: memory and archive consolidation bucket pending dedupe

## How Archon Should Control Darya/OpenHands
Archon should issue structured jobs to Darya rather than letting Darya choose system-wide goals. The minimum contract is task envelope with repo, branch, objective, constraints, and budget, allowed tool scope, result schema, audit trail, and callback into Archon state.

## How agency-agents Should Live
agency-agents should be a worker cluster behind Archon routing. Archon selects it when a task requires multi-agent decomposition or parallel execution. It should call tools through mcp2cli and DesktopCommanderMCP rather than owning direct uncontrolled integrations.

## How mcp2cli Should Reduce Token Overhead
mcp2cli should provide canonical short aliases and compressed invocation formats for tool usage. It should normalize desktop operations, repo inspection, deployment actions, MCP server calls, and OpenAPI tool calls. This reduces prompt bloat and prevents duplicated tool syntax across workers.

## Should DesktopCommanderMCP Be The Control Tower
Yes. It centralizes local machine control, process operations, file reads and writes, and observable execution boundaries. It should be used as the machine-facing sidecar under Archon policy.

## How Goose Should Be Integrated
Goose should not run blind. Archon should publish canonical repo inventory, repo tags and ownership classes, extension registry, approved tool bundles, and worker routing rules. Goose then becomes a governed cloud coding worker rather than a disconnected parallel system.

## How Pauli Fits Together
The Pauli stack should be organized as Notion for structured memory, pauli-comic-funnel for the public funnel, THE PAULI EFFECT for the brand layer, and pauli-repo-family as the backlog of content and legacy repos to dedupe, archive, or merge.

## What To Archive, Merge, Or Deprioritize
Archive or deprioritize zip-only or duplicate Pauli repos not mapped into the canonical stack, duplicated worker repos without a clear specialty, and direct tool wrappers superseded by DesktopCommanderMCP plus mcp2cli.

Merge candidates are Pauli content repos into a unified memory map, plugin wrappers into the mcp2cli invocation layer, and deployment edge configs into one Archon deployment manifest.

## Key Unfinished Work
- canonical repo registry is missing
- worker task contracts are not defined
- env ownership by service is not defined
- Goose extension and repo-awareness manifests are missing
- Pauli family repo dedupe is incomplete
- white-label product boundary between core platform and branded layers is not formalized

## Phased Implementation Plan
### Phase 1: Foundation
- create canonical repo registry
- create worker capability registry
- standardize DesktopCommanderMCP and mcp2cli as mandatory control layers
- define env ownership manifests

### Phase 2: Worker Integration
- integrate Darya/OpenHands behind Archon job contracts
- integrate agency-agents behind Archon routing
- connect Goose to repo inventory and extension registry
- register ralphy and Agent Zero as specialized workers

### Phase 3: Product Normalization
- normalize Pauli stack into memory, frontend, and product layers
- move The Pauli Effect onto shared Archon services
- archive duplicate Pauli repos and zip-only branches

### Phase 4: White-Label Platform
- externalize tenant and product configs
- package plugin bundles and worker bundles by vertical
- standardize deployment manifests and edge routing
- publish canonical APIs for memory, worker dispatch, and product shells
