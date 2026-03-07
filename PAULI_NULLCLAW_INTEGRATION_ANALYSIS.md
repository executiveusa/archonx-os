# NullClaw Integration Analysis — ARCHONX OpenClaw Enhancement

**Date:** March 4, 2026  
**Repo:** `git@github.com:executiveusa/pauli-nullclaw.git`  
**Current OpenClaw:** Franken-Claw (Python, 64 agents, port 18789)  
**NullClaw:** Zig-based edge runtime (678 KB binary, ~1 MB RAM, <2 ms startup)

---

## Executive Summary

**NullClaw is the missing lightweight edge layer for ARCHONX.** It's OpenClaw-compatible but built in Zig for extreme portability and minimal resource overhead. Your current Franken-Claw orchestration remains the **command center**, while NullClaw becomes:

1. **Edge agent runtime** — Deploy to ARM SBCs, edge devices, cheap cloud VMs
2. **Channel ingestion gateway** — Lightweight message collection (Telegram, Signal, Discord, Nostr, IRC)
3. **Memory synchronization bridge** — Hybrid memory (local SQLite ↔ Franken-Claw distributed memory)
4. **Specialized tool executor** — High-isolation sandbox for untrusted workloads
5. **Offline-first failover** — When central Franken-Claw is unavailable

---

## Current ARCHONX Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ARCHONX KERNEL (Port 18789)               │
│                    Franken-Claw (Python)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  White Crew  │  │  Black Crew  │  │ Orchestrator │      │
│  │  (32 agents) │  │  (32 agents) │  │   (Pauli)    │      │
│  └────────┬─────┘  └────────┬─────┘  └──────────┬───┘      │
│           │                 │                   │            │
│           └─────────────────┼───────────────────┘            │
│                             │                                │
│  ┌──────────────────────────▼──────────────────────────────┐│
│  │         PAULIWHEEL Compliance Routing                   ││
│  │  (Bead tracking, tool gating, safety layer)            ││
│  └──────────────────────────┬──────────────────────────────┘│
│                             │                                │
│  ┌──────────────────────────▼──────────────────────────────┐│
│  │    IronClaw Security + Channel Handlers                 ││
│  │  (WhatsApp, Telegram, Slack, Orgo, etc)               ││
│  └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
        │
        │ tool_dispatch()
        │ dispatch_tool(tool_name, params, client_id)
        │
   [Tools, Sandbox, Output Safety]
```

---

## NullClaw Architecture (Zig-based)

```
678 KB Binary | <1 MB RAM | <2 ms startup

┌────────────────────────────────────────────────────────────┐
│               NullClaw Runtime (Zig)                       │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Gateway (HTTP + WebSocket) — Port 3000               │ │
│  │ Authentication: 6-digit pairing + bearer token       │ │
│  └────────────┬─────────────────────────────────────────┘ │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐ │
│  │ Channel Vtable (19 channels)                         │ │
│  │ Telegram | Signal | Discord | Slack | Nostr | IRC   │ │
│  │ WhatsApp | Webhook | iMessage | Matrix | OneBot     │ │
│  └────────────┬─────────────────────────────────────────┘ │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐ │
│  │ Agent Loop + Tool Dispatch                           │ │
│  │ 22+ AI providers (OpenRoute, Anthropic, Groq, etc)  │ │
│  │ 18+ tools (shell, file, http_request, screenshot)   │ │
│  └────────────┬─────────────────────────────────────────┘ │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐ │
│  │ Memory (SQLite)                                      │ │
│  │ Vector DB + FTS5 Keyword Search + Hybrid Merge      │ │
│  └────────────┬─────────────────────────────────────────┘ │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐ │
│  │ Security Layers                                      │ │
│  │ Sandbox: Landlock | Firejail | Bubblewrap | Docker  │ │
│  │ Secrets: ChaCha20-Poly1305 encryption               │ │
│  │ Filesystem: workspace_only, symlink detection       │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Integration Strategy: 5-Layer Hybrid Architecture

