"""
Workspace Scope — Path traversal prevention and workspace-scoped file access.

Ensures agents can only access files within their configured workspace root.
Blocks symlink escapes, ``..`` traversal, and absolute paths outside scope.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path, PurePosixPath, PureWindowsPath

logger = logging.getLogger("archonx.security.workspace_scope")


class WorkspaceScopeError(Exception):
    """Raised when a path escapes the workspace boundary."""


class WorkspaceScope:
    """
    Enforces file access boundaries for agent operations.

    All path operations are resolved to real paths and compared against the
    workspace root to prevent traversal and symlink escape attacks.
    """

    def __init__(self, workspace_root: str | Path) -> None:
        self._root = Path(workspace_root).resolve()
        if not self._root.is_dir():
            raise WorkspaceScopeError(
                f"workspace root does not exist or is not a directory: {self._root}"
            )
        logger.info("WorkspaceScope bound to %s", self._root)

    @property
    def root(self) -> Path:
        return self._root

    def set_root(self, workspace_root: str | Path) -> None:
        """Change the workspace root (e.g. on session switch)."""
        new_root = Path(workspace_root).resolve()
        if not new_root.is_dir():
            raise WorkspaceScopeError(
                f"new workspace root does not exist or is not a directory: {new_root}"
            )
        self._root = new_root
        logger.info("WorkspaceScope root changed to %s", self._root)

    def validate(self, target: str | Path) -> Path:
        """
        Validate and resolve a path.

        Returns the resolved Path if safe; raises WorkspaceScopeError otherwise.
        """
        target_str = str(target)

        # Quick rejection of obvious traversal attempts in raw string
        if "\x00" in target_str:
            raise WorkspaceScopeError("null bytes in path")

        # Resolve relative to workspace root
        candidate = Path(target_str)
        if not candidate.is_absolute():
            candidate = self._root / candidate

        resolved = candidate.resolve()

        # Check containment
        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise WorkspaceScopeError(
                f"path escapes workspace: {target!s} -> {resolved}"
            ) from None

        # Check for symlink escape (resolve the parent chain)
        if resolved.exists() and resolved.is_symlink():
            real_target = resolved.resolve()
            try:
                real_target.relative_to(self._root)
            except ValueError:
                raise WorkspaceScopeError(
                    f"symlink escapes workspace: {target!s} -> {real_target}"
                ) from None

        return resolved

    def resolve_safe(self, target: str | Path) -> Path:
        """Alias for validate() — resolve path and confirm it's in scope."""
        return self.validate(target)

    def is_within(self, target: str | Path) -> bool:
        """Return True if the path is within the workspace (non-throwing)."""
        try:
            self.validate(target)
            return True
        except WorkspaceScopeError:
            return False

    def make_relative(self, target: str | Path) -> Path:
        """Return the workspace-relative portion of a validated path."""
        resolved = self.validate(target)
        return resolved.relative_to(self._root)
