from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


class Reporter:
    def __init__(self, root: Path):
        self.root = root
        self.graph_dir = root / "data" / "graphbrain"
        self.repo_graph_dir = self.graph_dir / "repo_graphs"
        self.audit_path = root / "data" / "audit" / "graphbrain.log"
        self.reports_dir = root / "data" / "reports"
        self.dashboard_dir = root / "data" / "dashboard"

        self.repo_graph_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict | list) -> None:
        path.write_text(json.dumps(payload, indent=2) + "\n")
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        audit_line = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "path": str(path.relative_to(self.root)),
            "sha256": digest,
        }
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(audit_line) + "\n")

    def write_all(self, payload: dict) -> None:
        self._write_json(self.graph_dir / "global_graph.json", payload["global_graph"])

        for repo_graph in payload["repo_graphs"]:
            filename = repo_graph["repo"].replace("/", "__") + ".json"
            self._write_json(self.repo_graph_dir / filename, repo_graph)

        self._write_json(self.graph_dir / "similarity.json", payload["similarity"])
        self._write_json(
            self.graph_dir / "consolidation_candidates.json", payload["consolidation_candidates"]
        )
        self._write_json(self.graph_dir / "risk_findings.json", payload["risk_findings"])
        self._write_json(self.graph_dir / "work_orders.json", payload["work_orders"])

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo_status": payload["repo_status"],
            "work_order_count": len(payload["work_orders"]),
        }
        self._write_json(self.reports_dir / "graphbrain_latest.json", report)

        self._write_json(self.dashboard_dir / "registry.json", payload["dashboard_registry"])
        self._write_json(self.dashboard_dir / "status.json", payload["dashboard_status"])
