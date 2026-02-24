"""Generate a cofounder activation snapshot from local control-plane artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_yaml_like(path: Path) -> dict[str, Any]:
    # Lightweight loader: file is simple and we only need a few sections.
    # Keeps dependencies minimal.
    data: dict[str, Any] = {"raw": path.read_text(encoding="utf-8")}
    return data


def generate_snapshot(root: Path, output_path: Path | None = None) -> Path:
    """Build and write the cofounder snapshot report."""
    backlog_path = root / "ops" / "cofounder" / "EXECUTION_BACKLOG.yaml"
    out_dir = root / "ops" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not backlog_path.exists():
        raise SystemExit(f"Missing backlog file: {backlog_path}")

    raw = backlog_path.read_text(encoding="utf-8")

    def _count(tag: str) -> int:
        return raw.count(f"tier: \"{tag}\"")

    snapshot = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "currentState": "Control-plane hardening in progress",
        "realPriority": "Execute tier1 backlog to stable shipping pipeline",
        "everythingElse": "Deferred items in parking_lot and tier2+",
        "metrics": {
            "tier1Count": _count("tier1"),
            "tier2Count": _count("tier2"),
            "tier3Count": _count("tier3"),
            "tier4Count": _count("tier4"),
            "parkingLotCount": raw.count("id: PL-"),
        },
        "directive": [
            "Complete active tier1 items before starting new scope",
            "Run loop tests and build validation",
            "Update decisions and session state after each milestone",
        ],
    }

    report_path = output_path or (out_dir / "cofounder_snapshot_latest.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate cofounder snapshot report")
    parser.add_argument("--root", help="Repository root path")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parents[1]
    output = Path(args.output) if args.output else None
    report_path = generate_snapshot(root=root, output_path=output)
    print(json.dumps({"ok": True, "report": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
