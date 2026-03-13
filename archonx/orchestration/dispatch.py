"""
Dispatch coordination between repo-aware routing and worker execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from archonx.integrations import (
    EnvCategoryRegistry,
    IntegrationRegistry,
    build_default_env_category_registry,
    build_default_integration_registry,
)
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
    required_env_categories: list[str]
    env_profiles: list[dict]

    def to_dict(self) -> dict:
        return {
            "plan": self.plan.to_dict(),
            "primary_worker": self.primary_worker.to_dict(),
            "envelope": self.envelope.to_dict(),
            "required_integrations": [
                integration.to_dict() for integration in self.required_integrations
            ],
            "required_env_categories": self.required_env_categories,
            "env_profiles": self.env_profiles,
        }


class DispatchCoordinator:
    """Builds Archon-owned dispatch decisions from routing plans."""

    def __init__(
        self,
        router: "Router",
        worker_registry: WorkerRegistry | None = None,
        integration_registry: IntegrationRegistry | None = None,
        env_category_registry: EnvCategoryRegistry | None = None,
    ) -> None:
        self.router = router
        self.worker_registry = worker_registry or build_default_worker_registry()
        self.integration_registry = integration_registry or build_default_integration_registry()
        self.env_category_registry = env_category_registry or build_default_env_category_registry()

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
        required_env_categories, env_profiles = self._resolve_env_requirements(plan)

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
            required_env_categories=required_env_categories,
            env_profiles=env_profiles,
        )

    def _validate_required_integrations(
        self, integrations: list[DispatchPlanIntegration]
    ) -> None:
        required_ids = sorted(
            integration.id for integration in integrations if integration.required
        )
        self.integration_registry.require(required_ids)
        if "mcp2cli" not in required_ids:
            raise ValueError("mcp2cli must be present in required integrations")

    def _resolve_env_requirements(
        self, plan: DispatchPlan
    ) -> tuple[list[str], list[dict]]:
        categories = {
            category
            for repo in plan.repos_metadata
            for category in repo.get("required_env_categories", [])
        }
        for integration in plan.required_integrations:
            capability = self.integration_registry.get(integration.id)
            if capability:
                categories.update(capability.env_categories)
        required_categories = sorted(categories)
        env_profiles = [
            profile.to_dict()
            for profile in self.env_category_registry.require(required_categories)
        ]
        return required_categories, env_profiles

    def _collect_required_approvals(self, worker: DispatchPlanWorker) -> list[str]:
        capability = self.worker_registry.get(worker.id)
        if not capability:
            return []
        return list(capability.requires_approval_for)
