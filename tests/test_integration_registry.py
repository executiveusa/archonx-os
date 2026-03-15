"""Tests for canonical integration and env ownership registries."""

from archonx.integrations import (
    build_default_env_category_registry,
    build_default_integration_registry,
)


def test_default_integration_registry_contains_control_path() -> None:
    registry = build_default_integration_registry()

    desktop_commander = registry.get("DesktopCommanderMCP")
    assert desktop_commander is not None
    assert desktop_commander.kind.value == "control_tower"
    assert desktop_commander.env_categories == ["desktop_control"]

    mcp_gateway = registry.get("mcp2cli")
    assert mcp_gateway is not None
    assert "tool_invocation" in mcp_gateway.env_categories


def test_env_category_registry_resolves_owner_profiles() -> None:
    registry = build_default_env_category_registry()

    profiles = registry.require(["tool_invocation", "edge_routing"])
    assert [profile.owner for profile in profiles] == ["mcp2cli", "Cloudflare Tunnel"]
    assert profiles[1].required_keys == ["CLOUDFLARE_API_TOKEN"]
