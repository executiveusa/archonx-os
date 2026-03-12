"""Data models for repo-awareness system."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List
from datetime import datetime


class DomainType(str, Enum):
    """Repository domain classification."""
    SAAS = "saas"
    TOOL = "tool"
    AGENT = "agent"
    TEMPLATE = "template"
    CONTENT = "content"
    UNKNOWN = "unknown"


class RepoVisibility(str, Enum):
    """Repository visibility."""
    PUBLIC = "public"
    PRIVATE = "private"


class RepoKind(str, Enum):
    """Repository kind."""
    ORIGINAL = "orig"
    FORK = "fork"


class RepoPlacement(str, Enum):
    """Canonical placement of a repo within the ArchonX architecture."""

    CORE_DEPENDENCY = "core_dependency"
    PLUGIN = "plugin"
    WORKER_SERVICE = "worker_service"
    SIDECAR = "sidecar"
    SUBMODULE = "submodule"
    STANDALONE_TOOL = "standalone_tool"
    MEMORY_LAYER = "memory_layer"
    FRONTEND_LAYER = "frontend_layer"
    UNKNOWN = "unknown"


@dataclass
class Team:
    """Team metadata."""
    id: str
    display: str
    owners: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Repo:
    """Repository metadata."""
    id: int
    name: str
    url: str
    visibility: RepoVisibility
    kind: RepoKind
    team_id: str
    domain_type_id: DomainType
    placement: RepoPlacement = RepoPlacement.UNKNOWN
    runtime_model: Optional[str] = None
    installed_under: Optional[str] = None
    capability_tags: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    required_env_categories: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "visibility": self.visibility.value,
            "kind": self.kind.value,
            "team_id": self.team_id,
            "domain_type_id": self.domain_type_id.value,
            "placement": self.placement.value,
            "runtime_model": self.runtime_model,
            "installed_under": self.installed_under,
            "capability_tags": self.capability_tags,
            "called_by": self.called_by,
            "calls": self.calls,
            "required_env_categories": self.required_env_categories,
        }


@dataclass
class DispatchPlanAgent:
    """Agent in a dispatch plan."""
    id: str
    role: str
    tools: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class DispatchPlan:
    """Dispatch plan for agent routing."""
    timestamp: str
    repo_ids: List[int]
    task_name: str
    team_id: str
    repos_metadata: List[dict]
    preflight_steps: List[str] = field(default_factory=list)
    recommended_agents: List[DispatchPlanAgent] = field(default_factory=list)
    token_tracker: dict = field(default_factory=lambda: {
        "enabled": True,
        "csv_path": "logs/token_savings.csv",
        "baseline_tokens": None,
        "tokensaver_tokens": None,
        "status": "pending",
    })
    notes: str = ""

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "repo_ids": self.repo_ids,
            "task_name": self.task_name,
            "team_id": self.team_id,
            "repos_metadata": self.repos_metadata,
            "preflight_steps": self.preflight_steps,
            "recommended_agents": [a.to_dict() for a in self.recommended_agents],
            "token_tracker": self.token_tracker,
            "notes": self.notes,
        }


@dataclass
class IngestHistory:
    """Ingest history record."""
    ingested_at_utc: str
    file_hash: str
    repo_count: int
    status: str
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)
