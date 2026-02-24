"""Devika PI task loop scaffold with PAULIWHEEL stages."""

from __future__ import annotations

from dataclasses import dataclass

from .context7_guard import Context7Guard
from .safe_commands import DevikaSafeCommandRunner
from .subagents import DevikaSubagentCoordinator


@dataclass(frozen=True)
class DevikaTaskRequest:
    prompt: str
    project_name: str
    execution_profile: str
    bead_id: str


@dataclass(frozen=True)
class DevikaTaskResult:
    status: str
    response: str
    plan_stage: str
    implement_stage: str
    test_stage: str
    evaluate_stage: str
    patch_stage: str


class DevikaTaskLoop:
    """Runs PLAN IMPLEMENT TEST EVALUATE PATCH REPEAT contract."""

    def __init__(self, request: DevikaTaskRequest) -> None:
        self.request = request
        self.context7_guard = Context7Guard()
        self.safe_runner = DevikaSafeCommandRunner(request.execution_profile)
        self.subagents = DevikaSubagentCoordinator()

    def run(self) -> DevikaTaskResult:
        plan = self._plan()
        implementation = self._implement(plan)
        test = self._test(implementation)
        evaluation = self._evaluate(test)
        patch = self._patch_if_needed(evaluation)

        return DevikaTaskResult(
            status="ok",
            response=f"Devika completed bead {self.request.bead_id}",
            plan_stage=plan,
            implement_stage=implementation,
            test_stage=test,
            evaluate_stage=evaluation,
            patch_stage=patch,
        )

    def _plan(self) -> str:
        plan = self.subagents.for_profile(self.request.execution_profile)
        return f"planner:{plan.planner}"

    def _implement(self, _plan_stage: str) -> str:
        self.safe_runner.enforce("python --version")
        return "implemented_with_safe_command_gate"

    def _test(self, _implement_stage: str) -> str:
        return "test_placeholder_pending_real_verification"

    def _evaluate(self, _test_stage: str) -> str:
        return "evaluation_placeholder_pending_acceptance_matrix"

    def _patch_if_needed(self, _evaluate_stage: str) -> str:
        return "no_patch_needed"

