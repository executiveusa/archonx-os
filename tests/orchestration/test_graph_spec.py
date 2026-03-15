"""Tests for canonical intent graph compilation."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from archonx.orchestration import (
    DispatchCoordinator,
    build_intent_graph_from_dispatch,
)
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


def _build_registry() -> RepoRegistry:
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_graph_spec.db"
    yaml_path = Path(tmpdir.name) / "graph_spec_index.yaml"
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


def test_build_intent_graph_from_dispatch() -> None:
    registry = _build_registry()
    with patch.dict(os.environ, {"ARCHONX_ENABLE_DESKTOP_CONTROL": "true"}, clear=False):
        coordinator = DispatchCoordinator(Router(registry), enforce_env_readiness=True)
        decision = coordinator.create_dispatch_decision(
            [1],
            "remote_desktop:test",
            task_intent="desktop_action",
            objective="Open the control dashboard from phone",
        )

    graph = build_intent_graph_from_dispatch(decision, source="phone")

    assert graph.intent == "desktop_action"
    assert graph.source == "phone"
    assert graph.metadata["approval_integrations"] == ["DesktopCommanderMCP"]
    assert [node.node_type for node in graph.nodes] == [
        "intent_input",
        "planner",
        "policy_gate",
        "env_gate",
        "worker",
        "result_schema",
    ]

    registry.close()
    registry._tempdir.cleanup()
