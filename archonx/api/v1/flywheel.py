"""Flywheel + billing endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/flywheel")


@router.get("")
async def get_flywheel_stats(request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    return JSONResponse(kernel.flywheel.stats)


@router.get("/billing/{user_id}")
async def get_billing(user_id: str, request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    return JSONResponse({
        "user_id": user_id,
        "balance": kernel.billing.balance(user_id),
        "history": [
            {"id": t.id, "amount": t.amount, "source": t.source, "description": t.description}
            for t in kernel.billing.history(user_id)
        ],
    })
