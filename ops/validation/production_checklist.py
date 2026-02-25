"""Production readiness checklist — final go/no-go check before deployment."""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).parent.parent.parent
OPS_REPORTS = REPO_ROOT / "ops" / "reports"
CONTRACTS_DIR = REPO_ROOT / "archonx" / "contracts"

# Ensure repo root is on sys.path so all ArchonX modules are importable
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ALL_EXPECTED_CONTRACT_FILES = [
    f"workflow_{str(n).zfill(3)}_"
    + {
        1: "phase_gate_approval",
        2: "phase_gate_rejection",
        3: "bead_execution_start",
        4: "bead_status_report",
        5: "build_checkpoint",
        6: "test_suite_run",
        7: "coverage_report",
        8: "rollback_trigger",
        9: "emergency_pause",
        10: "agent_telemetry",
        11: "dashboard_update",
        12: "alert_dispatch",
        13: "devika_task_receive",
        14: "context7_fetch",
        15: "code_generation",
        16: "test_execution",
        17: "build_validation",
        18: "approval_gate_check",
        19: "merge_to_main",
        20: "execution_report",
        21: "subagent_spawn",
        22: "subagent_status",
        23: "ralphy_coordination",
        24: "dependency_resolution",
        25: "parallel_execution",
        26: "result_consolidation",
        27: "error_handling",
        28: "retry_logic",
        29: "timeout_management",
        30: "agent_communication",
        31: "approval_gate_ui",
        32: "dashboard_refresh",
        33: "telemetry_update",
        34: "manual_intervention",
        35: "config_change",
        36: "credential_update",
        37: "report_generation",
        38: "health_check",
        39: "monitoring_alert",
        40: "log_aggregation",
        41: "compliance_audit",
        42: "archive_cleanup",
    }[n]
    + ".json"
    for n in range(1, 43)
]

AGENT_CONFIGS: list[Path] = [
    REPO_ROOT / "agents" / "devika" / "config.json",
    REPO_ROOT / "agents" / "devika" / "registry.json",
]

IMPORTABLE_MODULES: list[str] = [
    "archonx.security.devika_pi_policy",
    "archonx.tools.devika_pi_wrapper",
    "agents.lightning.bootstrap",
    "agents.lightning.bead_executor",
    "agents.lightning.registry",
    "agents.devika.extensions.task_loop",
    "agents.devika.extensions.context7_guard",
    "agents.devika.extensions.safe_commands",
    "agents.devika.extensions.subagents",
]


def _check(label: str, passed: bool, detail: str = "") -> dict[str, Any]:
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}" + (f"\n         {detail}" if detail else ""))
    return {"check": label, "status": status, "detail": detail}


def check_wrapper_importable() -> dict[str, Any]:
    """Verify devika_pi_wrapper.py exists and imports without error."""
    wrapper_path = REPO_ROOT / "archonx" / "tools" / "devika_pi_wrapper.py"
    if not wrapper_path.exists():
        return _check("devika_pi_wrapper.py exists and imports", False, "file not found")
    try:
        importlib.import_module("archonx.tools.devika_pi_wrapper")
        return _check("devika_pi_wrapper.py exists and imports", True)
    except Exception as exc:  # noqa: BLE001
        return _check("devika_pi_wrapper.py exists and imports", False, str(exc))


def check_all_contracts_exist() -> dict[str, Any]:
    """Verify all 42 contract JSON files are present."""
    missing = [f for f in ALL_EXPECTED_CONTRACT_FILES if not (CONTRACTS_DIR / f).exists()]
    return _check(
        "All 42 workflow contracts exist",
        not missing,
        f"Missing: {missing}" if missing else "",
    )


def check_agent_configs() -> dict[str, Any]:
    """Verify agent config files exist."""
    missing = [str(p.relative_to(REPO_ROOT)) for p in AGENT_CONFIGS if not p.exists()]
    return _check(
        "Agent config files exist",
        not missing,
        f"Missing: {missing}" if missing else "",
    )


def check_lightning_importable() -> dict[str, Any]:
    """Verify agents.lightning bootstrap package imports cleanly."""
    try:
        importlib.import_module("agents.lightning")
        return _check("agents.lightning bootstrap importable", True)
    except Exception as exc:  # noqa: BLE001
        return _check("agents.lightning bootstrap importable", False, str(exc))


def check_all_modules_importable() -> list[dict[str, Any]]:
    """Try to import all production modules."""
    results: list[dict[str, Any]] = []
    for module_name in IMPORTABLE_MODULES:
        try:
            importlib.import_module(module_name)
            results.append(_check(f"{module_name} importable", True))
        except Exception as exc:  # noqa: BLE001
            results.append(_check(f"{module_name} importable", False, str(exc)))
    return results


def check_policies_file() -> dict[str, Any]:
    """Verify workflow_policies.yaml exists and is non-empty."""
    policies_path = REPO_ROOT / "archonx" / "policies" / "workflow_policies.yaml"
    exists = policies_path.exists() and policies_path.stat().st_size > 0
    return _check("workflow_policies.yaml exists and non-empty", exists)


def check_config_yaml() -> dict[str, Any]:
    """Verify devika_pi_policy.yaml exists."""
    config_path = REPO_ROOT / "archonx" / "config" / "devika_pi_policy.yaml"
    exists = config_path.exists() and config_path.stat().st_size > 0
    return _check("devika_pi_policy.yaml exists and non-empty", exists)


def main() -> int:
    """Run all production readiness checks and emit PRODUCTION_READINESS.json."""
    print("=" * 60)
    print("ARCHONX PRODUCTION READINESS CHECKLIST")
    print("=" * 60)

    OPS_REPORTS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    results: list[dict[str, Any]] = []

    print("\n[1] Core module imports")
    results.extend(check_all_modules_importable())

    print("\n[2] devika_pi_wrapper.py")
    results.append(check_wrapper_importable())

    print("\n[3] Contract files")
    results.append(check_all_contracts_exist())

    print("\n[4] Agent configs")
    results.append(check_agent_configs())

    print("\n[5] Lightning bootstrap")
    results.append(check_lightning_importable())

    print("\n[6] Policy / config files")
    results.append(check_policies_file())
    results.append(check_config_yaml())

    total = len(results)
    passed_count = sum(1 for r in results if r["status"] == "PASS")
    failed_count = total - passed_count
    overall = "READY" if failed_count == 0 else "NOT_READY"

    report: dict[str, Any] = {
        "report_type": "PRODUCTION_READINESS",
        "generated_at": timestamp,
        "overall": overall,
        "total_checks": total,
        "passed": passed_count,
        "failed": failed_count,
        "checks": results,
    }

    report_path = OPS_REPORTS / "PRODUCTION_READINESS.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"PRODUCTION STATUS: {overall} ({passed_count}/{total} checks passed)")
    print(f"Report: {report_path}")
    print("=" * 60)

    return 0 if overall == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
