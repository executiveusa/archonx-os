"""Agent Theater — watch agents in action."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/theater")


@router.get("/events")
async def get_events(request: Request, limit: int = 50) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    events = kernel.theater.get_recent_events(limit)
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
        "stats": kernel.theater.stats,
    })


@router.post("/session")
async def start_session(body: dict[str, Any], request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    viewer_id = body.get("viewer_id", "anonymous")
    session = kernel.theater.start_session(viewer_id)
    return JSONResponse({"session_id": session.session_id, "viewer_id": viewer_id})


@router.delete("/session/{session_id}")
async def end_session(session_id: str, request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    session = kernel.theater.end_session(session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, status_code=404)
    return JSONResponse({
        "session_id": session.session_id,
        "tokens_spent": session.tokens_spent,
        "events_watched": session.events_watched,
    })
