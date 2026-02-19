"""
Tool Base & Registry
====================
All tools that agents can invoke follow this interface.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.tools.base")


@dataclass
class ToolResult:
    """Standard result returned by any tool execution."""

    tool: str
    status: str          # "success" | "error" | "pending"
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseTool(ABC):
    """Interface every ArchonX tool must implement."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """Run the tool with the given parameters."""


class ToolRegistry:
    """Central registry of available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.info("Tool registered: %s", tool.name)

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    async def execute(self, name: str, params: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        try:
            return await tool.execute(params)
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return ToolResult(tool=name, status="error", error=str(exc))
