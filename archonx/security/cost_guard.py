"""
Cost Guard — Budget and rate enforcement for agent operations.

Adapted from IronClaw's CostGuard. Tracks token spend + tool invocations
per agent per day with hard-stop at budget limits and alert thresholds.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.security.cost_guard")


@dataclass
class CostBudget:
    """Budget configuration for an agent or globally."""
    max_cost_per_day_cents: int = 5000
    max_actions_per_hour: int = 200
    max_tool_iterations: int = 25
    alert_threshold_percent: int = 80


@dataclass
class UsageRecord:
    """Tracks usage for a single agent in a rolling window."""
    cost_cents: float = 0.0
    actions_this_hour: int = 0
    tool_iterations: int = 0
    hour_start: float = field(default_factory=time.time)
    day_start: float = field(default_factory=time.time)
    alerted: bool = False


class CostGuard:
    """
    Budget enforcement layer.

    - Daily spend cap (cents)
    - Hourly action rate limit
    - Per-task iteration limit
    - Alert at configurable threshold
    """

    def __init__(self, budget: CostBudget | None = None) -> None:
        self.budget = budget or CostBudget()
        self._usage: dict[str, UsageRecord] = defaultdict(UsageRecord)
        logger.info(
            "CostGuard initialized: %d¢/day, %d actions/hr, %d iterations/task",
            self.budget.max_cost_per_day_cents,
            self.budget.max_actions_per_hour,
            self.budget.max_tool_iterations,
        )

    def _get_usage(self, agent_id: str) -> UsageRecord:
        record = self._usage[agent_id]
        now = time.time()
        # Reset hourly counter
        if now - record.hour_start > 3600:
            record.actions_this_hour = 0
            record.hour_start = now
        # Reset daily counter
        if now - record.day_start > 86400:
            record.cost_cents = 0.0
            record.day_start = now
            record.alerted = False
        return record

    def check_budget(self, agent_id: str) -> tuple[bool, str]:
        """
        Check if agent is within budget.
        Returns (allowed, reason).
        """
        record = self._get_usage(agent_id)

        # Daily cost cap
        if record.cost_cents >= self.budget.max_cost_per_day_cents:
            return False, f"Daily budget exhausted ({record.cost_cents:.0f}¢ / {self.budget.max_cost_per_day_cents}¢)"

        # Hourly action cap
        if record.actions_this_hour >= self.budget.max_actions_per_hour:
            return False, f"Hourly action limit reached ({record.actions_this_hour} / {self.budget.max_actions_per_hour})"

        # Alert threshold (non-blocking)
        threshold = self.budget.max_cost_per_day_cents * self.budget.alert_threshold_percent / 100
        if record.cost_cents >= threshold and not record.alerted:
            record.alerted = True
            logger.warning(
                "Agent %s reached %d%% of daily budget (%.0f¢)",
                agent_id, self.budget.alert_threshold_percent, record.cost_cents,
            )

        return True, "within_budget"

    def check_iterations(self, agent_id: str, iteration: int) -> tuple[bool, str]:
        """Check if current iteration exceeds per-task limit."""
        if iteration > self.budget.max_tool_iterations:
            return False, f"Iteration limit exceeded ({iteration} > {self.budget.max_tool_iterations})"
        return True, "within_limit"

    def record_cost(self, agent_id: str, cost_cents: float) -> None:
        """Record a cost event for an agent."""
        record = self._get_usage(agent_id)
        record.cost_cents += cost_cents

    def record_action(self, agent_id: str) -> None:
        """Record an action (tool call, API call, etc.)."""
        record = self._get_usage(agent_id)
        record.actions_this_hour += 1

    def get_usage(self, agent_id: str) -> dict[str, Any]:
        """Return current usage stats for an agent."""
        record = self._get_usage(agent_id)
        return {
            "agent_id": agent_id,
            "cost_cents": record.cost_cents,
            "budget_cents": self.budget.max_cost_per_day_cents,
            "actions_this_hour": record.actions_this_hour,
            "max_actions_per_hour": self.budget.max_actions_per_hour,
            "budget_remaining_pct": max(
                0.0,
                100.0 * (1 - record.cost_cents / max(1, self.budget.max_cost_per_day_cents)),
            ),
        }

    def reset(self, agent_id: str) -> None:
        """Reset usage for an agent."""
        if agent_id in self._usage:
            del self._usage[agent_id]
