"""
VisionClaw (PauliClaw) — Visual Intelligence Endpoints
=======================================================
FastAPI router that scaffolds image/video stream ingestion
for the VisionClaw agent (VCL-008). Bridges to Meta Ray-Ban
AI Glasses SDK when hardware is available.

Routes:
    POST /api/visionclaw/image       — Submit a single image for analysis
    POST /api/visionclaw/video-frame — Submit a video frame from live stream
    GET  /api/visionclaw/status      — Agent status and capabilities
    POST /api/visionclaw/configure   — Update VisionClaw configuration
    GET  /api/visionclaw/feed        — Get latest processed feed results
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("archonx.visionclaw")

router = APIRouter(prefix="/api/visionclaw", tags=["VisionClaw"])

# ---------------------------------------------------------------------------
# State — VCL-008 agent status
# ---------------------------------------------------------------------------
_visionclaw_state: dict[str, Any] = {
    "agent_id": "VCL-008",
    "name": "VisionClaw",
    "alias": "PauliClaw",
    "status": "active",
    "capabilities": [
        "image_analysis",
        "video_frame_analysis",
        "object_detection",
        "scene_description",
        "text_extraction",
    ],
    "hardware": {
        "meta_rayban_connected": False,
        "camera_resolution": None,
        "stream_fps": None,
    },
    "config": {
        "model": "gpt-4o",
        "max_image_size_mb": 10,
        "auto_describe": True,
        "feed_to_yappyverse": True,
    },
    "stats": {
        "images_processed": 0,
        "video_frames_processed": 0,
        "last_activity": None,
    },
}

# In-memory feed buffer (last N results)
_feed_buffer: list[dict[str, Any]] = []
_MAX_FEED = 50


class VisionClawConfig(BaseModel):
    model: str | None = None
    max_image_size_mb: int | None = None
    auto_describe: bool | None = None
    feed_to_yappyverse: bool | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status")
async def visionclaw_status() -> JSONResponse:
    """Return current VisionClaw agent status and capabilities."""
    return JSONResponse(_visionclaw_state)


@router.post("/image")
async def analyze_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Submit a single image for VisionClaw analysis.
    Returns a job ID and queued status. Actual vision model
    processing is handled asynchronously by the agent pipeline.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    max_size = _visionclaw_state["config"]["max_image_size_mb"]

    if size_mb > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large: {size_mb:.1f}MB (max {max_size}MB)",
        )

    job_id = str(uuid.uuid4())
    timestamp = time.time()

    result = {
        "job_id": job_id,
        "status": "queued",
        "filename": file.filename,
        "size_mb": round(size_mb, 2),
        "content_type": file.content_type,
        "timestamp": timestamp,
        "analysis": None,  # Populated when processing completes
    }

    _feed_buffer.append(result)
    if len(_feed_buffer) > _MAX_FEED:
        _feed_buffer.pop(0)

    _visionclaw_state["stats"]["images_processed"] += 1
    _visionclaw_state["stats"]["last_activity"] = timestamp

    logger.info("VisionClaw image queued: %s (%.2fMB) → job %s", file.filename, size_mb, job_id)

    return JSONResponse(result, status_code=202)


@router.post("/video-frame")
async def analyze_video_frame(file: UploadFile = File(...)) -> JSONResponse:
    """
    Submit a video frame from a live stream (Meta Ray-Ban or webcam).
    Lightweight endpoint optimized for high-frequency frame submission.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Frame must be an image")

    content = await file.read()
    job_id = str(uuid.uuid4())
    timestamp = time.time()

    result = {
        "job_id": job_id,
        "status": "queued",
        "frame_size_bytes": len(content),
        "timestamp": timestamp,
    }

    _visionclaw_state["stats"]["video_frames_processed"] += 1
    _visionclaw_state["stats"]["last_activity"] = timestamp

    return JSONResponse(result, status_code=202)


@router.post("/configure")
async def configure_visionclaw(config: VisionClawConfig) -> JSONResponse:
    """Update VisionClaw runtime configuration."""
    updates: dict[str, Any] = {}
    for field, value in config.model_dump(exclude_none=True).items():
        _visionclaw_state["config"][field] = value
        updates[field] = value

    logger.info("VisionClaw config updated: %s", updates)
    return JSONResponse({"updated": updates, "config": _visionclaw_state["config"]})


@router.get("/feed")
async def get_feed() -> JSONResponse:
    """Return the latest processed feed results (last 50)."""
    return JSONResponse({
        "count": len(_feed_buffer),
        "feed": list(reversed(_feed_buffer)),
    })


@router.get("/health")
async def health() -> JSONResponse:
    """Health check for VisionClaw subsystem."""
    return JSONResponse({
        "agent": "VCL-008",
        "alias": "PauliClaw",
        "status": _visionclaw_state["status"],
        "images_processed": _visionclaw_state["stats"]["images_processed"],
        "video_frames_processed": _visionclaw_state["stats"]["video_frames_processed"],
    })
