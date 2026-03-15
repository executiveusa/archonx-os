#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY="$ROOT_DIR/security/registry/agents.json"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <agent_id> [agent_type] [repo]" >&2
  exit 1
fi

AGENT_ID="$1"
AGENT_TYPE="${2:-coding}"
REPO="${3:-unknown}"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

python3 - "$REGISTRY" "$AGENT_ID" "$AGENT_TYPE" "$REPO" "$TS" <<'PY'
import json, sys
registry_path, agent_id, agent_type, repo, ts = sys.argv[1:6]
with open(registry_path) as f:
    data = json.load(f)
required = data.get("required_skills_for_coding_agents", [])
agents = data.setdefault("agents", [])
for a in agents:
    if a.get("agent_id") == agent_id:
        a.update({
            "agent_type": agent_type,
            "repo": repo,
            "required_skills_attached": True,
            "skills": sorted(set(a.get("skills", []) + required)),
            "last_synced_at": ts,
        })
        break
else:
    agents.append({
        "agent_id": agent_id,
        "agent_type": agent_type,
        "repo": repo,
        "required_skills_attached": True,
        "skills": required,
        "compliance_state": "compliant",
        "last_ack_at": None,
        "ack_hash": None,
        "last_synced_at": ts,
    })
with open(registry_path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print(f"enrolled {agent_id}")
PY
