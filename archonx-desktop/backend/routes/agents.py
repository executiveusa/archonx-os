"""Agent routes - integrates with ARCHONX kernel"""

import os
import sys
from typing import List
from fastapi import APIRouter, HTTPException
from models import Agent

router = APIRouter()

# Mock agent data
mock_agents = {
    "white": [
        Agent(id="w1", name="Bobby Fischer Protocol", status="idle", crew="white"),
        Agent(id="w2", name="Decision Validator", status="idle", crew="white"),
        Agent(id="w3", name="Reasoning Engine", status="idle", crew="white"),
    ],
    "black": [
        Agent(id="b1", name="Tyrone Protocol", status="idle", crew="black"),
        Agent(id="b2", name="Ethics Guardian", status="idle", crew="black"),
        Agent(id="b3", name="Risk Analyzer", status="busy", crew="black", current_task="Analyzing deployment risk"),
    ]
}


async def initialize():
    """Initialize agent system"""
    try:
        sys.path.insert(0, "/home/user/archonx-os")
        # Import ARCHONX kernel if available
        from archonx.kernel import get_agents
        print("ArchonX kernel loaded")
    except (ImportError, Exception) as e:
        print(f"Using mock agents: {e}")


@router.get("")
async def list_agents(crew: str = None):
    """List agents"""
    try:
        if crew:
            agents = mock_agents.get(crew, [])
        else:
            agents = [a for crew_agents in mock_agents.values() for a in crew_agents]

        return {"agents": agents, "total": len(agents)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    try:
        for crew_agents in mock_agents.values():
            for agent in crew_agents:
                if agent.id == agent_id:
                    return agent

        raise HTTPException(status_code=404, detail="Agent not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/task")
async def assign_task(agent_id: str, task: str, priority: int = 5):
    """Assign a task to an agent"""
    try:
        for crew_agents in mock_agents.values():
            for agent in crew_agents:
                if agent.id == agent_id:
                    agent.status = "busy"
                    agent.current_task = task
                    return {"status": "assigned", "agent_id": agent_id, "task": task}

        raise HTTPException(status_code=404, detail="Agent not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status"""
    try:
        for crew_agents in mock_agents.values():
            for agent in crew_agents:
                if agent.id == agent_id:
                    return {"agent_id": agent_id, "status": agent.status}

        raise HTTPException(status_code=404, detail="Agent not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crew/{crew}/task")
async def assign_crew_task(crew: str, task: str):
    """Assign a task to all agents in a crew"""
    try:
        crew_agents = mock_agents.get(crew)
        if not crew_agents:
            raise HTTPException(status_code=404, detail="Crew not found")

        for agent in crew_agents:
            agent.status = "busy"
            agent.current_task = task

        return {"status": "assigned_to_crew", "crew": crew, "count": len(crew_agents)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
