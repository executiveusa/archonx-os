"""
Grep MCP Tool
=============
Workspace-wide code and text search for all crews.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Any

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.grep_mcp")


class GrepMCPTool(BaseTool):
    """Run fast ripgrep searches as a shared MCP-style capability."""

    name = "grep_mcp"
    description = "Search code and docs with rg/grep across the workspace"

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        query = str(params.get("query", "")).strip()
        include = str(params.get("include", "")).strip()
        max_results = int(params.get("max_results", 50))
        root = str(params.get("root") or os.getcwd())

        if not query:
            return ToolResult(
                tool=self.name,
                status="error",
                error="query parameter is required",
            )

        rg_bin = shutil.which("rg")
        if rg_bin:
            cmd = [rg_bin, "--line-number", "--color", "never", query]
            if include:
                cmd.extend(["--glob", include])
        else:
            # Fallback for environments without rg.
            cmd = ["grep", "-R", "-n", query, "."]

        search_root = Path(root).resolve()
        logger.info("grep_mcp search: query=%s root=%s", query, search_root)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(search_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
        except Exception as exc:
            return ToolResult(tool=self.name, status="error", error=str(exc))

        if process.returncode not in (0, 1):
            return ToolResult(
                tool=self.name,
                status="error",
                error=stderr.decode("utf-8", errors="replace").strip() or "search failed",
            )

        lines = [line for line in stdout.decode("utf-8", errors="replace").splitlines() if line]
        lines = lines[:max_results]

        return ToolResult(
            tool=self.name,
            status="success",
            data={
                "query": query,
                "root": str(search_root),
                "count": len(lines),
                "matches": lines,
                "truncated": len(lines) >= max_results,
            },
        )
