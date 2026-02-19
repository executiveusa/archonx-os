#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="$ROOT_DIR/ops/reports"
mkdir -p "$REPORT_DIR"

WORK_ITEM_ID="WI-SELFTEST-$(date -u +%Y%m%d)"
LOGIN_JSON="$(curl -fsS -X POST http://localhost:8090/v1/login/mock -H 'Content-Type: application/json' -d '{"principal":"selftest","principal_type":"human","duration_minutes":60}')"

SECRET_JSON="$(curl -fsS -X POST http://localhost:8090/v1/secrets/upload -H 'Content-Type: application/json' -d '{"principal":"selftest","work_item_id":"'"$WORK_ITEM_ID"'","name":"selftest-secret","payload":{"API_KEY":"demo-selftest-key"}}')"

GRANT_REQUEST_JSON="$(curl -fsS -X POST http://localhost:8090/v1/grants/request -H 'Content-Type: application/json' -d '{"principal":"selftest","principal_type":"human","work_item_id":"'"$WORK_ITEM_ID"'","resource":"github","action":"write","duration_minutes":15}')"
GRANT_ID="$(printf '%s' "$GRANT_REQUEST_JSON" | python -c "import sys,json; print(json.load(sys.stdin)['grant_id'])")"

GRANT_APPROVE_JSON="$(curl -fsS -X POST http://localhost:8090/v1/grants/approve -H 'Content-Type: application/json' -d '{"grant_id":"'"$GRANT_ID"'","approver":"selftest-admin","work_item_id":"'"$WORK_ITEM_ID"'"}')"

AUDIT_JSON="$(curl -fsS 'http://localhost:8090/v1/audit/export?format=jsonl')"
EVIDENCE_JSON="$(curl -fsS 'http://localhost:8090/v1/evidence/export')"
VOICE_JSON="$(curl -fsS -X POST http://localhost:8091/v1/voice/dev/simulate -H 'Content-Type: application/json' -d '{"caller":"+15550000001","passphrase":"archonx-passphrase","pin":"1234","action":"status","work_item_id":"'"$WORK_ITEM_ID"'"}')"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$REPORT_DIR/access-kernel_selftest_${TS}.json"
printf '{"generatedAt":"%s","work_item_id":"%s","login":%s,"secretUpload":%s,"grantRequest":%s,"grantApprove":%s,"voice":%s,"evidence":%s}\n' \
  "$(date -u +%FT%TZ)" "$WORK_ITEM_ID" "$LOGIN_JSON" "$SECRET_JSON" "$GRANT_REQUEST_JSON" "$GRANT_APPROVE_JSON" "$VOICE_JSON" "$EVIDENCE_JSON" > "$OUT"

# Also write a compact audit export snapshot file
printf '%s\n' "$AUDIT_JSON" > "$REPORT_DIR/access-kernel_audit_${TS}.json"
printf '%s\n' "$OUT"
