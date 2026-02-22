"""
Sandbox Policy — Defines execution privilege levels for agent sandboxes.

Three-tier sandbox model inspired by IronClaw's Docker/WASM sandboxing,
adapted for lightweight Python enforcement.
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.security.sandbox_policy")


class SandboxLevel(enum.IntEnum):
    """
    Sandbox privilege levels (least to most permissive).
    """
    READ_ONLY = 0       # Can read files & call read-only tools
    WORKSPACE_WRITE = 1 # Can write within workspace scope
    FULL_ACCESS = 2     # Unrestricted (admin only)


@dataclass
class SandboxConfig:
    """Per-agent sandbox configuration."""
    level: SandboxLevel = SandboxLevel.WORKSPACE_WRITE
    max_memory_mb: int = 512
    max_cpu_seconds: int = 300
    network_allowed: bool = True
    network_allowlist: list[str] = field(default_factory=list)
    allowed_write_dirs: list[str] = field(default_factory=list)
    allow_subprocess: bool = False
    allow_network_bind: bool = False

    def __post_init__(self) -> None:
        if self.level == SandboxLevel.READ_ONLY:
            self.allow_subprocess = False
            self.allow_network_bind = False
        elif self.level == SandboxLevel.WORKSPACE_WRITE:
            self.allow_network_bind = False


class SandboxEnforcer:
    """
    Enforces sandbox policies before agent operations execute.

    Usage:
        enforcer = SandboxEnforcer()
        enforcer.set_config("agent-001", SandboxConfig(level=SandboxLevel.READ_ONLY))
        enforcer.check_write("agent-001", "/some/path")  # raises
    """

    def __init__(self) -> None:
        self._configs: dict[str, SandboxConfig] = {}
        # Default config for agents without explicit config
        self._default = SandboxConfig()

    def set_config(self, agent_id: str, config: SandboxConfig) -> None:
        """Assign a sandbox config to an agent."""
        self._configs[agent_id] = config
        logger.info(
            "Sandbox config set for %s: level=%s", agent_id, config.level.name
        )

    def get_config(self, agent_id: str) -> SandboxConfig:
        """Return the sandbox config for an agent (or default)."""
        return self._configs.get(agent_id, self._default)

    def check_write(self, agent_id: str, path: str) -> tuple[bool, str]:
        """Check if the agent is allowed to write to the given path."""
        cfg = self.get_config(agent_id)

        if cfg.level == SandboxLevel.READ_ONLY:
            return False, "read_only_sandbox"

        if cfg.level == SandboxLevel.WORKSPACE_WRITE and cfg.allowed_write_dirs:
            if not any(path.startswith(d) for d in cfg.allowed_write_dirs):
                return False, f"path_outside_allowed_dirs: {path}"

        return True, "allowed"

    def check_read(self, agent_id: str, path: str) -> tuple[bool, str]:
        """Check if the agent is allowed to read the given path. All levels can read."""
        # All sandbox levels permit reads (within workspace scope, enforced elsewhere)
        return True, "allowed"

    def check_subprocess(self, agent_id: str) -> tuple[bool, str]:
        """Check if the agent may spawn subprocesses."""
        cfg = self.get_config(agent_id)
        if not cfg.allow_subprocess:
            return False, f"subprocess_denied_at_level_{cfg.level.name}"
        return True, "allowed"

    def check_network(self, agent_id: str, host: str = "") -> tuple[bool, str]:
        """Check if the agent may make network requests."""
        cfg = self.get_config(agent_id)

        if not cfg.network_allowed:
            return False, "network_denied"

        if cfg.network_allowlist and host:
            if host not in cfg.network_allowlist:
                return False, f"host_not_in_allowlist: {host}"

        return True, "allowed"

    def check_bind(self, agent_id: str) -> tuple[bool, str]:
        """Check if the agent may bind to a network port."""
        cfg = self.get_config(agent_id)
        if not cfg.allow_network_bind:
            return False, f"bind_denied_at_level_{cfg.level.name}"
        return True, "allowed"
