"""ArchonX API v1 — versioned router package."""

from fastapi import APIRouter

from archonx.api.v1.health import router as health_router
from archonx.api.v1.agents import router as agents_router
from archonx.api.v1.board import router as board_router
from archonx.api.v1.theater import router as theater_router
from archonx.api.v1.cost import router as cost_router
from archonx.api.v1.tasks import router as tasks_router
from archonx.api.v1.conx import router as conx_router
from archonx.api.v1.flywheel import router as flywheel_router
from archonx.api.v1.cockpit import router as cockpit_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router, tags=["health"])
v1_router.include_router(agents_router, tags=["agents"])
v1_router.include_router(board_router, tags=["board"])
v1_router.include_router(theater_router, tags=["theater"])
v1_router.include_router(cost_router, tags=["cost"])
v1_router.include_router(tasks_router, tags=["tasks"])
v1_router.include_router(conx_router, tags=["conx"])
v1_router.include_router(flywheel_router, tags=["flywheel"])
v1_router.include_router(cockpit_router, tags=["cockpit"])
