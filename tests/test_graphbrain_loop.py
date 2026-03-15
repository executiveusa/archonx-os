from pathlib import Path

from services.graphbrain import GraphBrainRuntime, Reporter


def test_graphbrain_loop_mode_generates_phase_history() -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = GraphBrainRuntime(root)
    payload = runtime.run_loop(mode="light", max_iterations=2, max_retries=0, retry_delay=0)

    assert "loop" in payload
    loop = payload["loop"]
    assert loop["model"] == "ralphy-inspired"
    assert loop["iterations_completed"] >= 1
    assert isinstance(loop["phase_history"], list)
    assert len(loop["phase_history"]) >= 1

    first_iteration = loop["phase_history"][0]
    phase_names = [phase["name"] for phase in first_iteration["phases"]]
    assert phase_names == [
        "plan",
        "implement",
        "test",
        "evaluate",
        "patch",
        "repeat",
        "ship",
    ]

    reporter = Reporter(root)
    reporter.write_all(payload)
    assert (root / "data/reports/graphbrain_latest.json").exists()
