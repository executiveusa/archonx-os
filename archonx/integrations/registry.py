"""Canonical integration registry for ArchonX control-path services."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class IntegrationKind(str, Enum):
    """Canonical classes of integrations managed by Archon."""

    CONTROL_TOWER = "control_tower"
    INVOCATION_GATEWAY = "invocation_gateway"
    MEMORY_LAYER = "memory_layer"
    EDGE_ACCESS = "edge_access"
    EXTENSION_REGISTRY = "extension_registry"


@dataclass
class IntegrationCapability:
    """Machine-readable integration contract."""

    integration_id: str
    kind: IntegrationKind
    description: str
    env_categories: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    invocation_path: list[str] = field(default_factory=list)
    approval_required: bool = False

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        return payload


class IntegrationRegistry:
    """Registry of canonical integrations available to Archon."""

    def __init__(self) -> None:
        self._integrations: dict[str, IntegrationCapability] = {}

    def register(self, capability: IntegrationCapability) -> None:
        self._integrations[capability.integration_id] = capability

    def get(self, integration_id: str) -> IntegrationCapability | None:
        return self._integrations.get(integration_id)

    def require(self, integration_ids: list[str]) -> list[IntegrationCapability]:
        missing = [integration_id for integration_id in integration_ids if integration_id not in self._integrations]
        if missing:
            raise ValueError(f"Unknown required integrations: {sorted(missing)}")
        return [self._integrations[integration_id] for integration_id in integration_ids]

    def list(self) -> list[IntegrationCapability]:
        return [self._integrations[integration_id] for integration_id in sorted(self._integrations)]


def build_default_integration_registry() -> IntegrationRegistry:
    """Build the canonical integration registry for Archon-X."""

    registry = IntegrationRegistry()
    registry.register(
        IntegrationCapability(
            integration_id="DesktopCommanderMCP",
            kind=IntegrationKind.CONTROL_TOWER,
            description="Primary machine-control tower for local desktop and file execution.",
            env_categories=["desktop_control"],
            provides=["desktop_control", "file_ops", "process_control"],
            invocation_path=["archonx-os", "mcp2cli", "DesktopCommanderMCP"],
            approval_required=True,
        )
    )
    registry.register(
        IntegrationCapability(
            integration_id="mcp2cli",
            kind=IntegrationKind.INVOCATION_GATEWAY,
            description="Mandatory token-efficient invocation gateway for MCP and OpenAPI tools.",
            env_categories=["tool_invocation"],
            provides=["tool_invocation", "token_compression"],
            invocation_path=["archonx-os", "mcp2cli"],
        )
    )
    registry.register(
        IntegrationCapability(
            integration_id="Notion",
            kind=IntegrationKind.MEMORY_LAYER,
            description="Canonical memory backend for memory-layer repos and second-brain sync.",
            env_categories=["memory_backend"],
            provides=["knowledge_store", "second_brain_sync"],
            invocation_path=["archonx-os", "mcp2cli", "Notion"],
        )
    )
    registry.register(
        IntegrationCapability(
            integration_id="Cloudflare Tunnel",
            kind=IntegrationKind.EDGE_ACCESS,
            description="Edge publishing and secure ingress path for frontend and product layers.",
            env_categories=["edge_routing"],
            provides=["edge_ingress", "service_exposure"],
            invocation_path=["archonx-os", "Cloudflare Tunnel"],
            approval_required=True,
        )
    )
    registry.register(
        IntegrationCapability(
            integration_id="GooseExtensionRegistry",
            kind=IntegrationKind.EXTENSION_REGISTRY,
            description="Repo inventory and extension manifest feed for Goose cloud-coding workers.",
            env_categories=["repo_inventory"],
            provides=["repo_inventory", "extension_registry"],
            invocation_path=["archonx-os", "GooseExtensionRegistry"],
        )
    )
    return registry
