"""Tests for dispatch-aware orchestrator task creation."""

import asyncio
from pathlib import Path
import tempfile

import pytest

from archonx.beads.viewer import TaskManager
from archonx.orchestration.dispatch import DispatchCoordinator
from archonx.orchestration.orchestrator import Orchestrator, TaskType
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


@pytest.fixture
def temp_task_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield TaskManager(Path(tmpdir) / "tasks.json")


@pytest.fixture
def temp_dispatch_coordinator():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "repos.db"
        yaml_path = Path(tmpdir) / "repos.yaml"
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
        yield DispatchCoordinator(Router(registry))
        registry.close()


def test_create_task_attaches_dispatch_decision(
    temp_task_manager, temp_dispatch_coordinator
):
    orchestrator = Orchestrator(task_manager=temp_task_manager)
    orchestrator.dispatch_coordinator = temp_dispatch_coordinator

    result = asyncio.run(
        orchestrator.create_task(
            title="Ship Pauli frontend",
            description="Implement the approved frontend layer update",
            task_type=TaskType.CODE,
            metadata={"repo_ids": [1], "task_intent": "cloud_coding"},
        )
    )

    assert result.success is True
    assert result.data["dispatch_decision"] is not None
    task = result.data["task"]
    assert task["metadata"]["worker_id"] == "goose"
    assert task["metadata"]["required_integrations"] == ["mcp2cli"]
