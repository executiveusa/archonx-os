"""Tests for Router."""

import tempfile
from pathlib import Path
import pytest

from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router
from archonx.repos.models import DomainType


@pytest.fixture
def test_registry():
    """Create a test registry with sample data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_repos.db"
        yaml_path = Path(tmpdir) / "test_index.yaml"

        yaml_content = """
archonx_repo_index_spec:
  version: "1.0.0"
  mode: "index_only"
  do_not_clone: true
  do_not_vendor: true
  do_not_mirror: true

  teams:
    - id: team_a
      display: "Team A"
      owners: [user_a]
      regions: [Global]
    - id: team_b
      display: "Team B"
      owners: [user_b]
      regions: [Global]

  domain_types:
    - id: saas
      description: "SaaS"
    - id: tool
      description: "Tool"
    - id: agent
      description: "Agent"
    - id: template
      description: "Template"
    - id: content
      description: "Content"
    - id: unknown
      description: "Unknown"

  repos:
    - {id: 1, name: "saas-repo", url: "https://github.com/test/saas", vis: public, kind: orig, team_id: team_a, domain_type_id: saas}
    - {id: 2, name: "tool-repo", url: "https://github.com/test/tool", vis: private, kind: fork, team_id: team_a, domain_type_id: tool}
    - {id: 3, name: "agent-repo", url: "https://github.com/test/agent", vis: public, kind: orig, team_id: team_b, domain_type_id: agent}
    - {id: 4, name: "template-repo", url: "https://github.com/test/template", vis: public, kind: fork, team_id: team_b, domain_type_id: template}
    - {id: 5, name: "unknown-repo", url: "https://github.com/test/unknown", vis: private, kind: orig, team_id: team_a, domain_type_id: unknown}
