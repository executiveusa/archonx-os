"""Tests for Devika PI governance: policy, stage enforcement, and task loop."""

from __future__ import annotations

import pytest

from archonx.security.devika_pi_policy import (
    DevikaPIGovernance,
    ALLOWED_EXECUTION_PROFILES,
    PAULIWHEEL_STAGES,
)
from agents.devika.extensions.context7_guard import Context7Guard
from agents.devika.extensions.safe_commands import DevikaSafeCommandRunner, DevikaSafetyError
from agents.devika.extensions.subagents import DevikaSubagentCoordinator
from agents.devika.extensions.task_loop import DevikaTaskLoop, DevikaTaskRequest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def governance(tmp_path: "pytest.TempPathFactory") -> DevikaPIGovernance:
    """Return a fresh DevikaPIGovernance wired to a temp report dir."""
    return DevikaPIGovernance(report_dir=str(tmp_path))


@pytest.fixture()
def task_request_default() -> DevikaTaskRequest:
    return DevikaTaskRequest(
        prompt="print('hello')",
        project_name="test-project",
        execution_profile="devika-pi-default",
        bead_id="BEAD-DEVIKA-PI-001",
    )


@pytest.fixture()
def task_loop_default(task_request_default: DevikaTaskRequest) -> DevikaTaskLoop:
    return DevikaTaskLoop(task_request_default)


# ---------------------------------------------------------------------------
# 1. test_valid_profile_allowed
# ---------------------------------------------------------------------------


def test_valid_profile_allowed(governance: DevikaPIGovernance) -> None:
    """All three declared profiles must be allowed."""
    for profile in ALLOWED_EXECUTION_PROFILES:
        decision = governance.check_execution_profile(
            execution_profile=profile,
            bead_id="BEAD-DEVIKA-PI-001",
        )
        assert decision.allowed is True, f"Profile '{profile}' should be allowed"
        assert decision.reason == "ok"
        assert decision.error_code == "OK-000"


# ---------------------------------------------------------------------------
# 2. test_invalid_profile_blocked
# ---------------------------------------------------------------------------


def test_invalid_profile_blocked(governance: DevikaPIGovernance) -> None:
    """An unknown profile must be blocked with error code ERR-GOV-001."""
    decision = governance.check_execution_profile(
        execution_profile="devika-pi-UNKNOWN",
        bead_id="BEAD-DEVIKA-PI-001",
    )
    assert decision.allowed is False
    assert decision.reason == "invalid_execution_profile"
    assert decision.error_code == "ERR-GOV-001"


# ---------------------------------------------------------------------------
# 3. test_valid_bead_id_accepted (BEAD-DEVIKA-PI-001)
# ---------------------------------------------------------------------------


def test_valid_bead_id_accepted(governance: DevikaPIGovernance) -> None:
    """BEAD-DEVIKA-PI-001 must pass bead validation."""
    decision = governance.check_bead(bead_id="BEAD-DEVIKA-PI-001")
    assert decision.allowed is True
    assert decision.reason == "ok"
    assert decision.error_code == "OK-000"


# ---------------------------------------------------------------------------
# 4. test_phase_bead_id_accepted (BEAD-P2-001)
# ---------------------------------------------------------------------------


def test_phase_bead_id_accepted(governance: DevikaPIGovernance) -> None:
    """BEAD-P2-001 must be accepted as it starts with the BEAD-P prefix."""
    decision = governance.check_bead(bead_id="BEAD-P2-001")
    assert decision.allowed is True, f"Expected allowed but got: {decision.reason}"
    assert decision.error_code == "OK-000"


# ---------------------------------------------------------------------------
# 5. test_empty_bead_blocked
# ---------------------------------------------------------------------------


def test_empty_bead_blocked(governance: DevikaPIGovernance) -> None:
    """Empty bead ID must be blocked with error code ERR-GOV-003."""
    decision = governance.check_bead(bead_id="")
    assert decision.allowed is False
    assert decision.reason == "empty_bead_id"
    assert decision.error_code == "ERR-GOV-003"


# ---------------------------------------------------------------------------
# 6. test_invalid_bead_prefix_blocked
# ---------------------------------------------------------------------------


