from datetime import datetime, timezone
import json
from pathlib import Path


def emit_audit_event(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    with path.open("a") as f:
        f.write(json.dumps(enriched) + "\n")
