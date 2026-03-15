"""Tests for phone-originated remote desktop planning."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from archonx.agents import PhoneDesktopBridge
from archonx.orchestration import DispatchCoordinator
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


def _build_registry() -> RepoRegistry:
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_phone_desktop.db"
    yaml_path = Path(tmpdir.name) / "phone_desktop_index.yaml"
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
    - id: tool
      description: "Tool"

  repos:
    - {id: 1, name: "archonx-os", url: "https://github.com/executiveusa/archonx-os", vis: public, kind: orig, team_id: team_a, domain_type_id: tool, placement: core_dependency}
""",
        encoding="utf-8",
    )
    registry = RepoRegistry(db_path)
    registry.ingest_yaml(yaml_path)
    registry._tempdir = tmpdir
    return registry


def test_phone_desktop_bridge_creates_governed_remote_plan() -> None:
    registry = _build_registry()
    with patch.dict(os.environ, {"ARCHONX_ENABLE_DESKTOP_CONTROL": "true"}, clear=False):
        coordinator = DispatchCoordinator(Router(registry), enforce_env_readiness=True)
        bridge = PhoneDesktopBridge(coordinator)
        plan = bridge.plan_remote_desktop_action(
            command_text="Open the desktop browser and go to the admin panel.",
            repo_ids=[1],
            bead_id="BEAD-PHONE-DESKTOP-001",
            caller_number="+13235550000",
            persona_override="AX-PAULI-BRAIN-002",
        )

    assert plan.persona_id == "AX-PAULI-BRAIN-002"
    assert plan.approval_state == "awaiting_approval"
    assert plan.dispatch_decision["policy"]["approval_integrations"] == ["DesktopCommanderMCP"]
    assert plan.graph_spec["intent"] == "desktop_action"
    assert plan.graph_spec["source"] == "phone"

    registry.close()
    registry._tempdir.cleanup()
