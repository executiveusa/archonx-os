"""Coolify deployment API client for bead ZTE-20260304-0002."""
"""ZTE-20260303-9001: Coolify deployment API client."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
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
    """Async Coolify API wrapper backed by httpx."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("COOLIFY_API_KEY", "")
        self.base_url = (base_url or os.getenv("COOLIFY_BASE_URL", "")).rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
    """Minimal async Coolify API wrapper backed by urllib."""

    def __init__(self, api_key: str = "", base_url: str = "") -> None:
        self.api_key = api_key or os.getenv("COOLIFY_API_KEY", "")
        self.base_url = (base_url or os.getenv("COOLIFY_BASE_URL", "")).rstrip("/")

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("COOLIFY_BASE_URL is not configured")
        if not self.api_key:
            raise RuntimeError("COOLIFY_API_KEY is not configured")
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self._timeout_seconds,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        client = await self._ensure_client()
        try:
            response = await client.request(method, path, json=payload)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip() or "unknown error"
            raise RuntimeError(f"Coolify API error {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Coolify API request failed: {exc}") from exc

    async def trigger_deploy(self, app_uuid: str, force: bool = False) -> str:
        data = await self._request("POST", "/api/v1/deploy", {"uuid": app_uuid, "force": force})
        deployment_id = str(data.get("deployment_id") or data.get("id") or "")
        if not deployment_id:
            raise RuntimeError("Coolify deploy response did not include deployment ID")
        return deployment_id

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
            logs=[str(item) for item in data.get("logs", [])],
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
                raise RuntimeError(status.error or f"Deployment {deployment_id} failed with status={status.status}")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        raise TimeoutError(f"Deployment {deployment_id} did not finish in {timeout_seconds}s")
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
        await self._request("POST", f"/api/v1/applications/{app_uuid}/rollback", {"deployment_id": deployment_id})
        return True

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "CoolifyClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
        await self._request(
            "POST",
            f"/api/v1/applications/{app_uuid}/rollback",
            {"deployment_id": deployment_id},
        )
        return True
