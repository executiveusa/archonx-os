"""Agent Lightning registry — manages the set of known agent configurations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AgentConfig:
    """Configuration record for a registered ArchonX agent."""

    agent_id: str
    agent_type: str
    profile: str
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return asdict(self)


class AgentRegistry:
    """
    In-memory registry for ArchonX agent configurations.

    Provides register, deregister, and lookup operations.
    The registry is the authoritative source of which agents are
    active at any given time for the lightning bootstrap system.
    """

    def __init__(self) -> None:
        self._agents: dict[str, AgentConfig] = {}

    def register(self, agent_id: str, config: AgentConfig) -> None:
        """
        Register an agent with the given ID and config.

        Args:
            agent_id: Unique identifier for the agent.
            config: AgentConfig describing the agent.

        Raises:
            ValueError: If agent_id is already registered and active.
        """
        if agent_id in self._agents and self._agents[agent_id].active:
            raise ValueError(
                f"Agent '{agent_id}' is already registered and active. "
                "Deregister it first."
            )
        config.agent_id = agent_id
        self._agents[agent_id] = config

    def deregister(self, agent_id: str) -> None:
        """
        Mark an agent as inactive (soft-deregistration).

        Args:
            agent_id: ID of the agent to deregister.

        Raises:
            KeyError: If agent_id is not in the registry.
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found in registry.")
        self._agents[agent_id].active = False

    def get_active_agents(self) -> list[AgentConfig]:
        """Return a list of all currently active agent configs."""
        return [cfg for cfg in self._agents.values() if cfg.active]

    def get_agent(self, agent_id: str) -> AgentConfig:
        """
        Return the config for a single agent.

        Args:
            agent_id: ID of the agent to look up.

        Returns:
            AgentConfig for the specified agent.

        Raises:
            KeyError: If agent_id is not registered.
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found in registry.")
        return self._agents[agent_id]

    def list_all(self) -> list[AgentConfig]:
        """Return all agents (active and inactive)."""
        return list(self._agents.values())

    def count_active(self) -> int:
        """Return the number of currently active agents."""
        return sum(1 for cfg in self._agents.values() if cfg.active)

    def clear(self) -> None:
        """Remove all registered agents (for testing)."""
        self._agents.clear()
