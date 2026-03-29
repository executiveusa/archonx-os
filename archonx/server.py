"""
ArchonX FastAPI Server v2
=========================
Production-grade API server with versioned routers.
All routes under /v1/ — CORS locked, ConX authed, stateless-safe.
Legacy /api/* routes preserved for backward compatibility.
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from archonx.kernel import ArchonXKernel
from archonx.core.metrics import Leaderboard
from archonx.visualization.chessboard import ChessboardView
from archonx.visualization.dashboard import MetricsDashboard
from archonx.visualization.paulis_place_view import PaulisPlaceView
from archonx.api.state import AppState
from archonx.api.v1 import v1_router

logger = logging.getLogger("archonx.server")
_PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

# Explicit CORS origins — no wildcards in production
_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "https://archonx-os.vercel.app",
    "https://chess-theater.vercel.app",
    "https://synthia-3-0.vercel.app",
]


def _parse_allowed_origins() -> list[str]:
    extra = os.getenv("ARCHONX_ALLOWED_ORIGINS", "")
    origins = list(_ALLOWED_ORIGINS)
    if extra:
        origins.extend(o.strip() for o in extra.split(",") if o.strip())
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    state = AppState()

    # Boot kernel
    state.kernel = ArchonXKernel()
    await state.kernel.boot()

    # Build visualization state
    state.leaderboard = Leaderboard()
    state.chessboard = ChessboardView(state.kernel.registry)
    state.dashboard = MetricsDashboard(state.kernel.registry, state.leaderboard)
    state.paulis_view = PaulisPlaceView()

    app.state.app_state = state
    logger.info("Server ready — v2 routers live, %d agents.", len(state.kernel.registry.all()))
    yield

    # Shutdown
    await state.kernel.shutdown()
    logger.info("Server shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ArchonX OS",
        description="64-agent dual-crew AI operating system — US backend",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_allowed_origins(),
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],
        allow_credentials=True,
    )

    # API token middleware for mutating requests
    @app.middleware("http")
    async def require_api_token(request: Request, call_next):
        token = os.getenv("ARCHONX_API_TOKEN", "").strip()
        if (
            token
            and (request.url.path.startswith("/v1/") or request.url.path.startswith("/api/"))
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
        ):
            auth_header = request.headers.get("authorization", "")
            if auth_header != f"Bearer {token}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    # Mount v1 API router
    app.include_router(v1_router)

    # Legacy /api/* backwards compat — redirect to /v1/*
    @app.get("/api/board")
    async def legacy_board(request: Request) -> JSONResponse:
        state = request.app.state.app_state
        if state.chessboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(state.chessboard.to_dict())

    @app.get("/api/dashboard")
    async def legacy_dashboard(request: Request) -> JSONResponse:
        state = request.app.state.app_state
        if state.dashboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(state.dashboard.to_dict())

    @app.get("/api/agents")
    async def legacy_agents(request: Request) -> JSONResponse:
        kernel = request.app.state.app_state.kernel
        if kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        agents = [
            {"id": a.agent_id, "name": a.name, "crew": a.crew.value, "status": a.status.value}
            for a in kernel.registry.all()
        ]
        return JSONResponse({"agents": agents, "count": len(agents)})

    @app.get("/health")
    async def legacy_health() -> JSONResponse:
        return JSONResponse({"status": "ok", "version": "2.0.0", "note": "Use /v1/health for full status"})

    # WebSocket — stays on root for easy client connection
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        state = app.state.app_state
        state.ws_clients.add(ws)
        logger.info("WS connected (%d total)", len(state.ws_clients))
        try:
            while True:
                data = await ws.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
                elif msg.get("type") == "subscribe_board":
                    if state.chessboard:
                        await ws.send_json({"type": "board", "data": state.chessboard.to_dict()})
                elif msg.get("type") == "subscribe_dashboard":
                    if state.dashboard:
                        await ws.send_json({"type": "dashboard", "data": state.dashboard.to_dict()})
        except WebSocketDisconnect:
            state.ws_clients.discard(ws)
            logger.info("WS disconnected (%d remaining)", len(state.ws_clients))

    # Static frontend (last — so API routes take priority)
    if _PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(_PUBLIC_DIR), html=True), name="frontend")

    return app
