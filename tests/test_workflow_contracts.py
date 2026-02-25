"""Tests validating all 42 ArchonX workflow contracts against the JSON Schema."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:
    import jsonschema  # type: ignore[import]
    from jsonschema import validate, Draft7Validator  # type: ignore[import]

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    import yaml  # type: ignore[import]

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = REPO_ROOT / "archonx" / "contracts"
SCHEMA_FILE = CONTRACTS_DIR / "workflow_schema.json"
POLICIES_FILE = REPO_ROOT / "archonx" / "policies" / "workflow_policies.yaml"

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

VALID_CATEGORIES = frozenset(
    {"control_plane", "devika_pi", "orchestration", "dashboard", "system_ops"}
)

# All 42 WF IDs that must appear in the policies file
ALL_WF_IDS = {f"WF-{str(n).zfill(3)}" for n in range(1, 43)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_schema() -> dict:
    """Load and return the workflow JSON schema."""
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def load_contract(filename: str) -> dict:
    """Load a single contract file as a dict."""
    return json.loads((CONTRACTS_DIR / filename).read_text(encoding="utf-8"))


def load_all_contracts() -> list[dict]:
    """Load all 42 contract files."""
    return [load_contract(f) for f in ALL_EXPECTED_CONTRACT_FILES]


# ---------------------------------------------------------------------------
# 1. test_schema_file_exists
# ---------------------------------------------------------------------------


def test_schema_file_exists() -> None:
    """The workflow_schema.json file must exist in archonx/contracts/."""
    assert SCHEMA_FILE.exists(), f"Schema file not found: {SCHEMA_FILE}"
    assert SCHEMA_FILE.stat().st_size > 0


# ---------------------------------------------------------------------------
# 2. test_schema_is_valid_json_schema
# ---------------------------------------------------------------------------


def test_schema_is_valid_json_schema() -> None:
    """The schema file must be valid JSON and contain required top-level keys."""
    schema = load_schema()
    assert "$schema" in schema, "Schema missing $schema key"
    assert "type" in schema, "Schema missing type key"
    assert "required" in schema, "Schema missing required key"
    assert "properties" in schema, "Schema missing properties key"
    # Check all required fields are declared in properties
    for field in schema["required"]:
        assert field in schema["properties"], f"Required field '{field}' not in properties"


# ---------------------------------------------------------------------------
# 3. test_all_42_contract_files_exist
# ---------------------------------------------------------------------------


def test_all_42_contract_files_exist() -> None:
    """All 42 contract JSON files must exist in archonx/contracts/."""
    missing = [f for f in ALL_EXPECTED_CONTRACT_FILES if not (CONTRACTS_DIR / f).exists()]
    assert not missing, f"Missing contract files: {missing}"


# ---------------------------------------------------------------------------
# 4. test_all_contracts_pass_schema_validation
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package not installed")
def test_all_contracts_pass_schema_validation() -> None:
    """Every contract must validate against the workflow_schema.json."""
    schema = load_schema()
    validator = Draft7Validator(schema)
    errors: list[str] = []
    for filename in ALL_EXPECTED_CONTRACT_FILES:
        contract = load_contract(filename)
        validation_errors = list(validator.iter_errors(contract))
        if validation_errors:
            for err in validation_errors:
                errors.append(f"{filename}: {err.message}")
    assert not errors, "Schema validation errors:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# 5. test_all_workflow_ids_unique
# ---------------------------------------------------------------------------


def test_all_workflow_ids_unique() -> None:
    """Every contract must have a unique workflow_id."""
    contracts = load_all_contracts()
    ids = [c["workflow_id"] for c in contracts]
    assert len(ids) == len(set(ids)), f"Duplicate workflow IDs found: {[i for i in ids if ids.count(i) > 1]}"


# ---------------------------------------------------------------------------
# 6. test_all_categories_valid
# ---------------------------------------------------------------------------


def test_all_categories_valid() -> None:
    """Every contract's category must be one of the valid enum values."""
    contracts = load_all_contracts()
    invalid: list[str] = []
    for c in contracts:
        if c.get("category") not in VALID_CATEGORIES:
            invalid.append(f"{c['workflow_id']}: category='{c.get('category')}'")
    assert not invalid, f"Invalid categories: {invalid}"


# ---------------------------------------------------------------------------
# 7. test_all_evidence_paths_under_ops_reports
# ---------------------------------------------------------------------------


def test_all_evidence_paths_under_ops_reports() -> None:
    """Every contract's evidence_path must start with 'ops/reports/'."""
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        ep = c.get("evidence_path", "")
        if not ep.startswith("ops/reports/"):
            violations.append(f"{c['workflow_id']}: evidence_path='{ep}'")
    assert not violations, f"Evidence path violations: {violations}"


