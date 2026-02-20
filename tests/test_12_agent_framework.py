"""
Tests for 12-Agent Framework Implementation
============================================
Comprehensive tests for all new modules.

BEAD-008: Testing Implementation
"""

import pytest
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Test imports
from archonx.memory.byterover_client import ByteRoverClient, MemoryLayer, MemoryEntry
from archonx.memory.memory_manager import MemoryManager, AgentExpertise
from archonx.auth.oauth_server import OAuthServer, OAuthClient, GrantType
from archonx.auth.session_manager import SessionManager, User, Session
from archonx.auth.rbac import RBACManager, Role, Permission
from archonx.mail.server import AgentMailServer, AgentMessage, MessageType
from archonx.beads.viewer import BeadsViewer, TaskManager, Task, TaskStatus, TaskPriority
from archonx.orchestration.orchestrator import Orchestrator, OrchestratorCommand, TaskType
from archonx.kpis.dashboard import KPIDashboard, AgentMetrics, RevenueGoal, RevenueTracker
from archonx.automation.self_improvement import DailySelfImprovement, PAULIWHEELSync
from archonx.revenue.engine import RevenueEngine, LeadGenerator, Lead, LeadSource, LeadStatus


class TestByteRoverClient:
    """Tests for ByteRover memory client."""
    
    def test_memory_layer_enum(self):
        """Test MemoryLayer enum values."""
        assert MemoryLayer.PROJECT.value == "project"
        assert MemoryLayer.TEAM.value == "team"
        assert MemoryLayer.GLOBAL.value == "global"
    
    def test_memory_entry_creation(self):
        """Test MemoryEntry dataclass."""
        entry = MemoryEntry(
            key="test_key",
            value={"data": "test"},
            layer=MemoryLayer.PROJECT
        )
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.layer == MemoryLayer.PROJECT
        assert entry.version == 1
    
    @pytest.mark.asyncio
    async def test_byterover_client_save_and_get(self):
        """Test ByteRover client save and get operations."""
        client = ByteRoverClient(api_key="test_key")
        
        # Save
        entry = await client.save(
            key="test_key",
            value={"test": "data"},
            layer=MemoryLayer.PROJECT
        )
        assert entry.key == "test_key"
        
        # Get
        retrieved = await client.get("test_key")
        assert retrieved is not None
        assert retrieved.value == {"test": "data"}


class TestMemoryManager:
    """Tests for Memory Manager."""
    
    def test_agent_expertise_creation(self):
        """Test AgentExpertise dataclass."""
        expertise = AgentExpertise(
            agent_id="synthia_queen_white",
            domain="code_generation",
            problem="Build API endpoint",
            approach="Used FastAPI with async handlers",
            result="Successfully deployed",
            success_rate=0.95
        )
        assert expertise.agent_id == "synthia_queen_white"
        assert expertise.domain == "code_generation"
        assert expertise.success_rate == 0.95


class TestOAuthServer:
    """Tests for OAuth 2.0 Server."""
    
    def test_register_client(self):
        """Test client registration."""
        server = OAuthServer()
        client = server.register_client(
            name="Test App",
            redirect_uris=["http://localhost:3000/callback"]
        )
        
        assert client.name == "Test App"
        assert client.client_id.startswith("archonx_")
        assert "http://localhost:3000/callback" in client.redirect_uris
    
    def test_authorization_url(self):
        """Test authorization URL generation."""
        server = OAuthServer()
        client = server.register_client(
            name="Test App",
            redirect_uris=["http://localhost:3000/callback"]
        )
        
        url = server.get_authorization_url(client, "http://localhost:3000/callback")
        assert "authorize" in url
        assert "response_type=code" in url
        assert client.client_id in url
    
    def test_client_credentials_flow(self):
        """Test client credentials flow."""
        server = OAuthServer()
        client = server.register_client(
            name="Test Service",
            redirect_uris=[],
            is_confidential=True
        )
        
        token = server.client_credentials_flow(client)
        assert token.access_token is not None
        assert token.token_type == "Bearer"


class TestSessionManager:
    """Tests for Session Manager."""
    
    def test_create_session(self):
        """Test session creation."""
        manager = SessionManager()
        user = User(
            user_id="user_001",
            email="test@example.com",
            name="Test User"
        )
        
        session = manager.create_session(
            user=user,
            access_token="test_token"
        )
        
        assert session.session_id is not None
        assert session.user.user_id == "user_001"
    
    def test_get_session(self):
        """Test session retrieval."""
        manager = SessionManager()
        user = User(
            user_id="user_001",
            email="test@example.com",
            name="Test User"
        )
        
        session = manager.create_session(
            user=user,
            access_token="test_token"
        )
        
        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.user.user_id == "user_001"


