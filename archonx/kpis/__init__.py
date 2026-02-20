"""
ArchonX KPI Module
==================
Key Performance Indicators dashboard for agent performance tracking.

Components:
- KPIDashboard: Performance tracking and reporting
- AgentMetrics: Individual agent metrics
- RevenueTracker: Revenue tracking for $100M goal

BEAD-005: KPI Dashboard Implementation
"""

from archonx.kpis.dashboard import (
    KPIDashboard,
    AgentMetrics,
    RevenueTracker,
    RevenueGoal,
    get_kpi_dashboard
)

__all__ = [
    "KPIDashboard",
    "AgentMetrics",
    "RevenueTracker",
    "RevenueGoal",
    "get_kpi_dashboard",
]
