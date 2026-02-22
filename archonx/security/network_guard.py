"""
Network Guard — SSRF protection and outbound request validation.

Blocks requests to private IP ranges, cloud metadata endpoints, and
provides DNS rebinding protection by resolving hostnames and validating
the resulting IP before allowing the connection.
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from urllib.parse import urlparse

logger = logging.getLogger("archonx.security.network_guard")

# Cloud metadata endpoints to block
_METADATA_IPS: set[str] = {
    "169.254.169.254",       # AWS / GCP / Azure
    "100.100.100.200",       # Alibaba
    "fd00:ec2::254",         # AWS IPv6
}

_METADATA_HOSTS: set[str] = {
    "metadata.google.internal",
    "metadata.goog",
}


class NetworkGuardError(Exception):
    """Raised when a network request is blocked."""


class NetworkGuard:
    """
    Validates outbound network requests to prevent SSRF.

    Checks:
    - Private / loopback / link-local IP ranges
    - Cloud metadata endpoints
    - DNS rebinding (resolve-then-check)
    - Optional host allowlist
    """

    def __init__(
        self,
        host_allowlist: set[str] | None = None,
        allow_private: bool = False,
    ) -> None:
        self.host_allowlist = host_allowlist
        self.allow_private = allow_private

    def is_private_ip(self, ip_str: str) -> bool:
        """Return True if the IP is private, loopback, link-local, or reserved."""
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            return True  # If we can't parse it, treat as unsafe

        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        )

    def _is_metadata(self, host: str, ip_str: str) -> bool:
        """Check if target is a cloud metadata endpoint."""
        return ip_str in _METADATA_IPS or host.lower() in _METADATA_HOSTS

    def check_host(self, host: str, port: int = 443) -> tuple[bool, str]:
        """
        Resolve a hostname to IPs and validate all results.
        Returns (safe, reason).
        """
        # Check metadata hosts by name
        if host.lower() in _METADATA_HOSTS:
            return False, "metadata_endpoint"

        # Check allowlist
        if self.host_allowlist is not None and host not in self.host_allowlist:
            return False, f"host_not_in_allowlist: {host}"

        # Resolve DNS to detect rebinding
        try:
            results = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            return False, f"dns_resolution_failed: {host}"

        for family, stype, proto, canonname, sockaddr in results:
            ip_str = sockaddr[0]

            if self._is_metadata(host, ip_str):
                return False, f"metadata_endpoint: {ip_str}"

            if not self.allow_private and self.is_private_ip(ip_str):
                return False, f"private_ip: {ip_str} (resolved from {host})"

        return True, "allowed"

    def is_safe_url(self, url: str) -> tuple[bool, str]:
        """
        Validate a full URL.
        Parses the URL, extracts host+port, then delegates to check_host().
        """
        try:
            parsed = urlparse(url)
        except Exception:
            return False, "url_parse_failed"

        if not parsed.hostname:
            return False, "no_hostname"

        # Block file:// and other dangerous schemes
        if parsed.scheme not in ("http", "https"):
            return False, f"blocked_scheme: {parsed.scheme}"

        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        # Fast check: is hostname an IP literal?
        try:
            ip = ipaddress.ip_address(host)
            if self._is_metadata(host, str(ip)):
                return False, f"metadata_endpoint: {ip}"
            if not self.allow_private and self.is_private_ip(str(ip)):
                return False, f"private_ip: {ip}"
            return True, "allowed"
        except ValueError:
            pass  # Not an IP literal — proceed to DNS resolution

        return self.check_host(host, port)
