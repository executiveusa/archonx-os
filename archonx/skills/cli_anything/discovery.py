"""
Application Discovery Engine

Auto-detects installed applications that can be CLI-controlled.
"""

import logging
import platform
import subprocess
from pathlib import Path
from typing import Set

logger = logging.getLogger("archonx.skills.cli_anything.discovery")


class DiscoveryEngine:
    """Discovers installed applications available for CLI control."""

    # Known applications with CLI support
    KNOWN_APPS = {
        # Design/Graphics
        "gimp": ["gimp", "gimp-2.10"],
        "inkscape": ["inkscape"],
        "blender": ["blender"],
        "krita": ["krita"],
        # Office
        "libreoffice": ["libreoffice", "soffice"],
        "ms-word": ["winword"],
        "ms-excel": ["excel"],
        # Media
        "ffmpeg": ["ffmpeg"],
        "audacity": ["audacity"],
        "obs": ["obs", "obs-studio"],
        "kdenlive": ["kdenlive"],
        "shotcut": ["shotcut"],
        "handbrake": ["ghb", "HandBrakeCLI"],
        # Diagramming
        "drawio": ["draw.io", "drawio"],
        "graphviz": ["dot"],
        # 3D/CAD
        "freecad": ["freecad", "FreeCADCmd"],
        # Development
        "vscode": ["code"],
        "sublime": ["subl"],
        "idea": ["idea"],
    }

    def __init__(self):
        """Initialize discovery engine."""
        self.os_type = platform.system()
        self.discovered: Set[str] = set()

    def discover(self) -> list[str]:
        """
        Discover all installed applications.

        Returns:
            List of discovered application names
        """
        logger.info(f"Discovering applications on {self.os_type}")

        # Check each known application
        for app_name, binaries in self.KNOWN_APPS.items():
            if self._check_app_installed(binaries):
                self.discovered.add(app_name)
                logger.debug(f"Discovered: {app_name}")

        return sorted(list(self.discovered))

    def _check_app_installed(self, binaries: list[str]) -> bool:
        """
        Check if any binary from the list is installed.

        Args:
            binaries: List of possible binary names

        Returns:
            True if any binary is found
        """
        for binary in binaries:
            try:
                # Try to find binary in PATH
                result = subprocess.run(
                    self._which_command(binary),
                    capture_output=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    return True
            except Exception:
                pass

        return False

    def _which_command(self, binary: str) -> list[str]:
        """Get platform-specific 'which' command."""
        if self.os_type == "Windows":
            return ["where", binary]
        else:
            return ["which", binary]

    def get_app_binary_path(self, app_name: str) -> str | None:
        """
        Get the binary path for an application.

        Args:
            app_name: Application name

        Returns:
            Path to binary or None
        """
        if app_name not in self.KNOWN_APPS:
            return None

        binaries = self.KNOWN_APPS[app_name]
        for binary in binaries:
            try:
                result = subprocess.run(
                    self._which_command(binary),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass

        return None

    def register_custom_app(self, app_name: str, binary_paths: list[str]) -> None:
        """
        Register a custom application.

        Args:
            app_name: Application name
            binary_paths: List of possible binary paths
        """
        self.KNOWN_APPS[app_name] = binary_paths
        if self._check_app_installed(binary_paths):
            self.discovered.add(app_name)


def discover_all_apps() -> list[str]:
    """
    Discover all installed applications.

    Returns:
        List of discovered application names
    """
    engine = DiscoveryEngine()
    return engine.discover()


def get_app_info(app_name: str) -> dict | None:
    """
    Get information about an application.

    Args:
        app_name: Application name

    Returns:
        Application info dict or None
    """
    engine = DiscoveryEngine()
    binary_path = engine.get_app_binary_path(app_name)

    if not binary_path:
        return None

    return {
        "name": app_name,
        "binary": binary_path,
        "os": engine.os_type,
        "available": True,
    }
