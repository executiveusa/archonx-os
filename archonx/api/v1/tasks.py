"""Task submission + status endpoints."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from archonx.orchestration.orchestrator import Orchestrator, TaskType
from archonx.monitoring.metrics import metrics

router = APIRouter(prefix="/tasks")


class TaskPayload(BaseModel):
    message: str
    source: str = "api"
    priority: str = "normal"
    crew: str = "white"
    repo: str = ""
    environment: str = "staging"
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post("")
async def submit_task(payload: TaskPayload, request: Request) -> JSONResponse:
    state = request.app.state.app_state
    kernel = state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    result = await kernel.execute_task({
        "message": payload.message,
        "source": payload.source,
        "priority": payload.priority,
        "crew": payload.crew,
        "repo": payload.repo,
        "environment": payload.environment,
        **payload.metadata,
    })

    task_id = f"ZTE-{datetime.now(timezone.utc).timestamp()}"
    state.task_status[task_id] = {
        "status": result.get("status", "unknown"),
        "task_id": task_id,
        "result": result,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    await _broadcast_ws(state, {"event": "task_result", "data": result})
    return JSONResponse({"task_id": task_id, **result})


@router.get("")
async def list_tasks(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    return JSONResponse({
        "tasks": list(state.task_status.values()),
        "count": len(state.task_status),
    })


@router.get("/stats")
async def get_stats() -> JSONResponse:
    return JSONResponse(metrics.get_summary())


@router.get("/{task_id}")
async def get_task_status(task_id: str, request: Request) -> JSONResponse:
    state = request.app.state.app_state
    data = state.task_status.get(task_id)
    if not data:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse(data)


async def _broadcast_ws(state: Any, message: dict[str, Any]) -> None:
    dead = set()
    for ws in state.ws_clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    state.ws_clients -= dead
