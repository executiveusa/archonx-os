"""Bead executor for Agent Lightning — runs beads through PAULIWHEEL stages."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import structlog

logger = structlog.get_logger("agents.lightning.bead_executor")

VALID_STAGES: frozenset[str] = frozenset(
    {"PLAN", "IMPLEMENT", "TEST", "EVALUATE", "PATCH", "REPEAT"}
)


@dataclass
class BeadExecutionRecord:
    """Immutable record of a single bead execution."""

    run_id: str
    bead_id: str
    phase: str
    stage: str
    started_at: str
    finished_at: str | None = None
    status: str = "pending"
    output: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for reporting."""
        return asdict(self)


class BeadExecutor:
    """
    Executes a single bead through a specified PAULIWHEEL stage.

    Maintains an in-memory record of all executions for the lifetime
    of the executor instance.
    """

    def __init__(self) -> None:
        self._records: dict[str, BeadExecutionRecord] = {}

    def execute(
        self,
        bead_id: str,
        phase: str,
        stage: str,
        task_fn: Callable[[], Any],
    ) -> BeadExecutionRecord:
        """
        Execute a task function for a given bead, phase, and stage.

        Args:
            bead_id: The bead identifier (must pass BEAD-* prefix convention).
            phase:   Phase label (e.g. 'phase-2').
            stage:   PAULIWHEEL stage name (must be in VALID_STAGES).
            task_fn: Zero-argument callable that performs the actual work.

        Returns:
            BeadExecutionRecord with the result of the execution.

        Raises:
            ValueError: If stage is not a recognised PAULIWHEEL stage.
        """
        if stage not in VALID_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Must be one of: {sorted(VALID_STAGES)}"
            )

        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        record = BeadExecutionRecord(
            run_id=run_id,
            bead_id=bead_id,
            phase=phase,
            stage=stage,
            started_at=started_at,
        )
        self._records[run_id] = record

        logger.info(
            "Bead execution started",
            bead_id=bead_id,
            phase=phase,
            stage=stage,
            run_id=run_id,
        )

        try:
            output = task_fn()
            record.status = "complete"
            record.output = output
            logger.info(
                "Bead execution complete",
                bead_id=bead_id,
                stage=stage,
                run_id=run_id,
            )
        except Exception as exc:  # noqa: BLE001
            record.status = "failed"
            record.error = str(exc)
            logger.error(
                "Bead execution failed",
                bead_id=bead_id,
                stage=stage,
                run_id=run_id,
                error=str(exc),
            )

        record.finished_at = datetime.now(timezone.utc).isoformat()
        return record

    def get_status(self, bead_id: str) -> list[BeadExecutionRecord]:
        """
        Return all execution records for a given bead_id.

        Args:
            bead_id: The bead identifier to look up.

        Returns:
            List of BeadExecutionRecord entries for that bead (may be empty).
        """
        return [r for r in self._records.values() if r.bead_id == bead_id]

    def get_report(self) -> dict[str, Any]:
        """
        Return a summary execution report for all beads processed.

        Returns:
            Dict with total, complete, failed counts and a records list.
        """
        records = list(self._records.values())
        complete = sum(1 for r in records if r.status == "complete")
        failed = sum(1 for r in records if r.status == "failed")
        return {
            "total": len(records),
            "complete": complete,
            "failed": failed,
            "pending": len(records) - complete - failed,
            "records": [r.to_dict() for r in records],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
