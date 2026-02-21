"""Agents API — spawn, monitor, kill agents + Orgo computers."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AgentSpawnRequest(BaseModel):
    name: str
    task_id: str
    tools_allowed: list[str] = []


@router.get("/")
async def list_agents():
    """List all active agents and their statuses."""
    # STUB — will read from Notion Agents DB in P3
    return {"ok": True, "data": []}


@router.post("/spawn")
async def spawn_agent(body: AgentSpawnRequest):
    """Spawn a new agent with an Orgo computer and assign a task."""
    # STUB — will call orgo.create_computer() + start agent loop in P3
    return {
        "ok": True,
        "data": {
            "agent_id": "stub-agent-001",
            "computer_id": "stub-comp-001",
            "status": "starting",
            **body.model_dump(),
        },
    }


@router.post("/{agent_id}/kill")
async def kill_agent(agent_id: str):
    """Kill switch — stop agent loop and destroy its Orgo computer."""
    # STUB — will call orgo.destroy_computer() + update Notion in P3
    return {"ok": True, "data": {"agent_id": agent_id, "status": "killed"}}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get current agent detail: status, run, computer link."""
    # STUB
    return {
        "ok": True,
        "data": {
            "agent_id": agent_id,
            "status": "idle",
            "current_task": None,
            "computer_id": None,
        },
    }


@router.get("/{agent_id}/screenshot")
async def agent_screenshot(agent_id: str):
    """Get latest screenshot from the agent's Orgo computer."""
    # STUB — will call orgo.screenshot() in P3
    return {"ok": True, "data": {"agent_id": agent_id, "screenshot_url": None, "stub": True}}
