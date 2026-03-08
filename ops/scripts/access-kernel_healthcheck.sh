#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="$ROOT_DIR/ops/reports"
mkdir -p "$REPORT_DIR"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$REPORT_DIR/access-kernel_health_${TS}.json"

HEALTH_JSON="$(curl -fsS http://localhost:8090/v1/health)"
VOICE_JSON="$(curl -fsS http://localhost:8091/v1/health)"

printf '{"generatedAt":"%s","accessKernel":%s,"voiceGateway":%s}\n' "$(date -u +%FT%TZ)" "$HEALTH_JSON" "$VOICE_JSON" > "$OUT"
printf '%s\n' "$OUT"
