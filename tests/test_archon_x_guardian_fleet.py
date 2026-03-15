"""
BEAD: AX-MERGE-009
Tests for GuardianFleet
========================
3 tests — mock mode (no real GitHub API calls).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from archonx.agents.archon_x_guardian_fleet import GuardianFleet


@pytest.fixture
def fleet() -> GuardianFleet:
    """Create a GuardianFleet in mock mode (no GH_PAT)."""
    with patch.dict(os.environ, {}, clear=False):
        env = os.environ.copy()
        env.pop("GH_PAT", None)
        with patch.dict(os.environ, env, clear=True):
            return GuardianFleet()


def test_guardian_fleet_health_check_returns_dict(fleet: GuardianFleet) -> None:
    """check_repo_health() should return a dict with all required fields."""
    result = fleet.check_repo_health("archonx-os")

    assert isinstance(result, dict)
    assert "repo" in result
    assert result["repo"] == "archonx-os"
    assert "build_status" in result
    assert "open_issues" in result
    assert "last_commit" in result

    # In mock mode, should be passing
    assert result["build_status"] == "passing"
    assert result.get("mock") is True


def test_guardian_fleet_generates_report(fleet: GuardianFleet) -> None:
    """generate_fleet_report() should return a summary dict with required keys."""
    report = fleet.generate_fleet_report()

    assert isinstance(report, dict)
    assert "generated_at" in report
    assert "org" in report
    assert "total_checked" in report
    assert "healthy" in report
    assert "failing" in report
    assert "repos" in report

    # In mock mode, all repos should be healthy
    assert report["total_checked"] >= 1
    assert report["healthy"] >= 1
    assert isinstance(report["repos"], list)
    assert len(report["repos"]) == report["total_checked"]


def test_guardian_fleet_mock_all_repos_limit_10(fleet: GuardianFleet) -> None:
    """check_all_repos(limit=10) should return at most 10 repos in mock mode."""
    results = fleet.check_all_repos(limit=10)

    assert isinstance(results, list)
    assert len(results) <= 10
    assert len(results) >= 1  # at least one repo in mock

    # Each result should be a valid health dict
    for repo in results:
        assert "repo" in repo
        assert "build_status" in repo
        assert isinstance(repo["repo"], str)
        assert repo["build_status"] in ("passing", "failing", "unknown", "error", "not_found")
