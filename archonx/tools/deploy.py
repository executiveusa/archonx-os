"""Deployment Tool - Coolify-backed deployment orchestrator."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from archonx.notifications.notifier import Notifier, TaskResult
from archonx.tools.base import BaseTool, ToolResult
from archonx.tools.coolify_client import CoolifyClient

logger = logging.getLogger("archonx.tools.deploy")

_BEAD_ID = "ZTE-20260303-9001"
_CONFIG_PATH = Path(__file__).resolve().parents[2] / "archonx-config.json"


class DeploymentTool(BaseTool):
    name = "deployment"
    description = "Multi-stage deployment pipeline with rollback"

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        action = params.get("action", "deploy")
        repo = params.get("repo", "")
        env = params.get("environment", "staging")

        logger.info("[%s] deployment action=%s env=%s repo=%s", _BEAD_ID, action, env, repo)

        if action == "deploy":
            data = await self._deploy(repo, env, params.get("auto_test", True))
        elif action == "rollback":
            data = await self._rollback(repo, env, params.get("deployment_id", ""))
        elif action == "status":
            data = await self._status(repo, env)
        else:
            return ToolResult(tool=self.name, status="error", error=f"Unknown action: {action}")
        return ToolResult(tool=self.name, status="success", data=data)

    def _load_coolify_config(self) -> dict[str, str]:
        if not _CONFIG_PATH.exists():
            return {}
        raw = json.loads(_CONFIG_PATH.read_text())
        coolify = raw.get("coolify", {})
        return {
            "app_uuid": str(coolify.get("app_uuid", "")),
            "base_url": str(coolify.get("base_url", "")),
        }

    async def _deploy(self, repo: str, env: str, auto_test: bool) -> dict[str, Any]:
        coolify_cfg = self._load_coolify_config()
        app_uuid = coolify_cfg.get("app_uuid", "")
        if not app_uuid:
            raise RuntimeError("Missing coolify.app_uuid in archonx-config.json")

        notifier = Notifier()
        client = CoolifyClient(base_url=coolify_cfg.get("base_url", ""))

        deployment_id = ""
        try:
            deployment_id = await client.trigger_deploy(app_uuid=app_uuid)
            deploy_status = await client.wait_for_deploy(deployment_id, timeout_seconds=300)
            health = await client.check_health(app_uuid)
            result = {
                "status": "deployed",
                "repo": repo,
                "environment": env,
                "auto_test": auto_test,
                "deployment_id": deployment_id,
                "deploy_status": deploy_status.status,
                "health": health.status,
                "url": health.url,
                "rollback_available": True,
            }
            await notifier.notify(
                TaskResult(
                    bead_id=_BEAD_ID,
                    task_name="deployment",
                    success=True,
                    environment=env,
                    deploy_url=health.url,
                )
            )
            return result
        except Exception as exc:
            await notifier.notify(
                TaskResult(
                    bead_id=_BEAD_ID,
                    task_name="deployment",
                    success=False,
                    environment=env,
                    error_summary=str(exc),
                    stage_failed="deploy",
                )
            )
            raise

    async def _rollback(self, repo: str, env: str, deployment_id: str) -> dict[str, Any]:
        coolify_cfg = self._load_coolify_config()
        app_uuid = coolify_cfg.get("app_uuid", "")
        if not app_uuid:
            raise RuntimeError("Missing coolify.app_uuid in archonx-config.json")
        if not deployment_id:
            raise RuntimeError("rollback requires deployment_id")

        client = CoolifyClient(base_url=coolify_cfg.get("base_url", ""))
        ok = await client.rollback(app_uuid=app_uuid, deployment_id=deployment_id)
        health = await client.check_health(app_uuid)
        return {
            "status": "rolled_back" if ok else "rollback_failed",
            "repo": repo,
            "environment": env,
            "deployment_id": deployment_id,
            "health": health.status,
            "url": health.url,
        }

    async def _status(self, repo: str, env: str) -> dict[str, Any]:
        coolify_cfg = self._load_coolify_config()
        app_uuid = coolify_cfg.get("app_uuid", "")
        if not app_uuid:
            return {"status": "unknown", "repo": repo, "environment": env, "health": "unconfigured"}

        client = CoolifyClient(base_url=coolify_cfg.get("base_url", ""))
        health = await client.check_health(app_uuid)
        return {
            "status": "running" if health.status == "running" else "degraded",
            "repo": repo,
            "environment": env,
            "health": health.status,
            "url": health.url,
        }