### Layer 1: Edge Ingestion (Channels → Franken-Claw)

**What NullClaw provides that Franken-Claw needs:**
- Lightweight, deployable channel collectors (Telegram, Signal, Nostr, IRC)
- Minimal resource footprint for remote/edge deployments
- Out-of-the-box sandbox isolation per channel

**Implementation:**

```yaml
# ~/.nullclaw/config.json (edge instance)
channels:
  telegram:
    accounts:
      main:
        bot_token: "YOUR_TOKEN"
        allow_from: ["*"]
        # On message: POST to Franken-Claw webhook
        webhook_url: "http://franken-claw-central:18790/channel/telegram"
        auth_token: "WEBHOOK_SECRET"
  
  signal:
    accounts:
      main:
        phone: "+1234567890"
        signal_url: "http://signal-rest-api:8080"
        webhook_url: "http://franken-claw-central:18790/channel/signal"

gateway:
  port: 3000
  require_pairing: true
  allow_public_bind: false

tunnel:
  provider: "tailscale"  # or cloudflare/ngrok for remote access
```

**Franken-Claw receiver handler:**
```python
# archonx/openclaw/channels/nullclaw_edge.py (NEW)

class NullClawEdgeHandler(ChannelHandler):
    """
    Receive messages from edge NullClaw instances.
    Each edge instance is a lightweight channel collector
    that forwards normalized events to central Franken-Claw.
    """
    channel_name = "nullclaw_edge"
    
    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        """
        Receive normalized webhook from edge NullClaw.
        
        Expected payload:
        {
          "source_channel": "telegram|signal|discord|nostr",
          "source_gateway_id": "edge-east-1",
          "user_id": "...",
          "message": "...",
          "attachments": [...],
          "timestamp": "ISO8601"
        }
        """
        return IncomingMessage(
            channel="nullclaw_edge",
            client_id=raw.get("source_gateway_id", "unknown"),
            sender=raw.get("source_channel", ""),
            text=raw.get("message", ""),
            metadata={
                "origin_gateway": raw.get("source_gateway_id"),
                "origin_channel": raw.get("source_channel"),
                "original_user_id": raw.get("user_id"),
            },
        )
    
    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        """
        Route response back through edge NullClaw to original channel.
        """
        # NullClaw instance will handle channel-specific routing
        return {
            "status": "queued_to_edge",
            "edge_gateway": message.metadata.get("origin_gateway"),
            "target_channel": message.metadata.get("origin_channel"),
        }
```

**Benefit:** Deploy NullClaw on 5 continents for regional message ingestion. Franken-Claw stays central and never exposes port 18789 publicly.

---

### Layer 2: Memory Synchronization (Hybrid SQLite ↔ Distributed)

**NullClaw memory:** Local SQLite (vector + FTS5)  
**Franken-Claw memory:** Distributed (Redis/Postgres/custom)

**Sync bridge:**

```python
# archonx/openclaw/memory/nullclaw_sync.py (NEW)

class NullClawMemorySyncBridge:
    """
    Bidirectional memory sync between edge NullClaw
    and central Franken-Claw memory layer.
    
    Modes:
    - broadcast: Franken-Claw → all NullClaws
    - pull: NullClaw asks for central memory on startup
    - push: Edge NullClaw sends local memories to central (on idle)
    - migrate: nullclaw migrate openclaw --from EDGE
    """
    
    async def sync_to_edge(
        self,
        gateway_id: str,
        memory_snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Broadcast memory to edge gateway.
        Used when:
        - New agent spins up on edge
        - Central policy/context changes
        - Full sync requested
        """
        # POST to edge gateway's /memory/sync endpoint
        url = f"http://{gateway_id}/memory/sync"
        return await self._post(url, memory_snapshot)
    
    async def sync_from_edge(
        self,
        gateway_id: str,
        memory_export: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ingest local memories from edge NullClaw.
        Used for:
        - After offline period: merge new memories
        - Agent failover: transfer context to central
        - Scheduled consolidation (e.g., daily 02:00 UTC)
        """
        # Merge edge memories into central memory backend
        return await self._merge_memories(gateway_id, memory_export)
```

