"""Octelium compatibility layer for ArchonX Access Kernel.

This adapter intentionally keeps ArchonX API stable while allowing selective
use of Octelium patterns/components in development.
"""

from dataclasses import dataclass


@dataclass
class CompatConfig:
    enabled: bool = False
    upstream_mode: str = "none"  # none|dev


def map_archonx_grant_to_octelium_scope(resource: str, action: str) -> str:
    return f"service:{resource}:{action}"
