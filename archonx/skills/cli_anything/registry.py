"""
CLI Registry

Manages available CLI schemas across the system.
"""

import logging
from typing import Any

logger = logging.getLogger("archonx.skills.cli_anything.registry")


class CLIRegistry:
    """Manages registered CLI schemas."""

    def __init__(self):
        """Initialize the CLI registry."""
        self._clis: dict[str, dict[str, Any]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def register(self, app_name: str, schema: dict, metadata: dict | None = None) -> None:
        """
        Register a CLI schema.

        Args:
            app_name: Application name
            schema: CLI schema dict
            metadata: Optional metadata about the app
        """
        self._clis[app_name] = schema
        self._metadata[app_name] = metadata or {}
        logger.info(f"Registered CLI for {app_name}")

    def unregister(self, app_name: str) -> bool:
        """
        Unregister a CLI schema.

        Args:
            app_name: Application name

        Returns:
            True if unregistered, False if not found
        """
        if app_name in self._clis:
            del self._clis[app_name]
            if app_name in self._metadata:
                del self._metadata[app_name]
            logger.info(f"Unregistered CLI for {app_name}")
            return True
        return False

    def has_cli(self, app_name: str) -> bool:
        """
        Check if a CLI is registered.

        Args:
            app_name: Application name

        Returns:
            True if registered
        """
        return app_name in self._clis

    def get_cli(self, app_name: str) -> dict | None:
        """
        Get CLI schema for an application.

        Args:
            app_name: Application name

        Returns:
            CLI schema or None
        """
        return self._clis.get(app_name)

    def get_all(self) -> dict[str, list[str]]:
        """
        Get all registered CLIs grouped by command.

        Returns:
            Dict mapping app names to command lists
        """
        result = {}
        for app_name, schema in self._clis.items():
            if "commands" in schema:
                result[app_name] = list(schema["commands"].keys())
            else:
                result[app_name] = []
        return result

    def list_apps(self) -> list[str]:
        """
        List all registered applications.

        Returns:
            List of app names
        """
        return sorted(list(self._clis.keys()))

    def list_commands(self, app_name: str) -> list[str]:
        """
        List commands for an application.

        Args:
            app_name: Application name

        Returns:
            List of command names
        """
        cli = self.get_cli(app_name)
        if not cli or "commands" not in cli:
            return []
        return list(cli["commands"].keys())

    def get_command(self, app_name: str, command_name: str) -> dict | None:
        """
        Get command schema.

        Args:
            app_name: Application name
            command_name: Command name

        Returns:
            Command schema or None
        """
        cli = self.get_cli(app_name)
        if not cli or "commands" not in cli:
            return None
        return cli["commands"].get(command_name)

    def set_metadata(self, app_name: str, metadata: dict) -> None:
        """
        Set metadata for an application.

        Args:
            app_name: Application name
            metadata: Metadata dict
        """
        self._metadata[app_name] = metadata
        logger.debug(f"Updated metadata for {app_name}")

    def get_metadata(self, app_name: str) -> dict:
        """
        Get metadata for an application.

        Args:
            app_name: Application name

        Returns:
            Metadata dict
        """
        return self._metadata.get(app_name, {})

    def clear(self) -> None:
        """Clear all registered CLIs."""
        self._clis.clear()
        self._metadata.clear()
        logger.info("Cleared all registered CLIs")

    def stats(self) -> dict:
        """
        Get registry statistics.

        Returns:
            Stats dict
        """
        total_commands = sum(
            len(schema.get("commands", {}))
            for schema in self._clis.values()
        )
        return {
            "registered_apps": len(self._clis),
            "total_commands": total_commands,
            "apps": self.list_apps(),
        }
