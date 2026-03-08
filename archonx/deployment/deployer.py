import os
import json
import logging
import asyncio
import httpx
from typing import Any, Optional, Dict

from archonx.security.vault import ArchonXVault

logger = logging.getLogger("archonx.deployment.deployer")

class Deployer:
    """
    Handles autonomous deployments to Vercel (Frontend) and Coolify (Backend).
    Part of ArchonX Phase 4 Deployment Stage.
    """
    
    def __init__(self):
        self.vault = ArchonXVault()
        self._secrets = self.vault.load_secrets()
        self.vercel_token = self._secrets.get("VERCEL_TOKEN")
        self.coolify_token = self._secrets.get("COOLIFY_TOKEN")
        self.coolify_url = self._secrets.get("COOLIFY_URL", "https://app.coolify.io")

    async def deploy_vercel(self, project_id: str, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Trigger a new deployment on Vercel."""
        if not self.vercel_token:
            return {"success": False, "error": "VERCEL_TOKEN missing"}
            
        url = "https://api.vercel.com/v13/deployments"
        params = {}
        if team_id:
            params["teamId"] = team_id
            
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }
        
        # Note: A real deployment often needs more context (files, git integration)
        # Here we trigger a REDEPLOY of the latest commit for simplicity in Phase 4
        payload = {
            "name": "dashboard-agent-swarm",
            "gitSource": {
                "type": "github",
                "repoId": "executiveusa/archonx-os",
                "ref": "main"
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, params=params, json=payload)
                data = response.json()
                if response.status_code in (200, 201):
                    logger.info(f"Vercel deployment started: {data.get('id')}")
                    return {"success": True, "deployment_id": data.get("id"), "url": data.get("url")}
                else:
                    return {"success": False, "error": data.get("error", {}).get("message", "Unknown error")}
            except Exception as e:
                logger.exception("Vercel deployment failed")
                return {"success": False, "error": str(e)}

    async def get_vercel_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get status of a Vercel deployment."""
        url = f"https://api.vercel.com/v13/deployments/{deployment_id}"
        headers = {"Authorization": f"Bearer {self.vercel_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()

    async def deploy_coolify(self, service_uuid: str) -> Dict[str, Any]:
        """Trigger a deployment on Coolify."""
        if not self.coolify_token:
            return {"success": False, "error": "COOLIFY_TOKEN missing"}
            
        url = f"{self.coolify_url}/api/v1/deploy?uuid={service_uuid}"
        headers = {"Authorization": f"Bearer {self.coolify_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return {"success": True, "message": "Coolify deployment triggered"}
                else:
                    return {"success": False, "error": response.text}
            except Exception as e:
                return {"success": False, "error": str(e)}

def get_deployer() -> Deployer:
    return Deployer()