**NullClaw onboarding script (edge):**

```bash
#!/bin/bash
# scripts/edge-deploy.sh

# 1. Install NullClaw
brew install nullclaw  # or: zig build -Doptimize=ReleaseSmall

# 2. Setup with edge-specific config
nullclaw onboard --interactive \
  --api-key "$OPENROUTER_KEY" \
  --provider openrouter

# 3. Configure channels to forward to central
cat > ~/.nullclaw/config.json << 'EOF'
{
  "models": {
    "providers": {
      "openrouter": { "api_key": "$OPENROUTER_KEY" }
    }
  },
  "channels": {
    "telegram": {
      "accounts": {
        "main": {
          "bot_token": "$TELEGRAM_BOT_TOKEN",
          "webhook_url": "http://franken-claw-central:18790/channel/telegram",
          "auth_token": "$WEBHOOK_SECRET"
        }
      }
    }
  },
  "gateway": {
    "port": 3000,
    "require_pairing": true
  },
  "tunnel": {
    "provider": "tailscale"
  }
}
EOF

# 4. Start edge gateway
nullclaw gateway --port 3000 &
nullclaw service install
```

**Benefit:** Distributed memory with edge caching. Central Franken-Claw doesn't bottleneck on every memory query.

---

### Layer 3: Specialized Tool Executor (High-Isolation Sandbox)

**NullClaw's sandbox backends:** Landlock (Linux), Firejail, Bubblewrap, Docker  
**Use case:** Run untrusted tools with strict isolation

```python
# archonx/openclaw/backend.py (MODIFICATION)

class OpenClawBackend:
    async def dispatch_tool_via_nullclaw(
        self,
        tool_name: str,
        params: dict[str, Any],
        client_id: str,
        agent_id: str = "",
        sandbox_level: str = "high",  # "native", "high", "maximum"
        edge_gateway: str = "",  # e.g., "edge-us-west-1"
    ) -> dict[str, Any]:
        """
        Dispatch to NullClaw for high-isolation execution.
        
        Scenarios:
        1. User-submitted code (sandbox_level="maximum" + docker)
        2. Beta/untrusted tools (always via NullClaw)
        3. Resource-intensive tasks (run on edge closer to data)
        4. Fallback if central sandbox fails
        """
        
        if not edge_gateway:
            edge_gateway = self._select_nearest_edge(client_id)
        
        # Build NullClaw tool request
        request = {
            "tool": tool_name,
            "params": params,
            "sandbox": {
                "level": sandbox_level,
                "backend": "auto",  # NullClaw picks best available
                "workspace_only": True,
            }
        }
        
        # POST to edge NullClaw gateway
        edge_url = f"http://{edge_gateway}:3000/webhook"
        result = await self._post(edge_url, request, headers={
            "Authorization": f"Bearer {self._edge_token(edge_gateway)}"
        })
        
        # NullClaw returns execution result with sandbox metadata
        return {
            "status": result.get("status"),
            "tool": tool_name,
            "result": result.get("output"),
            "executed_on": edge_gateway,
            "sandbox_backend": result.get("sandbox_backend"),
            "exit_code": result.get("exit_code"),
        }
```

**NullClaw receiver (tool dispatch):**

```zig
// src/gateway.zig (NullClaw)
// Receive /webhook POST with tool execution request

async fn handle_webhook_tool(
    request: *const Request,
    tool_request: ToolRequest,
) !Response {
    // 1. Validate auth token
    const auth = request.headers.get("Authorization") orelse return error.Unauthorized;
    
    // 2. Extract tool + params
    const tool_name = tool_request.tool;
    const params = tool_request.params;
    
    // 3. Apply sandbox based on level
    const sandbox = switch (tool_request.sandbox.level) {
        "native" => Sandbox.none(),
        "high" => Sandbox.landlock(),  // or firejail
        "maximum" => Sandbox.docker(),
        else => Sandbox.auto(),
    };
    
    // 4. Dispatch tool through sandbox
    const result = try agent.dispatch_tool_sandboxed(
        tool_name,
        params,
        sandbox,
    );
    
    // 5. Return result to Franken-Claw
    return Response{
        .status = 200,
        .body = try json.stringify(result),
    };
}
```

