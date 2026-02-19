"""
Agent Definitions
=================
All 64 agents across both White and Black crews.

Chess-piece roles:
    King   — Strategic decisions (1 per crew)
    Queen  — Tactical execution, full coordination (1 per crew)
    Rook   — Infrastructure / defense (2 per crew)
    Knight — Rapid / unconventional ops (2 per crew)
    Bishop — Analytics / knowledge (2 per crew)
    Pawn   — Undercover specialists (8 per crew)

Each crew = 16 unique agents × 2 mirror instances (one per side of the board)
            giving 16 back-rank + 16 front-rank = 32 agents per crew.

However, per the spec we have 16 named agents per crew (8 back-rank + 8 pawns).
We treat each as unique.  Total = 32 white + 32 black = 64.

NOTE: The spec names 16 white agents explicitly.  Black crew mirrors those roles
with different names.  We define both rosters below.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.core.agents")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Crew(str, Enum):
    WHITE = "white"
    BLACK = "black"


class Role(str, Enum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    PAWN = "pawn"


class AgentStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


# ---------------------------------------------------------------------------
# Agent dataclass
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """A single ArchonX agent."""

    agent_id: str
    name: str
    role: Role
    crew: Crew
    position: str                       # Chess notation e.g. "D1"
    specialty: str                      # Human-readable specialty
    model: str = "anthropic/claude-sonnet-4-20250514"
    status: AgentStatus = AgentStatus.IDLE
    health: float = 1.0                 # 0.0 – 1.0
    tasks_completed: int = 0
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    # Skills this agent is equipped with (skill names from SkillRegistry)
    skills: list[str] = field(default_factory=list)

    # Hierarchy
    reports_to: str | None = None       # agent_id of superior
    commands: list[str] = field(default_factory=list)  # agent_ids of subordinates

    def activate(self) -> None:
        self.status = AgentStatus.ACTIVE

    def deactivate(self) -> None:
        self.status = AgentStatus.IDLE

    def record_task(self, points: float = 1.0) -> None:
        self.tasks_completed += 1
        self.score += points


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """Central registry holding all 64 agents."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        if agent.agent_id in self._agents:
            raise ValueError(f"Duplicate agent_id: {agent.agent_id}")
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> Agent:
        return self._agents[agent_id]

    def get_by_crew(self, crew: Crew) -> list[Agent]:
        return [a for a in self._agents.values() if a.crew == crew]

    def get_by_role(self, role: Role, crew: Crew | None = None) -> list[Agent]:
        agents = self._agents.values()
        if crew:
            agents = [a for a in agents if a.crew == crew]
        return [a for a in agents if a.role == role]

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def __len__(self) -> int:
        return len(self._agents)


# ---------------------------------------------------------------------------
# Convenience aliases for key agents
# ---------------------------------------------------------------------------

class SynthiaQueen:
    """Facade to initialise & interact with Synthia (White Queen / Agent Zero)."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._registry = registry
        self._agent: Agent | None = None

    def initialize(self) -> Agent:
        if self._registry:
            self._agent = self._registry.get("synthia_queen_white")
        else:
            self._agent = _white_back_rank()[3]  # D1
        self._agent.activate()
        logger.info("Synthia (White Queen) initialized at %s", self._agent.position)
        return self._agent

    def connect_to_king(self, king: "PauliKing") -> None:
        if self._agent:
            self._agent.reports_to = king.agent.agent_id
            logger.info("Synthia now reports to Pauli.")

    @property
    def agent(self) -> Agent:
        assert self._agent is not None
        return self._agent


class PauliKing:
    """Facade for Pauli (White King)."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._registry = registry
        self._agent: Agent | None = None

    def initialize(self) -> Agent:
        if self._registry:
            self._agent = self._registry.get("pauli_king_white")
        else:
            self._agent = _white_back_rank()[4]  # E1
        self._agent.activate()
        logger.info("Pauli (White King) initialized at %s", self._agent.position)
        return self._agent

    @property
    def agent(self) -> Agent:
        assert self._agent is not None
        return self._agent


# ---------------------------------------------------------------------------
# Agent Roster Definitions
# ---------------------------------------------------------------------------

