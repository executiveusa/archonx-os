# ArchonX Master Implementation TODO

## Purpose
This file is the execution checklist for the approved Archon-X architecture plan.
It converts the synthesis into concrete implementation work across controller, workers,
tooling, memory, products, and white-label packaging.

## Rules
- `archonx-os` remains the only controller.
- All worker integrations must be attached through Archon-owned contracts.
- `DesktopCommanderMCP` is the primary machine-control tower.
- `mcp2cli` is mandatory for MCP and OpenAPI invocation paths unless a documented exception exists.
- Frontend and visual work must follow the mandatory design law skill in `.archonx/toolbox/skills/mandatory-design-law/SKILL.md`.

## Phase 1: Foundation
- [ ] Create a canonical repo registry schema that supports repo placement, runtime model, capability tags, ownership, and product association.
- [ ] Extend the existing repo registry to store controller, worker, plugin, sidecar, memory, frontend, and product classifications.
- [ ] Add a worker capability registry for Darya/OpenHands, agency-agents, Goose, Agent Zero, ralphy, and future workers.
- [ ] Define a canonical task envelope schema with objective, repo scope, branch, constraints, tool budget, approvals, result schema, and trace identifiers.
- [ ] Add a routing policy layer that enforces controller-worker separation.
- [ ] Add environment ownership manifests by service and env category.
- [ ] Define a canonical integration manifest for sidecars, plugins, and edge services.
- [ ] Add architecture-bundle loaders so Archon can ingest `data/architecture/*.json` as runtime references.

## Phase 1A: Control Path Hardening
- [ ] Add first-class `DesktopCommanderMCP` registration in Archon control-plane configuration.
- [ ] Add first-class `mcp2cli` registration in Archon control-plane configuration.
- [ ] Make `mcp2cli` the default invocation adapter for MCP and OpenAPI tool calls.
- [ ] Add policy checks for destructive machine actions before forwarding to `DesktopCommanderMCP`.
- [ ] Add audit events for every routed machine-control action.
- [ ] Add failure handling and fallback semantics for control-tower outages.

## Phase 1B: Routing and Contracts
- [ ] Update router logic so worker selection is based on worker capabilities, not only repo domain class.
- [ ] Add worker intent categories such as `code_change`, `desktop_action`, `cloud_coding`, `multi_agent`, `content_sync`, and `deployment`.
- [ ] Add plugin routing for `ext-apps`, `jcodemunch-mcp`, and future MCP tools.
- [ ] Add edge-routing metadata for `Cloudflare Tunnel`.
- [ ] Add memory-routing metadata for `Notion` and Pauli memory flows.

## Phase 2: Worker Integration
- [ ] Build the `Darya/OpenHands` adapter behind the task envelope contract.
- [ ] Build the `agency-agents` adapter behind the task envelope contract.
- [ ] Build the `Agent Zero` adapter as a specialized worker class.
- [ ] Build the `ralphy` adapter as a specialized worker class.
- [ ] Build the `Goose` adapter as a cloud-coding worker class.
- [ ] Add worker registration, health checks, and capability self-reporting.
- [ ] Add execution trace persistence from all workers back into Archon state.
- [ ] Add job budget enforcement and timeouts across all worker adapters.

## Phase 2A: Goose Integration
- [ ] Publish a canonical repo inventory API that Goose can consume.
- [ ] Publish a canonical extension registry API that Goose can consume.
- [ ] Define an allowlist for Goose extensions and workflows.
- [ ] Add repo-awareness and extension-awareness tests for Goose.
- [ ] Add policy gating for cloud-coding jobs before Goose execution.

## Phase 2B: Tool Plugin Integration
- [ ] Define a plugin manifest contract for `ext-apps`.
- [ ] Define a plugin manifest contract for MCP-native tools like `jcodemunch-mcp`.
- [ ] Register plugin capabilities in the same registry used by workers.
- [ ] Route plugin calls through `mcp2cli` where supported.
- [ ] Add plugin audit and policy controls.

## Phase 3: Memory and Product Normalization
- [ ] Define the canonical `Notion` schema for second-brain content and operational memory.
- [ ] Add a memory service layer that isolates raw Notion access behind Archon APIs.
- [ ] Mark `pauli-comic-funnel` as the canonical Pauli frontend/public funnel.
- [ ] Mark `THE PAULI EFFECT` as a product and brand layer on top of shared Archon services.
- [ ] Build a Pauli repo family map that separates frontend, memory, product, archive, and duplicate assets.
- [ ] Archive or deprioritize duplicate Pauli repos not used in the canonical stack.
- [ ] Define content-sync flows between Archon memory and Pauli frontend layers.

## Phase 3A: Deployment and Edge
- [ ] Define shared deployment manifests for product layers.
- [ ] Centralize `Cloudflare Tunnel` route ownership in Archon deployment configs.
- [ ] Separate internal control-plane routes from public product routes.
- [ ] Add deployment metadata for white-label product variants.

## Phase 4: White-Label Productization
- [ ] Split platform configuration from product and brand configuration.
- [ ] Create a tenant/product manifest model for white-label deployments.
- [ ] Make worker bundles reusable across products.
- [ ] Make plugin bundles reusable across products.
- [ ] Add product-shell contracts so new brands can sit on the same platform core.
- [ ] Add white-label packaging docs and deployment examples.

## Cross-Cutting Work
- [ ] Add automated validation for canonical architecture files inside the repo.
- [ ] Add tests for repo registry, worker registry, and routing policy logic.
- [ ] Add tests for task envelope validation.
- [ ] Add tests for mandatory invocation-layer enforcement.
- [ ] Add architecture drift checks to CI.
- [ ] Update operational docs and onboarding docs to reflect the canonical topology.
- [ ] Keep README and routing docs aligned with the canonical architecture files.

## Frontend and Design Law
- [ ] Enforce the mandatory design skill for all frontend and visual tasks.
- [ ] Add design review checkpoints to PR and agent workflows.
- [ ] Require mobile responsiveness, clear hierarchy, and Steve Krug usability compliance for all visual work.
- [ ] Prevent generic, decorative, or confusing UI patterns from entering product layers.

## Immediate Next Build Slice
- [ ] Add controller and worker placement metadata to the repo registry models.
- [ ] Add a worker capability model and persistence layer.
- [ ] Add a canonical task envelope schema module.
- [ ] Add `DesktopCommanderMCP` and `mcp2cli` as typed integration entities in the registry.
- [ ] Add tests proving Archon remains the sole planner while workers stay execution-only.
