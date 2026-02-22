"""
Environment Scrubber — Strip sensitive env vars before subprocess execution.

Adapted from IronClaw's shell env scrubbing. Only an explicit allowlist
of environment variables is passed to child processes.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("archonx.security.env_scrubber")

# Safe env vars that can be passed to subprocesses
_DEFAULT_ALLOWLIST: set[str] = {
    "PATH",
    "HOME",
    "USERPROFILE",
    "USER",
    "USERNAME",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TERM",
    "TZ",
    "SHELL",
    "COMSPEC",          # Windows cmd.exe
    "SYSTEMROOT",       # Windows OS root
    "WINDIR",           # Windows directory
    "TEMP",
    "TMP",
    "TMPDIR",
    "VIRTUAL_ENV",      # Python venv
    "CONDA_PREFIX",     # Conda env
    "NODE_ENV",         # Node.js
    "PYTHONPATH",
    "PYTHONDONTWRITEBYTECODE",
}


class EnvScrubber:
    """
    Scrubs environment variables before subprocess execution.

    Only variables in the allowlist are passed. Everything else —
    API keys, tokens, database URIs — is stripped.
    """

    def __init__(
        self,
        allowlist: set[str] | None = None,
        extra_allowed: set[str] | None = None,
    ) -> None:
        self.allowlist = allowlist or _DEFAULT_ALLOWLIST.copy()
        if extra_allowed:
            self.allowlist |= extra_allowed
        logger.info("EnvScrubber initialized (%d allowed vars)", len(self.allowlist))

    def scrub(
        self,
        env: dict[str, str] | None = None,
        task_vars: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Return a clean env dict for subprocess.Popen / asyncio.create_subprocess.

        Args:
            env: Source environment (defaults to os.environ)
            task_vars: Additional task-specific vars to inject

        Returns:
            Scrubbed env dict containing only allowlisted + task vars
        """
        source = env if env is not None else dict(os.environ)
        clean: dict[str, str] = {}

        stripped_count = 0
        for key, val in source.items():
            if key in self.allowlist:
                clean[key] = val
            else:
                stripped_count += 1

        # Inject task-specific vars (these are intentionally passed)
        if task_vars:
            for key, val in task_vars.items():
                clean[key] = val

        if stripped_count > 0:
            logger.debug("Scrubbed %d env vars before subprocess", stripped_count)

        return clean

    def is_safe(self, key: str) -> bool:
        """Check if an env var is in the allowlist."""
        return key in self.allowlist

    def add_to_allowlist(self, keys: list[str]) -> None:
        """Add keys to the allowlist at runtime."""
        self.allowlist.update(keys)

    def remove_from_allowlist(self, keys: list[str]) -> None:
        """Remove keys from the allowlist."""
        self.allowlist -= set(keys)
