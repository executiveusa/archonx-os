"""
Command Guard — Shell command injection detection and allowlist enforcement.

Combines IronClaw's command injection detection with ZeroClaw's allowlist-only
model. Prevents destructive and arbitrary shell execution.
"""

from __future__ import annotations

import logging
import re
import shlex
from typing import Any

logger = logging.getLogger("archonx.security.command_guard")


# Destructive / dangerous command patterns (always blocked)
_BLOCKLIST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"rm\s+-r[f]?\s+/", re.I),
    re.compile(r"rm\s+-f?r\s+/", re.I),
    re.compile(r":()\s*\{\s*:\|:\s*&\s*\}", re.I),  # fork bomb
    re.compile(r"dd\s+if=/dev/(zero|random|urandom)", re.I),
    re.compile(r"mkfs\.\w+", re.I),
    re.compile(r">\s*/dev/sd[a-z]", re.I),
    re.compile(r"chmod\s+-R\s+777\s+/", re.I),
    re.compile(r"chown\s+-R\s+.*\s+/\s*$", re.I),
    re.compile(r"\bshutdown\b", re.I),
    re.compile(r"\breboot\b", re.I),
    re.compile(r"\binit\s+0\b", re.I),
    re.compile(r"\bhalt\b", re.I),
    re.compile(r"curl\s+.*\|\s*(ba)?sh", re.I),      # pipe-to-shell
    re.compile(r"wget\s+.*\|\s*(ba)?sh", re.I),
    re.compile(r"python\s+-c\s+['\"].*exec\(", re.I),  # exec injection
]

# Shell metacharacters that indicate injection attempts
_INJECTION_METACHAR = re.compile(r"[;`$\|]|&&|\|\||>\s*>")


class CommandGuard:
    """
    Two-mode command execution guard:
    1. Blocklist mode (default): block known-dangerous patterns
    2. Allowlist mode: only explicitly allowed commands may execute
    """

    def __init__(
        self,
        allowlist_mode: bool = False,
        allowed_commands: set[str] | None = None,
    ) -> None:
        self.allowlist_mode = allowlist_mode
        self.allowed_commands: set[str] = allowed_commands or {
            "git", "python", "python3", "pip", "pip3",
            "node", "npm", "npx", "bun",
            "pytest", "mypy", "ruff", "black",
            "ls", "dir", "cat", "echo", "cd", "pwd",
            "mkdir", "cp", "mv", "find", "grep",
        }
        logger.info(
            "CommandGuard initialized (mode=%s, %d allowed)",
            "allowlist" if allowlist_mode else "blocklist",
            len(self.allowed_commands),
        )

    def check(self, command: str) -> tuple[bool, str]:
        """
        Check if a shell command is safe to execute.
        Returns (allowed, reason).
        """
        if not command.strip():
            return False, "empty_command"

        # Always check blocklist patterns
        for pat in _BLOCKLIST_PATTERNS:
            if pat.search(command):
                logger.warning("Blocked dangerous command pattern: %s", pat.pattern)
                return False, f"blocked_pattern: {pat.pattern}"

        # Check for shell metacharacter injection
        if _INJECTION_METACHAR.search(command):
            # Allow common safe patterns
            if not self._is_safe_pipeline(command):
                logger.warning("Shell metacharacter injection detected")
                return False, "injection_metacharacters"

        # Allowlist mode — extract base command and check
        if self.allowlist_mode:
            base_cmd = self._extract_base_command(command)
            if base_cmd not in self.allowed_commands:
                return False, f"command_not_in_allowlist: {base_cmd}"

        return True, "allowed"

    def _extract_base_command(self, command: str) -> str:
        """Extract the base command name from a command string."""
        try:
            parts = shlex.split(command)
            return parts[0].split("/")[-1] if parts else ""
        except ValueError:
            # Malformed quoting
            first = command.strip().split()[0] if command.strip() else ""
            return first.split("/")[-1]

    def _is_safe_pipeline(self, command: str) -> bool:
        """Allow simple, safe piped commands (e.g., grep | head)."""
        # Only allow single pipe to safe commands
        if "|" in command and "||" not in command:
            parts = command.split("|")
            if len(parts) == 2:
                right_cmd = self._extract_base_command(parts[1].strip())
                safe_pipe_targets = {"head", "tail", "wc", "sort", "uniq", "grep", "less", "more"}
                return right_cmd in safe_pipe_targets
        return False

    def add_allowed(self, commands: list[str]) -> None:
        """Add commands to the allowlist."""
        self.allowed_commands.update(commands)

    def remove_allowed(self, commands: list[str]) -> None:
        """Remove commands from the allowlist."""
        self.allowed_commands -= set(commands)
