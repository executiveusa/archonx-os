"""Workflow routes - integrates with n8n"""

import os
import httpx
from fastapi import APIRouter, HTTPException
from models import WorkflowExecution

router = APIRouter()

n8n_url = os.getenv("N8N_URL", "")
n8n_api_key = os.getenv("N8N_API_KEY", "")


@router.get("")
async def list_workflows():
    """List all n8n workflows"""
    try:
        if not n8n_url:
            return {"workflows": []}

        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_api_key} if n8n_api_key else {}
            response = await client.get(f"{n8n_url}/api/v1/workflows", headers=headers)
            data = response.json()
            return {"workflows": data.get("data", [])}

    except Exception as e:
        print(f"Workflow error: {e}")
        return {"workflows": []}


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, payload: dict = None):
    """Execute a workflow"""
    try:
        if not n8n_url:
            return WorkflowExecution(
                execution_id="mock-123",
                workflow_id=workflow_id,
                status="queued",
                started_at="2024-01-01T00:00:00",
            )

        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_api_key} if n8n_api_key else {}
            response = await client.post(
                f"{n8n_url}/api/v1/workflows/{workflow_id}/execute",
                json=payload or {},
                headers=headers
            )
            data = response.json()

            return WorkflowExecution(
                execution_id=data.get("id"),
                workflow_id=workflow_id,
                status="queued",
                started_at=data.get("startedAt"),
                data=data
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions")
async def get_workflow_executions(workflow_id: str):
    """Get execution history for a workflow"""
    try:
        if not n8n_url:
            return {"executions": []}

        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_api_key} if n8n_api_key else {}
            response = await client.get(
                f"{n8n_url}/api/v1/workflows/{workflow_id}/executions",
                headers=headers
            )
            data = response.json()
            return {"executions": data.get("data", [])}

    except Exception as e:
        print(f"Execution history error: {e}")
        return {"executions": []}


@router.post("/webhook/documentary")
async def documentary_webhook(payload: dict):
    """Webhook for documentary processing workflow"""
    try:
        # Process documentary job
        return {"status": "received", "job_id": payload.get("job_id")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get execution status"""
    try:
        if not n8n_url:
            return {"execution_id": execution_id, "status": "unknown"}

        async with httpx.AsyncClient() as client:
            headers = {"X-N8N-API-KEY": n8n_api_key} if n8n_api_key else {}
            response = await client.get(
                f"{n8n_url}/api/v1/executions/{execution_id}",
                headers=headers
            )
            data = response.json()
            return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
