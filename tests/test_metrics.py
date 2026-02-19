"""
Tests — Metrics & Leaderboard
"""

from archonx.core.metrics import Leaderboard, MetricSnapshot


def test_composite_score_weights() -> None:
    snap = MetricSnapshot(
        crew="white",
        tasks_completed=10,  # × 0.30 = 3.0
        quality_score=1.0,   # × 0.25 = 0.25
        speed_score=1.0,     # × 0.20 = 0.20
        client_satisfaction=1.0,  # × 0.15 = 0.15
        innovation_points=1.0,   # × 0.10 = 0.10
    )
    # 3.0 + 0.25 + 0.20 + 0.15 + 0.10 = 3.70
    assert snap.composite_score == 3.70


def test_leaderboard_compare() -> None:
    lb = Leaderboard()
    lb.record(MetricSnapshot(crew="white", tasks_completed=5))
    lb.record(MetricSnapshot(crew="black", tasks_completed=3))
    result = lb.compare()
    assert result["leader"] == "white"
    assert result["white_score"] > result["black_score"]


def test_leaderboard_empty() -> None:
    lb = Leaderboard()
    result = lb.compare()
    assert result["white_score"] == 0.0
    assert result["black_score"] == 0.0


def test_leaderboard_to_dict() -> None:
    lb = Leaderboard()
    lb.record(MetricSnapshot(crew="white", tasks_completed=1))
    data = lb.to_dict()
    assert "white" in data
    assert len(data["white"]) == 1
