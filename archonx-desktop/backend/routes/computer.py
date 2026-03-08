"""Computer control routes - integrates browser and desktop automation"""

import os
import sys
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, HTTPException
from models import SessionModel, SessionEvent

router = APIRouter()

# Session store
sessions: dict[str, SessionModel] = {}
session_events: dict[str, list[SessionEvent]] = {}


@router.post("/sessions")
async def create_session(
    task: str,
    mode: str = "browser",  # browser, desktop, hybrid
    model: str = "claude-3-5-sonnet"
):
    """Create a new computer control session"""
    try:
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        session = SessionModel(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            mode=mode,
            task=task,
            status="pending",
            model=model,
            screenshots_dir=f"/tmp/archonx/screenshots/{session_id}",
            artifacts_dir=f"/tmp/archonx/artifacts/{session_id}",
        )

        sessions[session_id] = session
        session_events[session_id] = []

        # Log session created event
        event = SessionEvent(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=now,
            event_type="created",
            data={"mode": mode, "task": task}
        )
        session_events[session_id].append(event)

        return session

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions():
    """List all sessions"""
    try:
        return {
            "sessions": list(sessions.values()),
            "total": len(sessions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        return sessions[session_id]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/actions")
async def execute_action(session_id: str, action: str, params: dict = None):
    """Execute an action in a session"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        session.status = "running"

        # Log action event
        event = SessionEvent(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            event_type="action",
            data={"action": action, "params": params}
        )
        session_events[session_id].append(event)

        # In Phase 2, route to Open Interpreter or desktop/browser agent
        # For now, return mock execution result
        return {
            "session_id": session_id,
            "action": action,
            "status": "executed",
            "result": {"mock": "result"}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/events")
async def get_session_events(session_id: str):
    """Get all events for a session"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "events": session_events.get(session_id, []),
            "count": len(session_events.get(session_id, []))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/screenshots/{filename}")
async def get_screenshot(session_id: str, filename: str):
    """Get screenshot from session"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        # In production, serve actual screenshot file
        return {
            "session_id": session_id,
            "filename": filename,
            "url": f"/tmp/archonx/screenshots/{session_id}/{filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/render-replay")
async def render_replay(session_id: str):
    """Render session as replay video (Remotion)"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        # In Phase 2, trigger Remotion composition
        return {
            "session_id": session_id,
            "status": "rendering",
            "job_id": str(uuid.uuid4())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time session updates"""
    if session_id not in sessions:
        await websocket.close(code=404)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back or process command
            await websocket.send_json({
                "type": "pong",
                "session_id": session_id,
                "data": data
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
