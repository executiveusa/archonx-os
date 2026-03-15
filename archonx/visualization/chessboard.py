"""
Chessboard View
===============
8×8 grid showing all 64 agents in real-time:
    - Agent position glows when active
    - Lines show collaboration paths
    - Health bars per agent
    - Task counters
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from archonx.core.agents import Agent, AgentRegistry, AgentStatus, Crew

logger = logging.getLogger("archonx.visualization.chessboard")

# Board coordinates: columns A-H, rows 1-8
COLUMNS = "ABCDEFGH"
ROWS = range(1, 9)


@dataclass
class CellState:
    """Visual state of a single board cell."""

    position: str  # e.g. "D1"
    agent_id: str | None = None
    agent_name: str | None = None
    crew: str | None = None
    role: str | None = None
    status: str = "empty"
    health: float = 1.0
    tasks_completed: int = 0
    score: float = 0.0
    glowing: bool = False  # True when agent is actively processing


@dataclass
class CollaborationLine:
    """Visual link between two collaborating agents."""

    from_pos: str
    to_pos: str
    strength: float = 1.0  # 0.0-1.0 line opacity


class ChessboardView:
    """
    Generates the 8×8 chessboard visualization state.

    The frontend (web app) reads this state via WebSocket and
    renders the animated game-style display.
    """

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry
        self._collaboration_lines: list[CollaborationLine] = []

    def get_board_state(self) -> list[list[CellState]]:
        """
        Return an 8×8 grid of CellState objects.
        Row 0 = rank 8 (Black back rank), Row 7 = rank 1 (White back rank).
        """
        # Build position → agent lookup
        agents_by_pos: dict[str, Agent] = {}
        for agent in self._registry.all():
            agents_by_pos[agent.position] = agent

        board: list[list[CellState]] = []
        for row_idx, rank in enumerate(reversed(list(ROWS))):
            row: list[CellState] = []
            for col in COLUMNS:
                pos = f"{col}{rank}"
                agent = agents_by_pos.get(pos)
                if agent:
                    cell = CellState(
                        position=pos,
                        agent_id=agent.agent_id,
                        agent_name=agent.name,
                        crew=agent.crew.value,
                        role=agent.role.value,
                        status=agent.status.value,
                        health=agent.health,
                        tasks_completed=agent.tasks_completed,
                        score=agent.score,
                        glowing=agent.status == AgentStatus.ACTIVE,
                    )
                else:
                    cell = CellState(position=pos)
                row.append(cell)
            board.append(row)
        return board

    def add_collaboration(self, from_pos: str, to_pos: str, strength: float = 1.0) -> None:
        self._collaboration_lines.append(
            CollaborationLine(from_pos=from_pos, to_pos=to_pos, strength=strength)
        )

    def clear_collaborations(self) -> None:
        self._collaboration_lines.clear()

    @property
    def collaboration_lines(self) -> list[CollaborationLine]:
        return list(self._collaboration_lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize full board state for the frontend."""
        board = self.get_board_state()
        return {
            "board": [
                [
                    {
                        "position": cell.position,
                        "agent_id": cell.agent_id,
                        "agent_name": cell.agent_name,
                        "crew": cell.crew,
                        "role": cell.role,
                        "status": cell.status,
                        "health": cell.health,
                        "tasks": cell.tasks_completed,
                        "score": cell.score,
                        "glowing": cell.glowing,
                    }
                    for cell in row
                ]
                for row in board
            ],
            "collaborations": [
                {
                    "from": line.from_pos,
                    "to": line.to_pos,
                    "strength": line.strength,
                }
                for line in self._collaboration_lines
            ],
        }
