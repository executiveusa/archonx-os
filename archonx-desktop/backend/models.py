"""Data models for ArchonX Desktop API"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    model: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request"""
    model: str = "claude-3-5-sonnet"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    model: str
    tokens_used: Optional[int] = None


class DeploymentStatus(BaseModel):
    """Deployment status"""
    deployment_id: str
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    logs: List[str] = []
    error: Optional[str] = None


class Service(BaseModel):
    """Coolify service"""
    uuid: str
    name: str
    status: str
    url: Optional[str] = None
    last_deploy: Optional[str] = None
    replicas: Optional[int] = None


class Agent(BaseModel):
    """AI Agent"""
    id: str
    name: str
    status: str  # "idle", "busy", "error"
    crew: str  # "white", "black", "hybrid"
    current_task: Optional[str] = None
    skills: List[str] = []
    last_activity: Optional[str] = None


class SessionModel(BaseModel):
    """Computer/Agent session"""
    session_id: str
    created_at: str
    updated_at: str
    mode: str  # "browser", "desktop", "hybrid", "agent"
    task: str
    status: str  # "pending", "running", "completed", "error"
    current_step: int = 0
    model: Optional[str] = None
    backend: Optional[str] = None
    screenshots_dir: Optional[str] = None
    artifacts_dir: Optional[str] = None
    event_count: int = 0
    metadata: Dict[str, Any] = {}
    result_summary: Optional[str] = None
    error: Optional[str] = None


class SessionEvent(BaseModel):
    """Session event for monitoring"""
    event_id: str
    session_id: str
    timestamp: str
    event_type: str  # "started", "action", "screenshot", "result", "error"
    data: Dict[str, Any]


class VideoJobRequest(BaseModel):
    """Video generation request"""
    script: str
    title: Optional[str] = None
    style: Optional[str] = None
    duration: Optional[int] = None


class WorkflowExecution(BaseModel):
    """n8n workflow execution"""
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    data: Dict[str, Any] = {}


class ResearchQuery(BaseModel):
    """Research query"""
    query: str
    num_results: Optional[int] = 5


class ResearchResult(BaseModel):
    """Research result"""
    results: List[str]
    query: str
    timestamp: str
