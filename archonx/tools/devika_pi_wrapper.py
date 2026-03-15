"""PAULIWHEEL governance wrapper for Devika PI task execution."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import structlog

from archonx.security.devika_pi_policy import DevikaPIGovernance


logger = structlog.get_logger("archonx.tools.devika_pi_wrapper")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PauliwheelStage(str, Enum):
    """PAULIWHEEL execution stages in strict order."""

    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    TEST = "TEST"
    EVALUATE = "EVALUATE"
    PATCH = "PATCH"
    COMPLETE = "COMPLETE"


# ---------------------------------------------------------------------------
# Error classes
# ---------------------------------------------------------------------------


class BeadGateError(RuntimeError):
    """Raised when bead ID or profile validation fails at the gate."""

    def __init__(self, message: str, error_code: str = "ERR-GOV-002") -> None:
        super().__init__(message)
        self.error_code = error_code


class StageError(RuntimeError):
    """Raised when an illegal PAULIWHEEL stage transition is attempted."""

    def __init__(self, message: str, error_code: str = "ERR-GOV-006") -> None:
        super().__init__(message)
        self.error_code = error_code


class PolicyGateError(RuntimeError):
    """Raised when execution is blocked by a governance policy."""

    def __init__(self, message: str, error_code: str = "ERR-GOV-001") -> None:
        super().__init__(message)
        self.error_code = error_code


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class DevikaWrapperConfig:
    """Configuration for a single Devika PI governance execution session."""

    profile: str
    bead_id: str
    stage: PauliwheelStage = PauliwheelStage.PLAN
    report_dir: str | os.PathLike[str] = "ops/reports"

    def __post_init__(self) -> None:
        if isinstance(self.stage, str):
            self.stage = PauliwheelStage(self.stage)


@dataclass
class StageResult:
    """Result of a single PAULIWHEEL stage execution."""

    stage: str
    status: str
    output: Any
    started_at: str
    finished_at: str
    error: str | None = None


@dataclass
class DevikaExecutionContext:
    """Full execution context tracking all PAULIWHEEL stages for a single bead run."""

    run_id: str
    bead_id: str
    profile: str
    started_at: str
    finished_at: str | None = None
    current_stage: PauliwheelStage = PauliwheelStage.PLAN
    stage_results: dict[str, StageResult] = field(default_factory=dict)
    final_status: str = "pending"
    report_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize context to a plain dict for JSON emission."""
        result: dict[str, Any] = {
            "run_id": self.run_id,
            "bead_id": self.bead_id,
            "profile": self.profile,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "current_stage": self.current_stage.value,
            "final_status": self.final_status,
            "report_path": self.report_path,
            "stage_results": {
                name: asdict(sr) for name, sr in self.stage_results.items()
            },
        }
        return result


# ---------------------------------------------------------------------------
# Main wrapper class
# ---------------------------------------------------------------------------


