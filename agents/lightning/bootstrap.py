"""Agent Lightning bootstrap — Phase 4 agent lifecycle management."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import structlog

from agents.lightning.registry import AgentConfig, AgentRegistry

logger = structlog.get_logger("agents.lightning.bootstrap")


@dataclass
class AgentStatus:
    """Runtime status snapshot for a single registered agent."""

    agent_id: str
    agent_type: str
    profile: str
    active: bool
    health: str
    last_checked: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return asdict(self)


class AgentLightningBootstrap:
    """
    Phase 4 bootstrap system for the Agent Lightning subsystem.

    Manages agent lifecycle:
    - start():        Activates all registered agents and marks them running.
    - stop():         Gracefully deactivates all running agents.
    - status():       Returns a list of AgentStatus snapshots.
    - health_check(): Returns an overall health summary dict.
    """

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._registry = registry or AgentRegistry()
        self._running: bool = False
        self._started_at: str | None = None
        self._stopped_at: str | None = None

    # ------------------------------------------------------------------
    # Agent registration convenience wrappers
    # ------------------------------------------------------------------

    def register_agent(self, agent_id: str, config: AgentConfig) -> None:
        """Register an agent with the underlying registry."""
        self._registry.register(agent_id, config)
        logger.info("Agent registered", agent_id=agent_id, agent_type=config.agent_type)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> dict[str, Any]:
        """
        Activate all registered agents and mark the bootstrap as running.

        Returns:
            A dict with the startup summary (agent count, started_at).
        """
        active_agents = self._registry.get_active_agents()
        self._running = True
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._stopped_at = None

        logger.info(
            "AgentLightningBootstrap started",
            agent_count=len(active_agents),
            started_at=self._started_at,
        )
        return {
            "status": "running",
            "agent_count": len(active_agents),
            "started_at": self._started_at,
            "agents": [a.agent_id for a in active_agents],
        }

    def stop(self) -> dict[str, Any]:
        """
        Gracefully deactivate all running agents and mark the bootstrap as stopped.

        Returns:
            A dict with the shutdown summary (agent count, stopped_at).
        """
        active_agents = self._registry.get_active_agents()
        stopped_ids: list[str] = []
        for agent in active_agents:
            try:
                self._registry.deregister(agent.agent_id)
                stopped_ids.append(agent.agent_id)
            except KeyError:
                pass

        self._running = False
        self._stopped_at = datetime.now(timezone.utc).isoformat()

        logger.info(
            "AgentLightningBootstrap stopped",
            stopped_count=len(stopped_ids),
            stopped_at=self._stopped_at,
        )
        return {
            "status": "stopped",
            "stopped_count": len(stopped_ids),
            "stopped_ids": stopped_ids,
            "stopped_at": self._stopped_at,
        }

    def status(self) -> list[AgentStatus]:
        """
        Return runtime status snapshots for all registered agents.

        Returns:
            List of AgentStatus objects, one per registered agent.
        """
        now = datetime.now(timezone.utc).isoformat()
        statuses: list[AgentStatus] = []
        for cfg in self._registry.list_all():
            health = "healthy" if cfg.active and self._running else "stopped"
            statuses.append(
                AgentStatus(
                    agent_id=cfg.agent_id,
                    agent_type=cfg.agent_type,
                    profile=cfg.profile,
                    active=cfg.active,
                    health=health,
                    last_checked=now,
                )
            )
        return statuses

    def health_check(self) -> dict[str, Any]:
        """
        Perform an overall health check of the bootstrap system.

        Returns:
            A dict describing the overall health, running state, and per-agent summary.
        """
        agent_statuses = self.status()
        active_count = sum(1 for s in agent_statuses if s.active)
        unhealthy = [s.agent_id for s in agent_statuses if s.health != "healthy"]

        overall = "healthy" if self._running and not unhealthy else "degraded"
        if not self._running:
            overall = "stopped"

        result: dict[str, Any] = {
            "overall": overall,
            "running": self._running,
            "active_agent_count": active_count,
            "total_agent_count": len(agent_statuses),
            "unhealthy_agents": unhealthy,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("Health check completed", overall=overall, active_count=active_count)
        return result

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """True if the bootstrap is in the running state."""
        return self._running

    @property
    def registry(self) -> AgentRegistry:
        """Return the underlying AgentRegistry."""
        return self._registry
