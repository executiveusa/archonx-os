"""Shared application state — replaces module-level globals."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from archonx.kernel import ArchonXKernel
from archonx.core.metrics import Leaderboard
from archonx.visualization.chessboard import ChessboardView
from archonx.visualization.dashboard import MetricsDashboard
from archonx.visualization.paulis_place_view import PaulisPlaceView


@dataclass
class AppState:
    """Single object holding all server-wide state — injected via app.state."""

    kernel: ArchonXKernel | None = None
    chessboard: ChessboardView | None = None
    dashboard: MetricsDashboard | None = None
    paulis_view: PaulisPlaceView | None = None
    leaderboard: Leaderboard | None = None
    ws_clients: set[WebSocket] = field(default_factory=set)
    task_status: dict[str, dict[str, Any]] = field(default_factory=dict)
    registered_machines: dict[str, dict[str, Any]] = field(default_factory=dict)
