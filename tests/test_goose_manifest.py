"""Tests for Goose workspace manifest export."""

import tempfile
from pathlib import Path

from archonx.integrations import build_goose_workspace_manifest
from archonx.repos.registry import RepoRegistry


def _build_registry() -> RepoRegistry:
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_goose_manifest.db"
    yaml_path = Path(tmpdir.name) / "goose_index.yaml"
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
    - {id: 2, name: "memory-repo", url: "https://github.com/test/memory", vis: private, kind: orig, team_id: team_a, domain_type_id: saas, placement: memory_layer}
""",
        encoding="utf-8",
    )
    registry = RepoRegistry(db_path)
    registry.ingest_yaml(yaml_path)
    registry._tempdir = tmpdir
    return registry


def test_build_goose_workspace_manifest() -> None:
    registry = _build_registry()

    manifest = build_goose_workspace_manifest(registry)

    assert manifest.workspace == "archonx-os"
    assert len(manifest.repos) == 2
    assert manifest.repos[0].extensions == ["repo_inventory", "extension_registry", "cloud_coding"]
    assert manifest.repos[1].extensions == ["repo_inventory", "extension_registry", "memory_sync"]

    registry.close()
    registry._tempdir.cleanup()
