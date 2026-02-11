"""
ARCHONX Core Agents Package

This package contains all agent implementations for the ARCHONX dual-crew system.
"""

from .pauli import PauliAgent
from .synthia import SynthiaAgent

__version__ = "1.0.0"
__all__ = ["PauliAgent", "SynthiaAgent"]
