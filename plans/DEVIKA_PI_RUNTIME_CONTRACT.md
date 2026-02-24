# Devika PI Runtime Contract and Extension Pack Spec

## Purpose

Define the concrete contract to remove hardcoded model use in Devika UI and route execution through profile-driven PI runtime behavior.

## Current Contract Risk

- UI sends direct model id payload in [`DevikaAgent.tsx`](../dashboard-agent-swarm/src/pages/DevikaAgent.tsx)
- Backend route accepts generic payload in [`agents.ts`](../dashboard-agent-swarm/server/routes/agents.ts)
- No typed execution profile boundary

## Target Request Contract

```json
{
  "agentId": "devika-001",
  "orgId": "org-id",
  "projectId": "project-id",
  "taskKind": "coding",
  "input": "user task",
  "executionProfile": "devika-pi-default",
  "beadId": "BEAD-DEVIKA-PI-001",
  "metadata": {
    "source": "dashboard",
    "requiresContext7": true
  }
}
```

## Backend Route Behavior

1. Validate required fields and profile id
2. Validate bead id for code-affecting task kinds
3. Resolve profile to PI runtime settings
4. Invoke Devika PI wrapper with policy options
5. Emit stage telemetry PLAN IMPLEMENT TEST EVALUATE PATCH REPEAT
6. Persist run metadata and report links

## Profile Resolution

Profiles
- `devika-pi-default`
- `devika-pi-safe`
- `devika-pi-research`

Each profile defines
- model routing defaults and fallbacks
- tool permissions
- context budget strategy
- Context7 requirement policy
- subagent policy

## PI Extension Pack for Devika

Root
- `agents/devika/pi/extensions/`

Modules
1. `task-loop.extension.ts`
   - Maintains till-done task state
   - Requires explicit completion transitions
2. `subagents.extension.ts`
   - Team and subagent dispatch
   - Enforces max concurrency
3. `safe-commands.extension.ts`
   - Command allowlist/denylist
   - Blocks destructive patterns
4. `status-widget.extension.ts`
   - Displays active profile, stage, and policy mode
5. `context7-guard.extension.ts`
   - Requires Context7 docs resolution before third-party API code generation

## UI Changes Required

- Replace raw `model_id` sender with `executionProfile`
- Add profile selector control
- Add stage timeline panel
- Show policy block feedback when commands denied

## Validation Cases

1. UI request with profile routes successfully
2. Missing bead id on code-affecting task is rejected
3. Context7 required operation without docs is blocked
4. Unsafe command request is denied and logged
5. Successful run emits machine-readable report reference

