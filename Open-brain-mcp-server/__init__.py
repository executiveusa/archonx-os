"""
Open Brain MCP Server
Shared pgvector memory layer for ArchonX agents with jcodemunch token efficiency
"""

__version__ = "1.0.0"
__author__ = "ArchonX Team"

from .open_brain_mcp_server import OpenBrainDB, db

__all__ = ["OpenBrainDB", "db"]
