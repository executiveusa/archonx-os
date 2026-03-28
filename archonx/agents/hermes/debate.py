"""
BEAD-HERMES-001 — Hermes Agent debate & consensus data models.

DebateRound, ConsensusResult, ExecutionPlan, ExecutionResult, CouncilTask.
All pure dataclasses — no LLM I/O here.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CouncilMode(str, Enum):
    WHITE_ONLY = "WHITE_ONLY"
    BLACK_ONLY = "BLACK_ONLY"
    FULL_DEBATE = "FULL_DEBATE"


class AssignedCrew(str, Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    BOTH = "BOTH"


@dataclass
class CouncilTask:
    """Input contract for the Hermes Council."""
    task_id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    objective: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    council_mode: CouncilMode = CouncilMode.FULL_DEBATE
    max_rounds: int = 3
    timeout_seconds: int = 120
    requires_unanimous: bool = False


@dataclass
class DebateRound:
    round_number: int
    white_position: str
    black_position: str
    hermes_synthesis: str
    convergence_score: float   # 0-1
    timestamp: datetime = field(default_factory=_now)


@dataclass
class ConsensusResult:
    reached: bool
    rounds_taken: int
    winning_position: str
    confidence: float          # 0-1
    white_vote: float          # 0-1
    black_vote: float          # 0-1
    hermes_override: bool = False


@dataclass
class ExecutionPlan:
    plan_id: str = field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    consensus_result: ConsensusResult | None = None
    actions: list[dict[str, Any]] = field(default_factory=list)
    assigned_crew: AssignedCrew = AssignedCrew.WHITE
    cost_estimate: float = 0.0     # USD
    rollback_plan: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionResult:
    plan_id: str
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    completed_at: datetime = field(default_factory=_now)
    cost_actual: float = 0.0
