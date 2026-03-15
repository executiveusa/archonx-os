"""Deployment routes - integrates with Coolify"""

import os
import sys
from typing import List, Optional
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

# Coolify client
coolify_client = None
coolify_cache = {"services": []}


async def initialize():
    """Initialize deployment system"""
    global coolify_client
    try:
        # Try to import from parent archonx-os repo
        sys.path.insert(0, "/home/user/archonx-os")
        from archonx.tools.coolify_client import CoolifyClient

        api_key = os.getenv("COOLIFY_API_KEY")
        base_url = os.getenv("COOLIFY_BASE_URL")

        if api_key and base_url:
            coolify_client = CoolifyClient(api_key=api_key, base_url=base_url)
        else:
            print("Warning: Coolify credentials not configured")
    except (ImportError, Exception) as e:
        print(f"Warning: Could not initialize CoolifyClient: {e}")


@router.get("")
async def list_deployments():
    """List all Coolify services"""
    try:
        if coolify_client:
            # Use existing CoolifyClient
            services = await coolify_client.list_services()
            return {"services": services}
        else:
            # Return mock data if client not available
            return coolify_cache

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{uuid}")
async def get_deployment(uuid: str):
    """Get deployment details"""
    try:
        if coolify_client:
            status = await coolify_client.get_deployment_status(uuid)
            return {"status": status}
        else:
            return {"uuid": uuid, "status": "unknown"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{uuid}/deploy")
async def trigger_deploy(uuid: str, force: bool = False):
    """Trigger a deployment"""
    try:
        if not coolify_client:
            return {"deployment_id": "mock-123", "status": "queued"}

        deployment_id = await coolify_client.trigger_deploy(uuid, force=force)
        return {"deployment_id": deployment_id, "status": "queued"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}/logs")
async def get_deployment_logs(deployment_id: str):
    """Get deployment logs"""
    try:
        if coolify_client:
            logs = await coolify_client.get_deployment_logs(deployment_id)
            return {"deployment_id": deployment_id, "logs": logs}
        else:
            return {"deployment_id": deployment_id, "logs": ["Mock log entry"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/rollback")
async def rollback_deployment(deployment_id: str):
    """Rollback a deployment"""
    try:
        if coolify_client:
            result = await coolify_client.rollback(deployment_id)
            return {"deployment_id": deployment_id, "result": result}
        else:
            return {"deployment_id": deployment_id, "status": "rolled_back"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
