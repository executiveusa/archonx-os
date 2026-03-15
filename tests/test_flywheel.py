"""
Tests — Flywheel Engine
"""

from archonx.core.flywheel import FlywheelEngine, Improvement, ImprovementPriority


def _make_improvements(count: int = 3) -> list[dict]:
    return [
        {
            "description": f"Fix item {i}",
            "priority": ["critical", "high", "medium", "low"][i % 4],
            "category": "general",
            "suggested_action": f"Action {i}",
            "effort": ["small", "medium", "large"][i % 3],
        }
        for i in range(count)
    ]


def test_ingest_adds_to_backlog() -> None:
    fw = FlywheelEngine()
    added = fw.ingest(_make_improvements(3), "test_skill", "task-1")
    assert added == 3
    assert len(fw.backlog) == 3


def test_ingest_increments_counter() -> None:
    fw = FlywheelEngine()
    fw.ingest(_make_improvements(2), "a", "t1")
    fw.ingest(_make_improvements(3), "b", "t2")
    assert fw._counter == 5


def test_prioritized_backlog_sorted() -> None:
    fw = FlywheelEngine()
    fw.ingest(_make_improvements(4), "x", "t1")
    ordered = fw.prioritized_backlog()
    # All should be pending
    assert all(i.status == "pending" for i in ordered)
    # First should have highest score (critical × small effort = 4 × 3 = 12)
    assert ordered[0].priority == ImprovementPriority.CRITICAL


def test_generate_micro_tasks() -> None:
    fw = FlywheelEngine()
    fw.ingest(_make_improvements(10), "skill_a", "t1")
    tasks = fw.generate_micro_tasks(limit=3)
    assert len(tasks) == 3
    assert all(t["crew"] == "both" for t in tasks)
    assert fw._cycle_count == 1
    # Those 3 should now be in_progress
    in_prog = [i for i in fw.backlog if i.status == "in_progress"]
    assert len(in_prog) == 3


def test_mark_completed() -> None:
    fw = FlywheelEngine()
    fw.ingest([{"description": "Fix bug", "priority": "high"}], "s", "t")
    imp_id = fw.backlog[0].id
    fw.mark_completed(imp_id)
    assert len(fw.completed) == 1
    assert len(fw.backlog) == 0


def test_stats() -> None:
    fw = FlywheelEngine()
    fw.ingest(_make_improvements(5), "s", "t")
    fw.generate_micro_tasks(limit=2)
    fw.mark_completed(fw.backlog[0].id)
    stats = fw.stats
    assert stats["total_ingested"] == 5
    assert stats["completed"] >= 1
    assert stats["cycles_run"] == 1
    assert 0.0 <= stats["compound_ratio"] <= 1.0


def test_empty_engine_stats() -> None:
    fw = FlywheelEngine()
    stats = fw.stats
    assert stats["total_ingested"] == 0
    assert stats["compound_ratio"] == 0.0
