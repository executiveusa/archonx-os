"""ZTE-20260303-9001: Coolify deployment API client."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Any
from urllib import error, request


@dataclass
class DeploymentStatus:
    deployment_id: str
    status: str
    started_at: str = ""
    finished_at: str = ""
    logs: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class ServiceHealth:
    uuid: str
    name: str
    status: str
    url: str = ""
    last_deploy: str = ""


class CoolifyClient:
    """Minimal async Coolify API wrapper backed by urllib."""

    def __init__(self, api_key: str = "", base_url: str = "") -> None:
        self.api_key = api_key or os.getenv("COOLIFY_API_KEY", "")
        self.base_url = (base_url or os.getenv("COOLIFY_BASE_URL", "")).rstrip("/")

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("COOLIFY_BASE_URL is not configured")
        if not self.api_key:
            raise RuntimeError("COOLIFY_API_KEY is not configured")

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        def _send() -> dict[str, Any]:
            try:
                with request.urlopen(req, timeout=30) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body) if body else {}
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"Coolify API error {exc.code}: {body}") from exc
            except error.URLError as exc:
                raise RuntimeError(f"Coolify API unreachable: {exc.reason}") from exc

        return await asyncio.to_thread(_send)

    async def trigger_deploy(self, app_uuid: str, force: bool = False) -> str:
        data = await self._request("POST", "/api/v1/deploy", {"uuid": app_uuid, "force": force})
        return str(data.get("deployment_id") or data.get("id") or "")

    async def get_deployment_status(self, deployment_id: str) -> DeploymentStatus:
        data = await self._request("GET", f"/api/v1/deployments/{deployment_id}")
        return DeploymentStatus(
            deployment_id=deployment_id,
            status=str(data.get("status", "unknown")),
            started_at=str(data.get("created_at", "")),
            finished_at=str(data.get("finished_at", "")),
            logs=[str(log) for log in data.get("logs", [])],
            error=str(data.get("error", "")),
        )

    async def wait_for_deploy(
        self,
        deployment_id: str,
        timeout_seconds: int = 300,
        poll_interval: int = 10,
    ) -> DeploymentStatus:
        elapsed = 0
        while elapsed < timeout_seconds:
            status = await self.get_deployment_status(deployment_id)
            if status.status in {"finished", "success"}:
                return status
            if status.status in {"failed", "cancelled", "error"}:
                raise RuntimeError(status.error or f"Deployment {deployment_id} failed")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        raise TimeoutError(f"Deployment {deployment_id} timed out")

    async def check_health(self, app_uuid: str) -> ServiceHealth:
        data = await self._request("GET", f"/api/v1/applications/{app_uuid}")
        return ServiceHealth(
            uuid=app_uuid,
            name=str(data.get("name", "")),
            status=str(data.get("status", "unknown")),
            url=str(data.get("url") or data.get("fqdn") or ""),
            last_deploy=str(data.get("last_deploy", "")),
        )

    async def rollback(self, app_uuid: str, deployment_id: str) -> bool:
        await self._request(
            "POST",
            f"/api/v1/applications/{app_uuid}/rollback",
            {"deployment_id": deployment_id},
        )
        return True
