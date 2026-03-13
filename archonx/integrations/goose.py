"""Goose workspace manifests derived from the Archon repo registry."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from archonx.repos.models import RepoPlacement
from archonx.repos.registry import RepoRegistry


@dataclass
class GooseRepoManifestEntry:
    """One Goose-visible repo entry."""

    repo_id: int
    name: str
    url: str
    team_id: str
    placement: str
    runtime_model: str | None
    capability_tags: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GooseWorkspaceManifest:
    """Repo inventory and extension feed for Goose workers."""

    workspace: str
    generated_by: str
    repos: list[GooseRepoManifestEntry]

    def to_dict(self) -> dict:
        return {
            "workspace": self.workspace,
            "generated_by": self.generated_by,
            "repos": [repo.to_dict() for repo in self.repos],
        }


def build_goose_workspace_manifest(
    registry: RepoRegistry,
    workspace: str = "archonx-os",
    team_id: str | None = None,
) -> GooseWorkspaceManifest:
    """Build a Goose workspace manifest from the canonical repo registry."""

    repos = registry.get_repos(team_id=team_id)
    entries = [
        GooseRepoManifestEntry(
            repo_id=repo.id,
            name=repo.name,
            url=repo.url,
            team_id=repo.team_id,
            placement=repo.placement.value,
            runtime_model=repo.runtime_model,
            capability_tags=repo.capability_tags,
            extensions=_extensions_for_repo(repo.placement),
        )
        for repo in repos
    ]
    return GooseWorkspaceManifest(
        workspace=workspace,
        generated_by="archonx.integrations.goose",
        repos=entries,
    )


def write_goose_workspace_manifest(
    manifest: GooseWorkspaceManifest,
    output_path: str | Path,
) -> Path:
    """Persist a Goose workspace manifest as canonical JSON."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def _extensions_for_repo(placement: RepoPlacement) -> list[str]:
    extensions = ["repo_inventory", "extension_registry"]
    if placement == RepoPlacement.FRONTEND_LAYER:
        extensions.append("cloud_coding")
    if placement == RepoPlacement.MEMORY_LAYER:
        extensions.append("memory_sync")
    if placement == RepoPlacement.WORKER_SERVICE:
        extensions.append("worker_contracts")
    return extensions
