"""
ArchonX FastAPI Server
======================
WebSocket + REST API for the visualization frontend.
Serves:
    - /api/board       — Chessboard state
    - /api/dashboard   — Metrics dashboard
    - /api/meetings    — Pauli's Place scene
    - /ws              — Real-time WebSocket updates
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from archonx.kernel import ArchonXKernel
from archonx.core.metrics import Leaderboard
from archonx.visualization.chessboard import ChessboardView
from archonx.visualization.dashboard import MetricsDashboard
from archonx.visualization.paulis_place_view import PaulisPlaceView

logger = logging.getLogger("archonx.server")
_PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

# ---------------------------------------------------------------------------
# Globals (populated at startup)
# ---------------------------------------------------------------------------
_kernel: ArchonXKernel | None = None
_chessboard: ChessboardView | None = None
_dashboard: MetricsDashboard | None = None
_paulis_view: PaulisPlaceView | None = None
_leaderboard: Leaderboard | None = None
_ws_clients: set[WebSocket] = set()


def _parse_allowed_origins() -> list[str]:
    raw = os.getenv(
        "ARCHONX_ALLOWED_ORIGINS",
        "http://localhost:8080,http://localhost:5173,http://localhost:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _kernel, _chessboard, _dashboard, _paulis_view, _leaderboard

    # Boot kernel
    _kernel = ArchonXKernel()
    await _kernel.boot()

    # Build visualization state
    _leaderboard = Leaderboard()
    _chessboard = ChessboardView(_kernel.registry)
    _dashboard = MetricsDashboard(_kernel.registry, _leaderboard)
    _paulis_view = PaulisPlaceView()

    logger.info("Server ready — visualization live.")
    yield

    # Shutdown
    await _kernel.shutdown()
    logger.info("Server shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ArchonX OS",
        description="64-agent dual-crew AI operating system",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_allowed_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_api_token(request: Request, call_next):  # type: ignore[no-redef]
        token = os.getenv("ARCHONX_API_TOKEN", "").strip()
        if token and request.url.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            auth_header = request.headers.get("authorization", "")
            expected = f"Bearer {token}"
            if auth_header != expected:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    # ----- REST endpoints -----

    @app.get("/api/board")
    async def get_board() -> JSONResponse:
        if _chessboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_chessboard.to_dict())

    @app.get("/api/dashboard")
    async def get_dashboard() -> JSONResponse:
        if _dashboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_dashboard.to_dict())

    @app.get("/api/meetings")
    async def get_meetings() -> JSONResponse:
        if _paulis_view is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_paulis_view.to_dict())

    @app.get("/api/agents")
    async def get_agents() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        agents = [
            {
                "id": a.agent_id,
                "name": a.name,
                "crew": a.crew.value,
                "role": a.role.value,
                "position": a.position,
                "specialty": a.specialty,
                "status": a.status.value,
                "health": a.health,
                "tasks": a.tasks_completed,
                "score": a.score,
            }
            for a in _kernel.registry.all()
        ]
        return JSONResponse({"agents": agents, "count": len(agents)})

    @app.post("/api/task")
    async def submit_task(task: dict[str, Any]) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        result = await _kernel.execute_task(task)
        # Emit to theater
        _kernel.theater.emit(
            "task_complete", "", "kernel", f"Task completed: {task.get('type', 'unknown')}",
            data=result,
        )
        # Broadcast update to all WS clients
        await _broadcast({"event": "task_result", "data": result})
        return JSONResponse(result)

    # ----- Theater endpoints -----

    @app.get("/api/theater/events")
    async def get_theater_events(limit: int = 50) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        events = _kernel.theater.get_recent_events(limit)
        return JSONResponse({
            "events": [
                {
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "agent": e.agent_name,
                    "description": e.description,
                    "crew": e.crew,
                }
                for e in events
            ],
            "stats": _kernel.theater.stats,
        })

    @app.post("/api/theater/session")
    async def start_theater_session(body: dict[str, Any]) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        viewer_id = body.get("viewer_id", "anonymous")
        session = _kernel.theater.start_session(viewer_id)
        return JSONResponse({"session_id": session.session_id, "viewer_id": viewer_id})

    @app.delete("/api/theater/session/{session_id}")
    async def end_theater_session(session_id: str) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        session = _kernel.theater.end_session(session_id)
        if not session:
            return JSONResponse({"error": "session not found"}, status_code=404)
        return JSONResponse({
            "session_id": session.session_id,
            "tokens_spent": session.tokens_spent,
            "events_watched": session.events_watched,
        })

    # ----- Flywheel + Billing endpoints -----

    @app.get("/api/flywheel")
    async def get_flywheel_stats() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_kernel.flywheel.stats)

    @app.get("/api/billing/{user_id}")
    async def get_billing(user_id: str) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse({
            "user_id": user_id,
            "balance": _kernel.billing.balance(user_id),
            "history": [
                {"id": t.id, "amount": t.amount, "source": t.source, "description": t.description}
                for t in _kernel.billing.history(user_id)
            ],
        })

    @app.get("/api/skills")
    async def list_skills() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        skills = _kernel.skill_registry.list_skills()
        return JSONResponse({
            "skills": [
                {"name": s.name, "description": s.description, "category": s.category.value}
                for s in skills
            ],
            "count": len(skills),
        })

    @app.get("/api/tools")
    async def list_tools() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        tools = _kernel.tools.list_tools()
        return JSONResponse({"tools": tools})

    # ----- WebSocket -----

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        _ws_clients.add(ws)
        logger.info("WebSocket client connected (%d total)", len(_ws_clients))
        try:
            while True:
                data = await ws.receive_text()
                msg = json.loads(data)
                # Handle incoming WS commands
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
                elif msg.get("type") == "subscribe_board":
                    if _chessboard:
                        await ws.send_json({"type": "board", "data": _chessboard.to_dict()})
                elif msg.get("type") == "subscribe_dashboard":
                    if _dashboard:
                        await ws.send_json({"type": "dashboard", "data": _dashboard.to_dict()})
        except WebSocketDisconnect:
            _ws_clients.discard(ws)
            logger.info("WebSocket client disconnected (%d remaining)", len(_ws_clients))

    # Frontend static app (served last so /api and /ws stay authoritative)
    if _PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(_PUBLIC_DIR), html=True), name="frontend")

    return app


async def _broadcast(message: dict[str, Any]) -> None:
    """Send a message to all connected WebSocket clients."""
    dead: set[WebSocket] = set()
    for ws in _ws_clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    _ws_clients -= dead
