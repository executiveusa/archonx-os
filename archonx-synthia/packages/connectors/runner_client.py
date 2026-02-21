"""Runner connector — HTTP client for the Docker sandbox code-runner service."""

from __future__ import annotations

import uuid

import httpx


class RunnerClient:
    """Adapter for the sandboxed code-runner HTTP API."""

    def __init__(self, base_url: str = "http://code-runner:9000"):
        self._http = httpx.AsyncClient(base_url=base_url, timeout=300.0)

    async def exec(self, command: str, workdir: str = "/work", env_scoped: dict | None = None, network_mode: str = "none"):
        # STUB
        return {"ok": True, "data": {"stdout": "", "stderr": "", "exit_code": 0}, "trace_id": str(uuid.uuid4())}

    async def put_file(self, path: str, content_base64: str):
        # STUB
        return {"ok": True, "data": {"path": path, "written": True}, "trace_id": str(uuid.uuid4())}

    async def get_file(self, path: str):
        # STUB
        return {"ok": True, "data": {"path": path, "content_base64": ""}, "trace_id": str(uuid.uuid4())}

    async def close(self):
        await self._http.aclose()
