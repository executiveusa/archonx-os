import pytest
import asyncio
from unittest.mock import MagicMock, patch
from archonx.core.agents import Agent, Role, Crew, AgentStatus
from archonx.beads.viewer import Task, TaskStatus
from archonx.orchestration.agent_controller import AgentController

@pytest.mark.asyncio
async def test_execute_task_success():
    """Test successful task execution with mocked Ralphy subprocess."""
    # Setup
    agent = Agent(
        agent_id="synthia_queen_white",
        name="Synthia",
        role=Role.QUEEN,
        crew=Crew.WHITE,
        position="D1",
        specialty="Tactical"
    )
    task = Task(id="task-001", bead_id="BEAD-001", title="Implement Auth", description="Add login")
    
    controller = AgentController(workspace_root="/tmp", ralphy_path="/tmp/ralphy.sh")
    
    # Mock subprocess
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_process = MagicMock()
        mock_process.communicate = MagicMock(return_value=asyncio.Future())
        mock_process.communicate.return_value.set_result((b"Ralphy loop completed successfully", b""))
        mock_process.returncode = 0
        mock_exec.return_value = mock_process
        
        # Execute
        result = await controller.execute_task(agent, task)
        
        # Verify
        assert result.success is True
        assert task.status == TaskStatus.COMPLETED
        assert agent.status == AgentStatus.ACTIVE
        assert agent.tasks_completed == 1
        assert agent.score == 10.0

@pytest.mark.asyncio
async def test_execute_task_failure():
    """Test task execution failure handling."""
    agent = Agent(agent_id="test_agent", name="Test", role=Role.PAWN, crew=Crew.WHITE, position="A1", specialty="Test")
    task = Task(id="task-002", bead_id="BEAD-002", title="Faulty Task", description="Will fail")
    
    controller = AgentController(workspace_root="/tmp", ralphy_path="/tmp/ralphy.sh")
    
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_process = MagicMock()
        mock_process.communicate = MagicMock(return_value=asyncio.Future())
        mock_process.communicate.return_value.set_result((b"Something went wrong", b"Simulation error"))
        mock_process.returncode = 1
        mock_exec.return_value = mock_process
        
        result = await controller.execute_task(agent, task)
        
        assert result.success is False
        assert task.status == TaskStatus.FAILED
        assert task.error == "Simulation error"
        assert agent.status == AgentStatus.ACTIVE
