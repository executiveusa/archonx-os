"""
Auto-wires MCP servers into Claude Desktop config.

Handles cross-platform config file discovery and idempotent server registration.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("archonx.conx.mcp_wirer")


class MCPWirer:
    """Manages Claude Desktop MCP server configuration."""

    def __init__(self):
        """Initialize the MCP wirer."""
        self.config_path = self.find_claude_config()
        self.config: dict[str, Any] = {}

    def find_claude_config(self) -> Path:
        """
        Find claude_desktop_config.json on any OS.

        Returns:
            Path to the config file
        """
        # Windows
        if os.name == "nt":
            appdata = os.getenv("APPDATA")
            if appdata:
                path = Path(appdata) / "Claude" / "claude_desktop_config.json"
                if path.exists():
                    return path

        # macOS
        home = Path.home()
        macos_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        if macos_path.exists():
            return macos_path

        # Linux
        linux_path = home / ".config" / "Claude" / "claude_desktop_config.json"
        if linux_path.exists():
            return linux_path

        # Default to Linux config path if nothing found yet
        return linux_path

    def read_config(self) -> dict[str, Any]:
        """
        Read Claude Desktop config file.

        Returns:
            Config dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error reading config: {e}")
                self.config = {}
        else:
            # Initialize empty config
            self.config = {
                "mcpServers": {}
            }

        return self.config

    def add_server(
        self,
        name: str,
        command: str,
        args: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Add an MCP server to the config.

        Args:
            name: Server name
            command: Command to run
            args: Command arguments
            env: Environment variables
        """
        if "mcpServers" not in self.config:
            self.config["mcpServers"] = {}

        # Check if already exists
        if name in self.config["mcpServers"]:
            logger.info(f"Server '{name}' already configured, skipping")
            return

        self.config["mcpServers"][name] = {
            "command": command,
        }

        if args:
            self.config["mcpServers"][name]["args"] = args

        if env:
            self.config["mcpServers"][name]["env"] = env

        logger.info(f"Added server: {name}")

    def wire_desktop_commander(self) -> None:
        """Wire Desktop Commander MCP server."""
        self.add_server(
            "desktop-commander",
            "python",
            ["archonx/mcp/desktop_commander.py"],
            {"DESKTOP_COMMANDER_PORT": "3000"},
        )

    def wire_vault_agent(self) -> None:
        """Wire Vault Agent MCP server."""
        self.add_server(
            "vault-agent",
            "python",
            ["archonx/agents/vault_agent.py"],
        )

    def wire_notion(self) -> None:
        """Wire Notion MCP server."""
        self.add_server(
            "notion",
            "python",
            ["archonx/mcp/notion.py"],
            {"NOTION_API_KEY": "${NOTION_API_KEY}"},
        )

    def wire_open_brain(self, vps_url: str) -> None:
        """
        Wire Open Brain MCP server.

        Args:
            vps_url: VPS URL for open brain connection
        """
        self.add_server(
            "open-brain",
            "python",
            ["Open-brain-mcp-server/open_brain_mcp_server.py"],
            {
                "SUPABASE_URL": "${SUPABASE_URL}",
                "SUPABASE_KEY": "${SUPABASE_KEY}",
                "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
            },
        )

    def save_config(self) -> None:
        """Save config to file."""
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

        logger.info(f"Config saved to {self.config_path}")

    def get_wired_servers(self) -> list[str]:
        """
        Get list of currently wired servers.

        Returns:
            List of server names
        """
        if "mcpServers" not in self.config:
            return []
        return list(self.config["mcpServers"].keys())
