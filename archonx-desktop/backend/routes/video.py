"""Video generation routes - integrates with StoryToolkitAI"""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models import VideoJobRequest

router = APIRouter()

# Mock video jobs
video_jobs = {}


@router.post("/generate")
async def generate_video(request: VideoJobRequest):
    """Queue a video generation job"""
    try:
        job_id = str(uuid.uuid4())

        video_jobs[job_id] = {
            "job_id": job_id,
            "script": request.script,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
        }

        # In production, queue job to StoryToolkitAI or Remotion
        # For now, return mock response
        return {
            "job_id": job_id,
            "status": "queued",
            "script": request.script,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/status")
async def get_video_status(job_id: str):
    """Get video generation status"""
    try:
        if job_id not in video_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = video_jobs[job_id]
        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": job.get("progress", 0),
            "video_url": job.get("video_url"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/download")
async def download_video(job_id: str):
    """Download generated video"""
    try:
        if job_id not in video_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = video_jobs[job_id]
        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail="Video not ready")

        return {"video_url": job.get("video_url")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{session_id}")
async def render_session_replay(session_id: str):
    """Render a session replay video using Remotion"""
    try:
        job_id = str(uuid.uuid4())

        # In production, trigger Remotion composition
        return {
            "job_id": job_id,
            "session_id": session_id,
            "status": "rendering",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_videos():
    """List all generated videos"""
    try:
        return {
            "videos": list(video_jobs.values()),
            "total": len(video_jobs),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