**Benefit:** Xenophobic sandbox isolation. Untrusted code runs on NullClaw, not your central Franken-Claw.

---

### Layer 4: Offline-First Failover

**Problem:** Central Franken-Claw goes down → all agents blocked.  
**Solution:** NullClaw on-edge can buffer + replay.

```python
# archonx/openclaw/failover/nullclaw_buffering.py (NEW)

class NullClawFailoverBuffer:
    """
    When Franken-Claw is unreachable:
    1. NullClaw buffers incoming messages locally
    2. Queues tool execution requests
    3. Caches last-known agent context
    4. On reconnect: replays all buffered events
    """
    
    async def handle_central_offline(self, gateway_id: str) -> None:
        """NullClaw detects Franken-Claw is down."""
        logger.warning("Central Franken-Claw unreachable. Buffering mode ON.")
        
        # 1. Switch to offline-capable agent config
        config = self._get_offline_config(gateway_id)
        
        # 2. Use local models (not central dispatch)
        # e.g., switch to ollama or local groq
        config.models.providers.default = "ollama"
        
        # 3. Accept messages, queue them
        self.buffer.enable()
        
    async def replay_on_reconnect(self) -> None:
        """When Franken-Claw comes back online."""
        logger.info("Central Franken-Claw online. Replaying buffered events.")
        
        # 1. Get buffered messages
        buffered = self.buffer.flush()
        
        # 2. Replay in order
        for event in buffered:
            result = await self._post_to_central(event)
            if not result.ok:
                # Re-buffer if still failing
                self.buffer.append(event)
                break
```

**NullClaw config: offline fallback mode**

```json
{
  "offline_fallback": {
    "enabled": true,
    "buffer_size_mb": 512,
    "fallback_model": "groq/mixtral-8x7b-32768",
    "fallback_provider": "groq",
    "replay_on_reconnect": true
  }
}
```

**Benefit:** Message durability + graceful degradation. Users never see "gateway error" — they get fast local responses.

---

### Layer 5: Specialized Agent Runtime for Resource-Constrained Tasks

**Use NullClaw for:**
- Lightweight agents running on ARM SBCs
- IoT-adjacent tasks (sensor polling, edge inference)
- Regional sub-agents with local memory

```python
# Example: Deploy researcher agent on NullClaw for EMEA region

# ~/.nullclaw/config.json (EMEA edge)
{
  "agents": {
    "list": [
      {
        "id": "researcher-emea",
        "model": { "primary": "openrouter/anthropic/claude-sonnet-4" },
        "system_prompt": "You are a research agent focused on EMEA market trends...",
        "heartbeat": { "every": "30m" }
      }
    ]
  },
  "memory": {
    "backend": "sqlite",
    "embedding_provider": "openai",
    "auto_save": true,
    "snapshot_enabled": true,  # Export for central sync
    "snapshot_interval": "1h"
  }
}
```

**Franken-Claw orchestrator routes tasks:**

```python
# archonx/agents/orchestrator.py (MODIFICATION)

async def route_task(task: Task, client_id: str) -> str:
    """Route based on task type + geography."""
    
    if task.type == "research" and task.region == "EMEA":
        # Route to edge NullClaw agent
        edge_gateway = "researcher-emea-001"
        return await self.dispatch_to_edge(task, edge_gateway)
    
    elif task.requires_many_tools:
        # Route to central Franken-Claw (rich orchestration)
        agent = self.select_agent(task.domain)
        return await agent.execute(task)
    
    else:
        # Route to nearest edge for fast response
        edge = self.select_nearest_edge(client_id)
        return await self.dispatch_to_edge(task, edge)
```