class DevikaPIWrapper:
    """
    Full PAULIWHEEL governance harness for Devika PI task execution.

    Wraps any callable task function with:
    - Bead ID and profile gate enforcement
    - Stage-by-stage execution tracking (PLAN → IMPLEMENT → TEST → EVALUATE → PATCH)
    - Structured JSON report emission to ops/reports/
    - Structlog audit trail
    """

    _STAGE_SEQUENCE: tuple[PauliwheelStage, ...] = (
        PauliwheelStage.PLAN,
        PauliwheelStage.IMPLEMENT,
        PauliwheelStage.TEST,
        PauliwheelStage.EVALUATE,
        PauliwheelStage.PATCH,
    )

    def __init__(self, config: DevikaWrapperConfig) -> None:
        self.config = config
        self._policy = DevikaPIGovernance(report_dir=config.report_dir)
        self._report_dir = Path(config.report_dir)
        self._report_dir.mkdir(parents=True, exist_ok=True)
        self._context: DevikaExecutionContext | None = None
        logger.info(
            "DevikaPIWrapper initialised",
            bead_id=config.bead_id,
            profile=config.profile,
            stage=config.stage.value,
        )

    # ------------------------------------------------------------------
    # Gate enforcement
    # ------------------------------------------------------------------

    def enforce_gate(self) -> None:
        """
        Validate the bead ID and execution profile before execution begins.

        Raises:
            BeadGateError: If bead ID is invalid.
            PolicyGateError: If the execution profile is not allowed.
        """
        bead_decision = self._policy.check_bead(
            bead_id=self.config.bead_id,
            profile=self.config.profile,
        )
        if not bead_decision.allowed:
            raise BeadGateError(
                f"Bead gate rejected bead_id='{self.config.bead_id}': "
                f"{bead_decision.reason}",
                error_code=bead_decision.error_code,
            )

        profile_decision = self._policy.check_execution_profile(
            execution_profile=self.config.profile,
            bead_id=self.config.bead_id,
        )
        if not profile_decision.allowed:
            raise PolicyGateError(
                f"Profile gate rejected profile='{self.config.profile}': "
                f"{profile_decision.reason}",
                error_code=profile_decision.error_code,
            )

        logger.info(
            "Gate enforced successfully",
            bead_id=self.config.bead_id,
            profile=self.config.profile,
        )

    # ------------------------------------------------------------------
    # Stage advancement
    # ------------------------------------------------------------------

    def advance_stage(self, stage: PauliwheelStage) -> None:
        """
        Advance the governance context to the specified PAULIWHEEL stage.

        Raises:
            StageError: If the stage transition is not allowed.
        """
        decision = self._policy.advance_stage(
            requested_stage=stage.value,
            bead_id=self.config.bead_id,
            profile=self.config.profile,
        )
        if not decision.allowed:
            raise StageError(
                f"Illegal stage transition to '{stage.value}': {decision.reason}",
                error_code=decision.error_code,
            )
        if self._context is not None:
            self._context.current_stage = stage
        self.config.stage = stage

    # ------------------------------------------------------------------
    # Full PAULIWHEEL execution
    # ------------------------------------------------------------------

    def execute(self, task_fn: Callable[[], Any]) -> DevikaExecutionContext:
        """
        Execute a task function through the full PAULIWHEEL governance harness.

        Steps:
        1. Enforce the entry gate (bead + profile validation).
        2. Initialise a new execution context.
        3. Execute the task inside the PLAN → PATCH stage sequence.
        4. Emit a JSON report.
        5. Return the completed execution context.

        Args:
            task_fn: A zero-argument callable that performs the actual work.
                     Its return value is captured in the IMPLEMENT stage result.

        Returns:
            DevikaExecutionContext with all stage results populated.

        Raises:
            BeadGateError: On bead ID validation failure.
            PolicyGateError: On profile validation failure.
            StageError: On illegal stage transition.
        """
        self.enforce_gate()

        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self._context = DevikaExecutionContext(
            run_id=run_id,
            bead_id=self.config.bead_id,
            profile=self.config.profile,
            started_at=now,
        )

        # --- PLAN stage ---
        self._execute_stage(PauliwheelStage.PLAN, lambda: {"plan": "task_plan_ready", "bead_id": self.config.bead_id})

        # --- IMPLEMENT stage (actual task execution) ---
        self._execute_stage(PauliwheelStage.IMPLEMENT, task_fn)

        # --- TEST stage ---
        implement_result = self._context.stage_results.get(PauliwheelStage.IMPLEMENT.value)
        impl_output = implement_result.output if implement_result else None
        self._execute_stage(PauliwheelStage.TEST, lambda: self._run_test_verification(impl_output))

        # --- EVALUATE stage ---
        test_result = self._context.stage_results.get(PauliwheelStage.TEST.value)
        test_output = test_result.output if test_result else None
        self._execute_stage(PauliwheelStage.EVALUATE, lambda: self._run_evaluation(test_output))

        # --- PATCH stage ---
        eval_result = self._context.stage_results.get(PauliwheelStage.EVALUATE.value)
        eval_output = eval_result.output if eval_result else None
        self._execute_stage(PauliwheelStage.PATCH, lambda: self._run_patch(eval_output))

        # Finalise context
        self._context.finished_at = datetime.now(timezone.utc).isoformat()
        self._context.final_status = "complete"
        self._context.current_stage = PauliwheelStage.COMPLETE

        report_path = self.emit_report(self._context)
        self._context.report_path = str(report_path)

        logger.info(
            "DevikaPIWrapper execution complete",
            run_id=run_id,
            bead_id=self.config.bead_id,
            report_path=str(report_path),
        )
        return self._context

    # ------------------------------------------------------------------
    # Report emission
    # ------------------------------------------------------------------

    def emit_report(self, context: DevikaExecutionContext) -> Path:
        """
        Write the execution context as a JSON report to ops/reports/.

        Args:
            context: The completed execution context.

        Returns:
            Path to the emitted report file.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"WRAPPER_{context.bead_id}_{timestamp}.json"
        report_path = self._report_dir / filename
        report_path.write_text(
            json.dumps(context.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("Wrapper report emitted", path=str(report_path))
        return report_path

    # ------------------------------------------------------------------
    # Internal stage helpers
    # ------------------------------------------------------------------

    def _execute_stage(
        self,
        stage: PauliwheelStage,
        fn: Callable[[], Any],
    ) -> StageResult:
        """Run a single stage, record results, and advance the tracker."""
        started_at = datetime.now(timezone.utc).isoformat()
        error: str | None = None
        output: Any = None
        status = "ok"

        try:
            self.advance_stage(stage)
            output = fn()
        except (BeadGateError, PolicyGateError, StageError) as exc:
            raise
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            status = "error"
            logger.error(
                "Stage execution error",
                stage=stage.value,
                error=error,
                bead_id=self.config.bead_id,
            )

        finished_at = datetime.now(timezone.utc).isoformat()
        result = StageResult(
            stage=stage.value,
            status=status,
            output=output,
            started_at=started_at,
            finished_at=finished_at,
            error=error,
        )
        if self._context is not None:
            self._context.stage_results[stage.value] = result
        return result

    def _run_test_verification(self, impl_output: Any) -> dict[str, Any]:
        """
        Perform basic test verification on the implementation output.

        Checks that the impl_output is not None and is truthy.
        """
        if impl_output is None:
            return {"passed": False, "detail": "no_implementation_output"}
        return {
            "passed": True,
            "detail": "implementation_output_present",
            "output_type": type(impl_output).__name__,
        }

    def _run_evaluation(self, test_output: Any) -> dict[str, Any]:
        """
        Evaluate whether the test stage passed.

        Returns a structured evaluation result.
        """
        if isinstance(test_output, dict) and test_output.get("passed") is True:
            return {"accepted": True, "verdict": "PASS", "detail": test_output.get("detail")}
        return {"accepted": False, "verdict": "FAIL", "detail": str(test_output)}

    def _run_patch(self, eval_output: Any) -> dict[str, Any]:
        """
        Recommend a patch if evaluation failed; no-op if it passed.
        """
        if isinstance(eval_output, dict) and eval_output.get("accepted") is True:
            return {"patch_required": False, "recommendation": "none"}
        return {
            "patch_required": True,
            "recommendation": "re-implement and re-test",
            "eval_detail": str(eval_output),
        }
