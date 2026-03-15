import glob
import json
from pathlib import Path


def test_graphbrain_contract_files_exist():
    required = [
        "ecosystem/contracts/graphbrain-report.schema.json",
        "ecosystem/contracts/graphbrain-bead.schema.json",
        "ecosystem/contracts/github-webhook-contract.json",
    ]
    for item in required:
        assert Path(item).exists(), item


def test_latest_graphbrain_report_shape():
    reports = sorted(glob.glob("ops/reports/graphbrain/GRAPH_SNAPSHOT_*.json"))
    if not reports:
        return
    payload = json.loads(Path(reports[-1]).read_text())
    for key in ["report_id", "generated_at", "repos_indexed", "graph"]:
        assert key in payload
