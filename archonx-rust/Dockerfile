# Multi-stage Dockerfile for archonx-rust workspace.
# Produces minimal final images (~15MB) for archonx-api and archonx-graphbrain.
#
# Stage 1: chef — cargo-chef for dependency caching
# Stage 2: planner — compute dependency recipe
# Stage 3: builder — compile release binaries
# Stage 4: runtime — minimal runtime image

# ---- Stage 1: cargo-chef base ----
FROM rust:1.77-slim AS chef
RUN cargo install cargo-chef --locked
WORKDIR /app

# ---- Stage 2: planner ----
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# ---- Stage 3: builder ----
FROM chef AS builder

# Install build dependencies for reqwest (TLS) and sqlx (PG)
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=planner /app/recipe.json recipe.json

# Build dependencies only (cached layer)
RUN cargo chef cook --release --recipe-path recipe.json

# Build all binaries
COPY . .
RUN cargo build --release \
    --bin archonx-api \
    --bin archonx-graphbrain

# ---- Stage 4a: archonx-api runtime ----
FROM debian:bookworm-slim AS archonx-api

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/archonx-api /usr/local/bin/archonx-api

# Non-root user for security
RUN useradd -m -u 1001 archonx
USER archonx

ENV API_PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD wget -qO- http://localhost:8000/healthz || exit 1

CMD ["archonx-api"]

# ---- Stage 4b: archonx-graphbrain runtime ----
FROM debian:bookworm-slim AS archonx-graphbrain

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/archonx-graphbrain /usr/local/bin/archonx-graphbrain

RUN useradd -m -u 1001 archonx
USER archonx

WORKDIR /workspace

CMD ["archonx-graphbrain", "--mode", "full"]
