"""
Tests — Tools (deploy, browser_test, fixer, analytics)
"""

import pytest

from archonx.tools.base import ToolRegistry
from archonx.tools.deploy import GitHubDeployOrchestrator
from archonx.tools.browser_test import BrowserTestTool
from archonx.tools.fixer import FixerAgentTool
from archonx.tools.analytics import AnalyticsTool


@pytest.fixture
def tool_registry() -> ToolRegistry:
    tr = ToolRegistry()
    tr.register(GitHubDeployOrchestrator())
    tr.register(BrowserTestTool())
    tr.register(FixerAgentTool())
    tr.register(AnalyticsTool())
    return tr


def test_registry_has_four_tools(tool_registry: ToolRegistry) -> None:
    assert len(tool_registry.list_tools()) == 4


@pytest.mark.asyncio
async def test_deploy_trigger(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute(
        "github_deploy_orchestrator",
        {"action": "trigger", "site_path": "client/site"},
    )
    assert result.status == "success"
    assert result.data["action"] == "trigger"


@pytest.mark.asyncio
async def test_deploy_rollback(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute(
        "github_deploy_orchestrator",
        {"action": "rollback", "site_path": "client/site"},
    )
    assert result.status == "success"
    assert result.data["rolled_back"] is True


@pytest.mark.asyncio
async def test_browser_test(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute(
        "browser_test_tool",
        {"url": "https://staging.example.com", "tests": ["checkout", "mobile"]},
    )
    assert result.status == "success"
    assert result.data["all_passed"] is True


@pytest.mark.asyncio
async def test_browser_test_no_url(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute("browser_test_tool", {})
    assert result.status == "error"


@pytest.mark.asyncio
async def test_fixer(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute(
        "fixer_agent_tool",
        {"issue": "timeout", "repo": "client/api", "auto_deploy": True},
    )
    assert result.status == "success"
    assert result.data["auto_deployed"] is True


@pytest.mark.asyncio
async def test_analytics(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.execute(
        "analytics_tool",
        {"metric": "conversion_rate", "timeframe": "last_30_days"},
    )
    assert result.status == "success"
    assert result.data["metric"] == "conversion_rate"


@pytest.mark.asyncio
async def test_unknown_tool(tool_registry: ToolRegistry) -> None:
    with pytest.raises(KeyError):
        await tool_registry.execute("nonexistent_tool", {})
