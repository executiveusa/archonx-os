"""Notion connector — CRUD for Tasks, Runs, Artifacts, Approvals, Profiles, Agents DBs.

STUB — full implementation in P3.
Uses the official Notion API v2022-06-28.
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx


class NotionClient:
    """Adapter for the Notion API. All secrets read from env at init."""

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, token: str, db_ids: dict[str, str]):
        self._token = token
        self._db_ids = db_ids
        self._http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": self.API_VERSION,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    # ── Tasks ─────────────────────────────────────────────
    async def query_tasks(self, filters: dict[str, Any] | None = None):
        # STUB
        return {"ok": True, "data": [], "trace_id": str(uuid.uuid4())}

    async def create_task(self, payload: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"task_id": str(uuid.uuid4()), **payload}, "trace_id": str(uuid.uuid4())}

    async def update_task(self, task_id: str, patch: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"task_id": task_id, **patch}, "trace_id": str(uuid.uuid4())}

    # ── Runs ──────────────────────────────────────────────
    async def create_run(self, payload: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"run_id": str(uuid.uuid4()), **payload}, "trace_id": str(uuid.uuid4())}

    async def append_run_log(self, run_id: str, log_entry: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"run_id": run_id, "appended": True}, "trace_id": str(uuid.uuid4())}

    # ── Artifacts ─────────────────────────────────────────
    async def create_artifact(self, run_id: str, artifact_meta: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"artifact_id": str(uuid.uuid4()), "run_id": run_id}, "trace_id": str(uuid.uuid4())}

    # ── Approvals ─────────────────────────────────────────
    async def create_approval_request(self, payload: dict[str, Any]):
        # STUB
        return {"ok": True, "data": {"approval_id": str(uuid.uuid4()), **payload}, "trace_id": str(uuid.uuid4())}

    async def resolve_approval_request(self, approval_id: str, decision: str):
        # STUB
        return {"ok": True, "data": {"approval_id": approval_id, "status": decision}, "trace_id": str(uuid.uuid4())}

    async def close(self):
        await self._http.aclose()
