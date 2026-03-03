"""ZTE-20260303-9001: Deployment notification back-channel."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
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

    async def notify(self, result: TaskResult) -> None:
        message = self._format_success(result) if result.success else self._format_failure(result)
        logger.info("NOTIFICATION: %s", message)

        if self.channel == "webhook" and self.webhook_url:
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
