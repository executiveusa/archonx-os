"""ConX Layer — machine registration with token auth."""

from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/conx")

_CONX_TOKEN = os.getenv("ARCHONX_CONX_TOKEN", "").strip()


def _verify_conx_auth(authorization: str | None) -> bool:
    """Require Bearer token for ConX write operations."""
    if not _CONX_TOKEN:
        return True  # no token configured = no enforcement (dev mode)
    if not authorization:
        return False
    return hmac.compare_digest(authorization, f"Bearer {_CONX_TOKEN}")


@router.get("/status")
async def conx_status(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    machines = [
        {"machine_id": mid, **md}
        for mid, md in state.registered_machines.items()
    ]
    return JSONResponse({"machines": machines, "total": len(machines)})


@router.post("/register")
async def conx_register(
    body: dict[str, Any],
    request: Request,
    authorization: str | None = Header(default=None),
) -> JSONResponse:
    if not _verify_conx_auth(authorization):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    state = request.app.state.app_state
    hostname = body.get("hostname", "unknown")
    tunnel_url = body.get("tunnel_url", "")
    os_name = body.get("os", "unknown")
    mcp_servers = body.get("mcp_servers", [])

    if not tunnel_url:
        return JSONResponse({"error": "tunnel_url required"}, status_code=400)

    machine_id = f"{hostname}-{datetime.now(timezone.utc).timestamp()}"
    state.registered_machines[machine_id] = {
        "hostname": hostname,
        "tunnel_url": tunnel_url,
        "os": os_name,
        "mcp_servers_wired": mcp_servers,
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }

    return JSONResponse({"registered": True, "machine_id": machine_id})


@router.delete("/register/{machine_id}")
async def conx_deregister(
    machine_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> JSONResponse:
    if not _verify_conx_auth(authorization):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    state = request.app.state.app_state
    if machine_id in state.registered_machines:
        del state.registered_machines[machine_id]
        return JSONResponse({"deregistered": True})
    return JSONResponse({"error": "machine not found"}, status_code=404)


@router.get("/machines")
async def conx_machines(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    machines = []
    for mid, md in state.registered_machines.items():
        health = "unknown"
        tunnel = md.get("tunnel_url", "")
        if tunnel:
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{tunnel}/health", timeout=5.0)
                    health = "alive" if r.status_code == 200 else "offline"
            except Exception:
                health = "offline"
        machines.append({"machine_id": mid, "health": health, **md})
    return JSONResponse({"machines": machines, "total": len(machines)})


@router.post("/launch")
async def conx_launch(
    body: dict[str, Any],
    request: Request,
    authorization: str | None = Header(default=None),
) -> JSONResponse:
    if not _verify_conx_auth(authorization):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    state = request.app.state.app_state
    machine_id = body.get("machine_id", "")
    task = body.get("task", "")
    if not machine_id or not task:
        return JSONResponse({"error": "machine_id and task required"}, status_code=400)

    if machine_id not in state.registered_machines:
        return JSONResponse({"error": "machine not found"}, status_code=404)

    machine = state.registered_machines[machine_id]
    task_id = f"CONX-{datetime.now(timezone.utc).timestamp()}"
    state.task_status[task_id] = {
        "status": "queued",
        "task_id": task_id,
        "machine_id": machine_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    tunnel_url = machine.get("tunnel_url", "")
    if tunnel_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{tunnel_url}/webhook/task",
                    json={"message": task, "source": "conx"},
                    timeout=10.0,
                )
            state.task_status[task_id]["status"] = "sent"
        except Exception as e:
            state.task_status[task_id]["status"] = "error"
            state.task_status[task_id]["error"] = str(e)

    return JSONResponse({"task_id": task_id, "status": state.task_status[task_id]["status"]})
