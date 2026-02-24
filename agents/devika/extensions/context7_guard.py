"""Context7 compliance guard for Devika PI workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Context7CheckResult:
    allowed: bool
    reason: str


class Context7Guard:
    """Tracks and validates Context7 resolve and docs checks per task."""

    def __init__(self) -> None:
        self._resolved: set[str] = set()
        self._queried: set[str] = set()

    def mark_resolved(self, library_name: str) -> None:
        self._resolved.add(library_name.strip().lower())

    def mark_queried(self, library_name: str) -> None:
        self._queried.add(library_name.strip().lower())

    def check_library_use(self, library_name: str) -> Context7CheckResult:
        normalized = library_name.strip().lower()
        if normalized not in self._resolved:
            return Context7CheckResult(False, f"context7_resolve_missing:{library_name}")
        if normalized not in self._queried:
            return Context7CheckResult(False, f"context7_query_missing:{library_name}")
        return Context7CheckResult(True, "ok")

    def reset(self) -> None:
        self._resolved.clear()
        self._queried.clear()
