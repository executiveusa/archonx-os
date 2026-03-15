"""
Metrics Engine
==============
Competitive scoring between White and Black crews.

Weights (from spec):
    tasks_completed   30 %
    quality_scores    25 %
    speed_metrics     20 %
    client_satisfaction 15 %
    innovation_points 10 %
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricSnapshot:
    """Point-in-time metric reading for one crew."""

    crew: str
    tasks_completed: int = 0
    quality_score: float = 0.0       # 0.0 – 1.0
    speed_score: float = 0.0         # 0.0 – 1.0
    client_satisfaction: float = 0.0  # 0.0 – 1.0 (NPS normalised)
    innovation_points: float = 0.0   # 0.0 – 1.0
    timestamp: float = field(default_factory=time.time)

    @property
    def composite_score(self) -> float:
        """Weighted composite score."""
        return round(
            self.tasks_completed * 0.30
            + self.quality_score * 0.25
            + self.speed_score * 0.20
            + self.client_satisfaction * 0.15
            + self.innovation_points * 0.10,
            4,
        )


class Leaderboard:
    """Tracks and compares crew metrics over time."""

    def __init__(self) -> None:
        self._history: dict[str, list[MetricSnapshot]] = {"white": [], "black": []}

    def record(self, snapshot: MetricSnapshot) -> None:
        self._history.setdefault(snapshot.crew, []).append(snapshot)

    def latest(self, crew: str) -> MetricSnapshot | None:
        history = self._history.get(crew, [])
        return history[-1] if history else None

    def compare(self) -> dict[str, Any]:
        """Return current competitive standing."""
        w = self.latest("white")
        b = self.latest("black")
        white_score = w.composite_score if w else 0.0
        black_score = b.composite_score if b else 0.0
        return {
            "white_score": white_score,
            "black_score": black_score,
            "leader": "white" if white_score >= black_score else "black",
            "margin": abs(white_score - black_score),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            crew: [
                {
                    "composite": s.composite_score,
                    "tasks": s.tasks_completed,
                    "quality": s.quality_score,
                    "speed": s.speed_score,
                    "satisfaction": s.client_satisfaction,
                    "innovation": s.innovation_points,
                    "ts": s.timestamp,
                }
                for s in snapshots
            ]
            for crew, snapshots in self._history.items()
        }
