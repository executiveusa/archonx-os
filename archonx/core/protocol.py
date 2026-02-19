"""
Bobby Fischer Protocol
======================
Every decision in ArchonX passes through this protocol:
    1. Calculate N moves ahead (min 5, prefer 10)
    2. Data-driven only — never guess
    3. Probabilistic scoring (0.0 – 1.0)
    4. Confidence threshold (default 0.7)
    5. Pattern recognition from historical library
    6. Execute with rollback plan
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.core.protocol")


@dataclass
class Decision:
    """Result of running the Bobby Fischer protocol on a task."""

    approved: bool
    confidence: float
    depth: int
    reason: str
    rollback_plan: str | None = None
    patterns_matched: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class PatternLibrary:
    """
    Historical pattern repository.
    In production this would be backed by a vector DB or Redis.
    """

    def __init__(self) -> None:
        self._patterns: list[dict[str, Any]] = []

    def record(self, pattern: dict[str, Any]) -> None:
        self._patterns.append(pattern)

    def match(self, task: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
        """Naive keyword-based matcher — swap for embedding search in prod."""
        task_type = task.get("type", "")
        matches = [p for p in self._patterns if p.get("type") == task_type]
        return matches[:top_k]


class BobbyFischerProtocol:
    """
    Core decision engine for the ArchonX kernel.

    Usage::

        protocol = BobbyFischerProtocol()
        decision = protocol.evaluate(task)
        if decision.approved:
            execute(task)
    """

    def __init__(
        self,
        min_depth: int = 5,
        preferred_depth: int = 10,
        confidence_threshold: float = 0.7,
    ) -> None:
        self.min_depth = min_depth
        self.preferred_depth = preferred_depth
        self.confidence_threshold = confidence_threshold
        self.pattern_library = PatternLibrary()
        self._decision_log: list[Decision] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, task: dict[str, Any]) -> Decision:
        """Run the full Fischer protocol on *task*."""
        logger.info("Fischer protocol — evaluating task: %s", task.get("type", "unknown"))

        # Step 1 — calculate moves ahead
        depth = self._determine_depth(task)
        future_states = self._calculate_moves_ahead(task, depth)

        # Step 2 — data sufficiency check
        if not self._has_sufficient_data(task):
            decision = Decision(
                approved=False,
                confidence=0.0,
                depth=depth,
                reason="REQUEST_MORE_DATA — insufficient information to proceed.",
            )
            self._log(decision)
            return decision

        # Step 3 — probabilistic scoring
        scores = self._score_options(task, future_states)

        # Step 4 — confidence check
        best_score = max(scores.values()) if scores else 0.0
        if best_score < self.confidence_threshold:
            decision = Decision(
                approved=False,
                confidence=best_score,
                depth=depth,
                reason=f"CONFIDENCE_TOO_LOW ({best_score:.2f} < {self.confidence_threshold})",
                scores=scores,
            )
            self._log(decision)
            return decision

        # Step 5 — pattern matching
        patterns = self.pattern_library.match(task)
        pattern_names = [p.get("name", "unnamed") for p in patterns]

        # Step 6 — build rollback plan
        rollback = self._build_rollback_plan(task)

        decision = Decision(
            approved=True,
            confidence=best_score,
            depth=depth,
            reason="Approved — all checks passed.",
            rollback_plan=rollback,
            patterns_matched=pattern_names,
            scores=scores,
        )
        self._log(decision)
        return decision

    @property
    def decision_history(self) -> list[Decision]:
        return list(self._decision_log)

    # ------------------------------------------------------------------
    # Internal steps
    # ------------------------------------------------------------------

    def _determine_depth(self, task: dict[str, Any]) -> int:
        """Pick analysis depth based on task complexity."""
        complexity = task.get("complexity", "medium")
        if complexity == "high":
            return self.preferred_depth
        if complexity == "low":
            return self.min_depth
        return (self.min_depth + self.preferred_depth) // 2

    def _calculate_moves_ahead(
        self, task: dict[str, Any], depth: int
    ) -> list[dict[str, Any]]:
        """
        Simulate future states.
        In production, this would use Monte Carlo tree search
        or a planning LLM call.
        """
        states: list[dict[str, Any]] = []
        for step in range(1, depth + 1):
            states.append({
                "step": step,
                "task_type": task.get("type"),
                "projected_outcome": "success",  # placeholder
                "risk_factor": max(0.0, 1.0 - step * 0.08),
            })
        return states

    def _has_sufficient_data(self, task: dict[str, Any]) -> bool:
        """Check whether we have enough data to make a decision."""
        required_fields = {"type"}
        return required_fields.issubset(task.keys())

    def _score_options(
        self, task: dict[str, Any], future_states: list[dict[str, Any]]
    ) -> dict[str, float]:
        """
        Score available options probabilistically.
        Returns mapping of option_label -> score (0.0-1.0).
        """
        options = task.get("options", [task.get("type", "default")])
        scores: dict[str, float] = {}
        for i, opt in enumerate(options):
            label = opt if isinstance(opt, str) else str(opt)
            # Placeholder scoring — replace with real model in prod
            base = 0.75
            variance = (i % 3) * 0.05
            risk_avg = (
                sum(s["risk_factor"] for s in future_states) / len(future_states)
                if future_states
                else 0.5
            )
            scores[label] = round(min(1.0, base + variance - (1 - risk_avg) * 0.1), 3)
        return scores

    def _build_rollback_plan(self, task: dict[str, Any]) -> str:
        """Generate a rollback strategy string."""
        task_type = task.get("type", "generic")
        return (
            f"Rollback plan for '{task_type}': "
            f"1) Snapshot current state, "
            f"2) Execute with monitoring, "
            f"3) On failure → revert to snapshot, "
            f"4) Notify Pauli & log incident."
        )

    def _log(self, decision: Decision) -> None:
        self._decision_log.append(decision)
        level = logging.INFO if decision.approved else logging.WARNING
        logger.log(level, "Decision: approved=%s confidence=%.2f reason=%s",
                   decision.approved, decision.confidence, decision.reason)
