"""Chat routes - integrates Claude API and multi-model support"""

import os
from typing import List
from fastapi import APIRouter, HTTPException
import httpx

from models import ChatRequest, ChatResponse, Message

router = APIRouter()

# Initialize clients
anthropic_client = None
available_models = [
    "claude-3-5-sonnet",
    "claude-3-opus",
    "claude-3-haiku",
]


async def initialize():
    """Initialize chat system"""
    global anthropic_client
    try:
        from anthropic import Anthropic
        api_key = os.getenv("CLAUDE_API_KEY")
        if api_key:
            anthropic_client = Anthropic(api_key=api_key)
    except ImportError:
        print("Warning: anthropic library not installed")


@router.get("/models")
async def get_models():
    """Get available models"""
    return {"models": available_models}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get response"""
    if not anthropic_client:
        raise HTTPException(status_code=503, detail="Claude client not initialized")

    try:
        # Convert messages to Claude format
        messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]

        # Call Claude API
        response = anthropic_client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            messages=messages
        )

        return ChatResponse(
            response=response.content[0].text,
            model=request.model,
            tokens_used=response.usage.output_tokens
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response (SSE)"""
    if not anthropic_client:
        raise HTTPException(status_code=503, detail="Claude client not initialized")

    async def generate():
        try:
            messages = [
                {"role": m.role, "content": m.content}
                for m in request.messages
            ]

            with anthropic_client.messages.stream(
                model=request.model,
                max_tokens=request.max_tokens,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {text}\n\n"

        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"

    return {
        "status": "streaming",
        "generator": generate()
    }