def test_invalid_bead_prefix_blocked(governance: DevikaPIGovernance) -> None:
    """A bead ID that does not start with a valid prefix must be blocked."""
    decision = governance.check_bead(bead_id="INVALID-PREFIX-001")
    assert decision.allowed is False
    assert decision.reason == "invalid_bead_id"
    assert decision.error_code == "ERR-GOV-002"


# ---------------------------------------------------------------------------
# 7. test_safe_command_allowed (python --version)
# ---------------------------------------------------------------------------


def test_safe_command_allowed(governance: DevikaPIGovernance) -> None:
    """'python --version' must be allowed for the default profile."""
    decision = governance.check_command(
        execution_profile="devika-pi-default",
        command="python --version",
        bead_id="BEAD-DEVIKA-PI-001",
    )
    assert decision.allowed is True
    assert decision.error_code == "OK-000"


# ---------------------------------------------------------------------------
# 8. test_dangerous_command_blocked (rm -rf /)
# ---------------------------------------------------------------------------


def test_dangerous_command_blocked(governance: DevikaPIGovernance) -> None:
    """'rm -rf /' must be blocked regardless of profile."""
    decision = governance.check_command(
        execution_profile="devika-pi-default",
        command="rm -rf /",
        bead_id="BEAD-DEVIKA-PI-001",
    )
    assert decision.allowed is False
    assert decision.error_code == "ERR-GOV-007"


# ---------------------------------------------------------------------------
# 9. test_stage_advance_allowed (PLAN→IMPLEMENT)
# ---------------------------------------------------------------------------


def test_stage_advance_allowed(governance: DevikaPIGovernance) -> None:
    """Advancing from PLAN to IMPLEMENT must be allowed after PLAN is set."""
    # Advance to PLAN first
    plan_decision = governance.advance_stage(
        requested_stage="PLAN",
        bead_id="BEAD-DEVIKA-PI-001",
    )
    assert plan_decision.allowed is True

    # Advance to IMPLEMENT
    impl_decision = governance.advance_stage(
        requested_stage="IMPLEMENT",
        bead_id="BEAD-DEVIKA-PI-001",
    )
    assert impl_decision.allowed is True
    assert impl_decision.error_code == "OK-000"


# ---------------------------------------------------------------------------
# 10. test_invalid_stage_advance_blocked (COMPLETE→PLAN equivalent: skip stages)
# ---------------------------------------------------------------------------


def test_invalid_stage_advance_blocked(governance: DevikaPIGovernance) -> None:
    """Skipping stages (e.g. going straight to TEST from PLAN) must be blocked."""
    governance.advance_stage("PLAN", bead_id="BEAD-DEVIKA-PI-001")
    # Try skipping IMPLEMENT and going directly to TEST
    decision = governance.advance_stage("TEST", bead_id="BEAD-DEVIKA-PI-001")
    assert decision.allowed is False
    assert decision.reason == "illegal_stage_advance"
    assert decision.error_code == "ERR-GOV-006"


# ---------------------------------------------------------------------------
# 11. test_context7_guard_blocks_unresolved_library
# ---------------------------------------------------------------------------


def test_context7_guard_blocks_unresolved_library() -> None:
    """Context7Guard must block use of a library that has not been resolved."""
    guard = Context7Guard()
    result = guard.check_library_use("numpy")
    assert result.allowed is False
    assert "context7_resolve_missing" in result.reason


# ---------------------------------------------------------------------------
# 12. test_context7_guard_allows_resolved_library
# ---------------------------------------------------------------------------


def test_context7_guard_allows_resolved_library() -> None:
    """Context7Guard must allow use of a library that has been resolved and queried."""
    guard = Context7Guard()
    guard.mark_resolved("numpy")
    guard.mark_queried("numpy")
    result = guard.check_library_use("numpy")
    assert result.allowed is True
    assert result.reason == "ok"


# ---------------------------------------------------------------------------
# 13. test_safe_runner_raises_on_blocked_command
# ---------------------------------------------------------------------------


def test_safe_runner_raises_on_blocked_command() -> None:
    """DevikaSafeCommandRunner.enforce() must raise DevikaSafetyError for 'rm -rf /'."""
    runner = DevikaSafeCommandRunner(profile="devika-pi-default")
    with pytest.raises(DevikaSafetyError):
        runner.enforce("rm -rf /")


# ---------------------------------------------------------------------------
# 14. test_subagent_coordinator_returns_correct_agents_for_profile
# ---------------------------------------------------------------------------