"""
        yaml_path.write_text(yaml_content, encoding="utf-8")

        registry = RepoRegistry(db_path)
        registry.ingest_yaml(yaml_path)

        yield registry

        registry.close()


class TestRouter:
    """Test Router functionality."""

    def test_route_single_repo_saas(self, test_registry):
        """Test routing a single SAAS repo."""
        router = Router(test_registry)
        plan = router.route([1], "audit")

        assert plan.repo_ids == [1]
        assert plan.task_name == "audit"
        assert plan.team_id == "team_a"
        assert plan.task_intent == "code_change"
        assert len(plan.repos_metadata) == 1
        assert plan.repos_metadata[0]["domain_type_id"] == "saas"

        # SAAS should include design, backend, qa, sec, prd
        agent_ids = {a.id for a in plan.recommended_agents}
        assert "design_agent" in agent_ids
        assert "backend_agent" in agent_ids
        assert "qa_agent" in agent_ids
        assert "sec_agent" in agent_ids
        assert "prd_agent" in agent_ids
        worker_ids = {w.id for w in plan.recommended_workers}
        assert "darya_openhands" in worker_ids
        integration_ids = {i.id for i in plan.required_integrations}
        assert "mcp2cli" in integration_ids
        assert "DesktopCommanderMCP" in integration_ids

    def test_route_single_repo_tool(self, test_registry):
        """Test routing a single TOOL repo."""
        router = Router(test_registry)
        plan = router.route([2], "audit")

        # TOOL should include backend, sec, prd
        agent_ids = {a.id for a in plan.recommended_agents}
        assert "design_agent" not in agent_ids
        assert "backend_agent" in agent_ids
        assert "qa_agent" not in agent_ids
        assert "sec_agent" in agent_ids
        assert "prd_agent" in agent_ids

    def test_route_single_repo_agent(self, test_registry):
        """Test routing a single AGENT repo."""
        router = Router(test_registry)
        plan = router.route([3], "audit")

        # AGENT should include agent_ops, sec, prd
        agent_ids = {a.id for a in plan.recommended_agents}
        assert "agent_ops_agent" in agent_ids
        assert "sec_agent" in agent_ids
        assert "prd_agent" in agent_ids
        assert "design_agent" not in agent_ids

    def test_route_single_repo_template(self, test_registry):
        """Test routing a single TEMPLATE repo."""
        router = Router(test_registry)
        plan = router.route([4], "audit")

        # TEMPLATE should only include prd
        agent_ids = {a.id for a in plan.recommended_agents}
        assert agent_ids == {"prd_agent"}

    def test_route_single_repo_unknown(self, test_registry):
        """Test routing a single UNKNOWN repo."""
        router = Router(test_registry)
        plan = router.route([5], "audit")

        # UNKNOWN should include recon, prd
        agent_ids = {a.id for a in plan.recommended_agents}
        assert "recon_agent" in agent_ids
        assert "prd_agent" in agent_ids

    def test_route_multiple_repos_same_team(self, test_registry):
        """Test routing multiple repos from same team."""
        router = Router(test_registry)
        plan = router.route([1, 2, 5], "audit")

        assert plan.repo_ids == [1, 2, 5]
        assert plan.team_id == "team_a"
        assert len(plan.repos_metadata) == 3

        # Union of domains: saas + tool + unknown
        agent_ids = {a.id for a in plan.recommended_agents}
        assert "design_agent" in agent_ids  # from saas
        assert "backend_agent" in agent_ids  # from saas + tool
        assert "recon_agent" in agent_ids  # from unknown

    def test_route_multiple_repos_multi_team(self, test_registry):
        """Test routing repos from multiple teams."""
        router = Router(test_registry)
        plan = router.route([1, 3], "audit")

        assert plan.team_id == "multi_team"
        assert len(plan.repos_metadata) == 2

    def test_route_respects_explicit_task_intent(self, test_registry):
        """Explicit task intent should drive worker selection."""
        router = Router(test_registry)
        plan = router.route([1], "implement_ui", task_intent="cloud_coding")

        assert plan.task_intent == "cloud_coding"
        worker_ids = {worker.id for worker in plan.recommended_workers}
        assert "goose" in worker_ids

    def test_route_unknown_repo_defaults_to_repo_analysis(self, test_registry):
        """Unknown repos should default to repo analysis intent."""
        router = Router(test_registry)
        plan = router.route([5], "discover")

        assert plan.task_intent == "repo_analysis"
        worker_ids = {worker.id for worker in plan.recommended_workers}
        assert "darya_openhands" in worker_ids

    def test_route_required_integrations_include_control_path(self, test_registry):
        """Control path integrations should be attached to dispatch plans."""
        router = Router(test_registry)
        plan = router.route([1], "audit")

        integrations = {integration.id for integration in plan.required_integrations}
        assert integrations == {"DesktopCommanderMCP", "mcp2cli"}

    def test_route_preflight_steps(self, test_registry):
        """Test that preflight steps are included."""
        router = Router(test_registry)
        plan = router.route([1], "audit")

        assert len(plan.preflight_steps) > 0
        assert any("mcp connect" in step for step in plan.preflight_steps)
        assert any("mcp verify" in step for step in plan.preflight_steps)
        assert any("tokensaver" in step for step in plan.preflight_steps)

    def test_route_token_tracker_present(self, test_registry):
        """Test that token tracker is initialized."""
        router = Router(test_registry)
        plan = router.route([1], "audit")

        assert plan.token_tracker is not None
        assert plan.token_tracker["enabled"] is True
        assert "csv_path" in plan.token_tracker
        assert plan.token_tracker["status"] == "pending"

    def test_route_determinism(self, test_registry):
        """Test that routing is deterministic."""
        router = Router(test_registry)

        plan1 = router.route([1, 2, 3], "test_task")
        plan2 = router.route([1, 2, 3], "test_task")

        dict1 = plan1.to_dict()
        dict2 = plan2.to_dict()

        # Remove timestamps for comparison
        dict1.pop("timestamp")
        dict2.pop("timestamp")

        assert dict1 == dict2

    def test_route_invalid_repo_id(self, test_registry):
        """Test that routing fails for non-existent repo."""
        router = Router(test_registry)

        with pytest.raises(ValueError, match="not found"):
            router.route([999], "audit")

    def test_route_empty_repo_list(self, test_registry):
        """Test that routing fails for empty repo list."""
        router = Router(test_registry)

        with pytest.raises(ValueError, match="empty"):
            router.route([], "audit")

    def test_agent_profiles_include_all_tools(self, test_registry):
        """Test that agent profiles have defined tools."""
        router = Router(test_registry)
        plan = router.route([1], "audit")

        for agent in plan.recommended_agents:
            assert agent.id is not None
            assert agent.role is not None
            assert isinstance(agent.tools, list)
            assert len(agent.tools) > 0

    def test_agent_ordering_deterministic(self, test_registry):
        """Test that agents are ordered deterministically."""
        router = Router(test_registry)

        plan1 = router.route([1], "audit")
        plan2 = router.route([1], "audit")

        agent_ids_1 = [a.id for a in plan1.recommended_agents]
        agent_ids_2 = [a.id for a in plan2.recommended_agents]

        assert agent_ids_1 == agent_ids_2
