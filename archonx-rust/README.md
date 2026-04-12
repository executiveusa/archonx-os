# archonx-rust

Rust rewrite of the ArchonX-OS Python backend. Replaces Python services with a
Cargo workspace of focused crates, each compiled to a fast, memory-safe binary.

## Workspace Structure

```
archonx-rust/
├── Cargo.toml              # Workspace manifest (resolver = "2")
├── Dockerfile              # Multi-stage build → ~15MB binaries
├── MIGRATION_NOTES.md      # Python→Rust behavioral differences
│
├── archonx-core/           # Types, agents, protocol, flywheel
├── archonx-agents/         # Persona trait + task router
├── archonx-orchestration/  # Orchestrator singleton + swarm
├── archonx-memory/         # Memory manager (SQLx + in-memory fallback)
├── archonx-billing/        # Lock-free token meter
├── archonx-revenue/        # Revenue engine ($100M target)
├── archonx-graphbrain/     # Knowledge graph (bin: archonx-graphbrain)
└── archonx-api/            # Axum HTTP API (bin: archonx-api)
```

## Binaries

### `archonx-api`

Axum HTTP server. Serves the control tower frontend.

```
API_PORT=8000 archonx-api
```

Endpoints:
- `GET /healthz` → `{"ok": true}`
- `GET /api/agents` → `{"data": [...]}`  (all 64 agents)
- `GET /api/approvals` → `{"data": [...]}`

### `archonx-graphbrain`

Knowledge graph runner. Replaces Python cron.

```
archonx-graphbrain --mode light --root /path/to/archonx-os
archonx-graphbrain --mode full  --root /path/to/archonx-os
```

Writes `data/reports/graphbrain_latest.json`.

## Building

```bash
cd archonx-rust

# Development build
cargo build

# Release binaries
cargo build --release

# Run all tests
cargo test --workspace

# Run specific crate tests
cargo test -p archonx-core
cargo test -p archonx-billing
```

## Docker

```bash
# Build API image
docker build --target archonx-api -t archonx-api:latest archonx-rust/

# Build graphbrain image
docker build --target archonx-graphbrain -t archonx-graphbrain:latest archonx-rust/

# Run API
docker run -p 8000:8000 archonx-api:latest

# Run graphbrain
docker run -v $(pwd):/workspace archonx-graphbrain:latest --mode light
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_PORT` | `8000` | HTTP listen port for archonx-api |
| `DATABASE_URL` | (none) | PostgreSQL URL for memory persistence |
| `GRAPHBRAIN_REPORT_URL` | (none) | Webhook URL for report delivery |
| `RUST_LOG` | `info` | Log level (`trace`, `debug`, `info`, `warn`, `error`) |

## Key Architecture Decisions

- **tokio**: async runtime for I/O-bound work (HTTP, DB)
- **rayon**: CPU-bound parallelism (repo indexing, MCTS)
- **DashMap**: lock-free concurrent hash maps (agent registry, billing)
- **AtomicI64 + CAS**: overdraft-safe billing hot path
- **sqlx**: compile-time SQL verification with PostgreSQL
- **axum 0.7**: type-safe HTTP routing, zero-cost extractors
- **serde**: zero-copy JSON ser/de throughout

See `MIGRATION_NOTES.md` for detailed Python→Rust behavioral differences.
