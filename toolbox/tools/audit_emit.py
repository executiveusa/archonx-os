#!/usr/bin/env python3
"""Minimal toolbox wrapper for audit event emission."""

import json
import os
from datetime import datetime, timezone


def main() -> int:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent_id": os.getenv("ARCHONX_AGENT_ID", "unknown-agent"),
        "repo_slug": os.getenv("ARCHONX_REPO_SLUG", "unknown-repo"),
        "work_item_id": os.getenv("ARCHONX_WORK_ITEM_ID", "missing"),
        "action": "toolbox.audit_emit",
    }
    print(json.dumps(event))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
