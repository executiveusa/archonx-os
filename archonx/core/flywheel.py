"""
Flywheel Engine
===============
The self-reinforcing improvement loop at the heart of ArchonX.

Every task execution can surface improvements. Those improvements become
new tasks, which themselves can surface more improvements. This is the
compounding mechanism — the system gets better at getting better.

Cycle:
    execute_task → skill returns improvements_found → flywheel ingests →
    prioritizes → spawns micro-tasks → those execute → more improvements → ...
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.core.flywheel")


class ImprovementPriority(str, Enum):
    CRITICAL = "critical"   # Blocks revenue / security
    HIGH = "high"           # Enables new capability
    MEDIUM = "medium"       # Performance / UX
    LOW = "low"             # Nice-to-have


@dataclass
class Improvement:
    """A single discoverable improvement from task execution."""
    id: str
    source_skill: str
    source_task_id: str
    description: str
    priority: ImprovementPriority = ImprovementPriority.MEDIUM
    category: str = "general"
    suggested_action: str = ""
    estimated_effort: str = "small"  # small | medium | large
    created_at: float = field(default_factory=time.time)
    status: str = "pending"  # pending | in_progress | completed | skipped
    metadata: dict[str, Any] = field(default_factory=dict)


class FlywheelEngine:
    """
    Manages the improvement backlog and drives the self-build loop.

    The flywheel:
    1. Collects improvements from skill/task execution
    2. Prioritizes by impact × effort
    3. Generates micro-tasks that re-enter the kernel
    4. Tracks compound growth metrics
    """

    def __init__(self) -> None:
        self.backlog: list[Improvement] = []
        self.completed: list[Improvement] = []
        self._counter = 0
        self._cycle_count = 0

    # ------------------------------------------------------------------
    # Ingest improvements
    # ------------------------------------------------------------------

    def ingest(self, improvements: list[dict[str, Any]], source_skill: str, task_id: str) -> int:
        """Add discovered improvements to the backlog. Returns count ingested."""
        added = 0
        for raw in improvements:
            self._counter += 1
            imp = Improvement(
                id=f"imp-{self._counter:05d}",
                source_skill=source_skill,
                source_task_id=task_id,
                description=raw.get("description", ""),
                priority=ImprovementPriority(raw.get("priority", "medium")),
                category=raw.get("category", "general"),
                suggested_action=raw.get("suggested_action", ""),
                estimated_effort=raw.get("effort", "small"),
                metadata=raw.get("metadata", {}),
            )
            self.backlog.append(imp)
            added += 1
            logger.info("Flywheel ingested: %s [%s] — %s", imp.id, imp.priority.value, imp.description)
        return added

    # ------------------------------------------------------------------
    # Prioritize and generate micro-tasks
    # ------------------------------------------------------------------

    PRIORITY_WEIGHTS = {
        ImprovementPriority.CRITICAL: 4,
        ImprovementPriority.HIGH: 3,
        ImprovementPriority.MEDIUM: 2,
        ImprovementPriority.LOW: 1,
    }
    EFFORT_WEIGHTS = {"small": 3, "medium": 2, "large": 1}

    def prioritized_backlog(self) -> list[Improvement]:
        """Return backlog sorted by impact score (priority × inverse effort)."""
        pending = [i for i in self.backlog if i.status == "pending"]
        return sorted(
            pending,
            key=lambda i: self.PRIORITY_WEIGHTS.get(i.priority, 1) * self.EFFORT_WEIGHTS.get(i.estimated_effort, 1),
            reverse=True,
        )

    def generate_micro_tasks(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        Pop the top-N improvements and convert them to kernel-executable tasks.
        These re-enter execute_task() to close the loop.
        """
        top = self.prioritized_backlog()[:limit]
        tasks = []
        for imp in top:
            imp.status = "in_progress"
            tasks.append({
                "type": imp.category,
                "description": imp.description,
                "crew": "both",  # collaborative reasoning for improvements
                "flywheel_improvement_id": imp.id,
                "suggested_action": imp.suggested_action,
                "metadata": {"source": imp.source_skill, "priority": imp.priority.value},
            })
        self._cycle_count += 1
        logger.info("Flywheel cycle %d: generated %d micro-tasks from %d pending", self._cycle_count, len(tasks), len(self.backlog))
        return tasks

    def mark_completed(self, improvement_id: str) -> None:
        """Mark an improvement as done."""
        for imp in self.backlog:
            if imp.id == improvement_id:
                imp.status = "completed"
                self.completed.append(imp)
                self.backlog.remove(imp)
                logger.info("Flywheel: completed %s", improvement_id)
                return

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "total_ingested": self._counter,
            "backlog_pending": len([i for i in self.backlog if i.status == "pending"]),
            "backlog_in_progress": len([i for i in self.backlog if i.status == "in_progress"]),
            "completed": len(self.completed),
            "cycles_run": self._cycle_count,
            "compound_ratio": len(self.completed) / max(self._counter, 1),
        }
