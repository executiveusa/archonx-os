"""Board state + dashboard endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/board")


@router.get("")
async def get_board(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    if state.chessboard is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    return JSONResponse(state.chessboard.to_dict())


@router.get("/dashboard")
async def get_dashboard(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    if state.dashboard is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    return JSONResponse(state.dashboard.to_dict())


@router.get("/meetings")
async def get_meetings(request: Request) -> JSONResponse:
    state = request.app.state.app_state
    if state.paulis_view is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    return JSONResponse(state.paulis_view.to_dict())