class TestRBACManager:
    """Tests for RBAC Manager."""
    
    def test_assign_role(self):
        """Test role assignment."""
        rbac = RBACManager()
        user_role = rbac.assign_role("user_001", Role.WHITE_QUEEN)
        
        assert user_role.user_id == "user_001"
        assert user_role.role == Role.WHITE_QUEEN
    
    def test_has_permission(self):
        """Test permission checking."""
        rbac = RBACManager()
        rbac.assign_role("user_001", Role.WHITE_QUEEN)
        
        # White Queen should have task write permission
        assert rbac.has_permission("user_001", Permission.TASK_WRITE)
        
        # White Queen should not have admin permission
        assert not rbac.has_permission("user_001", Permission.ADMIN_SYSTEM)
    
    def test_admin_has_all_permissions(self):
        """Test admin has all permissions."""
        rbac = RBACManager()
        rbac.assign_role("admin_001", Role.ADMIN)
        
        for permission in Permission:
            assert rbac.has_permission("admin_001", permission)


class TestAgentMailServer:
    """Tests for Agent Mail Server."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = AgentMessage(
            id="mail-000001",
            sender="synthia_queen_white",
            recipient="pauli_king_white",
            message_type=MessageType.REQUEST,
            subject="Test Message",
            payload={"text": "Hello!"}
        )
        
        assert message.sender == "synthia_queen_white"
        assert message.recipient == "pauli_king_white"
        assert message.message_type == MessageType.REQUEST
    
    def test_message_to_dict(self):
        """Test message serialization."""
        message = AgentMessage(
            id="mail-000001",
            sender="synthia_queen_white",
            recipient="pauli_king_white",
            message_type=MessageType.REQUEST,
            subject="Test Message"
        )
        
        data = message.to_dict()
        assert data["sender"] == "synthia_queen_white"
        assert data["message_type"] == "request"


class TestTaskManager:
    """Tests for Task Manager."""
    
    def test_create_task(self):
        """Test task creation."""
        manager = TaskManager()
        task = manager.create_task(
            title="Test Task",
            description="Test description",
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "Test Task"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
    
    def test_assign_task(self):
        """Test task assignment."""
        manager = TaskManager()
        task = manager.create_task(title="Test Task")
        
        updated = manager.assign_task(task.id, "synthia_queen_white")
        assert updated.assigned_agent == "synthia_queen_white"
    
    def test_advance_stage(self):
        """Test Ralphy loop stage advancement."""
        manager = TaskManager()
        task = manager.create_task(title="Test Task")
        
        # Initial stage is PLAN
        assert task.current_stage == "PLAN"
        
        # Advance to IMPLEMENT
        updated = manager.advance_stage(task.id)
        assert updated.current_stage == "IMPLEMENT"


class TestOrchestrator:
    """Tests for Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_create_task_command(self):
        """Test CREATE command."""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        result = await orchestrator.create_task(
            title="Build API",
            task_type=TaskType.CODE
        )
        
        assert result.success
        assert result.command == OrchestratorCommand.CREATE
        assert "task_id" in result.data
    
    @pytest.mark.asyncio
    async def test_status_command(self):
        """Test STATUS command."""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        result = await orchestrator.get_status()
        
        assert result.success
        assert "agents" in result.data
        assert "tasks" in result.data
    
    @pytest.mark.asyncio
    async def test_list_command(self):
        """Test LIST command."""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        # Create a task first
        await orchestrator.create_task(title="Test Task")
        
        result = await orchestrator.list_tasks()
        
        assert result.success
        assert "tasks" in result.data


class TestKPIDashboard:
    """Tests for KPI Dashboard."""
    
    def test_initialize_agent(self):
        """Test agent initialization."""
        dashboard = KPIDashboard()
        metrics = dashboard.initialize_agent(
            agent_id="synthia_queen_white",
            agent_name="Synthia",
            crew="white",
            role="queen"
        )
        
        assert metrics.agent_id == "synthia_queen_white"
        assert metrics.agent_name == "Synthia"
    
    def test_record_task(self):
        """Test task recording."""
        dashboard = KPIDashboard()
        dashboard.initialize_agent(
            agent_id="synthia_queen_white",
            agent_name="Synthia",
            crew="white",
            role="queen"
        )
        
        dashboard.record_task(
            agent_id="synthia_queen_white",
            task_id="task-000001",
            success=True,
            duration=120.5,
            revenue=500.0
        )
        
        metrics = dashboard.get_agent_metrics("synthia_queen_white")
        assert metrics.tasks_completed == 1
        assert metrics.revenue_generated == 500.0
    
    def test_generate_report(self):
        """Test report generation."""
        dashboard = KPIDashboard()
        dashboard.initialize_agent(
            agent_id="synthia_queen_white",
            agent_name="Synthia",
            crew="white",
            role="queen"
        )
        
        report = dashboard.generate_report()
        
        assert "summary" in report
        assert "top_performers" in report
        assert "crew_performance" in report