**Benefit:** Global agent deployment without latency tax. Specialized regional agents with local context.

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Clone pauli-nullclaw into `services/nullclaw/`
- [ ] Create `archonx/openclaw/channels/nullclaw_edge.py` handler
- [ ] Deploy test NullClaw instance on localhost:3000
- [ ] Document channel forwarding webhook contract

### Phase 2: Ingestion (Week 3-4)
- [ ] Add Telegram → Franken-Claw webhook relay
- [ ] Add Signal → Franken-Claw webhook relay
- [ ] Add Discord → Franken-Claw webhook relay
- [ ] Test multi-channel message flow

### Phase 3: Memory Sync (Week 5-6)
- [ ] Implement `NullClawMemorySyncBridge`
- [ ] Add `/memory/sync` endpoints to both systems
- [ ] Test bidirectional memory flow
- [ ] Implement `nullclaw migrate openclaw` integration

### Phase 4: Sandbox Dispatch (Week 7-8)
- [ ] Add `dispatch_tool_via_nullclaw()` method
- [ ] Implement sandbox level routing
- [ ] Deploy edge NullClaw with sandbox testing
- [ ] Create isolation test suite

### Phase 5: Failover & Offline (Week 9-10)
- [ ] Implement buffering on NullClaw
- [ ] Test central offline scenario
- [ ] Implement replay logic
- [ ] End-to-end failover test

### Phase 6: Global Deployment (Week 11-12)
- [ ] Containerize NullClaw for ARM
- [ ] Deploy to 5+ edge locations
- [ ] Create agent routing logic
- [ ] Production observability + monitoring

---

## File Changes Summary

### New Files to Create

```
archonx/openclaw/
├── channels/nullclaw_edge.py           # Edge channel handler
├── memory/nullclaw_sync.py             # Memory bridge
├── failover/nullclaw_buffering.py      # Offline buffer
└── tools/nullclaw_dispatch.py          # Tool executor router

services/nullclaw/                       # Submodule (fork)
├── config.example.json                 # Edge config template
├── edge-deploy.sh                      # Deployment script
└── docker-compose.edge.yml             # ARM-compatible stack
```

### Modified Files

```
archonx/openclaw/backend.py
  - Add dispatch_tool_via_nullclaw()
  - Add _select_nearest_edge()
  - Add _edge_token() auth

archonx/kernels.py (or similar)
  - Register nullclaw_edge channel handler
  - Add edge heartbeat monitoring

tests/
  - Add test_nullclaw_edge_channel.py
  - Add test_nullclaw_memory_sync.py
  - Add test_nullclaw_failover.py

docs/
  - Add NULLCLAW_INTEGRATION.md
  - Add edge-deployment-guide.md
```

---

## Configuration Changes

### Franken-Claw (Central)

```yaml
# archonx-config.json

openclaw:
  # Existing
  port: 18789
  
  # NEW: Edge integration
  edge_gateways:
    - id: "edge-us-west-1"
      url: "http://edge-us-west-1:3000"
      auth_token: "ENV:EDGE_US_WEST_TOKEN"
      region: "us-west-2"
      channels: ["telegram", "signal"]
    
    - id: "edge-emea-1"
      url: "http://edge-emea-1:3000"
      auth_token: "ENV:EDGE_EMEA_TOKEN"
      region: "eu-west-1"
      channels: ["telegram", "discord", "nostr"]
  
  memory_sync:
    enabled: true
    mode: "broadcast_on_change"  # or "pull", "push", "manual"
    interval_secs: 3600
    bidirectional: true
  
  failover:
    nullclaw_buffering: true
    offline_mode_timeout_secs: 300
    replay_on_reconnect: true
```

### NullClaw (Edge)

