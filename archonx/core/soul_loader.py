"""
BEAD-SOUL-001 — Agent Soul Initialization System
=================================================
Reads all .soul.md files from .agent-souls/ on kernel boot.
Parses the markdown-style metadata header and body, builds a
SoulRegistry, and injects each soul into matching crew agents.

Soul files use markdown bold-key format:
    **ID:** pauli_king_white
    **Piece:** King
    **Crew:** WHITE (Offense)
    …
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.core.soul_loader")

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

VALID_CREWS = {"white", "black"}
VALID_PIECE_TYPES = {"king", "queen", "rook", "bishop", "knight", "pawn"}

_BOLD_KEY_RE = re.compile(r"^\*\*([^*]+)\*\*[:\s]+(.+)$")


@dataclass
class AgentSoul:
    """Parsed soul configuration for one agent."""

    agent_id: str
    role: str
    crew: str                              # "white" | "black"
    piece_type: str                        # "king" | "queen" | …
    voice_id: str | None = None
    voice_name: str | None = None
    model: str = "claude-3-5-sonnet-20241022"
    personality_traits: list[str] = field(default_factory=list)
    communication_style: str = ""
    primary_tools: list[str] = field(default_factory=list)
    email: str | None = None
    twitter_handle: str | None = None
    linkedin_url: str | None = None
    board_position: str | None = None
    department: str | None = None
    description: str = ""
    soul_file_path: Path | None = None
    loaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "crew": self.crew,
            "piece_type": self.piece_type,
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "model": self.model,
            "personality_traits": self.personality_traits,
            "communication_style": self.communication_style,
            "primary_tools": self.primary_tools,
            "email": self.email,
            "twitter_handle": self.twitter_handle,
            "board_position": self.board_position,
            "department": self.department,
            "description": self.description[:200],
            "soul_file_path": str(self.soul_file_path) if self.soul_file_path else None,
            "loaded_at": self.loaded_at.isoformat(),
        }


class SoulRegistry:
    """Collection of all loaded souls, indexed by agent_id."""

    def __init__(self) -> None:
        self._souls: dict[str, AgentSoul] = {}

    def _register(self, soul: AgentSoul) -> None:
        self._souls[soul.agent_id] = soul

    def get(self, agent_id: str) -> AgentSoul | None:
        return self._souls.get(agent_id)

    def get_crew(self, crew: str) -> list[AgentSoul]:
        return [s for s in self._souls.values() if s.crew == crew.lower()]

    def get_by_piece(self, piece_type: str) -> list[AgentSoul]:
        return [s for s in self._souls.values() if s.piece_type == piece_type.lower()]

    def all(self) -> list[AgentSoul]:
        return list(self._souls.values())

    def count(self) -> int:
        return len(self._souls)

    def __repr__(self) -> str:
        return f"SoulRegistry({self.count()} souls)"


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def _parse_markdown_meta(content: str) -> tuple[dict[str, str], str]:
    """
    Extract **KEY:** value pairs from the top of a soul markdown file.
    Returns (meta_dict, body_text).

    The header ends at the first `---` horizontal rule or the first `##` heading.
    """
    lines = content.splitlines()
    meta: dict[str, str] = {}
    body_lines: list[str] = []
    in_meta = True

    for line in lines:
        stripped = line.strip()
        if in_meta:
            match = _BOLD_KEY_RE.match(stripped)
            if match:
                key = match.group(1).strip().lower().replace(" ", "_")
                value = match.group(2).strip()
                meta[key] = value
                continue
            # Once we hit `---` or a `##` section header, switch to body
            if stripped.startswith("---") or stripped.startswith("##"):
                in_meta = False
        body_lines.append(line)

    return meta, "\n".join(body_lines).strip()


def _normalise_crew(raw: str) -> str:
    """'WHITE (Offense)' → 'white'."""
    return raw.split("(")[0].strip().lower()


def _normalise_piece(raw: str) -> str:
    """'King', 'PAWN', 'Knight' → normalised lowercase."""
    return raw.strip().lower()


# ---------------------------------------------------------------------------
# Soul Loader
# ---------------------------------------------------------------------------

class SoulLoader:
    """
    Reads .soul.md files, builds SoulRegistry, injects into agents.

    Usage:
        loader = SoulLoader(souls_dir=Path(".agent-souls"))
        registry = loader.load_all()
        loader.inject_into_crew(crew.agents, registry)
    """

    def __init__(self, souls_dir: Path = Path(".agent-souls")) -> None:
        self.souls_dir = souls_dir

    def load_all(self) -> SoulRegistry:
        """
        Scan souls_dir recursively, parse all .soul.md files.
        Returns a populated SoulRegistry.
        """
        registry = SoulRegistry()

        if not self.souls_dir.exists():
            logger.warning(
                "SoulLoader: souls directory '%s' not found — skipping soul load.",
                self.souls_dir,
            )
            return registry

        soul_files = list(self.souls_dir.rglob("*.soul.md"))
        logger.info("SoulLoader: found %d soul files in '%s'", len(soul_files), self.souls_dir)

        for path in soul_files:
            try:
                soul = self._parse_soul_file(path)
                registry._register(soul)
                logger.debug("SoulLoader: loaded soul '%s' (%s/%s)", soul.agent_id, soul.crew, soul.piece_type)
            except Exception as exc:
                logger.warning("SoulLoader: failed to parse '%s': %s", path, exc)

        warnings = self.validate_registry(registry)
        for w in warnings:
            logger.warning("SoulLoader validation: %s", w)

        logger.info(
            "SoulLoader: registry ready — %d souls loaded (%d white, %d black)",
            registry.count(),
            len(registry.get_crew("white")),
            len(registry.get_crew("black")),
        )
        return registry

    def _parse_soul_file(self, path: Path) -> AgentSoul:
        """Parse one .soul.md file into an AgentSoul."""
        content = path.read_text(encoding="utf-8")
        meta, body = _parse_markdown_meta(content)

        # agent_id: prefer explicit ID field; fallback to stem
        raw_id = (
            meta.get("id")
            or meta.get("agent_id")
            or path.stem.replace(".soul", "")
        )
        agent_id = raw_id.lower().replace(" ", "_").replace("-", "_")

        raw_crew = meta.get("crew", "white")
        crew = _normalise_crew(raw_crew)

        raw_piece = meta.get("piece", meta.get("piece_type", "pawn"))
        piece_type = _normalise_piece(raw_piece)

        role = meta.get("role", meta.get("department", "agent")).lower().replace(" ", "_")

        return AgentSoul(
            agent_id=agent_id,
            role=role,
            crew=crew,
            piece_type=piece_type,
            voice_id=meta.get("voice_id") or meta.get("elevenlabs_voice_id"),
            voice_name=meta.get("voice_name"),
            model=meta.get("model", "claude-3-5-sonnet-20241022"),
            personality_traits=[],   # body parsing not required for v1
            communication_style=meta.get("communication_style", ""),
            primary_tools=[],
            email=meta.get("email"),
            twitter_handle=meta.get("twitter_handle"),
            linkedin_url=meta.get("linkedin_url"),
            board_position=meta.get("board_position"),
            department=meta.get("department"),
            description=body[:500],
            soul_file_path=path,
        )

    def inject_into_crew(self, crew_agents: list[Any], registry: SoulRegistry) -> None:
        """
        For each agent in the list, find a matching soul by agent_id and
        attach it as agent.soul.  Falls back to partial-match on agent.name.
        """
        injected = 0
        for agent in crew_agents:
            agent_id = getattr(agent, "id", None) or getattr(agent, "name", "")
            soul = registry.get(agent_id)

            # Try partial-match: "pauli_king" matches "pauli_king_white"
            if soul is None:
                for registered_id, registered_soul in registry._souls.items():
                    if agent_id and agent_id in registered_id:
                        soul = registered_soul
                        break

            if soul is not None:
                agent.soul = soul
                injected += 1
                logger.debug("SoulLoader: injected soul '%s' into agent '%s'", soul.agent_id, agent_id)
            else:
                logger.debug("SoulLoader: no soul found for agent '%s'", agent_id)

        logger.info("SoulLoader: injected %d/%d souls into crew agents", injected, len(crew_agents))

    def validate_registry(self, registry: SoulRegistry) -> list[str]:
        """Return list of validation warnings."""
        warnings: list[str] = []
        seen_ids: set[str] = set()

        for soul in registry.all():
            if soul.agent_id in seen_ids:
                warnings.append(f"Duplicate agent_id: '{soul.agent_id}'")
            seen_ids.add(soul.agent_id)

            if soul.crew not in VALID_CREWS:
                warnings.append(f"Unknown crew '{soul.crew}' for agent '{soul.agent_id}'")

            if soul.piece_type not in VALID_PIECE_TYPES:
                warnings.append(
                    f"Unknown piece_type '{soul.piece_type}' for agent '{soul.agent_id}'"
                )

        return warnings
