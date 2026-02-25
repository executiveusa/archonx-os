"""Devika PI governance policy with full audit logging and PAULIWHEEL stage enforcement."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from archonx.security.command_guard import CommandGuard


logger = structlog.get_logger("archonx.security.devika_pi_policy")

ALLOWED_EXECUTION_PROFILES: frozenset[str] = frozenset(
    {
        "devika-pi-default",
        "devika-pi-safe",
        "devika-pi-research",
    }
)

PAULIWHEEL_STAGES: tuple[str, ...] = (
    "PLAN",
    "IMPLEMENT",
    "TEST",
    "EVALUATE",
    "PATCH",
    "REPEAT",
)

VALID_BEAD_PREFIXES: tuple[str, ...] = (
    "BEAD-DEVIKA-PI-",
    "BEAD-P",
)

_STAGE_ORDER: dict[str, int] = {stage: idx for idx, stage in enumerate(PAULIWHEEL_STAGES)}

_ERROR_CODES: dict[str, str] = {
    "invalid_execution_profile": "ERR-GOV-001",
    "invalid_bead_id": "ERR-GOV-002",
    "empty_bead_id": "ERR-GOV-003",
    "bead_id_too_short": "ERR-GOV-004",
    "invalid_stage": "ERR-GOV-005",
    "illegal_stage_advance": "ERR-GOV-006",
    "blocked_command": "ERR-GOV-007",
    "ok": "OK-000",
}


@dataclass
class AuditEntry:
    """Structured audit log entry for Devika PI governance decisions."""

    timestamp: str
    bead_id: str
    profile: str
    check_type: str
    allowed: bool
    reason: str
    error_code: str
    stage: str | None = None
    command: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the entry to a plain dict."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize the entry to a JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass(frozen=True)
class DevikaPolicyDecision:
    """Result of a single governance policy check."""

    allowed: bool
    reason: str
    error_code: str = "OK-000"
    stage: str | None = None


class DevikaPIGovernance:
    """
    Validates Devika PI execution contracts and command safety.

    Enforces:
    - Execution profile allowlist
    - Bead ID prefix and minimum length
    - PAULIWHEEL stage ordering
    - Command safety via CommandGuard
    - Structured audit logging to ops/reports/
    """

    _MIN_BEAD_ID_LENGTH: int = 10

    def __init__(self, report_dir: str | os.PathLike[str] = "ops/reports") -> None:
        self._default_guard = CommandGuard(allowlist_mode=False)
        self._safe_guard = CommandGuard(allowlist_mode=True)
        self._report_dir = Path(report_dir)
        self._audit_log: list[AuditEntry] = []
        self._current_stage: str | None = None
        self._report_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "DevikaPIGovernance initialised",
            report_dir=str(self._report_dir),
        )

    # ------------------------------------------------------------------
    # Public policy check methods
    # ------------------------------------------------------------------

    def check_execution_profile(
        self,
        execution_profile: str,
        bead_id: str = "",
    ) -> DevikaPolicyDecision:
        """Validate that the given execution profile is in the allowlist."""
        if execution_profile not in ALLOWED_EXECUTION_PROFILES:
            decision = DevikaPolicyDecision(
                allowed=False,
                reason="invalid_execution_profile",
                error_code=_ERROR_CODES["invalid_execution_profile"],
            )
        else:
            decision = DevikaPolicyDecision(
                allowed=True,
                reason="ok",
                error_code=_ERROR_CODES["ok"],
            )
        self._record_audit(
            bead_id=bead_id,
            profile=execution_profile,
            check_type="execution_profile",
            decision=decision,
        )
        return decision

    def check_bead(self, bead_id: str, profile: str = "") -> DevikaPolicyDecision:
        """Validate bead ID format, prefix, and minimum length."""
        if not bead_id:
            decision = DevikaPolicyDecision(
                allowed=False,
                reason="empty_bead_id",
                error_code=_ERROR_CODES["empty_bead_id"],
            )
        elif len(bead_id) < self._MIN_BEAD_ID_LENGTH:
            decision = DevikaPolicyDecision(
                allowed=False,
                reason="bead_id_too_short",
                error_code=_ERROR_CODES["bead_id_too_short"],
            )
        elif not any(bead_id.startswith(prefix) for prefix in VALID_BEAD_PREFIXES):
            decision = DevikaPolicyDecision(
                allowed=False,
                reason="invalid_bead_id",
                error_code=_ERROR_CODES["invalid_bead_id"],
            )
        else:
            decision = DevikaPolicyDecision(
                allowed=True,
                reason="ok",
                error_code=_ERROR_CODES["ok"],
            )
        self._record_audit(
            bead_id=bead_id,
            profile=profile,
            check_type="bead_validation",
            decision=decision,
        )
        return decision

    def check_stage(
        self,
        current_stage: str | None,
        requested_stage: str,
        bead_id: str = "",
        profile: str = "",
    ) -> DevikaPolicyDecision:
        """
        Validate PAULIWHEEL stage advancement.

        Rules:
        - REPEAT is always allowed from any stage (restart cycle).
        - PLAN is only allowed as the first stage (current_stage is None).
        - All other stages must follow the declared order exactly.
        """
        if requested_stage not in _STAGE_ORDER:
            decision = DevikaPolicyDecision(
                allowed=False,
                reason="invalid_stage",
                error_code=_ERROR_CODES["invalid_stage"],
                stage=requested_stage,
            )
        elif requested_stage == "REPEAT":
            # REPEAT restarts the cycle — always permitted
            decision = DevikaPolicyDecision(
                allowed=True,
                reason="ok",
                error_code=_ERROR_CODES["ok"],
                stage=requested_stage,
            )
        elif current_stage is None:
            # First stage must be PLAN
            if requested_stage == "PLAN":
                decision = DevikaPolicyDecision(
                    allowed=True,
                    reason="ok",
                    error_code=_ERROR_CODES["ok"],
                    stage=requested_stage,
                )
            else:
                decision = DevikaPolicyDecision(
                    allowed=False,
                    reason="illegal_stage_advance",
                    error_code=_ERROR_CODES["illegal_stage_advance"],
                    stage=requested_stage,
                )
        else:
            current_idx = _STAGE_ORDER.get(current_stage, -1)
            requested_idx = _STAGE_ORDER.get(requested_stage, -1)
            expected_next = current_idx + 1
            if requested_idx == expected_next:
                decision = DevikaPolicyDecision(
                    allowed=True,
                    reason="ok",
                    error_code=_ERROR_CODES["ok"],
                    stage=requested_stage,
                )
            else:
                decision = DevikaPolicyDecision(
                    allowed=False,
                    reason="illegal_stage_advance",
                    error_code=_ERROR_CODES["illegal_stage_advance"],
                    stage=requested_stage,
                )
        self._record_audit(
            bead_id=bead_id,
            profile=profile,
            check_type="stage_enforcement",
            decision=decision,
            stage=requested_stage,
        )
        return decision

    def check_command(
        self,
        execution_profile: str,
        command: str,
        bead_id: str = "",
    ) -> DevikaPolicyDecision:
        """Run a command through the profile-appropriate CommandGuard."""
        guard = (
            self._safe_guard
            if execution_profile == "devika-pi-safe"
            else self._default_guard
        )
        allowed, reason = guard.check(command)
        error_code = _ERROR_CODES["ok"] if allowed else _ERROR_CODES["blocked_command"]
        decision = DevikaPolicyDecision(
            allowed=allowed,
            reason=reason,
            error_code=error_code,
        )
        self._record_audit(
            bead_id=bead_id,
            profile=execution_profile,
            check_type="command_check",
            decision=decision,
            command=command,
        )
        return decision

    # ------------------------------------------------------------------
    # Stage tracking helpers
    # ------------------------------------------------------------------

    def advance_stage(
        self,
        requested_stage: str,
        bead_id: str = "",
        profile: str = "",
    ) -> DevikaPolicyDecision:
        """Attempt to advance to the next PAULIWHEEL stage."""
        decision = self.check_stage(
            current_stage=self._current_stage,
            requested_stage=requested_stage,
            bead_id=bead_id,
            profile=profile,
        )
        if decision.allowed:
            if requested_stage == "REPEAT":
                self._current_stage = None
                logger.info("PAULIWHEEL cycle reset via REPEAT", bead_id=bead_id)
            else:
                self._current_stage = requested_stage
                logger.info(
                    "PAULIWHEEL stage advanced",
                    stage=requested_stage,
                    bead_id=bead_id,
                )
        else:
            logger.warning(
                "PAULIWHEEL stage advance blocked",
                from_stage=self._current_stage,
                to_stage=requested_stage,
                reason=decision.reason,
                bead_id=bead_id,
            )
        return decision

    # ------------------------------------------------------------------
    # Report emission
    # ------------------------------------------------------------------

    def emit_audit_report(self, bead_id: str) -> Path:
        """Write all accumulated audit entries for this session to ops/reports/."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"AUDIT_{bead_id}_{timestamp}.json"
        report_path = self._report_dir / filename
        payload: dict[str, Any] = {
            "bead_id": bead_id,
            "generated_at": timestamp,
            "total_checks": len(self._audit_log),
            "entries": [e.to_dict() for e in self._audit_log],
        }
        report_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        logger.info(
            "Audit report emitted",
            path=str(report_path),
            entries=len(self._audit_log),
        )
        return report_path

    def get_audit_log(self) -> list[AuditEntry]:
        """Return a copy of all recorded audit entries."""
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_audit(
        self,
        bead_id: str,
        profile: str,
        check_type: str,
        decision: DevikaPolicyDecision,
        stage: str | None = None,
        command: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Append a structured audit entry and emit a structlog event."""
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            bead_id=bead_id,
            profile=profile,
            check_type=check_type,
            allowed=decision.allowed,
            reason=decision.reason,
            error_code=decision.error_code,
            stage=stage,
            command=command,
            metadata=metadata or {},
        )
        self._audit_log.append(entry)
        log_fn = logger.info if decision.allowed else logger.warning
        log_fn(
            "policy_check",
            check_type=check_type,
            allowed=decision.allowed,
            reason=decision.reason,
            error_code=decision.error_code,
            bead_id=bead_id,
            profile=profile,
            stage=stage,
        )
