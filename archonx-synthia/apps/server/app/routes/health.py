"""Health / readiness probe."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz():
    return {"ok": True, "service": "synthia-server", "version": "0.1.0"}


@router.get("/readyz")
async def readyz():
    # TODO P3: check Notion, Orgo, GLM-5 connectivity
    return {"ok": True, "checks": {"notion": "stub", "orgo": "stub", "glm5": "stub"}}