```json
{
  "gateway": {
    "port": 3000,
    "require_pairing": true,
    "allow_public_bind": false
  },
  
  "tunnel": {
    "provider": "tailscale",
    "tailscale": {
      "auth_key": "ENV:TAILSCALE_AUTH_KEY"
    }
  },
  
  "channels": {
    "telegram": {
      "webhook_url": "http://franken-claw-central:18790/channel/telegram",
      "auth_token": "ENV:WEBHOOK_SECRET"
    }
  },
  
  "memory": {
    "backend": "sqlite",
    "sync_url": "http://franken-claw-central:18790/memory/sync",
    "sync_interval_secs": 3600,
    "buffer_size_mb": 512
  },
  
  "offline_fallback": {
    "enabled": true,
    "fallback_model": "groq/mixtral-8x7b-32768",
    "fallback_provider": "groq"
  }
}
```

---

## Testing Strategy

```python
# tests/test_nullclaw_integration.py

class TestNullClawEdgeChannel:
    async def test_telegram_webhook_forwarding(self):
        """NullClaw receives Telegram → forwards to Franken-Claw."""
        ...
    
    async def test_channel_handler_routing(self):
        """Franken-Claw routes edge messages to correct agent."""
        ...

class TestNullClawMemorySync:
    async def test_memory_broadcast_to_edge(self):
        """Central memory syncs to edge on startup."""
        ...
    
    async def test_memory_merge_from_edge(self):
        """Edge memories consolidated back to central."""
        ...
    
    async def test_bidirectional_consistency(self):
        """Memory stays in sync after multiple round-trips."""
        ...

class TestNullClawToolDispatch:
    async def test_high_isolation_sandbox(self):
        """Tool runs in docker sandbox on edge."""
        ...
    
    async def test_sandbox_level_routing(self):
        """Unsafe tools auto-route to NullClaw."""
        ...

class TestFailoverBehavior:
    async def test_central_offline_buffering(self):
        """Messages buffer when Franken-Claw unreachable."""
        ...
    
    async def test_replay_on_reconnect(self):
        """Buffered messages replay in order."""
        ...
    
    async def test_offline_fallback_model(self):
        """Edge uses local model when central down."""
        ...
```

---

## Benefits Summary

| Aspect | Current (Franken-Claw only) | With NullClaw Integration |
|--------|------------------------------|--------------------------|
| **Deployment** | Single central host | Central + 5+ edge nodes |
| **Channel ingestion** | All in Python | NullClaw lightweight collectors |
| **Memory footprint** | N/A | ~1 MB per edge instance |
| **Resource sprawl** | Growing CPU/RAM on central | Distributed to edges |
| **Failover latency** | No failover (hard-fail) | <1s buffering + replay |
| **Tool isolation** | Native/Firejail only | Landlock/Docker/Firejail picker |
| **Startup time** | N/A | <2 ms edge deployment |
| **Geographic latency** | Single point, global latency | Regional agents, <50 ms |
| **Binary portability** | Python 3.9+ required | Single 678 KB statically-linked binary |
| **Edge deployment** | Not feasible | Raspberry Pi / $5 boards |
| **Memory consolidation** | N/A | Hybrid sync (SQLite ↔ distributed) |

---

## Next Steps

1. **Week 1:** Review this analysis with architecture team. Confirm priorities (ingestion > memory > failover?).
2. **Week 2:** Set up NullClaw test instance locally. Validate OpenClaw config compatibility.
3. **Week 3:** Implement edge channel handler. Start with Telegram → Franken-Claw flow.
4. **Week 4+:** Iterate through roadmap phases.

---

## Questions for Stakeholder Review

1. **Priority:** Which layer is most valuable first? (Ingestion / Failover / Memory / Sandbox / Global)
2. **Regions:** Where should edge NullClaw instances be deployed? (AWS regions? Hetzner? Personal infra?)
3. **Failover tolerance:** How many minutes of downtime is acceptable before switching to offline mode?
4. **Memory policy:** Should edge memories auto-sync to central, or pull-on-demand?
5. **Sandbox stringency:** Should all untrusted tools auto-route to NullClaw, or opt-in per agent?

---

**Document prepared by:** GitHub Copilot (Claude Haiku 4.5)  
**Status:** Ready for stakeholder review + implementation sprint planning
