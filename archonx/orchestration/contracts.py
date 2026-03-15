"""
Canonical task envelope contracts for ArchonX worker dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskEnvelope:
    """Controller-owned task contract handed from Archon to workers."""

    objective: str
    intent: str
    repo: str
    branch: str = "main"
    constraints: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    required_approvals: list[str] = field(default_factory=list)
    budget: dict[str, Any] = field(default_factory=dict)
    result_schema: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    requested_by: str = "archonx-os"

    def validate(self) -> list[str]:
        """Validate required task-envelope invariants."""
        errors: list[str] = []
        if not self.objective.strip():
            errors.append("objective is required")
        if not self.intent.strip():
            errors.append("intent is required")
        if not self.repo.strip():
            errors.append("repo is required")
        if self.requested_by != "archonx-os":
            errors.append("requested_by must be archonx-os")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "intent": self.intent,
            "repo": self.repo,
            "branch": self.branch,
            "constraints": self.constraints,
            "allowed_tools": self.allowed_tools,
            "required_approvals": self.required_approvals,
            "budget": self.budget,
            "result_schema": self.result_schema,
            "trace_id": self.trace_id,
            "requested_by": self.requested_by,
        }
