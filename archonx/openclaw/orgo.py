"""Orgo API integration for bead ZTE-20260304-0002.

Expected API shape (validated against current Orgo docs during implementation):
- POST   /v1/sessions
- POST   /v1/sessions/{session_id}/actions
- GET    /v1/sessions/{session_id}/screenshot
- DELETE /v1/sessions/{session_id}
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger("archonx.openclaw.orgo")


@dataclass
class OrgoSession:
    session_id: str
    status: str = "pending"
    vm_url: str = ""
    screenshots: list[str] = field(default_factory=list)
    actions_taken: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class OrgoClient:
    """Async Orgo client. Falls back to local simulation if ORGO_API_TOKEN is absent."""

    def __init__(self, api_key: str = "", base_url: str = "https://api.orgo.ai") -> None:
        self.api_key = api_key or os.getenv("ORGO_API_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self._sessions: dict[str, OrgoSession] = {}
        self._counter = 0
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=60.0,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def create_session(self, task: str, config: dict[str, Any] | None = None) -> OrgoSession:
        if not self.api_key:
            self._counter += 1
            session = OrgoSession(
                session_id=f"orgo-local-{self._counter:05d}",
                status="active",
                vm_url=f"{self.base_url}/sessions/orgo-local-{self._counter:05d}",
                metadata={"task": task, "config": config or {}, "mode": "simulated"},
            )
            self._sessions[session.session_id] = session
            return session

        client = await self._http()
        response = await client.post("/v1/sessions", json={"task": task, "config": config or {}})
        response.raise_for_status()
        data = response.json()
        session = OrgoSession(
            session_id=str(data.get("id") or data.get("session_id") or ""),
            status=str(data.get("status", "active")),
            vm_url=str(data.get("url") or data.get("vm_url") or ""),
            metadata=data,
        )
        self._sessions[session.session_id] = session
        logger.info("Orgo session created: %s", session.session_id)
        return session

    async def execute_action(self, session_id: str, action: dict[str, Any]) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}

        if not self.api_key:
            session.actions_taken += 1
            return {
                "session_id": session_id,
                "action": action.get("type", "unknown"),
                "status": "completed",
                "screenshot": f"screenshot_{session.actions_taken}.png",
            }

        client = await self._http()
        response = await client.post(f"/v1/sessions/{session_id}/actions", json=action)
        response.raise_for_status()
        session.actions_taken += 1
        return response.json()

    async def get_screenshot(self, session_id: str) -> str:
        session = self._sessions.get(session_id)
        if not session:
            return ""

        if not self.api_key:
            return f"{self.base_url}/screenshots/{session_id}/latest.png"

        client = await self._http()
        response = await client.get(f"/v1/sessions/{session_id}/screenshot")
        response.raise_for_status()
        data = response.json()
        shot_url = str(data.get("url") or data.get("screenshot_url") or "")
        if shot_url:
            session.screenshots.append(shot_url)
        return shot_url

    async def close_session(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.status = "completed"
        if self.api_key:
            client = await self._http()
            response = await client.delete(f"/v1/sessions/{session_id}")
            response.raise_for_status()

    @property
    def active_sessions(self) -> list[OrgoSession]:
        return [s for s in self._sessions.values() if s.status == "active"]

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "OrgoClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
