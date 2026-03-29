"""Deployment notification back-channel for bead ZTE-20260304-0002."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from urllib import request

logger = logging.getLogger("archonx.notifications")


@dataclass
class TaskResult:
    bead_id: str
    task_name: str
    success: bool
    environment: str = "staging"
    pr_url: str = ""
    deploy_url: str = ""
    elapsed_seconds: int = 0
    cost_cents: int = 0
    error_summary: str = ""
    stage_failed: str = ""


class Notifier:
    def __init__(self) -> None:
        self.channel = os.getenv("NOTIFICATION_CHANNEL", "log_only")
        self.webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL", "")

    def _format_success(self, result: TaskResult) -> str:
        elapsed_min, elapsed_sec = divmod(result.elapsed_seconds, 60)
        lines = [
            f"✅ {result.bead_id} | {result.task_name} | COMPLETE",
            f"→ Deployed: {result.environment}",
        ]
        if result.pr_url:
            lines.append(f"→ PR: {result.pr_url}")
        if result.deploy_url:
            lines.append(f"→ Live: {result.deploy_url}")
        lines.append(f"→ Time: {elapsed_min}m {elapsed_sec}s | Cost: ${result.cost_cents/100:.2f}")
        return "\n".join(lines)

    def _format_failure(self, result: TaskResult) -> str:
        return (
            f"❌ {result.bead_id} | {result.task_name} | FAILED at Stage {result.stage_failed}\n"
            f"→ Reason: {result.error_summary}\n"
            "→ Auto-rollback: triggered\n"
            "→ Manual review needed"
        )

    async def notify(self, result: TaskResult) -> None:
        message = self._format_success(result) if result.success else self._format_failure(result)
        logger.info("NOTIFICATION: %s", message)

        if self.channel == "webhook" and self.webhook_url:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json={
                        "text": message,
                        "bead_id": result.bead_id,
                        "success": result.success,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
                response.raise_for_status()
            body = json.dumps(
                {
                    "text": message,
                    "bead_id": result.bead_id,
                    "success": result.success,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ).encode("utf-8")
            req = request.Request(
                self.webhook_url,
                method="POST",
                data=body,
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=15):
                pass

    def _format_success(self, result: TaskResult) -> str:
        return f"✅ {result.bead_id} | {result.task_name} | COMPLETE → Deployed: {result.environment}"

    def _format_failure(self, result: TaskResult) -> str:
        return (
            f"❌ {result.bead_id} | {result.task_name} | FAILED at Stage {result.stage_failed}"
            f" → Reason: {result.error_summary}"
        )
