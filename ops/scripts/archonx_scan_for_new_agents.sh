#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENROLL_SCRIPT="$ROOT_DIR/ops/scripts/archonx_enroll_agent.sh"
MANIFEST="$ROOT_DIR/ecosystem/manifest.json"

python3 - "$MANIFEST" <<'PY' | while IFS=$'\t' read -r agent_id repo; do
import json, sys
manifest_path = sys.argv[1]
with open(manifest_path) as f:
    data = json.load(f)
for repo in data.get("repos", []):
    slug = repo.get("slug", "")
    if any(x in slug for x in ["agent", "swarm", "openclaw"]):
        aid = slug.split("/")[-1].replace("-", "_")
        print(f"{aid}\t{slug}")
PY
  "$ENROLL_SCRIPT" "$agent_id" "coding" "$repo"
done
