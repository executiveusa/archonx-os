"""Env ownership registry for canonical ArchonX integrations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import os


@dataclass
class EnvCategoryProfile:
    """Ownership and key profile for one env category."""

    category: str
    owner: str
    purpose: str
    required_keys: list[str] = field(default_factory=list)
    optional_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EnvAuditResult:
    """Audit result for required env categories."""

    categories: list[str]
    present_keys: list[str] = field(default_factory=list)
    missing_keys: list[str] = field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return not self.missing_keys

    def to_dict(self) -> dict:
        return {
            "categories": self.categories,
            "present_keys": self.present_keys,
            "missing_keys": self.missing_keys,
            "is_ready": self.is_ready,
        }


class EnvCategoryRegistry:
    """Registry of env categories used by Archon integrations."""

    def __init__(self) -> None:
        self._profiles: dict[str, EnvCategoryProfile] = {}

    def register(self, profile: EnvCategoryProfile) -> None:
        self._profiles[profile.category] = profile

    def get(self, category: str) -> EnvCategoryProfile | None:
        return self._profiles.get(category)

    def require(self, categories: list[str]) -> list[EnvCategoryProfile]:
        missing = [category for category in categories if category not in self._profiles]
        if missing:
            raise ValueError(f"Unknown env categories: {sorted(missing)}")
        return [self._profiles[category] for category in categories]

    def audit(
        self,
        categories: list[str],
        environ: dict[str, str] | None = None,
    ) -> EnvAuditResult:
        profiles = self.require(categories)
        environment = environ if environ is not None else os.environ
        present_keys: list[str] = []
        missing_keys: list[str] = []
        for profile in profiles:
            for key in profile.required_keys:
                if environment.get(key):
                    present_keys.append(key)
                else:
                    missing_keys.append(key)
        return EnvAuditResult(
            categories=list(categories),
            present_keys=sorted(set(present_keys)),
            missing_keys=sorted(set(missing_keys)),
        )


def build_default_env_category_registry() -> EnvCategoryRegistry:
    """Build canonical env ownership for the core control path."""

    registry = EnvCategoryRegistry()
    registry.register(
        EnvCategoryProfile(
            category="desktop_control",
            owner="DesktopCommanderMCP",
            purpose="Desktop, process, file, and local workspace control boundary.",
            required_keys=["ARCHONX_ENABLE_DESKTOP_CONTROL"],
        )
    )
    registry.register(
        EnvCategoryProfile(
            category="tool_invocation",
            owner="mcp2cli",
            purpose="Token-efficient MCP/OpenAPI invocation path and budgets.",
            optional_keys=["ARCHONX_TOKEN_BUDGET", "ARCHONX_MCP_PROFILE"],
        )
    )
    registry.register(
        EnvCategoryProfile(
            category="memory_backend",
            owner="Notion",
            purpose="Second-brain sync, memory persistence, and Pauli knowledge routing.",
            required_keys=["NOTION_TOKEN"],
            optional_keys=["NOTION_DATABASE_IDS"],
        )
    )
    registry.register(
        EnvCategoryProfile(
            category="edge_routing",
            owner="Cloudflare Tunnel",
            purpose="Public ingress, route exposure, and frontend/product publish paths.",
            required_keys=["CLOUDFLARE_API_TOKEN"],
            optional_keys=["CLOUDFLARE_TUNNEL_ID", "CLOUDFLARE_ACCOUNT_ID"],
        )
    )
    registry.register(
        EnvCategoryProfile(
            category="repo_inventory",
            owner="archonx-os",
            purpose="Repo inventory and extension manifest publication for worker routing.",
            optional_keys=["ARCHONX_REPO_INDEX_PATH"],
        )
    )
    return registry
