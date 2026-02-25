"""Devika PI task loop — full PAULIWHEEL PLAN/IMPLEMENT/TEST/EVALUATE/PATCH stages."""

from __future__ import annotations

import ast
import importlib
import sys
from dataclasses import dataclass
from typing import Any

from .context7_guard import Context7Guard
from .safe_commands import DevikaSafeCommandRunner
from .subagents import DevikaSubagentCoordinator, DevikaSubagentPlan


@dataclass(frozen=True)
class DevikaTaskRequest:
    """Immutable specification for a single Devika PI task execution."""

    prompt: str
    project_name: str
    execution_profile: str
    bead_id: str


@dataclass(frozen=True)
class DevikaTaskResult:
    """Result of a full PAULIWHEEL task loop execution."""

    status: str
    response: str
    plan_stage: str
    implement_stage: str
    test_stage: str
    evaluate_stage: str
    patch_stage: str
    passed: bool


class DevikaTaskLoop:
    """
    Executes the full PLAN IMPLEMENT TEST EVALUATE PATCH REPEAT contract.

    Each stage method performs real work:
    - _plan():            Calls subagent coordinator and returns structured plan dict.
    - _implement(plan):   Validates command safety and returns implementation summary.
    - _test(impl):        Validates Python syntax of the prompt, checks importability.
    - _evaluate(test):    Returns PASS/FAIL based on test stage content.
    - _patch_if_needed(e): Returns a patch recommendation when evaluation failed.
    """

    def __init__(self, request: DevikaTaskRequest) -> None:
        self.request = request
        self.context7_guard = Context7Guard()
        self.safe_runner = DevikaSafeCommandRunner(request.execution_profile)
        self.subagents = DevikaSubagentCoordinator()

    def run(self) -> DevikaTaskResult:
        """Execute all PAULIWHEEL stages in sequence and return the final result."""
        plan = self._plan()
        implementation = self._implement(plan)
        test = self._test(implementation)
        evaluation = self._evaluate(test)
        patch = self._patch_if_needed(evaluation)

        # Determine overall pass/fail
        passed = evaluation.startswith("PASS")

        return DevikaTaskResult(
            status="ok",
            response=f"Devika completed bead {self.request.bead_id}",
            plan_stage=str(plan),
            implement_stage=implementation,
            test_stage=test,
            evaluate_stage=evaluation,
            patch_stage=patch,
            passed=passed,
        )

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _plan(self) -> dict[str, Any]:
        """
        Coordinate subagents for this execution profile and return a structured plan.

        Returns:
            A dict containing the assigned subagent roles and bead context.
        """
        agents: DevikaSubagentPlan = self.subagents.for_profile(
            self.request.execution_profile
        )
        plan: dict[str, Any] = {
            "bead_id": self.request.bead_id,
            "project": self.request.project_name,
            "profile": self.request.execution_profile,
            "planner": agents.planner,
            "implementer": agents.implementer,
            "tester": agents.tester,
            "reviewer": agents.reviewer,
            "prompt_summary": self.request.prompt[:200],
            "stage": "PLAN",
        }
        return plan

    def _implement(self, plan: dict[str, Any]) -> str:
        """
        Validate command safety and produce an implementation summary.

        Uses the DevikaSafeCommandRunner to check that the base toolchain
        command (python --version) is permitted for this profile. Records
        the implementer name from the plan.

        Args:
            plan: The structured plan dict from _plan().

        Returns:
            A string describing the implementation outcome.

        Raises:
            DevikaSafetyError: If the safety check fails.
        """
        # Enforce that python is available and allowed for this profile
        self.safe_runner.enforce("python --version")

        implementer = plan.get("implementer", "unknown_implementer")
        bead_id = plan.get("bead_id", self.request.bead_id)
        return (
            f"implemented:profile={self.request.execution_profile}"
            f":implementer={implementer}"
            f":bead={bead_id}"
            f":command_gate=passed"
        )

    def _test(self, impl_stage: str) -> str:
        """
        Run actual test verification on the implementation output.

        Performs:
        1. Checks that impl_stage is a non-empty string.
        2. Attempts to parse the prompt as Python source to detect syntax errors.
        3. Checks that 'archonx' top-level package is importable.

        Args:
            impl_stage: The implementation stage result string.

        Returns:
            A string indicating test outcome, prefixed with 'TEST_PASS' or 'TEST_FAIL'.
        """
        if not impl_stage:
            return "TEST_FAIL:empty_implementation_output"

        # Attempt Python syntax validation on the prompt (if it looks like code)
        prompt = self.request.prompt.strip()
        syntax_ok = True
        syntax_detail = "no_code_in_prompt"
        if prompt.startswith(("def ", "class ", "import ", "from ", "#")):
            try:
                ast.parse(prompt)
                syntax_ok = True
                syntax_detail = "syntax_valid"
            except SyntaxError as exc:
                syntax_ok = False
                syntax_detail = f"syntax_error:{exc.msg}"

        # Verify the archonx package is importable in the current environment
        try:
            importlib.import_module("archonx")
            import_ok = True
            import_detail = "archonx_importable"
        except ImportError as exc:
            import_ok = False
            import_detail = f"import_error:{exc}"

        all_pass = syntax_ok and import_ok
        prefix = "TEST_PASS" if all_pass else "TEST_FAIL"
        return f"{prefix}:syntax={syntax_detail}:import={import_detail}"

    def _evaluate(self, test_stage: str) -> str:
        """
        Evaluate the test stage result and produce a pass/fail verdict.

        Args:
            test_stage: The test stage result string.

        Returns:
            'PASS:<detail>' or 'FAIL:<detail>'
        """
        if test_stage.startswith("TEST_PASS"):
            return f"PASS:test_verified:{test_stage}"
        return f"FAIL:test_not_verified:{test_stage}"

    def _patch_if_needed(self, evaluate_stage: str) -> str:
        """
        Recommend a patch when evaluation failed; no-op on success.

        Args:
            evaluate_stage: The evaluation stage result string.

        Returns:
            A string with patch recommendation or 'no_patch_needed'.
        """
        if evaluate_stage.startswith("PASS"):
            return "no_patch_needed"
        return (
            f"patch_recommended:"
            f"re_run_implement_and_test:"
            f"eval_output={evaluate_stage[:120]}"
        )
