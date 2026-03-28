"""
CLI-Anything Skills Module

Auto-generates command-line interfaces for any installed software,
making previously inaccessible applications controllable by agents.
"""

import logging
from pathlib import Path

logger = logging.getLogger("archonx.skills.cli_anything")

# Version and metadata
__version__ = "0.1.0"
__all__ = [
    "CLIGenerator",
    "CLIRegistry",
    "CLIExecutor",
    "DiscoveryEngine",
    "discover_all_apps",
    "list_available_clis",
    "execute_cli_command",
    "has_app",
]

from archonx.skills.cli_anything.discovery import DiscoveryEngine, discover_all_apps
from archonx.skills.cli_anything.generator import CLIGenerator
from archonx.skills.cli_anything.registry import CLIRegistry
from archonx.skills.cli_anything.executor import CLIExecutor

# Global registry instance
_registry = CLIRegistry()


def list_available_clis() -> dict[str, list[str]]:
    """List all available CLIs across the system."""
    return _registry.get_all()


def execute_cli_command(
    app: str,
    command: str,
    params: dict | None = None,
    machine_id: str | None = None,
    timeout: int = 30,
) -> dict:
    """
    Execute a CLI command for a given application.

    Args:
        app: Application name (e.g., 'gimp', 'blender')
        command: Command name (e.g., 'create_image', 'render_scene')
        params: Command parameters
        machine_id: Machine to execute on (for ConX Layer)
        timeout: Execution timeout in seconds

    Returns:
        Result dictionary with status and output
    """
    executor = CLIExecutor()
    return executor.execute(
        app=app,
        command=command,
        params=params or {},
        machine_id=machine_id,
        timeout=timeout,
    )


def has_app(app_name: str) -> bool:
    """Check if an application CLI is available."""
    return _registry.has_cli(app_name)


def discover_installed_apps() -> list[str]:
    """Discover all installed applications with available CLIs."""
    engine = DiscoveryEngine()
    return engine.discover()


# Initialize registry on import
def _init_registry():
    """Initialize the CLI registry with discovered applications."""
    try:
        engine = DiscoveryEngine()
        apps = engine.discover()
        for app in apps:
            generator = CLIGenerator(app)
            cli_schema = generator.generate()
            if cli_schema:
                _registry.register(app, cli_schema)
    except Exception as e:
        logger.warning(f"Failed to initialize CLI registry: {e}")


# Auto-initialize on import
try:
    _init_registry()
except Exception as e:
    logger.debug(f"CLI registry initialization deferred: {e}")
