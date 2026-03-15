"""Code Runner API — proxy to the Docker sandbox service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RunCommand(BaseModel):
    command: str
    workdir: str = "/work"
    env_scoped: dict[str, str] = {}
    network_mode: str = "none"


class PutFile(BaseModel):
    path: str
    content_base64: str


@router.post("/exec")
async def exec_command(body: RunCommand):
    """Execute a command in the Docker sandbox."""
    # STUB — will proxy to runner container HTTP API in P3
    return {"ok": True, "data": {"stdout": "", "stderr": "", "exit_code": 0, "stub": True}}


@router.post("/put-file")
async def put_file(body: PutFile):
    """Upload a file to the sandbox /work directory."""
    # STUB
    return {"ok": True, "data": {"path": body.path, "written": True, "stub": True}}


@router.get("/get-file")
async def get_file(path: str):
    """Retrieve a file from the sandbox."""
    # STUB
    return {"ok": True, "data": {"path": path, "content_base64": "", "stub": True}}
