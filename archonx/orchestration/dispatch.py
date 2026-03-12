"""
Dispatch coordination between repo-aware routing and worker execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from archonx.orchestration.contracts import TaskEnvelope
from archonx.orchestration.workers import WorkerRegistry, build_default_worker_registry
from archonx.repos.models import DispatchPlan, DispatchPlanIntegration, DispatchPlanWorker

if TYPE_CHECKING:
    from archonx.repos.router import Router


@dataclass
class DispatchDecision:
    """Executable dispatch decision derived from a routing plan."""

    plan: DispatchPlan
    primary_worker: DispatchPlanWorker
    envelope: TaskEnvelope
    required_integrations: list[DispatchPlanIntegration]

    def to_dict(self) -> dict:
        return {
            "plan": self.plan.to_dict(),
            "primary_worker": self.primary_worker.to_dict(),
            "envelope": self.envelope.to_dict(),
            "required_integrations": [
                integration.to_dict() for integration in self.required_integrations
            ],
        }


class DispatchCoordinator:
    """Builds Archon-owned dispatch decisions from routing plans."""

    def __init__(
        self,
        router: "Router",
        worker_registry: WorkerRegistry | None = None,
    ) -> None:
        self.router = router
        self.worker_registry = worker_registry or build_default_worker_registry()

    def create_dispatch_decision(
        self,
        repo_ids: list[int],
        task_name: str,
        task_intent: str | None = None,
        objective: str | None = None,
    ) -> DispatchDecision:
        """Create a dispatch decision with worker selection and task envelope."""
        plan = self.router.route(repo_ids, task_name, task_intent=task_intent)
        self._validate_required_integrations(plan.required_integrations)

        if not plan.recommended_workers:
            raise ValueError("No recommended workers available for dispatch plan")

        primary_worker = plan.recommended_workers[0]
        primary_repo = plan.repos_metadata[0]["url"]
        envelope = TaskEnvelope(
            objective=objective or f"Execute {task_name} via {primary_worker.id}",
            intent=plan.task_intent,
            repo=primary_repo,
            branch="main",
            constraints=[
                "archonx-os remains the only planner",
                "worker must execute within approved tool scope",
            ],
            allowed_tools=primary_worker.tools,
            required_approvals=self._collect_required_approvals(primary_worker),
            budget={"mode": "bounded", "task_name": task_name},
            result_schema={
                "status": "string",
                "worker_id": "string",
                "artifacts": "array",
            },
            trace_id=f"dispatch:{task_name}:{primary_worker.id}",
        )
        errors = envelope.validate()
        if errors:
            raise ValueError(f"Invalid task envelope: {errors}")

        return DispatchDecision(
            plan=plan,
            primary_worker=primary_worker,
            envelope=envelope,
            required_integrations=plan.required_integrations,
        )

    def _validate_required_integrations(
        self, integrations: list[DispatchPlanIntegration]
    ) -> None:
        required_ids = {integration.id for integration in integrations if integration.required}
        missing = {
            integration_id
            for integration_id in required_ids
            if integration_id not in {"DesktopCommanderMCP", "mcp2cli", "Notion", "Cloudflare Tunnel"}
        }
        if missing:
            raise ValueError(f"Unknown required integrations: {sorted(missing)}")
        if "mcp2cli" not in required_ids:
            raise ValueError("mcp2cli must be present in required integrations")

    def _collect_required_approvals(self, worker: DispatchPlanWorker) -> list[str]:
        capability = self.worker_registry.get(worker.id)
        if not capability:
            return []
        return list(capability.requires_approval_for)
