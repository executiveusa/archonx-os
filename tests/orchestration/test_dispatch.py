"""Tests for dispatch coordination from routing plan to worker envelope."""

import tempfile
from pathlib import Path

from archonx.orchestration import DispatchCoordinator
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


def _build_registry() -> RepoRegistry:
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_dispatch.db"
    yaml_path = Path(tmpdir.name) / "dispatch_index.yaml"
    yaml_path.write_text(
        """
archonx_repo_index_spec:
  version: "1.0.0"
  mode: "index_only"
  do_not_clone: true
  do_not_vendor: true
  do_not_mirror: true

  teams:
    - id: team_a
      display: "Team A"

  domain_types:
    - id: saas
      description: "SaaS"

  repos:
    - {id: 1, name: "frontend-repo", url: "https://github.com/test/frontend", vis: public, kind: orig, team_id: team_a, domain_type_id: saas, placement: frontend_layer}
""",
        encoding="utf-8",
    )
    registry = RepoRegistry(db_path)
    registry.ingest_yaml(yaml_path)
    registry._tempdir = tmpdir
    return registry


def test_dispatch_decision_builds_task_envelope() -> None:
    registry = _build_registry()
    coordinator = DispatchCoordinator(Router(registry))

    decision = coordinator.create_dispatch_decision(
        [1],
        "ship_ui",
        objective="Ship the frontend update",
    )

    assert decision.plan.task_intent == "frontend_change"
    assert decision.primary_worker.id == "goose"
    assert decision.envelope.objective == "Ship the frontend update"
    assert decision.envelope.allowed_tools == ["mcp2cli", "repo_inventory", "extension_registry"]
    assert decision.required_env_categories == ["tool_invocation"]
    assert decision.env_profiles[0]["owner"] == "mcp2cli"
    assert decision.policy["approval_integrations"] == []
    assert decision.env_audit["is_ready"] is True
    assert decision.envelope.required_approvals == []
    assert decision.envelope.validate() == []
    registry.close()
    registry._tempdir.cleanup()


def test_dispatch_requires_mcp2cli() -> None:
    registry = _build_registry()
    coordinator = DispatchCoordinator(Router(registry))
    plan = coordinator.router.route([1], "ship_ui")
    plan.required_integrations = []

    try:
        coordinator._validate_required_integrations(plan.required_integrations)
    except ValueError as exc:
        assert "mcp2cli" in str(exc)
    else:
        raise AssertionError("expected mcp2cli validation failure")
    registry.close()
    registry._tempdir.cleanup()
