#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="$ROOT_DIR/ops/reports"
mkdir -p "$REPORT_DIR"

POLICY_FILE="$ROOT_DIR/services/access-kernel/config/policy.json"
BASELINE_FILE="$ROOT_DIR/ops/reports/policy.hash"
CURRENT_HASH="$(sha256sum "$POLICY_FILE" | awk '{print $1}')"

if [[ ! -f "$BASELINE_FILE" ]]; then
  echo "$CURRENT_HASH" > "$BASELINE_FILE"
fi

BASE_HASH="$(cat "$BASELINE_FILE")"
STATUS="ok"
if [[ "$CURRENT_HASH" != "$BASE_HASH" ]]; then
  STATUS="drift_detected"
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
printf '{"generatedAt":"%s","status":"%s","baseline":"%s","current":"%s"}\n' "$(date -u +%FT%TZ)" "$STATUS" "$BASE_HASH" "$CURRENT_HASH" > "$REPORT_DIR/policy_drift_${TS}.json"
