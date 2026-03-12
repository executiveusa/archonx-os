"""
Canonical worker registry for ArchonX controller-worker orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WorkerKind(str, Enum):
    """Canonical worker classes in the ArchonX ecosystem."""

    EXECUTION = "execution"
    MULTI_AGENT = "multi_agent"
    CLOUD_CODING = "cloud_coding"
    MACHINE_CONTROL = "machine_control"
    SPECIALIZED = "specialized"


@dataclass(frozen=True)
class WorkerCapability:
    """Describes what a worker can do and what it depends on."""

    worker_id: str
    display_name: str
    kind: WorkerKind
    intents: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    requires_approval_for: list[str] = field(default_factory=list)
    can_plan: bool = False

    def supports_intent(self, intent: str) -> bool:
        return intent in self.intents


class WorkerRegistry:
    """In-memory registry of canonical workers and their capabilities."""

    def __init__(self) -> None:
        self._workers: dict[str, WorkerCapability] = {}

    def register(self, capability: WorkerCapability) -> None:
        self._workers[capability.worker_id] = capability

    def get(self, worker_id: str) -> WorkerCapability | None:
        return self._workers.get(worker_id)

    def list_all(self) -> list[WorkerCapability]:
        return [self._workers[key] for key in sorted(self._workers.keys())]

    def find_by_intent(self, intent: str) -> list[WorkerCapability]:
        return [
            worker for worker in self.list_all() if worker.supports_intent(intent)
        ]

    def validate_controller_boundary(self) -> list[str]:
        """Return violations where workers are incorrectly marked as planners."""
        violations: list[str] = []
        for worker in self._workers.values():
            if worker.can_plan:
                violations.append(
                    f"{worker.worker_id} violates the controller-worker boundary"
                )
        return violations


def build_default_worker_registry() -> WorkerRegistry:
    """Build the canonical worker registry approved for ArchonX."""
    registry = WorkerRegistry()
    registry.register(
        WorkerCapability(
            worker_id="darya_openhands",
            display_name="Darya/OpenHands",
            kind=WorkerKind.EXECUTION,
            intents=["code_change", "repo_analysis", "task_execution"],
            tools=["DesktopCommanderMCP", "mcp2cli", "git"],
            dependencies=["DesktopCommanderMCP", "mcp2cli"],
            requires_approval_for=["destructive_file_ops", "shell_execution"],
        )
    )
    registry.register(
        WorkerCapability(
            worker_id="agency_agents",
            display_name="agency-agents",
            kind=WorkerKind.MULTI_AGENT,
            intents=["multi_agent", "parallel_execution", "task_execution"],
            tools=["mcp2cli", "DesktopCommanderMCP"],
            dependencies=["mcp2cli", "DesktopCommanderMCP"],
        )
    )
    registry.register(
        WorkerCapability(
            worker_id="agent_zero",
            display_name="Agent Zero",
            kind=WorkerKind.SPECIALIZED,
            intents=["specialized_execution", "task_execution"],
            tools=["mcp2cli", "DesktopCommanderMCP"],
            dependencies=["mcp2cli"],
        )
    )
    registry.register(
        WorkerCapability(
            worker_id="goose",
            display_name="Goose",
            kind=WorkerKind.CLOUD_CODING,
            intents=["cloud_coding", "repo_analysis"],
            tools=["mcp2cli", "repo_inventory", "extension_registry"],
            dependencies=["mcp2cli", "repo_inventory", "extension_registry"],
        )
    )
    registry.register(
        WorkerCapability(
            worker_id="ralphy",
            display_name="ralphy",
            kind=WorkerKind.SPECIALIZED,
            intents=["specialized_execution", "automation"],
            tools=["mcp2cli", "DesktopCommanderMCP"],
            dependencies=["mcp2cli"],
        )
    )
    return registry
