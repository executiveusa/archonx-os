# Universal Platform Blueprint

## Objective

Turn the existing repo ecosystem into one white-labelable program with a clean split between:

- **ArchonX** as the backend operating system
- **Vibe Cockpit** as the frontend shell and client experience
- **Hermes** as the execution worker and repo operator
- **Pauli Claw Code** as the harness/runtime lab feeding runtime primitives into production

The end state is a voice-first, chat-first, visually rich operating system that lets a human describe intent while the platform routes tasks, executes them, shows live work, and returns artifacts, code changes, and approvals.

---

## Product Shape

### Public product surfaces

1. **ArchonX Landing Page**
   - cinematic branded page
   - explains the backend operating system
   - premium motion design
   - hero concept: seated operator in a rattan chair moving through space beside the ship / vessel motif

2. **Studio Cockpit**
   - Jarvis-style control surface
   - voice/chat first
   - live activity pane
   - project context
   - approval queue
   - artifact/result pane

3. **White-label Client Frontend**
   - secret-free frontend deployable to Cloudflare/Vercel
   - points to ArchonX backend
   - supports BYO model and BYO API key
   - themeable and rebrandable

---

## Canonical Architecture

```text
User voice/chat
   ↓
Frontend shell / MCP Apps / Studio cockpit
   ↓
ArchonX API + WebSocket + MCP
   ↓
Run engine + provider router + policy engine + state manager
   ↓
Hermes workers + browser/computer-use + repo ops + asset generation
   ↓
Artifacts, events, diffs, approvals, live run state
```

---

## Repo Responsibilities

## 1. `archonx-os`

Use as the **system of record**.

### Owns
- workspace / tenant model
- run state machine
- agent registry
- provider router
- BYO key handling
- secrets policy
- auth / billing gate
- WebSocket/event streaming
- MCP server tools/resources
- audit trail
- durable job state

### Must expose
- API
- MCP
- CLI
- event stream

### Must not do long-term
- serve the final client frontend as an inseparable backend artifact
- hold client-side branding logic
- leak secrets into frontend builds

---

## 2. `pauli-vibe_cockpit`

Use as the **frontend shell**.

### Owns
- landing page
- studio cockpit
- white-label theming
- conversational shell UI
- live run visibility
- approvals UX
- project/repo/operator views

### Design principle
- minimize manual clicking
- maximize conversational control + visible execution

---

## 3. `pauli-hermes-agent`

Use as the **execution worker**.

### Owns
- repo review
- project review
- patch planning
- repo patching
- front-end uplift
- asset/image workflows
- browser/session workflows
- GitHub-connected execution

### Runtime behavior
- autonomous for safe read-only work
- approval gated for writes / deploys / public actions / destructive changes

---

## 4. `pauli-claw-code`

Use as the **harness/runtime laboratory**.

### Supplies production concepts for import
- turn loops
- command registry
- tool registry
- permission context
- session persistence
- remote runtime modes
- parity audit ideas

Do not merge this repo wholesale into production systems. Import primitives only.

---

## Canonical Runtime Objects

These should converge across repos.

### Workspace
- id
- brand config
- billing status
- model policy
- secret policy

### Project
- id
- workspace_id
- name
- repo bindings
- trajectory
- status

### Run
- id
- project_id
- workspace_id
- intent
- requested_by
- status
- active_tool
- active_agent
- approval_state
- outputs
- audit log

### Artifact
- id
- run_id
- type (`report`, `diff`, `image`, `prompt_set`, `asset_map`, `preview`, `pr_link`)
- uri or payload

### Approval
- id
- run_id
- action_type
- risk_level
- requested_action
- expires_at
- decision

### Provider Credential
- id
- workspace_id
- provider
- label
- encrypted_secret_ref
- scopes
- enabled

---

## Core Execution Modes

### 1. Review only
- inspect project/repo
- summarize state
- recommend trajectory
- no mutation

### 2. Plan only
- generate implementation plan
- produce assets/specs/diffs
- no mutation

### 3. Execute with approvals
- branch
- patch files
- create assets
- commit / PR
- request approval when policy requires it

### 4. Background automation
- watch project state
- open review runs
- propose fixes
- create recurring reports

---

## BYO Key / Provider Model

### Goals
- clients can use their own provider and their own key
- frontend contains no secrets
- ArchonX routes all inference through workspace policy
- subscriptions can be enforced by backend access control without breaking the frontend shell

### Required providers
- OpenAI
- Anthropic
- Google
- OpenRouter
- custom OpenAI-compatible endpoints

---

## White-label Deployment Model

### Frontend
- deploy independently to Cloudflare/Vercel
- secret-free
- workspace-specific branding config
- runtime API endpoint configuration

### Backend
- ArchonX remains the control plane and billing gate
- workspace can be enabled/disabled centrally
- customer access can be cut off by backend policy without redeploying frontend

---

## Agent Theater Requirement

Live computer-use visibility is a first-class feature.

### Required views
- current task
- current page / app / window
- screenshots or streamed viewport
- current tool call
- repo/file in focus
- approvals / pause / takeover actions

This is essential for user trust and product differentiation.

---

## MCP Apps Strategy

Use MCP Apps as the inline UI layer for:

- run monitor
- project review
- repo action preview
- asset picker / asset application
- model/provider setup
- live theater widgets

The conversation remains the primary shell. Rich UIs appear inline when helpful.

---

## Production Hardening Priorities

1. decouple frontend deployment from backend serving
2. eliminate hard-coded infrastructure configuration
3. centralize run/tool/project schemas
4. add policy-based approval engine
5. add encrypted workspace-scoped secret storage
6. add event streaming and durable run logs
7. add automated health, replay, and rollback paths
8. move runtime-critical layers to Rust without changing external contracts

---

## Rust Migration Order

### Move first
- run engine
- event bus
- policy engine
- provider router
- MCP server / bridge
- connector layer
- graph/index engine
- computer-use control primitives

### Keep flexible initially
- prompt composition
- experimental workflows
- fast-moving agent logic
- feature iteration glue

---

## Success Condition

A user can talk to the system naturally, watch it operate in real time, approve risky actions only when needed, and receive completed work across repos, assets, and applications without manually orchestrating tools.
