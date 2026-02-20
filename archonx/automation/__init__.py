"""
ArchonX Automation Module
=========================
Automated tasks and self-improvement cycles.

Components:
- DailySelfImprovement: 3 AM automated tasks
- PAULIWHEELSync: Scheduled sync meetings
- AutomatedReporting: Report generation

BEAD-006: Daily Self-Improvement Cycle Implementation
"""

from archonx.automation.self_improvement import (
    DailySelfImprovement,
    PAULIWHEELSync,
    AutomatedTask,
    get_self_improvement
)

__all__ = [
    "DailySelfImprovement",
    "PAULIWHEELSync",
    "AutomatedTask",
    "get_self_improvement",
]
