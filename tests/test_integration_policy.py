"""Tests for integration policy and env auditing."""

from archonx.integrations import (
    IntegrationPolicyEnforcer,
    build_default_env_category_registry,
)


def test_integration_policy_requires_approval_for_control_tower() -> None:
    enforcer = IntegrationPolicyEnforcer()

    result = enforcer.evaluate(["DesktopCommanderMCP", "mcp2cli"])

    assert result.blocked_integrations == []
    assert result.approval_integrations == ["DesktopCommanderMCP"]


def test_env_category_audit_detects_missing_required_keys() -> None:
    registry = build_default_env_category_registry()

    audit = registry.audit(["memory_backend"], environ={})

    assert audit.is_ready is False
    assert audit.missing_keys == ["NOTION_TOKEN"]