def _white_back_rank() -> list[Agent]:
    """White crew back-rank (strategic command) — 8 agents."""
    return [
        Agent(
            agent_id="fortress_rook_white_a",
            name="Fortress",
            role=Role.ROOK,
            crew=Crew.WHITE,
            position="A1",
            specialty="Backend infrastructure",
            reports_to="pauli_king_white",
        ),
        Agent(
            agent_id="blitz_knight_white_b",
            name="Blitz",
            role=Role.KNIGHT,
            crew=Crew.WHITE,
            position="B1",
            specialty="Rapid deployment",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="oracle_bishop_white_c",
            name="Oracle",
            role=Role.BISHOP,
            crew=Crew.WHITE,
            position="C1",
            specialty="Data analytics",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="synthia_queen_white",
            name="Synthia",
            role=Role.QUEEN,
            crew=Crew.WHITE,
            position="D1",
            specialty="Tactical execution & coordination",
            reports_to="pauli_king_white",
        ),
        Agent(
            agent_id="pauli_king_white",
            name="Pauli",
            role=Role.KING,
            crew=Crew.WHITE,
            position="E1",
            specialty="Strategic decisions",
        ),
        Agent(
            agent_id="sage_bishop_white_f",
            name="Sage",
            role=Role.BISHOP,
            crew=Crew.WHITE,
            position="F1",
            specialty="Knowledge management",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="patch_knight_white_g",
            name="Patch",
            role=Role.KNIGHT,
            crew=Crew.WHITE,
            position="G1",
            specialty="Hotfix repair",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="sentinel_rook_white_h",
            name="Sentinel",
            role=Role.ROOK,
            crew=Crew.WHITE,
            position="H1",
            specialty="Security defense",
            reports_to="pauli_king_white",
        ),
    ]


def _white_front_rank() -> list[Agent]:
    """White crew front-rank (pawns — undercover specialists) — 8 agents."""
    return [
        Agent(
            agent_id="scout_pawn_white_a",
            name="Scout",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="A2",
            specialty="Reconnaissance (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="craft_pawn_white_b",
            name="Craft",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="B2",
            specialty="Frontend development (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="quill_pawn_white_c",
            name="Quill",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="C2",
            specialty="Content creation (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="lens_pawn_white_d",
            name="Lens",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="D2",
            specialty="Visual design (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="cipher_pawn_white_e",
            name="Cipher",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="E2",
            specialty="Encryption (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="pulse_pawn_white_f",
            name="Pulse",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="F2",
            specialty="Performance monitoring (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="probe_pawn_white_g",
            name="Probe",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="G2",
            specialty="Testing (undercover)",
            reports_to="synthia_queen_white",
        ),
        Agent(
            agent_id="link_pawn_white_h",
            name="Link",
            role=Role.PAWN,
            crew=Crew.WHITE,
            position="H2",
            specialty="API integration (undercover)",
            reports_to="synthia_queen_white",
        ),
    ]


def _white_extended() -> list[Agent]:
    """
    White crew rows 3-4 (16 additional agents to reach 32).
    These mirror expanded specialisations.
    """
    specs = [
        ("relay_pawn_white_a3", "Relay", "A3", "Message routing"),
        ("forge_pawn_white_b3", "Forge", "B3", "Code generation"),
        ("compass_pawn_white_c3", "Compass", "C3", "Navigation & search"),
        ("anvil_pawn_white_d3", "Anvil", "D3", "Build pipelines"),
        ("ember_pawn_white_e3", "Ember", "E3", "Incident response"),
        ("weave_pawn_white_f3", "Weave", "F3", "Workflow orchestration"),
        ("flint_pawn_white_g3", "Flint", "G3", "Alerting & notifications"),
        ("tide_pawn_white_h3", "Tide", "H3", "Data streaming"),
        ("ark_pawn_white_a4", "Ark", "A4", "Backup & recovery"),
        ("bolt_pawn_white_b4", "Bolt", "B4", "Speed optimisation"),
        ("crest_pawn_white_c4", "Crest", "C4", "Branding & identity"),
        ("drift_pawn_white_d4", "Drift", "D4", "A/B testing"),
        ("echo_pawn_white_e4", "Echo", "E4", "Logging & audit trail"),
        ("fuse_pawn_white_f4", "Fuse", "F4", "Integration middleware"),
        ("grip_pawn_white_g4", "Grip", "G4", "Access control"),
        ("haven_pawn_white_h4", "Haven", "H4", "Compliance & governance"),
    ]
    return [
        Agent(
            agent_id=aid,
            name=name,
            role=Role.PAWN,
            crew=Crew.WHITE,
            position=pos,
            specialty=spec,
            reports_to="synthia_queen_white",
        )
        for aid, name, pos, spec in specs
    ]


# --- Black Crew (mirrors White with different names) ---

