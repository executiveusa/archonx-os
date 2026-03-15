"""
Agent Identity — Portable agent persona files.

Each agent can have a persistent identity that includes its name, role,
capabilities, personality traits, and operational parameters. Identities
are serializable to JSON for export/import across deployments.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.core.agent_identity")


@dataclass
class AgentIdentity:
    """Portable agent identity descriptor."""
    agent_id: str
    name: str
    role: str
    crew: str
    capabilities: list[str] = field(default_factory=list)
    personality_traits: dict[str, Any] = field(default_factory=dict)
    operational_params: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentIdentity":
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            role=data["role"],
            crew=data["crew"],
            capabilities=data.get("capabilities", []),
            personality_traits=data.get("personality_traits", {}),
            operational_params=data.get("operational_params", {}),
            version=data.get("version", "1.0.0"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentIdentity":
        return cls.from_dict(json.loads(json_str))


class AgentIdentityManager:
    """
    Manages agent identities — load, save, export, import.

    Identities are stored as .identity.json files in a configurable directory.
    """

    def __init__(self, identity_dir: str | Path = "data/identities") -> None:
        self._dir = Path(identity_dir)
        self._identities: dict[str, AgentIdentity] = {}

    def _ensure_dir(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)

    def register(self, identity: AgentIdentity) -> None:
        """Register an identity in memory."""
        self._identities[identity.agent_id] = identity
        logger.info("Registered identity: %s (%s)", identity.name, identity.agent_id)

    def get(self, agent_id: str) -> AgentIdentity | None:
        """Get an identity by agent ID."""
        return self._identities.get(agent_id)

    def list_all(self) -> list[AgentIdentity]:
        """Return all registered identities."""
        return list(self._identities.values())

    def save(self, agent_id: str) -> Path:
        """Persist an identity to disk as .identity.json."""
        identity = self._identities.get(agent_id)
        if identity is None:
            raise KeyError(f"no identity registered for {agent_id}")

        self._ensure_dir()
        path = self._dir / f"{agent_id}.identity.json"
        path.write_text(identity.to_json(), encoding="utf-8")
        logger.info("Saved identity to %s", path)
        return path

    def save_all(self) -> list[Path]:
        """Persist all identities to disk."""
        paths = []
        for agent_id in self._identities:
            paths.append(self.save(agent_id))
        return paths

    def load(self, agent_id: str) -> AgentIdentity | None:
        """Load a single identity from disk."""
        path = self._dir / f"{agent_id}.identity.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        identity = AgentIdentity.from_dict(data)
        self._identities[identity.agent_id] = identity
        return identity

    def load_all(self) -> list[AgentIdentity]:
        """Load all identity files from the identity directory."""
        if not self._dir.exists():
            return []
        loaded = []
        for path in self._dir.glob("*.identity.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            identity = AgentIdentity.from_dict(data)
            self._identities[identity.agent_id] = identity
            loaded.append(identity)
        logger.info("Loaded %d identities from %s", len(loaded), self._dir)
        return loaded

    def export_bundle(self, output_path: str | Path) -> Path:
        """Export all identities as a single JSON bundle."""
        bundle = {
            "version": "1.0.0",
            "exported_at": time.time(),
            "identities": [i.to_dict() for i in self._identities.values()],
        }
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        logger.info("Exported %d identities to %s", len(bundle["identities"]), out)
        return out

    def import_bundle(self, input_path: str | Path) -> list[AgentIdentity]:
        """Import identities from a JSON bundle."""
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))
        imported = []
        for entry in data.get("identities", []):
            identity = AgentIdentity.from_dict(entry)
            self._identities[identity.agent_id] = identity
            imported.append(identity)
        logger.info("Imported %d identities", len(imported))
        return imported

    def delete(self, agent_id: str) -> bool:
        """Remove an identity from memory and disk."""
        removed = self._identities.pop(agent_id, None)
        path = self._dir / f"{agent_id}.identity.json"
        if path.exists():
            path.unlink()
        return removed is not None
