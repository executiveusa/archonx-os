"""Sandboxed code-runner HTTP API.

Runs inside the Docker sandbox container. Accepts commands
via HTTP, executes them as the non-root 'runner' user,
and returns stdout/stderr/exit_code.

Security invariants:
- Non-root execution
- /work is the only writable directory
- Network disabled by default (docker-compose network_mode)
- Resource limits enforced by docker-compose (mem_limit, cpus)
"""

from __future__ import annotations

import asyncio
import base64
import os
import subprocess
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SYNTHIA Code Runner (Sandbox)")

MAX_RUNTIME = int(os.environ.get("RUNNER_MAX_RUNTIME_SECONDS", "300"))
WORK_DIR = Path("/work")


class ExecRequest(BaseModel):
    command: str
    workdir: str = "/work"
    timeout: int = MAX_RUNTIME


class PutFileRequest(BaseModel):
    path: str
    content_base64: str


@app.get("/healthz")
async def healthz():
    return {"ok": True, "service": "code-runner", "user": os.getenv("USER", "runner")}


@app.post("/exec")
async def exec_command(body: ExecRequest):
    """Execute a command in the sandbox. Blocks until completion or timeout."""
    workdir = body.workdir if body.workdir.startswith("/work") else "/work"
    timeout = min(body.timeout, MAX_RUNTIME)

    try:
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_shell(
                body.command,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "HOME": "/work"},
            ),
            timeout=timeout,
        )
        stdout_raw, stderr_raw = await proc.communicate()
        return {
            "ok": proc.returncode == 0,
            "data": {
                "stdout": stdout_raw.decode(errors="replace")[:50_000],
                "stderr": stderr_raw.decode(errors="replace")[:50_000],
                "exit_code": proc.returncode,
            },
        }
    except asyncio.TimeoutError:
        return {"ok": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/put-file")
async def put_file(body: PutFileRequest):
    """Write a file to /work. Path must be under /work."""
    target = WORK_DIR / body.path.lstrip("/")
    resolved = target.resolve()
    if not str(resolved).startswith(str(WORK_DIR.resolve())):
        return {"ok": False, "error": "Path traversal blocked — must be under /work"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(base64.b64decode(body.content_base64))
    return {"ok": True, "data": {"path": str(resolved), "size": resolved.stat().st_size}}


@app.get("/get-file")
async def get_file(path: str):
    """Read a file from /work, returned as base64."""
    target = (WORK_DIR / path.lstrip("/")).resolve()
    if not str(target).startswith(str(WORK_DIR.resolve())):
        return {"ok": False, "error": "Path traversal blocked"}
    if not target.is_file():
        return {"ok": False, "error": "File not found"}
    content = base64.b64encode(target.read_bytes()).decode()
    return {"ok": True, "data": {"path": str(target), "content_base64": content}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("RUNNER_PORT", "9000")))
