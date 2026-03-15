"""FastAPI application factory — ARCHONX:SYNTHIA orchestrator."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import agents, approvals, health, onboarding, runner, tasks, voice

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("synthia.server.starting", base_url=settings.base_url)
    yield
    logger.info("synthia.server.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ARCHONX:SYNTHIA",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ── CORS (lock down in production) ────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request-ID middleware ─────────────────────────────
    @app.middleware("http")
    async def inject_trace_id(request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response

    # ── Global error handler ──────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_error", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Internal server error"},
        )

    # ── Routers ───────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
    app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
    app.include_router(runner.router, prefix="/api/runner", tags=["runner"])
    app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
    app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])

    return app


app = create_app()