class TestRevenueGoal:
    """Tests for Revenue Goal tracking."""
    
    def test_progress_percentage(self):
        """Test progress calculation."""
        goal = RevenueGoal(current_amount=25_000_000)
        assert goal.progress_percentage == 25.0
    
    def test_add_revenue(self):
        """Test revenue addition."""
        goal = RevenueGoal(current_amount=0)
        
        milestones = goal.add_revenue(1_000_000)
        
        assert goal.current_amount == 1_000_000
        assert len(milestones) == 1
        assert milestones[0]["name"] == "First Million"


class TestRevenueEngine:
    """Tests for Revenue Engine."""
    
    def test_create_lead(self):
        """Test lead creation."""
        engine = RevenueEngine()
        lead = engine.create_lead(
            company_name="Acme Corp",
            contact_name="John Doe",
            contact_email="john@acme.com",
            source=LeadSource.WEBSITE,
            estimated_value=50000
        )
        
        assert lead.company_name == "Acme Corp"
        assert lead.estimated_value == 50000
    
    def test_update_lead_status(self):
        """Test lead status update."""
        engine = RevenueEngine()
        lead = engine.create_lead(
            company_name="Acme Corp",
            contact_name="John Doe",
            contact_email="john@acme.com",
            source=LeadSource.WEBSITE
        )
        
        updated = engine.update_lead(lead.lead_id, LeadStatus.QUALIFIED)
        
        assert updated.status == LeadStatus.QUALIFIED
        assert updated.probability == 0.4  # Auto-set for QUALIFIED
    
    def test_get_revenue_progress(self):
        """Test revenue progress."""
        engine = RevenueEngine()
        progress = engine.get_revenue_progress()
        
        assert "target" in progress
        assert "current" in progress
        assert progress["target"] == 100_000_000


class TestPAULIWHEELSync:
    """Tests for PAULIWHEEL Sync."""
    
    @pytest.mark.asyncio
    async def test_run_meeting(self):
        """Test sync meeting execution."""
        sync = PAULIWHEELSync()
        result = await sync.run_meeting()
        
        assert result.meeting_id is not None
        assert result.eco_prompt_version is not None
        assert result.toolbox_version is not None


class TestDailySelfImprovement:
    """Tests for Daily Self-Improvement."""
    
    def test_register_task(self):
        """Test task registration."""
        improvement = DailySelfImprovement()
        
        task = improvement.register_task(
            task_id="custom_task",
            name="Custom Task",
            description="A custom automated task",
            frequency="daily",
            handler=lambda: {"status": "ok"}
        )
        
        assert task.task_id == "custom_task"
        assert task.name == "Custom Task"
    
    def test_get_task_status(self):
        """Test task status retrieval."""
        improvement = DailySelfImprovement()
        status = improvement.get_task_status()
        
        assert "running" in status
        assert "tasks" in status
        assert "sync_schedule" in status


# Integration Tests

class TestIntegration:
    """Integration tests for the complete framework."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from lead to revenue."""
        # Initialize components
        engine = RevenueEngine()
        dashboard = KPIDashboard()
        orchestrator = Orchestrator()
        
        await orchestrator.initialize()
        
        # Create lead
        lead = engine.create_lead(
            company_name="Test Corp",
            contact_name="Jane Doe",
            contact_email="jane@test.com",
            source=LeadSource.WEBSITE,
            estimated_value=10000
        )
        
        # Update lead through pipeline
        engine.update_lead(lead.lead_id, LeadStatus.CONTACTED)
        engine.update_lead(lead.lead_id, LeadStatus.QUALIFIED)
        engine.update_lead(lead.lead_id, LeadStatus.PROPOSAL)
        engine.update_lead(lead.lead_id, LeadStatus.WON)
        
        # Convert to client
        client = engine.convert_lead(lead.lead_id)
        assert client is not None
        
        # Create orchestrator task
        task_result = await orchestrator.create_task(
            title="Onboard Test Corp",
            task_type=TaskType.INTEGRATION
        )
        assert task_result.success
        
        # Record revenue
        dashboard.initialize_agent(
            agent_id="orchestrator",
            agent_name="Orchestrator",
            crew="white",
            role="king"
        )
        
        dashboard.record_task(
            agent_id="orchestrator",
            task_id=task_result.data["task_id"],
            success=True,
            duration=300.0,
            revenue=10000.0
        )
        
        # Verify revenue progress
        progress = engine.get_revenue_progress()
        assert progress["current"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
