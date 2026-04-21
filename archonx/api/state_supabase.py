"""Supabase-backed state manager shim for server lifecycle wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SupabaseStateManager:
    """Lightweight async state manager used by `archonx.server` lifespan hooks."""

    database_url: str

    async def initialize(self) -> None:
        """Initialize database resources (no-op in local test mode)."""
        return None

    async def close(self) -> None:
        """Close database resources (no-op in local test mode)."""
        return None

    async def health(self) -> dict[str, Any]:
        """Return a simple health payload for observability."""
        return {"status": "ok", "database_url_configured": bool(self.database_url)}
