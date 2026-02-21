"""Orgo connector — computer-use adapter for creating/controlling ephemeral desktops.

STUB — full implementation in P3.
Uses the Orgo MCP / REST API.
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx


class OrgoClient:
    """Adapter for the Orgo computer-use API."""

    def __init__(self, api_key: str, base_url: str = "https://api.orgo.ai"):
        self._api_key = api_key
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def create_computer(self, spec: dict[str, Any] | None = None):
        # STUB
        return {
            "ok": True,
            "data": {
                "computer_id": str(uuid.uuid4()),
                "status": "starting",
                "connection_url": "https://orgo.ai/desktop/stub",
            },
            "trace_id": str(uuid.uuid4()),
        }

    async def destroy_computer(self, computer_id: str):
        # STUB
        return {"ok": True, "data": {"computer_id": computer_id, "status": "destroyed"}, "trace_id": str(uuid.uuid4())}

    async def get_computer_status(self, computer_id: str):
        # STUB
        return {"ok": True, "data": {"computer_id": computer_id, "status": "running"}, "trace_id": str(uuid.uuid4())}

    async def screenshot(self, computer_id: str):
        # STUB — returns base64 PNG in production
        return {
            "ok": True,
            "data": {"computer_id": computer_id, "screenshot_base64": "", "format": "png"},
            "trace_id": str(uuid.uuid4()),
        }

    async def input(self, computer_id: str, actions: list[dict[str, Any]]):
        # STUB
        return {
            "ok": True,
            "data": {"computer_id": computer_id, "actions_executed": len(actions)},
            "trace_id": str(uuid.uuid4()),
        }

    async def open_url(self, computer_id: str, url: str):
        # STUB
        return {
            "ok": True,
            "data": {"computer_id": computer_id, "url": url, "status": "navigated"},
            "trace_id": str(uuid.uuid4()),
        }

    async def close(self):
        await self._http.aclose()
