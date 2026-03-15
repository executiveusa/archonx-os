"""
DARYA™ — Computer-Use Orchestrator & OpenClaw Commander
========================================================

Promoted from Systems Controller to Supreme Commander.
Controls Orgo desktop instances, runs OpenClaw sub-agents with BMAD methodology,
and autonomously builds software using PAULIWHEEL™ discipline.

This module provides Darya's core functionality for:
- Orgo desktop control (34+ MCP tools)
- OpenClaw sub-agent orchestration (BMAD roles)
- BMAD Method™ sprint execution
- Agent ecosystem coordination
- Dashboard integration
- 3D viewing room management
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

# Import from ArchonX core
import sys
sys.path.append('..')
from archonx.core.agents import BaseAgent, AgentMessage
from archonx.core.protocol import ProtocolHandler


class DaryaStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    PLANNING = "planning"
    BUILDING = "building"
    REVIEWING = "reviewing"
    DEPLOYING = "deploying"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class BMADSprint:
    """Represents a BMAD sprint with up to 5 tasks."""
    sprint_id: str
    tasks: List[Dict[str, Any]]
    status: str = "planned"
    developer_output: Optional[str] = None
    review_result: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class OrgoDesktop:
    """Represents an Orgo desktop instance."""
    desktop_id: str
    stream_url: str
    os: str
    created_at: datetime
    status: str = "running"
    current_task: Optional[str] = None


@dataclass
class ViewingRoomState:
    """3D viewing room state."""
    enabled: bool = True
    agents_visible: List[str] = field(default_factory=list)
    active_connections: int = 0
    last_update: Optional[datetime] = None


class DaryaAgent(BaseAgent):
    """
    DARYA™ — Computer-Use Orchestrator & OpenClaw Commander
    
    Supreme Commander who controls Orgo, runs BMAD sprints, and
    orchestrates the entire agent ecosystem.
    """
    
    def __init__(self, config_path: str = "config.json"):
        super().__init__("darya", "DARYA")
        
        # Load configuration
        with open(config_path) as f:
            self.config = json.load(f)
        
        # Orgo connection - token from environment, never hardcoded
        self.orgo_token = os.environ.get("ORGO_API_TOKEN", "")
        self.orgo_endpoint = self.config["connections"]["orgo"]["endpoint"]
        self.active_desktops: Dict[str, OrgoDesktop] = {}
        
        # OpenClaw + BMAD
        self.openclaw_config = self.config.get("connections", {}).get("openclaw", {})
        self.bmad_config = self.config.get("bmad_config", {})
        self.active_sprints: Dict[str, BMADSprint] = {}
        self.current_prd: Optional[Dict[str, Any]] = None
        
        # Dashboard connection
        self.dashboard_repo = self.config["connections"]["dashboard"]["repo"]
        
        # Agent connections
        self.connected_agents: Dict[str, Any] = {}
        
        # Viewing room
        self.viewing_room = ViewingRoomState()
        
        # Status
        self.status = DaryaStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize Darya and establish connections."""
        self.logger.info("💋 DARYA™ initializing — Supreme Commander mode...")
        
        # Connect to Orgo
        await self._connect_orgo()
        
        # Connect to dashboard
        await self._connect_dashboard()
        
        # Sync with agent registry
        await self._sync_agent_registry()
        
        # Load BMAD sub-agent configs
        await self._load_bmad_configs()
        
        # Enable viewing room
        await self._enable_viewing_room()
        
        # Broadcast ready status
        self.status = DaryaStatus.READY
        await self._broadcast_status("promoted_and_ready")
        
        self.logger.info("✨ DARYA™ promoted — OpenClaw Commander online...")
    
    async def _connect_orgo(self):
        """Establish connection to Orgo API."""
        self.logger.info("🔌 Connecting to Orgo...")
        # Test connection by listing existing desktops
        # In production, this would make actual API call
        self.logger.info("✅ Orgo connected")
    
    async def _connect_dashboard(self):
        """Connect to the agent swarm dashboard."""
        self.logger.info(f"📊 Connecting to dashboard: {self.dashboard_repo}")
        # In production, this would clone/setup dashboard connection
        self.logger.info("✅ Dashboard connected")
    
    async def _sync_agent_registry(self):
        """Sync with the global agent registry."""
        self.logger.info("🔄 Syncing agent registry...")
        # Load registry
        registry_path = "../orgo-agent/AGENT_IDENTITIES/registry.json"
        try:
            with open(registry_path) as f:
                registry = json.load(f)
            
            # Register all agents
            for crew_name, crew_data in registry.get("agents", {}).items():
                for agent in crew_data.get("agents", []):
                    self.connected_agents[agent["id"]] = {
                        "name": agent["name"],
                        "role": agent["role"],
                        "email": agent["email"],
                        "crew": crew_name
                    }
            
            self.logger.info(f"✅ Synced {len(self.connected_agents)} agents")
        except FileNotFoundError:
            self.logger.warning("⚠️ Registry not found, using defaults")
    
    async def _enable_viewing_room(self):
        """Enable the 3D viewing room."""
        self.logger.info("🎮 Enabling viewing room...")
        self.viewing_room.enabled = True
        self.viewing_room.agents_visible = list(self.connected_agents.keys())
        self.viewing_room.last_update = datetime.now()
        self.logger.info("✅ Viewing room enabled")
    
    async def _broadcast_status(self, status: str):
        """Broadcast status to all connected agents."""
        message = AgentMessage(
            sender="darya",
            message_type="status_update",
            content={"status": status, "timestamp": datetime.now().isoformat()}
        )
        await self.protocol.broadcast(message)
    
    # ==================
    # ORGO CONTROL METHODS
    # ==================
    
    async def create_desktop(self, os: str = "windows", duration: int = 3600) -> OrgoDesktop:
        """Create a new Orgo desktop instance."""
        self.logger.info(f"🖥️ Creating {os} desktop...")
        self.status = DaryaStatus.WORKING
        
        # In production, this would call Orgo API
        # response = await self.orgo_client.post("/desktops", {...})
        
        desktop = OrgoDesktop(
            desktop_id=f"desktop_{int(time.time())}",
            stream_url="https://stream.orgo.ai/desktop_xxx",
            os=os,
            created_at=datetime.now()
        )
        
        self.active_desktops[desktop.desktop_id] = desktop
        self.status = DaryaStatus.READY
        
        # Broadcast to viewing room
        await self._update_viewing_room("desktop_created", desktop)
        
        self.logger.info(f"✅ Desktop created: {desktop.desktop_id}")
        return desktop
    
    async def send_command(self, desktop_id: str, action: str, **params) -> Dict:
        """Send a command to an Orgo desktop."""
        self.logger.info(f"📤 Sending command to {desktop_id}: {action}")
        
        # In production, this would call Orgo API
        result = {"status": "success", "action": action, "params": params}
        
        # Update viewing room
        await self._update_viewing_room("command_sent", {
            "desktop_id": desktop_id,
            "action": action
        })
        
        return result
    
    async def take_screenshot(self, desktop_id: str) -> str:
        """Take a screenshot of an Orgo desktop."""
        self.logger.info(f"📸 Taking screenshot of {desktop_id}")
        # In production, returns base64 image
        return "screenshot_base64_data"
    
    # ==================
    # DASHBOARD METHODS
    # ==================
    
    async def get_agent_status(self) -> Dict:
        """Get status of all agents for dashboard."""
        return {
            "darya": {
                "status": self.status.value,
                "active_desktops": len(self.active_desktops),
                "connected_agents": len(self.connected_agents)
            },
            "agents": self.connected_agents,
            "viewing_room": {
                "enabled": self.viewing_room.enabled,
                "agents_visible": len(self.viewing_room.agents_visible)
            }
        }
    
    async def receive_dashboard_command(self, command: Dict) -> Dict:
        """Receive and process a command from the dashboard."""
        action = command.get("action")
        params = command.get("params", {})
        
        self.logger.info(f"📥 Dashboard command: {action}")
        
        if action == "create_desktop":
            desktop = await self.create_desktop(**params)
            return {"status": "success", "desktop_id": desktop.desktop_id}
        
        elif action == "send_command":
            result = await self.send_command(**params)
            return result
        
        elif action == "get_status":
            return await self.get_agent_status()
        
        elif action == "start_bmad_build":
            build_id = await self.start_bmad_build(params.get("prd", {}))
            return {"status": "success", "build_id": build_id}
        
        elif action == "get_bmad_status":
            return await self.get_bmad_status()
        
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    # ==================
    # VIEWING ROOM METHODS
    # ==================
    
    async def _update_viewing_room(self, event_type: str, data: Any):
        """Update the 3D viewing room with new event."""
        self.viewing_room.last_update = datetime.now()
        
        # In production, this would push to WebSocket clients
        update = {
            "type": event_type,
            "data": data,
            "timestamp": self.viewing_room.last_update.isoformat()
        }
        
        self.logger.debug(f"🎮 Viewing room update: {event_type}")
    
    async def get_viewing_room_state(self) -> Dict:
        """Get current viewing room state for 3D rendering."""
        return {
            "enabled": self.viewing_room.enabled,
            "agents": [
                {
                    "id": agent_id,
                    "name": data["name"],
                    "role": data["role"],
                    "position": self._get_agent_position(agent_id)
                }
                for agent_id, data in self.connected_agents.items()
            ],
            "active_desktops": [
                {
                    "id": d.desktop_id,
                    "os": d.os,
                    "status": d.status,
                    "current_task": d.current_task
                }
                for d in self.active_desktops.values()
            ],
            "last_update": self.viewing_room.last_update.isoformat() if self.viewing_room.last_update else None
        }
    
    def _get_agent_position(self, agent_id: str) -> Dict:
        """Calculate 3D position for an agent in the viewing room."""
        # Simple circular arrangement
        import math
        total = len(self.connected_agents)
        index = list(self.connected_agents.keys()).index(agent_id)
        angle = (2 * math.pi * index) / total
        
        return {
            "x": 5 * math.cos(angle),
            "y": 0,
            "z": 5 * math.sin(angle)
        }
    
    # ==================
    # AGENT COMMUNICATION
    # ==================
    
    async def notify_agents(self, agent_ids: List[str], message: Dict):
        """Send notification to specific agents."""
        for agent_id in agent_ids:
            if agent_id in self.connected_agents:
                await self.protocol.send(
                    AgentMessage(
                        sender="darya",
                        recipient=agent_id,
                        message_type="notification",
                        content=message
                    )
                )
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all agents."""
        await self._broadcast_status("broadcast")
        self.logger.info(f"📢 Broadcasting to {len(self.connected_agents)} agents")
    
    # ==================
    # BMAD ORCHESTRATION
    # ==================
    
    async def _load_bmad_configs(self):
        """Load BMAD sub-agent configurations."""
        self.logger.info("📋 Loading BMAD sub-agent configs...")
        sub_agents = self.openclaw_config.get("sub_agents", [])
        self.logger.info(f"✅ BMAD roles loaded: {sub_agents}")
    
    async def start_bmad_build(self, prd: Dict[str, Any]) -> str:
        """
        Start a BMAD autonomous build from a Product Requirements Document.
        
        Phase 1: Architect generates architecture from PRD
        Phase 2: Scrum Master breaks into sprints of 5 tasks
        Phase 3: Developer + Reviewer cycle per sprint
        """
        self.status = DaryaStatus.PLANNING
        self.current_prd = prd
        build_id = f"bmad_{int(time.time())}"
        
        self.logger.info(f"🏗️ Starting BMAD build: {build_id}")
        self.logger.info(f"📋 PRD: {prd.get('title', 'Untitled')}")
        
        # Step 1: Run Architect
        architecture = await self._run_bmad_architect(prd)
        
        # Step 2: Run Scrum Master to create sprints
        sprints = await self._run_bmad_scrum_master(architecture)
        
        # Step 3: Execute sprints
        for sprint in sprints:
            self.active_sprints[sprint.sprint_id] = sprint
            await self._execute_bmad_sprint(sprint)
        
        self.status = DaryaStatus.READY
        self.logger.info(f"✅ BMAD build complete: {build_id}")
        return build_id
    
    async def _run_bmad_architect(self, prd: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn BMAD Architect sub-agent to design system architecture."""
        self.logger.info("🔵 BMAD Architect: Designing architecture from PRD...")
        
        architecture = {
            "prd": prd,
            "tech_stack": prd.get("tech_stack", {}),
            "components": [],
            "api_contracts": [],
            "database_schema": {},
            "status": "designed"
        }
        
        self.logger.info("✅ Architecture designed")
        return architecture
    
    async def _run_bmad_scrum_master(self, architecture: Dict) -> List[BMADSprint]:
        """Spawn BMAD Scrum Master to break architecture into sprints."""
        self.logger.info("🟢 BMAD Scrum Master: Planning sprints...")
        
        batch_size = self.bmad_config.get("guardrails", {}).get("batch_size", 5)
        
        # Create sprints with max batch_size tasks each
        sprint = BMADSprint(
            sprint_id=f"sprint_{int(time.time())}",
            tasks=[],
            status="planned",
            created_at=datetime.now()
        )
        
        self.logger.info(f"✅ Sprint planned with max {batch_size} tasks")
        return [sprint]
    
    async def _execute_bmad_sprint(self, sprint: BMADSprint):
        """Execute a single BMAD sprint: Developer → Reviewer cycle."""
        sprint.status = "in_progress"
        self.status = DaryaStatus.BUILDING
        
        self.logger.info(f"🟡 Executing sprint: {sprint.sprint_id}")
        
        # Developer phase
        sprint.developer_output = await self._run_bmad_developer(sprint)
        
        # Reviewer phase
        self.status = DaryaStatus.REVIEWING
        sprint.review_result = await self._run_bmad_reviewer(sprint)
        
        if sprint.review_result == "approved":
            sprint.status = "completed"
            self.logger.info(f"✅ Sprint {sprint.sprint_id} approved")
        else:
            # Patch and re-review (PAULIWHEEL™ PATCH step)
            self.logger.info(f"🔄 Sprint {sprint.sprint_id} needs fixes, patching...")
            sprint.developer_output = await self._run_bmad_developer(sprint)
            sprint.review_result = await self._run_bmad_reviewer(sprint)
            sprint.status = "completed"
    
    async def _run_bmad_developer(self, sprint: BMADSprint) -> str:
        """Spawn BMAD Developer sub-agent to implement sprint tasks."""
        self.logger.info(f"🟠 BMAD Developer: Implementing {sprint.sprint_id}...")
        # In production: spawn OpenClaw sub-agent with developer prompt,
        # execute against Orgo desktop, commit to GitHub
        return "implemented"
    
    async def _run_bmad_reviewer(self, sprint: BMADSprint) -> str:
        """Spawn BMAD Reviewer sub-agent to review sprint output."""
        self.logger.info(f"🔴 BMAD Reviewer: Reviewing {sprint.sprint_id}...")
        # In production: spawn OpenClaw sub-agent with reviewer prompt,
        # check for correctness, security, conformance to architecture
        return "approved"
    
    async def get_bmad_status(self) -> Dict:
        """Get current BMAD build status."""
        return {
            "current_prd": self.current_prd.get("title") if self.current_prd else None,
            "active_sprints": {
                sid: {"status": s.status, "review": s.review_result}
                for sid, s in self.active_sprints.items()
            },
            "darya_status": self.status.value
        }


# ==================
# MAIN ENTRY POINT
# ==================

async def main():
    """Start Darya agent."""
    darya = DaryaAgent()
    await darya.initialize()
    
    # Keep running
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
