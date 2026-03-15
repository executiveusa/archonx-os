"""
BEAD: AX-MERGE-007
mDNS Discovery Tool
====================
Discovers local network devices via mDNS/Zeroconf.
Returns empty list when zeroconf is not available.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.mdns_discovery")

_DISCOVERY_TIMEOUT = 3.0  # seconds to listen for mDNS advertisements


class MDNSDiscoveryTool(BaseTool):
    """
    Local network device discovery via mDNS/Zeroconf.

    Browses mDNS service types and returns discovered hosts.
    Returns empty list when zeroconf library is not available.
    """

    name: str = "mdns_discovery"
    description: str = "Discover local network devices via mDNS/Zeroconf"

    def __init__(self) -> None:
        """Initialise mDNS discovery tool."""
        self._has_zeroconf: bool = self._check_zeroconf()
        if not self._has_zeroconf:
            logger.warning("MDNSDiscoveryTool: zeroconf not available — returns empty list")

    def _check_zeroconf(self) -> bool:
        """Check if zeroconf is installed."""
        try:
            import zeroconf  # type: ignore[import-untyped]  # noqa: F401
            return True
        except ImportError:
            return False

    def run(
        self,
        bead_id: str,
        service_type: str = "_http._tcp.local.",
    ) -> dict[str, Any]:
        """
        Discover local network devices via mDNS.

        Args:
            bead_id: BEAD ID for traceability (required).
            service_type: mDNS service type to browse (e.g. "_http._tcp.local.",
                          "_octoprint._tcp.local.", "_klipper._tcp.local.").

        Returns:
            Dict with key:
                - devices (list[dict]): Each with name, host, port, type.
        """
        if not bead_id:
            return {"error": "bead_id is required", "status": "error", "devices": []}

        if not self._has_zeroconf:
            logger.info(
                "MDNSDiscovery mock: zeroconf unavailable, returning empty list (bead=%s)",
                bead_id,
            )
            return {"devices": [], "status": "mock", "service_type": service_type}

        return self._discover(service_type, bead_id)

    def _discover(self, service_type: str, bead_id: str) -> dict[str, Any]:
        """Run actual mDNS discovery using zeroconf."""
        try:
            from zeroconf import ServiceBrowser, Zeroconf  # type: ignore[import-untyped]

            discovered: list[dict[str, Any]] = []

            class _Listener:
                def add_service(self, zc: Any, type_: str, name: str) -> None:
                    info = zc.get_service_info(type_, name)
                    if info:
                        addr = ".".join(str(b) for b in info.addresses[0]) if info.addresses else ""
                        discovered.append(
                            {
                                "name": name,
                                "host": addr,
                                "port": info.port,
                                "type": type_,
                            }
                        )

                def remove_service(self, zc: Any, type_: str, name: str) -> None:
                    pass

                def update_service(self, zc: Any, type_: str, name: str) -> None:
                    pass

            zc = Zeroconf()
            browser = ServiceBrowser(zc, service_type, _Listener())
            time.sleep(_DISCOVERY_TIMEOUT)
            zc.close()

            logger.info(
                "MDNSDiscovery: found %d devices of type '%s' (bead=%s)",
                len(discovered),
                service_type,
                bead_id,
            )
            return {
                "devices": discovered,
                "status": "success",
                "service_type": service_type,
            }
        except Exception as exc:
            logger.exception("MDNSDiscovery failed: %s", exc)
            return {"devices": [], "status": "error", "error": str(exc)}

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute via ToolRegistry interface.

        Args:
            params: Dict with bead_id and optional service_type.

        Returns:
            ToolResult wrapping run() output.
        """
        bead_id = params.get("bead_id", "")
        service_type: str = params.get("service_type", "_http._tcp.local.")

        data = self.run(bead_id=bead_id, service_type=service_type)
        if data.get("status") == "error":
            return ToolResult(
                tool=self.name, status="error", data=data, error=data.get("error", "")
            )
        return ToolResult(tool=self.name, status="success", data=data)
