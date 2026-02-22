"""
ArchonX Kernel
==============
Central orchestrator for the 64-agent swarm.
Boots both crews, loads config, and manages the agent lifecycle.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from archonx.core.agents import AgentRegistry, build_all_agents
from archonx.core.protocol import BobbyFischerProtocol
from archonx.core.tyrone_protocol import TyroneProtocol, enforce_four_pillars
from archonx.crews.white_crew import WhiteCrew
from archonx.crews.black_crew import BlackCrew
from archonx.meetings.paulis_place import PaulisPlaceManager
from archonx.tools.base import ToolRegistry
from archonx.tools.fixer import FixerAgentTool
from archonx.tools.browser_test import BrowserTestTool
from archonx.tools.deploy import DeploymentTool
from archonx.tools.analytics import AnalyticsTool
from archonx.tools.computer_use import ComputerUseTool
from archonx.tools.remotion import RemotionTool
from archonx.tools.grep_mcp import GrepMCPTool
from archonx.skills.registry import SkillRegistry
from archonx.core.chess_reasoning import CollaborativeMatch
from archonx.core.flywheel import FlywheelEngine
from archonx.core.agent_mail import AgentMailbox
from archonx.core.self_build import SelfBuildDirective
from archonx.core.brenner_protocol import BrennerProtocol
from archonx.visualization.agent_theater import AgentTheater
from archonx.billing.token_meter import TokenMeter

# --- New modules (BEAD-009) ---
from archonx.auth.oauth_server import OAuthServer
from archonx.auth.session_manager import SessionManager
from archonx.auth.rbac import RBACManager
from archonx.mail.server import AgentMailServer
from archonx.beads.viewer import TaskManager, RobotTriage
from archonx.orchestration.orchestrator import Orchestrator
from archonx.kpis.dashboard import KPIDashboard
from archonx.automation.self_improvement import DailySelfImprovement
from archonx.revenue.engine import RevenueEngine
from archonx.memory.memory_manager import MemoryManager

# --- Security modules (Sprint 1-3) ---
from archonx.security.safety_layer import SafetyLayer
from archonx.security.leak_detector import LeakDetector
from archonx.security.cost_guard import CostGuard, CostBudget
from archonx.security.tool_gating import ToolGatekeeper
from archonx.security.command_guard import CommandGuard
from archonx.security.workspace_scope import WorkspaceScope
from archonx.security.sandbox_policy import SandboxEnforcer
from archonx.security.network_guard import NetworkGuard
from archonx.security.env_scrubber import EnvScrubber

# --- Sprint 4 modules ---
from archonx.core.memory_sqlite import SQLiteMemory
from archonx.core.agent_identity import AgentIdentityManager

logger = logging.getLogger("archonx.kernel")

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "archonx-config.json"


@dataclass
class KernelConfig:
    """Parsed archonx-config.json."""

    raw: dict[str, Any] = field(default_factory=dict)

    # Protocol
    protocol_min_depth: int = 5
    protocol_preferred_depth: int = 10
    confidence_threshold: float = 0.7

    # OpenClaw
    gateway_port: int = 18789

    # Feature flags
    enable_theater: bool = True
    enable_revenue_engine: bool = True
    enable_mail_server: bool = True
    enable_self_improvement: bool = True
    enable_memory_sqlite: bool = True
    enable_agent_identity: bool = True

    # Security
    security_enabled: bool = True
    cost_guard_enabled: bool = True
    command_guard_allowlist_mode: bool = False

    # Memory
    memory_backend: str = "sqlite"
    sqlite_path: str = "data/archonx_memory.db"

    @classmethod
    def from_file(cls, path: Path = CONFIG_PATH) -> "KernelConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        proto = data.get("protocol", {})
        oc = data.get("integration", {}).get("openclaw", {})
        features = data.get("features", {})
        security = data.get("security", {})
        cost = data.get("cost_guard", {})
        memory = data.get("memory", {})
        return cls(
            raw=data,
            protocol_min_depth=proto.get("min_depth", 5),
            protocol_preferred_depth=proto.get("preferred_depth", 10),
            confidence_threshold=proto.get("confidence_threshold", 0.7),
            gateway_port=oc.get("gateway_port", 18789),
            enable_theater=features.get("enable_theater", True),
            enable_revenue_engine=features.get("enable_revenue_engine", True),
            enable_mail_server=features.get("enable_mail_server", True),
            enable_self_improvement=features.get("enable_self_improvement", True),
            enable_memory_sqlite=features.get("enable_memory_sqlite", True),
            enable_agent_identity=features.get("enable_agent_identity", True),
            security_enabled=bool(security),
            cost_guard_enabled=cost.get("enabled", True),
            command_guard_allowlist_mode=security.get("command_guard", {}).get("allowlist_mode", False),
            memory_backend=memory.get("backend", "sqlite"),
            sqlite_path=memory.get("sqlite_path", "data/archonx_memory.db"),
        )


class ArchonXKernel:
    """
    The ArchonX operating system kernel.

    Responsibilities:
    - Boot the 64-agent swarm (White + Black crews)
    - Enforce the Bobby Fischer protocol on all decisions
    - Manage Pauli's Place daily meeting schedule
    - Provide the single entry-point for task execution
    """

    def __init__(self, config: KernelConfig | None = None) -> None:
        self.config = config or KernelConfig.from_file()
        self.protocol = BobbyFischerProtocol(
            min_depth=self.config.protocol_min_depth,
            preferred_depth=self.config.protocol_preferred_depth,
            confidence_threshold=self.config.confidence_threshold,
        )
        
        # TYRONE DAVIS PROTOCOL - FOUR PILLARS (IMMUTABLE)
        self.tyrone = TyroneProtocol()

        # Build agent registry
        self.registry = AgentRegistry()
        build_all_agents(self.registry)

        # Tool registry — all BaseTool implementations
        self.tools = ToolRegistry()
        self.tools.register(FixerAgentTool())
        self.tools.register(BrowserTestTool())
        self.tools.register(DeploymentTool())
        self.tools.register(AnalyticsTool())
        self.tools.register(ComputerUseTool())
        self.tools.register(RemotionTool())
        self.tools.register(GrepMCPTool())

        # Skill registry — auto-discover all BaseSkill subclasses
        self.skill_registry = SkillRegistry()
        self.skill_registry.auto_discover()

        # Flywheel — self-reinforcing improvement engine
        self.flywheel = FlywheelEngine()

        # Agent mail — inter-agent messaging
        self.mailbox = AgentMailbox()

        # Self-build directive — constitutional self-improvement
        self.self_build = SelfBuildDirective()

        # Brenner protocol — structured agent collaboration handshakes
        self.brenner = BrennerProtocol()

        # Crews
        self.white_crew = WhiteCrew(self.registry, self.tools, self.skill_registry)
        self.black_crew = BlackCrew(self.registry, self.tools, self.skill_registry)

        # Meetings
        self.paulis_place = PaulisPlaceManager()

        # Chess reasoning — collaborative match engine
        self.match_engine = CollaborativeMatch(self.white_crew, self.black_crew)

        # Agent Theater — "Watch Agent in Action"
        self.theater = AgentTheater()

        # Token billing
        self.billing = TokenMeter()

        # --- New subsystems (BEAD-009) ---
        # Authentication & SSO
        self.oauth_server = OAuthServer()
        self.session_manager = SessionManager()
        self.rbac = RBACManager()

        # Agent Mail WebSocket server (port 8765)
        self.mail_server = AgentMailServer(port=8765)

        # Task management
        self.task_manager = TaskManager()
        self.triage = RobotTriage(self.task_manager)

        # Orchestrator (wired to registry + task manager + mail)
        self.orchestrator = Orchestrator(
            registry=self.registry,
            task_manager=self.task_manager,
            mail_server=self.mail_server,
        )

        # KPI dashboard
        self.kpi_dashboard = KPIDashboard(registry=self.registry)

        # Revenue engine
        self.revenue_engine = RevenueEngine(kpi_dashboard=self.kpi_dashboard)

        # Memory manager
        self.memory_manager = MemoryManager()

        # --- Security subsystems (Sprint 1-3) ---
        if self.config.security_enabled:
            self.safety_layer = SafetyLayer()
            self.leak_detector = LeakDetector()
            self.command_guard = CommandGuard(
                allowlist_mode=self.config.command_guard_allowlist_mode,
            )
            self.workspace_scope: WorkspaceScope | None = None  # set per-session
            self.sandbox_enforcer = SandboxEnforcer()
            self.network_guard = NetworkGuard()
            self.env_scrubber = EnvScrubber()
            self.tool_gatekeeper = ToolGatekeeper()
            logger.info("Security subsystems initialized")
        else:
            self.safety_layer = None  # type: ignore[assignment]
            self.leak_detector = None  # type: ignore[assignment]
            self.command_guard = None  # type: ignore[assignment]
            self.workspace_scope = None
            self.sandbox_enforcer = None  # type: ignore[assignment]
            self.network_guard = None  # type: ignore[assignment]
            self.env_scrubber = None  # type: ignore[assignment]
            self.tool_gatekeeper = None  # type: ignore[assignment]

        if self.config.cost_guard_enabled:
            self.cost_guard = CostGuard()
        else:
            self.cost_guard = None  # type: ignore[assignment]

        # --- Feature-flagged subsystems (Sprint 4) ---
        if self.config.enable_memory_sqlite:
            self.sqlite_memory = SQLiteMemory(db_path=self.config.sqlite_path)
            logger.info("SQLite memory backend enabled (%s)", self.config.sqlite_path)
        else:
            self.sqlite_memory = None  # type: ignore[assignment]

        if self.config.enable_agent_identity:
            self.agent_identity = AgentIdentityManager()
            logger.info("Agent identity manager enabled")
        else:
            self.agent_identity = None  # type: ignore[assignment]

        # Daily self-improvement (3 AM tasks + PAULIWHEEL sync 3x/day)
        self.self_improvement = DailySelfImprovement(
            registry=self.registry,
            kpi_dashboard=self.kpi_dashboard,
            orchestrator=self.orchestrator,
        )

        self._booted = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def boot(self) -> None:
        """Initialize all subsystems."""
        logger.info("Booting ArchonX Kernel v%s (%s)", "0.1.0", "Daily at Pauli's")
        await self.white_crew.initialize()
        await self.black_crew.initialize()
        self.paulis_place.schedule_daily_meetings()

        # Initialize orchestrator (activates all 64 agents)
        await self.orchestrator.initialize()

        # Initialize KPI metrics for all agents
        for agent in self.registry.all():
            self.kpi_dashboard.initialize_agent(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                crew=agent.crew.value,
                role=agent.role.value,
            )

        # Start Agent Mail WebSocket server
        if self.config.enable_mail_server:
            try:
                await self.mail_server.start()
                logger.info("Agent Mail server started on port 8765")
            except Exception as exc:
                logger.warning("Agent Mail server failed to start: %s", exc)

        # Start daily self-improvement scheduler
        if self.config.enable_self_improvement:
            try:
                await self.self_improvement.start()
                logger.info("Self-improvement scheduler started")
            except Exception as exc:
                logger.warning("Self-improvement scheduler failed to start: %s", exc)

        # Initialize SQLite memory
        if self.sqlite_memory is not None:
            try:
                self.sqlite_memory.initialize()
                logger.info("SQLite memory initialized")
            except Exception as exc:
                logger.warning("SQLite memory failed to initialize: %s", exc)

        self._booted = True
        logger.info("Kernel boot complete — 64 agents online.")

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("Shutting down ArchonX Kernel…")

        # Stop new subsystems
        try:
            await self.self_improvement.stop()
        except Exception:
            pass
        try:
            await self.mail_server.stop()
        except Exception:
            pass

        await self.white_crew.shutdown()
        await self.black_crew.shutdown()
        self.paulis_place.cancel_all()

        # Cleanup auth
        self.oauth_server.cleanup_expired()
        self.session_manager.cleanup_expired()

        # Close SQLite memory
        if self.sqlite_memory is not None:
            self.sqlite_memory.close()

        self._booted = False
        logger.info("Kernel shutdown complete.")

    # ------------------------------------------------------------------
    # Task execution
    # ------------------------------------------------------------------

    async def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Top-level task execution entry-point.

        1. Applies Bobby Fischer protocol (depth calc, confidence check)
        2. Applies Tyrone Protocol (Four Pillars ethical alignment)
        3. Delegates to the appropriate crew
        4. Returns results with metrics
        """
        if not self._booted:
            raise RuntimeError("Kernel has not been booted. Call boot() first.")

        # Protocol check (Fischer - technical)
        decision = self.protocol.evaluate(task)
        if not decision.approved:
            return {
                "status": "rejected",
                "reason": decision.reason,
                "confidence": decision.confidence,
                "protocol": "fischer",
            }
        
        # Four Pillars check (Tyrone - ethical)
        decision_dict = {
            "confidence": decision.confidence,
            "depth": decision.depth,
            "rollback_plan": decision.rollback_plan,
            "reason": decision.reason,
        }
        pillars_approved, violations = enforce_four_pillars(task, decision_dict, self.tyrone)
        
        if not pillars_approved:
            return {
                "status": "rejected",
                "reason": "FOUR PILLARS VIOLATION - critical ethical constraints breached",
                "violations": [str(v) for v in violations],
                "confidence": decision.confidence,
                "protocol": "tyrone",
            }

        # Route to crew or collaborative match
        crew_name = task.get("crew", "white")

        if crew_name == "both":
            # Collaborative chess reasoning: both crews evaluate, merge result
            merged = await self.match_engine.play(task, decision)
            # Harvest flywheel improvements from merged result
            return {
                "status": "completed",
                "verdict": merged.verdict.value,
                "approach": merged.chosen_approach,
                "confidence": merged.confidence,
                "depth_analyzed": decision.depth,
                "merged_strengths": merged.merged_strengths,
                "remaining_risks": merged.mitigated_risks,
                "escalation_reason": merged.escalation_reason,
            }

        crew = self.white_crew if crew_name == "white" else self.black_crew
        result = await crew.execute(task, decision)

        return {
            "status": "completed",
            "result": result,
            "confidence": decision.confidence,
            "depth_analyzed": decision.depth,
        }
