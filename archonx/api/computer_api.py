"""
Computer Control API

FastAPI routes for browser automation, desktop control, and voice-triggered execution.
Integrates Open Interpreter, Playwright, and Desktop Commander runtimes.

ZTE-20260308-0006: Computer control API
"""

from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks
import logging
from typing import Optional, Dict, Any
import json
from datetime import datetime

from archonx.integrations.open_interpreter_runtime import (
    get_runtime,
    InterpreterSession
)
from archonx.monitoring.session_monitor import (
    get_monitor,
    EventType
)
from archonx.services.session_store import get_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions")
async def create_session(
    task: str,
    mode: str = "browser",
    model: str = "claude-3-5-sonnet",
    metadata: Dict[str, Any] = None
):
    """Create new interpreter session"""
    try:
        runtime = await get_runtime()
        monitor = get_monitor()

        session = await runtime.create_session(task, mode, metadata)

        # Log event
        await monitor.log_event(
            session.session_id,
            EventType.SESSION_CREATED,
            data={"task": task, "mode": mode, "model": model}
        )

        return session

    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions():
    """List all sessions"""
    try:
        runtime = await get_runtime()
        monitor = get_monitor()

        sessions = runtime.list_sessions()
        summaries = [
            {**session.__dict__, "events": monitor.get_event_count(session.session_id)}
            for session in sessions
        ]

        return {
            "sessions": summaries,
            "total": len(summaries)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    try:
        runtime = await get_runtime()
        monitor = get_monitor()

        session = runtime.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            **session.__dict__,
            "event_count": monitor.get_event_count(session_id),
            "summary": monitor.get_session_summary(session_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/execute")
async def execute_task(
    session_id: str,
    prompt: str,
    background_tasks: BackgroundTasks
):
    """Execute task in session"""
    try:
        runtime = await get_runtime()
        monitor = get_monitor()
        store = get_store()

        session = runtime.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Log task started
        await monitor.log_event(
            session_id,
            EventType.TASK_RECEIVED,
            data={"prompt": prompt[:200]}
        )

        # Execute and stream results
        results = []
        async for output in runtime.execute(session_id, prompt):
            results.append(output)
            await monitor.log_event(
                session_id,
                EventType.RESULT_RECEIVED,
                data={"output": output[:100]}
            )

        # Save session
        background_tasks.add_task(
            store.save_session,
            session_id,
            {
                "session_id": session_id,
                "task": session.task,
                "mode": session.mode,
                "status": session.status,
                "result": "\n".join(results),
                "created_at": session.created_at,
                "updated_at": datetime.now().isoformat()
            }
        )

        return {
            "session_id": session_id,
            "status": "completed",
            "output": "\n".join(results)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execute error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Get session events"""
    try:
        monitor = get_monitor()

        # Parse event type if provided
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = EventType[event_type.upper()]
            except KeyError:
                pass

        events = monitor.get_events(session_id, event_type_enum, limit)

        return {
            "session_id": session_id,
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/artifacts")
async def list_artifacts(session_id: str):
    """List session artifacts"""
    try:
        store = get_store()
        artifacts = await store.list_artifacts(session_id)

        return {
            "session_id": session_id,
            "artifacts": artifacts,
            "count": len(artifacts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/artifacts/{filename}")
async def get_artifact(session_id: str, filename: str):
    """Download artifact"""
    try:
        store = get_store()
        data = await store.load_artifact(session_id, filename)

        if not data:
            raise HTTPException(status_code=404, detail="Artifact not found")

        return {
            "session_id": session_id,
            "filename": filename,
            "size": len(data)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/screenshot")
async def capture_screenshot(session_id: str):
    """Capture screenshot in session"""
    try:
        runtime = await get_runtime()
        monitor = get_monitor()
        store = get_store()

        filename = await runtime.screenshot(session_id)
        if not filename:
            raise HTTPException(status_code=400, detail="Screenshot failed")

        await monitor.log_event(
            session_id,
            EventType.SCREENSHOT,
            data={"filename": filename}
        )

        return {
            "session_id": session_id,
            "filename": filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/replay")
async def render_replay(session_id: str):
    """Render session as replay video"""
    try:
        monitor = get_monitor()

        await monitor.log_event(
            session_id,
            EventType.VIDEO_RENDER_REQUESTED,
            data={"session_id": session_id}
        )

        # Phase 2: Trigger Remotion composition
        return {
            "session_id": session_id,
            "status": "rendering",
            "job_id": f"replay-{session_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    monitor = get_monitor()
    await websocket.accept()

    async def send_event(event):
        """Send event to client"""
        try:
            await websocket.send_json(event.to_dict())
        except Exception as e:
            logger.error(f"WebSocket send error: {e}")

    # Subscribe to events
    listener_id = await monitor.subscribe(session_id, send_event)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await monitor.unsubscribe(session_id, listener_id)


@router.get("/stats")
async def get_statistics():
    """Get system statistics"""
    try:
        monitor = get_monitor()
        store = get_store()

        return {
            "monitor": monitor.get_event_count("all"),
            "store": await store.get_statistics()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
