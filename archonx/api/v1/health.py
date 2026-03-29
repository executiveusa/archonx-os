"""Health endpoint — plain REST for load balancers and Coolify."""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    kernel = state.kernel

    services = {
        "kernel": "operational" if kernel and kernel._booted else "booting",
        "agents": len(kernel.registry.all()) if kernel else 0,
        "cost_guard": "active" if kernel and kernel.cost_guard else "disabled",
        "popebot": "active" if kernel and kernel.popebot else "inactive",
        "hermes": "active" if kernel and kernel.hermes else "inactive",
    }

    all_ok = services["kernel"] == "operational"
    return JSONResponse({
        "status": "ok" if all_ok else "degraded",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
    }, status_code=200 if all_ok else 206)
