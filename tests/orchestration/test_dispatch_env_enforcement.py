"""Tests for dispatch env-readiness enforcement."""

import tempfile
from pathlib import Path

import pytest

from archonx.orchestration import DispatchCoordinator
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


def _build_registry() -> RepoRegistry:
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_dispatch_env.db"
    yaml_path = Path(tmpdir.name) / "dispatch_env_index.yaml"
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
    - {id: 1, name: "memory-repo", url: "https://github.com/test/memory", vis: public, kind: orig, team_id: team_a, domain_type_id: saas, placement: memory_layer}
""",
        encoding="utf-8",
    )
    registry = RepoRegistry(db_path)
    registry.ingest_yaml(yaml_path)
    registry._tempdir = tmpdir
    return registry


def test_dispatch_fails_when_required_env_is_missing() -> None:
    registry = _build_registry()
    coordinator = DispatchCoordinator(Router(registry), enforce_env_readiness=True)

    with pytest.raises(ValueError, match="Missing required env keys"):
        coordinator.create_dispatch_decision([1], "sync_memory")

    registry.close()
    registry._tempdir.cleanup()
