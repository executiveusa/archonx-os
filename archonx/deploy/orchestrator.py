"""
Deployment Orchestrator
=======================
Full lifecycle management for ArchonX OS deployments.
Handles: staging → testing → deploy → verify → rollback-if-needed.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.deploy.orchestrator")


class DeployStage(str, Enum):
    INIT = "init"
    STAGING = "staging"
    TESTING = "testing"
    SECURITY_SCAN = "security_scan"
    DEPLOY = "deploy"
    VERIFY = "verify"
    COMPLETE = "complete"
    ROLLBACK = "rollback"
    FAILED = "failed"


@dataclass
class DeploymentPlan:
    """A full deployment plan with rollback strategy."""

    deployment_id: str
    client_id: str
    target: str  # e.g. "e-commerce site", "api-gateway"
    repo: str
    mode: str = "staging_first"  # staging_first | direct | ab_test
    stages: list[DeployStage] = field(default_factory=lambda: [
        DeployStage.INIT,
        DeployStage.STAGING,
        DeployStage.TESTING,
        DeployStage.SECURITY_SCAN,
        DeployStage.DEPLOY,
        DeployStage.VERIFY,
        DeployStage.COMPLETE,
    ])
    current_stage: DeployStage = DeployStage.INIT
    results: dict[str, Any] = field(default_factory=dict)
    rollback_snapshots: list[dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    confidence: float = 0.0

    @property
    def elapsed_seconds(self) -> float:
        end = self.completed_at or time.time()
        return round(end - self.started_at, 2)


class DeploymentOrchestrator:
    """
    Orchestrates the full deployment pipeline.

    Maps to the spec's task execution workflow:
    1. Receive task from Pauli (strategic decision)
    2. Break down into stages
    3. Assign to specialists (Blitz, Probe, Sentinel)
    4. Monitor execution
    5. Handle incidents with rollback
    6. Report back to Pauli
    7. Update competitive score
    """

    def __init__(self) -> None:
        self._active_deployments: dict[str, DeploymentPlan] = {}
        self._history: list[DeploymentPlan] = []

    def create_plan(
        self,
        deployment_id: str,
        client_id: str,
        target: str,
        repo: str,
        mode: str = "staging_first",
    ) -> DeploymentPlan:
        """Create a new deployment plan."""
        plan = DeploymentPlan(
            deployment_id=deployment_id,
            client_id=client_id,
            target=target,
            repo=repo,
            mode=mode,
        )

        if mode == "direct":
            plan.stages = [
                DeployStage.INIT,
                DeployStage.DEPLOY,
                DeployStage.VERIFY,
                DeployStage.COMPLETE,
            ]
        elif mode == "ab_test":
            plan.stages = [
                DeployStage.INIT,
                DeployStage.STAGING,
                DeployStage.TESTING,
                DeployStage.SECURITY_SCAN,
                DeployStage.DEPLOY,  # deploys to A/B split
                DeployStage.VERIFY,
                DeployStage.COMPLETE,
            ]

        self._active_deployments[deployment_id] = plan
        logger.info(
            "Deployment plan created: %s → %s (%s mode, %d stages)",
            client_id,
            target,
            mode,
            len(plan.stages),
        )
        return plan

    async def execute_plan(self, deployment_id: str) -> DeploymentPlan:
        """Execute all stages of a deployment plan sequentially."""
        plan = self._active_deployments.get(deployment_id)
        if not plan:
            raise ValueError(f"No deployment plan found: {deployment_id}")

        logger.info("=== DEPLOYMENT START: %s ===", deployment_id)

        for stage in plan.stages:
            plan.current_stage = stage
            logger.info("  Stage: %s", stage.value)

            try:
                result = await self._execute_stage(plan, stage)
                plan.results[stage.value] = result

                # Snapshot for rollback
                plan.rollback_snapshots.append({
                    "stage": stage.value,
                    "timestamp": time.time(),
                    "result": result,
                })

                # Check if stage failed
                if result.get("status") == "failed":
                    logger.error("Stage %s failed — initiating rollback", stage.value)
                    await self._rollback(plan)
                    return plan

            except Exception as exc:
                logger.exception("Stage %s error", stage.value)
                plan.current_stage = DeployStage.FAILED
                plan.results[stage.value] = {"status": "error", "error": str(exc)}
                await self._rollback(plan)
                return plan

        plan.current_stage = DeployStage.COMPLETE
        plan.completed_at = time.time()
        self._history.append(plan)
        del self._active_deployments[deployment_id]
        logger.info(
            "=== DEPLOYMENT COMPLETE: %s (%.1fs) ===",
            deployment_id,
            plan.elapsed_seconds,
        )
        return plan

    async def _execute_stage(
        self, plan: DeploymentPlan, stage: DeployStage
    ) -> dict[str, Any]:
        """Execute a single deployment stage."""
        handlers = {
            DeployStage.INIT: self._stage_init,
            DeployStage.STAGING: self._stage_staging,
            DeployStage.TESTING: self._stage_testing,
            DeployStage.SECURITY_SCAN: self._stage_security,
            DeployStage.DEPLOY: self._stage_deploy,
            DeployStage.VERIFY: self._stage_verify,
            DeployStage.COMPLETE: self._stage_complete,
        }
        handler = handlers.get(stage, self._stage_noop)
        return await handler(plan)

    async def _rollback(self, plan: DeploymentPlan) -> None:
        """Rollback to last known good state."""
        plan.current_stage = DeployStage.ROLLBACK
        logger.warning("Rolling back deployment %s", plan.deployment_id)

        # Walk snapshots in reverse, undo each
        for snapshot in reversed(plan.rollback_snapshots):
            logger.info("  Reverting stage: %s", snapshot["stage"])

        plan.current_stage = DeployStage.FAILED
        plan.completed_at = time.time()
        self._history.append(plan)
        if plan.deployment_id in self._active_deployments:
            del self._active_deployments[plan.deployment_id]

    # ------------------------------------------------------------------
    # Stage handlers (stubs — integrate with real infra in production)
    # ------------------------------------------------------------------

    async def _stage_init(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Initializing deployment for %s", plan.client_id)
        return {"status": "success", "message": "Deployment initialized"}

    async def _stage_staging(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Deploying %s to staging", plan.repo)
        # In prod: Blitz (Knight B1) deploys to staging env
        return {"status": "success", "env": "staging", "url": f"https://staging.{plan.client_id}.archonx.io"}

    async def _stage_testing(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Running test suite on staging")
        # In prod: Probe (Pawn G2) runs full browser tests
        return {"status": "success", "tests_run": 42, "tests_passed": 42, "tests_failed": 0}

    async def _stage_security(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Running security scan")
        # In prod: Sentinel (Rook H1) runs security audit
        return {"status": "success", "vulnerabilities": 0, "scan_type": "full"}

    async def _stage_deploy(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Deploying %s to production", plan.repo)
        # In prod: GitHub Actions or direct deploy
        return {"status": "success", "env": "production", "url": f"https://{plan.client_id}.archonx.io"}

    async def _stage_verify(self, plan: DeploymentPlan) -> dict[str, Any]:
        logger.info("Verifying production deployment")
        # In prod: smoke tests + health checks
        plan.confidence = 0.95
        return {"status": "success", "health": "green", "confidence": 0.95}

    async def _stage_complete(self, plan: DeploymentPlan) -> dict[str, Any]:
        return {"status": "success", "message": "Deployment complete"}

    async def _stage_noop(self, plan: DeploymentPlan) -> dict[str, Any]:
        return {"status": "skipped"}

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def active_deployments(self) -> list[DeploymentPlan]:
        return list(self._active_deployments.values())

    @property
    def history(self) -> list[DeploymentPlan]:
        return list(self._history)

    def get_plan(self, deployment_id: str) -> DeploymentPlan | None:
        return self._active_deployments.get(deployment_id)
