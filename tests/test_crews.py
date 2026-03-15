"""
Tests — Crew coordination
"""

import pytest

from archonx.core.agents import AgentRegistry, AgentStatus, Crew, build_all_agents
from archonx.core.protocol import Decision
from archonx.crews.white_crew import WhiteCrew
from archonx.crews.black_crew import BlackCrew


@pytest.fixture
def registry() -> AgentRegistry:
    r = AgentRegistry()
    build_all_agents(r)
    return r


@pytest.mark.asyncio
async def test_white_crew_initialize(registry: AgentRegistry) -> None:
    crew = WhiteCrew(registry)
    await crew.initialize()
    assert len(crew.agents) == 32
    assert crew.king.name == "Pauli"
    assert crew.queen.name == "Synthia"


@pytest.mark.asyncio
async def test_black_crew_initialize(registry: AgentRegistry) -> None:
    crew = BlackCrew(registry)
    await crew.initialize()
    assert len(crew.agents) == 32
    assert crew.king.name == "Mirror"
    assert crew.queen.name == "Shadow"


@pytest.mark.asyncio
async def test_crew_execute_task(registry: AgentRegistry) -> None:
    crew = WhiteCrew(registry)
    await crew.initialize()
    decision = Decision(approved=True, confidence=0.85, depth=7, reason="test")
    result = await crew.execute({"type": "deployment"}, decision)
    assert result["crew"] == "white"
    assert result["subtasks_executed"] >= 1


@pytest.mark.asyncio
async def test_crew_shutdown(registry: AgentRegistry) -> None:
    crew = WhiteCrew(registry)
    await crew.initialize()
    await crew.shutdown()
    assert all(a.status == AgentStatus.OFFLINE for a in crew.agents)
