"""
BEAD-BMAD-001 — BMAD Protocol Enforcer
=======================================
Mechanical enforcement of the Architect↔Builder A2A discipline.

Classes:
    BMAdPhase           — Phase enum (PHASE_0 … COMPLETE | BLOCKED)
    PhaseGate           — Locked gate between phases
    ArchitectHandoff    — Structured spec delivery record
    BuilderBlocker      — Structured blocker report
    BMAdState           — Persisted state across sessions
    BMAdProtocol        — Main enforcement class

Persistence:
    .archonx/bmad_state.json — written atomically on every state change
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.protocols.bmad")

_DEFAULT_STATE_FILE = Path(".archonx/bmad_state.json")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BMAdPhase(str, Enum):
    PHASE_0 = "PHASE_0"
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"
    PHASE_3 = "PHASE_3"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class BlockerSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PhaseGateLocked(Exception):
    """Raised when a builder tries to execute a locked phase."""

    def __init__(self, gate_id: str, current_phase: BMAdPhase, required_token: str) -> None:
        self.gate_id = gate_id
        self.current_phase = current_phase
        self.required_token = required_token
        super().__init__(
            f"PHASE GATE LOCKED: {gate_id}. "
            f"Current phase: {current_phase.value}. "
            f"Architect must provide: '{required_token}' to advance."
        )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PhaseGate:
    """Blocks execution at a phase boundary until explicitly unlocked."""
    gate_id: str
    from_phase: str          # BMAdPhase value
    to_phase: str            # BMAdPhase value
    required_token: str
    locked: bool = True
    unlock_token: str | None = None
    unlocked_at: str | None = None
    unlocked_by: str | None = None

    def unlock(self, token: str, unlocked_by: str = "architect") -> bool:
        if token.strip() == self.required_token.strip():
            self.locked = False
            self.unlock_token = token
            self.unlocked_at = _now_iso()
            self.unlocked_by = unlocked_by
            return True
        return False


@dataclass
class ArchitectHandoff:
    """Structured spec delivery from Architect to Builder."""
    handoff_id: str = field(default_factory=lambda: f"HANDOFF-{uuid.uuid4().hex[:8].upper()}")
    phase: str = BMAdPhase.PHASE_1.value
    spec_files: list[str] = field(default_factory=list)
    approval_phrase: str = ""
    notes: str = ""
    timestamp: str = field(default_factory=_now_iso)
    acknowledged_by_builder: bool = False


@dataclass
class BuilderBlocker:
    """Structured blocker report from Builder to Architect."""
    blocker_id: str = field(default_factory=lambda: f"BLOCKER-{uuid.uuid4().hex[:8].upper()}")
    phase: str = BMAdPhase.PHASE_2.value
    component: str = ""
    description: str = ""
    options_considered: list[str] = field(default_factory=list)
    request: str = ""
    severity: str = BlockerSeverity.HIGH.value
    blocks_phase_completion: bool = True
    timestamp: str = field(default_factory=_now_iso)
    resolved: bool = False
    resolution: str | None = None


@dataclass
class PhaseHistoryEntry:
    phase: str
    entered_at: str
    exited_at: str | None = None
    deliverables: list[str] = field(default_factory=list)


@dataclass
class BMAdState:
    """Persisted BMAD state — survives kernel restarts."""
    current_phase: str = BMAdPhase.PHASE_2.value
    gates: dict[str, dict] = field(default_factory=dict)
    handoffs: list[dict] = field(default_factory=list)
    blockers: list[dict] = field(default_factory=list)
    phase_history: list[dict] = field(default_factory=list)
    last_updated: str = field(default_factory=_now_iso)

    @classmethod
    def default(cls) -> "BMAdState":
        state = cls()
        # Bootstrap the four phase gates
        gates = [
            PhaseGate(
                gate_id="GATE_P0_TO_P1",
                from_phase=BMAdPhase.PHASE_0.value,
                to_phase=BMAdPhase.PHASE_1.value,
                required_token="APPROVED: START PHASE_1",
                locked=False,   # Already in PHASE_2, so retrospectively unlocked
                unlocked_at=_now_iso(),
                unlocked_by="architect",
            ),
            PhaseGate(
                gate_id="GATE_P1_TO_P2",
                from_phase=BMAdPhase.PHASE_1.value,
                to_phase=BMAdPhase.PHASE_2.value,
                required_token="APPROVED: START PHASE_2",
                locked=False,   # Architect approved Phase 2 in this session
                unlocked_at=_now_iso(),
                unlocked_by="architect",
            ),
            PhaseGate(
                gate_id="GATE_P2_TO_P3",
                from_phase=BMAdPhase.PHASE_2.value,
                to_phase=BMAdPhase.PHASE_3.value,
                required_token="APPROVED: START PHASE_3",
                locked=True,
            ),
            PhaseGate(
                gate_id="GATE_P3_TO_COMPLETE",
                from_phase=BMAdPhase.PHASE_3.value,
                to_phase=BMAdPhase.COMPLETE.value,
                required_token="DEPLOYMENT COMPLETE",
                locked=True,
            ),
        ]
        state.gates = {g.gate_id: asdict(g) for g in gates}
        return state

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BMAdState":
        return cls(
            current_phase=data.get("current_phase", BMAdPhase.PHASE_2.value),
            gates=data.get("gates", {}),
            handoffs=data.get("handoffs", []),
            blockers=data.get("blockers", []),
            phase_history=data.get("phase_history", []),
            last_updated=data.get("last_updated", _now_iso()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_phase": self.current_phase,
            "gates": self.gates,
            "handoffs": self.handoffs,
            "blockers": self.blockers,
            "phase_history": self.phase_history,
            "last_updated": self.last_updated,
        }


# ---------------------------------------------------------------------------
# BMAD Protocol enforcer
# ---------------------------------------------------------------------------

class BMAdProtocol:
    """
    Main BMAD enforcement class.
    The kernel holds one instance. All phase transitions go through here.
    """

    def __init__(self, state_file: Path | str = _DEFAULT_STATE_FILE) -> None:
        self._state_file = Path(state_file) if not isinstance(state_file, Path) else state_file
        self._state: BMAdState = self._load_or_init()

    # ------------------------------------------------------------------
    # State I/O
    # ------------------------------------------------------------------

    def _load_or_init(self) -> BMAdState:
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                state = BMAdState.from_dict(data)
                logger.info(
                    "BMAdProtocol: loaded state from '%s' — phase=%s",
                    self._state_file,
                    state.current_phase,
                )
                return state
            except Exception as exc:
                logger.warning(
                    "BMAdProtocol: could not parse state file '%s' (%s) — reinitialising.",
                    self._state_file,
                    exc,
                )
        state = BMAdState.default()
        self._persist(state)
        return state

    def _persist(self, state: BMAdState) -> None:
        state.last_updated = _now_iso()
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        tmp.replace(self._state_file)   # atomic rename

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> "BMAdState":
        return self._state

    # Phase management
    # ------------------------------------------------------------------

    def get_current_phase(self) -> BMAdPhase:
        return BMAdPhase(self._state.current_phase)

    def check_phase_allowed(self, target_phase: BMAdPhase) -> None:
        """
        Raises PhaseGateLocked if the gate to target_phase is locked.
        Called by kernel.execute_task() to guard PHASE_2 execution.
        """
        gate = self._find_gate_to(target_phase)
        if gate and gate["locked"]:
            raise PhaseGateLocked(
                gate_id=gate["gate_id"],
                current_phase=self.get_current_phase(),
                required_token=gate["required_token"],
            )

    def advance_phase(self, approval_token: str, advanced_by: str = "architect") -> BMAdPhase:
        """
        Check token matches the required_token for the next gate.
        Unlock the gate and advance current_phase.
        Returns the new phase.
        """
        current = self.get_current_phase()

        # Find the gate leading OUT of current phase
        next_gate: dict | None = None
        for gate_data in self._state.gates.values():
            if gate_data["from_phase"] == current.value and gate_data["locked"]:
                next_gate = gate_data
                break

        if next_gate is None:
            logger.info("BMAdProtocol: no locked gate from phase %s", current.value)
            return current

        gate_obj = PhaseGate(**next_gate)
        if not gate_obj.unlock(approval_token, advanced_by):
            logger.warning(
                "BMAdProtocol: advance_phase token mismatch. Expected '%s', got '%s'.",
                next_gate["required_token"],
                approval_token,
            )
            return current

        # Update state
        self._state.gates[gate_obj.gate_id] = asdict(gate_obj)
        old_phase = self._state.current_phase
        self._state.current_phase = gate_obj.to_phase

        # Record history
        self._state.phase_history.append({
            "phase": old_phase,
            "entered_at": _now_iso(),
            "exited_at": _now_iso(),
            "deliverables": [],
        })

        self._persist(self._state)
        new_phase = BMAdPhase(self._state.current_phase)
        logger.info("BMAdProtocol: phase advanced %s → %s", old_phase, new_phase.value)
        return new_phase

    # ------------------------------------------------------------------
    # Blockers
    # ------------------------------------------------------------------

    def register_blocker(self, blocker: BuilderBlocker) -> str:
        self._state.blockers.append(asdict(blocker))
        self._persist(self._state)
        logger.warning(
            "BMAdProtocol: BLOCKER registered [%s] %s — %s",
            blocker.severity,
            blocker.blocker_id,
            blocker.component,
        )
        return blocker.blocker_id

    def resolve_blocker(self, blocker_id: str, resolution: str) -> None:
        for b in self._state.blockers:
            if b["blocker_id"] == blocker_id:
                b["resolved"] = True
                b["resolution"] = resolution
                break
        self._persist(self._state)
        logger.info("BMAdProtocol: blocker %s resolved", blocker_id)

    def get_active_blockers(self) -> list[BuilderBlocker]:
        return [
            BuilderBlocker(**b)
            for b in self._state.blockers
            if not b.get("resolved", False)
        ]

    # ------------------------------------------------------------------
    # Handoffs
    # ------------------------------------------------------------------

    def record_handoff(self, handoff: ArchitectHandoff) -> None:
        self._state.handoffs.append(asdict(handoff))
        self._persist(self._state)
        logger.info("BMAdProtocol: handoff recorded — %s", handoff.handoff_id)

    # ------------------------------------------------------------------
    # Status export
    # ------------------------------------------------------------------

    def export_status(self) -> dict[str, Any]:
        return {
            "current_phase": self._state.current_phase,
            "gates": self._state.gates,
            "active_blockers": [asdict(b) for b in self.get_active_blockers()],
            "handoff_count": len(self._state.handoffs),
            "phase_history": self._state.phase_history,
            "last_updated": self._state.last_updated,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_gate_to(self, target: BMAdPhase) -> dict | None:
        for gate in self._state.gates.values():
            if gate["to_phase"] == target.value:
                return gate
        return None