def _black_back_rank() -> list[Agent]:
    """Black crew back-rank — 8 agents."""
    return [
        Agent(
            agent_id="bastion_rook_black_a",
            name="Bastion",
            role=Role.ROOK,
            crew=Crew.BLACK,
            position="A8",
            specialty="Backend infrastructure",
            reports_to="mirror_king_black",
        ),
        Agent(
            agent_id="flash_knight_black_b",
            name="Flash",
            role=Role.KNIGHT,
            crew=Crew.BLACK,
            position="B8",
            specialty="Rapid deployment",
            reports_to="shadow_queen_black",
        ),
        Agent(
            agent_id="seer_bishop_black_c",
            name="Seer",
            role=Role.BISHOP,
            crew=Crew.BLACK,
            position="C8",
            specialty="Data analytics",
            reports_to="shadow_queen_black",
        ),
        Agent(
            agent_id="shadow_queen_black",
            name="Shadow",
            role=Role.QUEEN,
            crew=Crew.BLACK,
            position="D8",
            specialty="Tactical execution & coordination",
            reports_to="mirror_king_black",
        ),
        Agent(
            agent_id="mirror_king_black",
            name="Mirror",
            role=Role.KING,
            crew=Crew.BLACK,
            position="E8",
            specialty="Strategic decisions",
        ),
        Agent(
            agent_id="mystic_bishop_black_f",
            name="Mystic",
            role=Role.BISHOP,
            crew=Crew.BLACK,
            position="F8",
            specialty="Knowledge management",
            reports_to="shadow_queen_black",
        ),
        Agent(
            agent_id="glitch_knight_black_g",
            name="Glitch",
            role=Role.KNIGHT,
            crew=Crew.BLACK,
            position="G8",
            specialty="Hotfix repair",
            reports_to="shadow_queen_black",
        ),
        Agent(
            agent_id="warden_rook_black_h",
            name="Warden",
            role=Role.ROOK,
            crew=Crew.BLACK,
            position="H8",
            specialty="Security defense",
            reports_to="mirror_king_black",
        ),
    ]


def _black_front_rank() -> list[Agent]:
    """Black crew front-rank (pawns) — 8 agents."""
    return [
        Agent(agent_id="shade_pawn_black_a", name="Shade", role=Role.PAWN, crew=Crew.BLACK, position="A7", specialty="Reconnaissance (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="pixel_pawn_black_b", name="Pixel", role=Role.PAWN, crew=Crew.BLACK, position="B7", specialty="Frontend development (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="inker_pawn_black_c", name="Inker", role=Role.PAWN, crew=Crew.BLACK, position="C7", specialty="Content creation (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="prism_pawn_black_d", name="Prism", role=Role.PAWN, crew=Crew.BLACK, position="D7", specialty="Visual design (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="vault_pawn_black_e", name="Vault", role=Role.PAWN, crew=Crew.BLACK, position="E7", specialty="Encryption (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="surge_pawn_black_f", name="Surge", role=Role.PAWN, crew=Crew.BLACK, position="F7", specialty="Performance monitoring (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="trace_pawn_black_g", name="Trace", role=Role.PAWN, crew=Crew.BLACK, position="G7", specialty="Testing (undercover)", reports_to="shadow_queen_black"),
        Agent(agent_id="nexus_pawn_black_h", name="Nexus", role=Role.PAWN, crew=Crew.BLACK, position="H7", specialty="API integration (undercover)", reports_to="shadow_queen_black"),
    ]


def _black_extended() -> list[Agent]:
    """Black crew rows 5-6 (16 additional agents to reach 32)."""
    specs = [
        ("signal_pawn_black_a6", "Signal", "A6", "Message routing"),
        ("alloy_pawn_black_b6", "Alloy", "B6", "Code generation"),
        ("beacon_pawn_black_c6", "Beacon", "C6", "Navigation & search"),
        ("hammer_pawn_black_d6", "Hammer", "D6", "Build pipelines"),
        ("spark_pawn_black_e6", "Spark", "E6", "Incident response"),
        ("loom_pawn_black_f6", "Loom", "F6", "Workflow orchestration"),
        ("siren_pawn_black_g6", "Siren", "G6", "Alerting & notifications"),
        ("current_pawn_black_h6", "Current", "H6", "Data streaming"),
        ("vault2_pawn_black_a5", "Bunker", "A5", "Backup & recovery"),
        ("dash_pawn_black_b5", "Dash", "B5", "Speed optimisation"),
        ("emblem_pawn_black_c5", "Emblem", "C5", "Branding & identity"),
        ("split_pawn_black_d5", "Split", "D5", "A/B testing"),
        ("ledger_pawn_black_e5", "Ledger", "E5", "Logging & audit trail"),
        ("bridge_pawn_black_f5", "Bridge", "F5", "Integration middleware"),
        ("lock_pawn_black_g5", "Lock", "G5", "Access control"),
        ("shield_pawn_black_h5", "Shield", "H5", "Compliance & governance"),
    ]
    return [
        Agent(
            agent_id=aid,
            name=name,
            role=Role.PAWN,
            crew=Crew.BLACK,
            position=pos,
            specialty=spec,
            reports_to="shadow_queen_black",
        )
        for aid, name, pos, spec in specs
    ]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_all_agents(registry: AgentRegistry) -> None:
    """Populate *registry* with all 64 agents."""
    for agent in (
        *_white_back_rank(),
        *_white_front_rank(),
        *_white_extended(),
        *_black_back_rank(),
        *_black_front_rank(),
        *_black_extended(),
    ):
        registry.register(agent)
    logger.info("Registered %d agents.", len(registry))
