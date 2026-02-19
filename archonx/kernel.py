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

    @classmethod
    def from_file(cls, path: Path = CONFIG_PATH) -> "KernelConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        proto = data.get("protocol", {})
        oc = data.get("openclaw", {})
        return cls(
            raw=data,
            protocol_min_depth=proto.get("min_depth", 5),
            protocol_preferred_depth=proto.get("preferred_depth", 10),
            confidence_threshold=proto.get("confidence_threshold", 0.7),
            gateway_port=oc.get("gateway_port", 18789),
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
        self._booted = True
        logger.info("Kernel boot complete — 64 agents online.")

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("Shutting down ArchonX Kernel…")
        await self.white_crew.shutdown()
        await self.black_crew.shutdown()
        self.paulis_place.cancel_all()
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
