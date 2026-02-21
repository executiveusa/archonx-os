"""Tasks API — CRUD + queue operations backed by Notion Tasks DB."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    priority: str = "med"
    context: str = ""
    tags: list[str] = []
    requires_approval: bool = False


class TaskPatch(BaseModel):
    status: str | None = None
    priority: str | None = None
    context: str | None = None
    owner_agent: str | None = None


@router.get("/")
async def list_tasks(status: str | None = None):
    """Query tasks from Notion Tasks DB."""
    # STUB — will call notion.query_tasks() in P3
    return {"ok": True, "data": [], "stub": True}


@router.post("/")
async def create_task(body: TaskCreate):
    """Create a new task in Notion."""
    # STUB — will call notion.create_task() in P3
    return {"ok": True, "data": {"task_id": "stub-task-001", **body.model_dump()}}


@router.patch("/{task_id}")
async def update_task(task_id: str, body: TaskPatch):
    """Update a task in Notion."""
    # STUB — will call notion.update_task() in P3
    return {"ok": True, "data": {"task_id": task_id, **body.model_dump(exclude_none=True)}}


@router.get("/{task_id}")
async def get_task(task_id: str):
    """Get a single task by ID."""
    # STUB
    return {"ok": True, "data": {"task_id": task_id, "title": "Stub task", "status": "backlog"}}