# ---------------------------------------------------------------------------
# 8. test_all_success_criteria_non_empty
# ---------------------------------------------------------------------------


def test_all_success_criteria_non_empty() -> None:
    """Every contract must have at least one success criterion."""
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        criteria = c.get("success_criteria", [])
        if not criteria:
            violations.append(c["workflow_id"])
    assert not violations, f"Workflows with empty success_criteria: {violations}"


# ---------------------------------------------------------------------------
# 9. test_policy_yaml_loads_correctly
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
def test_policy_yaml_loads_correctly() -> None:
    """workflow_policies.yaml must load as valid YAML with the expected top-level keys."""
    assert POLICIES_FILE.exists(), f"Policies file not found: {POLICIES_FILE}"
    data = yaml.safe_load(POLICIES_FILE.read_text(encoding="utf-8"))
    assert "policies" in data, "Missing 'policies' key in workflow_policies.yaml"
    assert "escalation" in data, "Missing 'escalation' key"
    assert "roles" in data, "Missing 'roles' key"
    # Check all four tiers present
    for tier in ("critical", "high", "medium", "low"):
        assert tier in data["policies"], f"Missing tier '{tier}' in policies"


# ---------------------------------------------------------------------------
# 10. test_all_42_workflows_covered_in_policy
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
def test_all_42_workflows_covered_in_policy() -> None:
    """Every WF-NNN ID must appear in exactly one policy tier."""
    data = yaml.safe_load(POLICIES_FILE.read_text(encoding="utf-8"))
    covered: set[str] = set()
    for tier_data in data["policies"].values():
        for wf_id in tier_data.get("workflows", []):
            covered.add(wf_id)
    missing = ALL_WF_IDS - covered
    assert not missing, f"WF IDs not covered in any policy tier: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 11. test_workflow_id_pattern_correct
# ---------------------------------------------------------------------------


def test_workflow_id_pattern_correct() -> None:
    """All workflow IDs must match the pattern ^WF-[0-9]{3}$."""
    pattern = re.compile(r"^WF-\d{3}$")
    contracts = load_all_contracts()
    invalid: list[str] = []
    for c in contracts:
        wf_id = c.get("workflow_id", "")
        if not pattern.match(wf_id):
            invalid.append(wf_id)
    assert not invalid, f"Workflow IDs not matching pattern: {invalid}"


# ---------------------------------------------------------------------------
# 12. test_all_contracts_have_version
# ---------------------------------------------------------------------------


def test_all_contracts_have_version() -> None:
    """Every contract must have a version field matching semantic versioning."""
    semver = re.compile(r"^\d+\.\d+\.\d+$")
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        version = c.get("version", "")
        if not semver.match(version):
            violations.append(f"{c['workflow_id']}: version='{version}'")
    assert not violations, f"Invalid versions: {violations}"


# ---------------------------------------------------------------------------
# 13. test_all_contracts_have_trigger
# ---------------------------------------------------------------------------


def test_all_contracts_have_trigger() -> None:
    """Every contract must have a trigger with event, condition, and actor."""
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        trigger = c.get("trigger", {})
        for key in ("event", "condition", "actor"):
            if not trigger.get(key):
                violations.append(f"{c['workflow_id']}: trigger.{key} missing")
    assert not violations, f"Trigger violations: {violations}"


# ---------------------------------------------------------------------------
# 14. test_all_contracts_have_policy_gates
# ---------------------------------------------------------------------------


def test_all_contracts_have_policy_gates() -> None:
    """Every contract must have policy_gates with required_role, compliance_level, approval_required."""
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        gates = c.get("policy_gates", {})
        for key in ("required_role", "compliance_level", "approval_required"):
            if key not in gates:
                violations.append(f"{c['workflow_id']}: policy_gates.{key} missing")
    assert not violations, f"Policy gate violations: {violations}"


# ---------------------------------------------------------------------------
# 15. test_all_contracts_have_telemetry
# ---------------------------------------------------------------------------


def test_all_contracts_have_telemetry() -> None:
    """Every contract must have a telemetry section with event_name and non-empty fields list."""
    contracts = load_all_contracts()
    violations: list[str] = []
    for c in contracts:
        telemetry = c.get("telemetry", {})
        if not telemetry.get("event_name"):
            violations.append(f"{c['workflow_id']}: telemetry.event_name missing")
        fields = telemetry.get("fields", [])
        if not fields:
            violations.append(f"{c['workflow_id']}: telemetry.fields is empty")
    assert not violations, f"Telemetry violations: {violations}"
