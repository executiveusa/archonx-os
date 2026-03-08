"""ArchonX Desktop Control Tower - FastAPI Backend"""

import os
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routes import chat, deployments, agents, workflows, video, research, computer
from models import SessionModel

# Initialize FastAPI app
app = FastAPI(
    title="ArchonX Desktop API",
    description="Control tower for ArchonX OS agent deployment and monitoring",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(deployments.router, prefix="/api/deployments", tags=["deployments"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(computer.router, prefix="/api/computer", tags=["computer"])

# Global session store (can be upgraded to database)
active_sessions: dict = {}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("ArchonX Desktop API starting...")
    await chat.initialize()
    await deployments.initialize()
    await agents.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("ArchonX Desktop API shutting down...")


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }


@app.get("/api/status")
async def status():
    """Get system status"""
    return {
        "uptime": "running",
        "active_sessions": len(active_sessions),
        "components": {
            "chat": "ready",
            "deployments": "ready",
            "agents": "ready",
            "video": "ready",
        }
    }


@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    return {
        "coolify_url": os.getenv("COOLIFY_BASE_URL", ""),
        "openclaw_url": os.getenv("OPENCLAW_URL", "ws://127.0.0.1:18789"),
        "n8n_url": os.getenv("N8N_URL", ""),
        "default_model": os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet"),
    }


@app.post("/api/settings")
async def save_settings(config: dict):
    """Save settings (in-memory for now)"""
    # In production, persist to database or config file
    for key, value in config.items():
        os.environ[key.upper()] = value
    return {"status": "saved"}


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process based on message type
            await websocket.send_json({"type": "pong", "data": data})
    except Exception as e:
        print(f"WebSocket error: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
