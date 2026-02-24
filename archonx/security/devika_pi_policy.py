"""Devika PI governance wrapper for command and profile enforcement."""

from __future__ import annotations

from dataclasses import dataclass

from archonx.security.command_guard import CommandGuard


ALLOWED_EXECUTION_PROFILES = {
    "devika-pi-default",
    "devika-pi-safe",
    "devika-pi-research",
}


@dataclass(frozen=True)
class DevikaPolicyDecision:
    allowed: bool
    reason: str


class DevikaPIGovernance:
    """Validates Devika PI execution contracts and command safety."""

    def __init__(self) -> None:
        self._default_guard = CommandGuard(allowlist_mode=False)
        self._safe_guard = CommandGuard(allowlist_mode=True)

    def check_execution_profile(self, execution_profile: str) -> DevikaPolicyDecision:
        if execution_profile not in ALLOWED_EXECUTION_PROFILES:
            return DevikaPolicyDecision(False, "invalid_execution_profile")
        return DevikaPolicyDecision(True, "ok")

    def check_bead(self, bead_id: str) -> DevikaPolicyDecision:
        if not bead_id or not bead_id.startswith("BEAD-DEVIKA-PI-"):
            return DevikaPolicyDecision(False, "invalid_bead_id")
        return DevikaPolicyDecision(True, "ok")

    def check_command(self, execution_profile: str, command: str) -> DevikaPolicyDecision:
        guard = self._safe_guard if execution_profile == "devika-pi-safe" else self._default_guard
        allowed, reason = guard.check(command)
        return DevikaPolicyDecision(allowed=allowed, reason=reason)

