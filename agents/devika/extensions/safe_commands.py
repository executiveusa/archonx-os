"""Safe command runner for Devika PI execution modes."""

from __future__ import annotations

from dataclasses import dataclass

from archonx.security.command_guard import CommandGuard


class DevikaSafetyError(RuntimeError):
    """Raised when a command violates Devika safety policy."""


@dataclass(frozen=True)
class SafeCommandDecision:
    allowed: bool
    reason: str


class DevikaSafeCommandRunner:
    """Profile-aware command checker backed by CommandGuard."""

    def __init__(self, profile: str) -> None:
        self.profile = profile
        allowlist_mode = profile == "devika-pi-safe"
        self._guard = CommandGuard(allowlist_mode=allowlist_mode)

    def check(self, command: str) -> SafeCommandDecision:
        allowed, reason = self._guard.check(command)
        return SafeCommandDecision(allowed=allowed, reason=reason)

    def enforce(self, command: str) -> None:
        decision = self.check(command)
        if not decision.allowed:
            raise DevikaSafetyError(
                f"command blocked for profile={self.profile}: {decision.reason}"
            )

