"""Phase 5 validation script — checks all deliverables and emits a validation report."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).parent.parent.parent
OPS_REPORTS = REPO_ROOT / "ops" / "reports"
CONTRACTS_DIR = REPO_ROOT / "archonx" / "contracts"

ALL_EXPECTED_CONTRACT_FILES = [
    "workflow_001_phase_gate_approval.json",
    "workflow_002_phase_gate_rejection.json",
    "workflow_003_bead_execution_start.json",
    "workflow_004_bead_status_report.json",
    "workflow_005_build_checkpoint.json",
    "workflow_006_test_suite_run.json",
    "workflow_007_coverage_report.json",
    "workflow_008_rollback_trigger.json",
    "workflow_009_emergency_pause.json",
    "workflow_010_agent_telemetry.json",
    "workflow_011_dashboard_update.json",
    "workflow_012_alert_dispatch.json",
    "workflow_013_devika_task_receive.json",
    "workflow_014_context7_fetch.json",
    "workflow_015_code_generation.json",
    "workflow_016_test_execution.json",
    "workflow_017_build_validation.json",
    "workflow_018_approval_gate_check.json",
    "workflow_019_merge_to_main.json",
    "workflow_020_execution_report.json",
    "workflow_021_subagent_spawn.json",
    "workflow_022_subagent_status.json",
    "workflow_023_ralphy_coordination.json",
    "workflow_024_dependency_resolution.json",
    "workflow_025_parallel_execution.json",
    "workflow_026_result_consolidation.json",
    "workflow_027_error_handling.json",
    "workflow_028_retry_logic.json",
    "workflow_029_timeout_management.json",
    "workflow_030_agent_communication.json",
    "workflow_031_approval_gate_ui.json",
    "workflow_032_dashboard_refresh.json",
    "workflow_033_telemetry_update.json",
    "workflow_034_manual_intervention.json",
    "workflow_035_config_change.json",
    "workflow_036_credential_update.json",
    "workflow_037_report_generation.json",
    "workflow_038_health_check.json",
    "workflow_039_monitoring_alert.json",
    "workflow_040_log_aggregation.json",
    "workflow_041_compliance_audit.json",
    "workflow_042_archive_cleanup.json",
]

PHASE_2_4_DELIVERABLES: list[Path] = [
    # Phase 2 — Security & governance
    REPO_ROOT / "archonx" / "security" / "devika_pi_policy.py",
    REPO_ROOT / "archonx" / "tools" / "devika_pi_wrapper.py",
    REPO_ROOT / "archonx" / "config" / "devika_pi_policy.yaml",
    REPO_ROOT / "archonx" / "contracts" / "workflow_schema.json",
    REPO_ROOT / "archonx" / "policies" / "workflow_policies.yaml",
    REPO_ROOT / "agents" / "devika" / "extensions" / "task_loop.py",
    # Phase 3 — Tests
    REPO_ROOT / "tests" / "test_devika_pi_governance.py",
    REPO_ROOT / "tests" / "test_workflow_contracts.py",
    # Phase 4 — Lightning
    REPO_ROOT / "agents" / "lightning" / "__init__.py",
    REPO_ROOT / "agents" / "lightning" / "bootstrap.py",
    REPO_ROOT / "agents" / "lightning" / "bead_executor.py",
    REPO_ROOT / "agents" / "lightning" / "registry.py",
]


def _check(label: str, passed: bool, detail: str = "") -> dict[str, Any]:
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return {"check": label, "status": status, "detail": detail}


def validate_contracts() -> list[dict[str, Any]]:
    """Verify all 42 contract JSON files exist and contain valid JSON."""
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid_json: list[str] = []

    for filename in ALL_EXPECTED_CONTRACT_FILES:
        fpath = CONTRACTS_DIR / filename
        if not fpath.exists():
            missing.append(filename)
        else:
            try:
                json.loads(fpath.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                invalid_json.append(f"{filename}: {exc}")

    results.append(_check("All 42 contract files exist", not missing, str(missing) if missing else ""))
    results.append(_check("All contract files contain valid JSON", not invalid_json, str(invalid_json) if invalid_json else ""))
    return results


def validate_deliverables() -> list[dict[str, Any]]:
    """Verify all Phase 2–4 deliverable files exist."""
    results: list[dict[str, Any]] = []
    missing = [str(p.relative_to(REPO_ROOT)) for p in PHASE_2_4_DELIVERABLES if not p.exists()]
    results.append(_check("All Phase 2–4 deliverables exist", not missing, str(missing) if missing else ""))
    return results


def validate_tests() -> list[dict[str, Any]]:
    """Run pytest and report pass/fail."""
    results: list[dict[str, Any]] = []
    cmd = [sys.executable, "-m", "pytest",
           str(REPO_ROOT / "tests" / "test_devika_pi_governance.py"),
           str(REPO_ROOT / "tests" / "test_workflow_contracts.py"),
           "-v", "--tb=short", "-q"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=120,
        )
        passed = proc.returncode == 0
        detail = proc.stdout[-500:] if proc.stdout else proc.stderr[-500:]
        results.append(_check("pytest test suite passes", passed, detail.strip()))
    except subprocess.TimeoutExpired:
        results.append(_check("pytest test suite passes", False, "timeout"))
    except FileNotFoundError as exc:
        results.append(_check("pytest test suite passes", False, str(exc)))
    return results


def main() -> int:
    """Run all Phase 5 validation checks and emit a JSON report."""
    print("=" * 60)
    print("ARCHONX PHASE 5 VALIDATION")
    print("=" * 60)

    OPS_REPORTS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    all_results: list[dict[str, Any]] = []

    print("\n[1] Contract file validation")
    all_results.extend(validate_contracts())

    print("\n[2] Phase 2–4 deliverable presence")
    all_results.extend(validate_deliverables())

    print("\n[3] Test suite execution")
    all_results.extend(validate_tests())

    total = len(all_results)
    passed_count = sum(1 for r in all_results if r["status"] == "PASS")
    failed_count = total - passed_count
    overall_status = "PASS" if failed_count == 0 else "FAIL"

    report: dict[str, Any] = {
        "report_type": "PHASE_5_VALIDATION_REPORT",
        "generated_at": timestamp,
        "overall_status": overall_status,
        "total_checks": total,
        "passed": passed_count,
        "failed": failed_count,
        "results": all_results,
    }

    report_path = OPS_REPORTS / "PHASE_5_VALIDATION_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"OVERALL: {overall_status} ({passed_count}/{total} checks passed)")
    print(f"Report:  {report_path}")
    print("=" * 60)

    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