def test_subagent_coordinator_returns_correct_agents_for_profile() -> None:
    """DevikaSubagentCoordinator must return profile-specific agent names."""
    coordinator = DevikaSubagentCoordinator()

    # Default profile
    default_plan = coordinator.for_profile("devika-pi-default")
    assert default_plan.planner == "default_planner"
    assert default_plan.implementer == "default_implementer"

    # Safe profile
    safe_plan = coordinator.for_profile("devika-pi-safe")
    assert safe_plan.planner == "guardrail_planner"
    assert safe_plan.implementer == "safe_implementer"

    # Research profile
    research_plan = coordinator.for_profile("devika-pi-research")
    assert research_plan.planner == "research_planner"
    assert research_plan.implementer == "prototype_builder"


# ---------------------------------------------------------------------------
# 15. test_task_loop_returns_result_with_bead_id
# ---------------------------------------------------------------------------


def test_task_loop_returns_result_with_bead_id(
    task_loop_default: DevikaTaskLoop,
) -> None:
    """DevikaTaskLoop.run() must return a result that references the bead_id."""
    result = task_loop_default.run()
    assert result.status == "ok"
    assert "BEAD-DEVIKA-PI-001" in result.response
    assert result.bead_id if hasattr(result, "bead_id") else "BEAD-DEVIKA-PI-001" in result.response


# ---------------------------------------------------------------------------
# 16. test_task_loop_plan_stage_contains_bead_info
# ---------------------------------------------------------------------------


def test_task_loop_plan_stage_contains_bead_info(
    task_loop_default: DevikaTaskLoop,
) -> None:
    """The plan_stage result should contain bead_id information."""
    result = task_loop_default.run()
    assert "BEAD-DEVIKA-PI-001" in result.plan_stage


# ---------------------------------------------------------------------------
# 17. test_task_loop_implement_stage_passed_command_gate
# ---------------------------------------------------------------------------


def test_task_loop_implement_stage_passed_command_gate(
    task_loop_default: DevikaTaskLoop,
) -> None:
    """The implement_stage string must confirm the command gate passed."""
    result = task_loop_default.run()
    assert "command_gate=passed" in result.implement_stage


# ---------------------------------------------------------------------------
# 18. test_task_loop_test_stage_not_fail_on_valid_prompt
# ---------------------------------------------------------------------------


def test_task_loop_test_stage_not_fail_on_valid_prompt() -> None:
    """A valid Python prompt must produce TEST_PASS in the test stage."""
    request = DevikaTaskRequest(
        prompt="def add(a, b): return a + b",
        project_name="test-proj",
        execution_profile="devika-pi-default",
        bead_id="BEAD-DEVIKA-PI-002",
    )
    loop = DevikaTaskLoop(request)
    result = loop.run()
    assert result.test_stage.startswith("TEST_PASS")


# ---------------------------------------------------------------------------
# 19. test_task_loop_passed_field_true_on_success
# ---------------------------------------------------------------------------


def test_task_loop_passed_field_true_on_success() -> None:
    """passed=True when the test stage passes evaluation."""
    request = DevikaTaskRequest(
        prompt="x = 1 + 1",
        project_name="test-proj",
        execution_profile="devika-pi-default",
        bead_id="BEAD-DEVIKA-PI-003",
    )
    loop = DevikaTaskLoop(request)
    result = loop.run()
    # Evaluate stage depends on test; as long as TEST_PASS appears, passed is True
    if result.test_stage.startswith("TEST_PASS"):
        assert result.passed is True
    else:
        assert result.passed is False


# ---------------------------------------------------------------------------
# 20. test_audit_log_populated_after_checks
# ---------------------------------------------------------------------------


def test_audit_log_populated_after_checks(governance: DevikaPIGovernance) -> None:
    """Audit log must contain entries for each policy check performed."""
    governance.check_execution_profile("devika-pi-default", bead_id="BEAD-DEVIKA-PI-001")
    governance.check_bead("BEAD-DEVIKA-PI-001")
    governance.check_command("devika-pi-default", "python --version", bead_id="BEAD-DEVIKA-PI-001")

    log = governance.get_audit_log()
    assert len(log) >= 3
    check_types = {entry.check_type for entry in log}
    assert "execution_profile" in check_types
    assert "bead_validation" in check_types
    assert "command_check" in check_types
