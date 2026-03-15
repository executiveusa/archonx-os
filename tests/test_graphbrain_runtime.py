from pathlib import Path

from services.graphbrain import GraphBrainRuntime, Reporter


def test_graphbrain_full_writes_required_files() -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = GraphBrainRuntime(root)
    payload = runtime.run(mode="light")
    reporter = Reporter(root)
    reporter.write_all(payload)

    required = [
        root / "data/graphbrain/global_graph.json",
        root / "data/graphbrain/similarity.json",
        root / "data/graphbrain/consolidation_candidates.json",
        root / "data/graphbrain/risk_findings.json",
        root / "data/graphbrain/work_orders.json",
        root / "data/dashboard/registry.json",
        root / "data/dashboard/status.json",
        root / "data/audit/graphbrain.log",
    ]
    for file_path in required:
        assert file_path.exists()
