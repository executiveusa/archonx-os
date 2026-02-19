"""
Metrics Dashboard
=================
Real-time competitive dashboard:
    - White vs Black crew score
    - Tasks completed today
    - System health overview
    - Client satisfaction NPS
    - Agent leaderboard
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.core.agents import AgentRegistry, Crew
from archonx.core.metrics import Leaderboard

logger = logging.getLogger("archonx.visualization.dashboard")


class MetricsDashboard:
    """
    Generates the metrics dashboard state for the frontend.
    Displayed on phone or desktop web app.
    """

    def __init__(self, registry: AgentRegistry, leaderboard: Leaderboard) -> None:
        self._registry = registry
        self._leaderboard = leaderboard

    def get_crew_scores(self) -> dict[str, Any]:
        """Current White vs Black competitive standing."""
        return self._leaderboard.compare()

    def get_tasks_today(self) -> dict[str, int]:
        """Tasks completed today per crew."""
        white = sum(
            a.tasks_completed for a in self._registry.get_by_crew(Crew.WHITE)
        )
        black = sum(
            a.tasks_completed for a in self._registry.get_by_crew(Crew.BLACK)
        )
        return {"white": white, "black": black, "total": white + black}

    def get_system_health(self) -> dict[str, Any]:
        """Aggregate health across all 64 agents."""
        all_agents = self._registry.all()
        if not all_agents:
            return {"average_health": 0.0, "agents_online": 0, "agents_total": 0}

        avg_health = sum(a.health for a in all_agents) / len(all_agents)
        online = sum(1 for a in all_agents if a.status.value != "offline")
        return {
            "average_health": round(avg_health, 3),
            "agents_online": online,
            "agents_total": len(all_agents),
        }

    def get_agent_leaderboard(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Top agents by score."""
        agents = sorted(self._registry.all(), key=lambda a: a.score, reverse=True)
        return [
            {
                "rank": i + 1,
                "agent_id": a.agent_id,
                "name": a.name,
                "crew": a.crew.value,
                "role": a.role.value,
                "score": a.score,
                "tasks": a.tasks_completed,
            }
            for i, a in enumerate(agents[:top_n])
        ]

    def to_dict(self) -> dict[str, Any]:
        """Full dashboard state for the frontend."""
        return {
            "crew_scores": self.get_crew_scores(),
            "tasks_today": self.get_tasks_today(),
            "system_health": self.get_system_health(),
            "leaderboard": self.get_agent_leaderboard(),
        }
