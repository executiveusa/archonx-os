"""ArchonX Repo Awareness & Routing Fabric.

This module provides repo-awareness and intelligent routing for the 268-repo Guardian Fleet.
It ingests a canonical YAML index (repos.index.yaml) and maintains an internal registry for
agent routing, without cloning or mirroring any repositories.

Core components:
- RepoRegistry: SQLite-based repo metadata storage
- Router: Maps repos + tasks to agent dispatch plans
- Models: Data structures for teams, repos, domain types

Key principles:
- INDEX-ONLY: Never clone, download, or mirror repos
- MCP-FIRST: Require preflight verification before operations
- PLANNING-ONLY: Generate dispatch plans without executing tasks
"""

from archonx.repos.models import (
    DomainType,
    Repo,
    RepoPlacement,
    Team,
    DispatchPlan,
    DispatchPlanAgent,
)
from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router

__all__ = [
    "RepoRegistry",
    "Router",
    "Team",
    "Repo",
    "DomainType",
    "RepoPlacement",
    "DispatchPlan",
    "DispatchPlanAgent",
]
