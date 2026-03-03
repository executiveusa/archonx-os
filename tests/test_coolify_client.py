import asyncio

import pytest

from archonx.tools.coolify_client import CoolifyClient, DeploymentStatus


def test_trigger_deploy_returns_id(monkeypatch):
    client = CoolifyClient(api_key="k", base_url="http://coolify")

    async def fake_request(method, path, payload=None):
        assert method == "POST"
        assert path == "/api/v1/deploy"
        return {"deployment_id": "dep-123"}

    monkeypatch.setattr(client, "_request", fake_request)
    assert asyncio.run(client.trigger_deploy("app-1")) == "dep-123"


def test_wait_for_deploy_success(monkeypatch):
    client = CoolifyClient(api_key="k", base_url="http://coolify")
    calls = {"n": 0}

    async def fake_status(_deployment_id):
        calls["n"] += 1
        if calls["n"] < 2:
            return DeploymentStatus(deployment_id="dep", status="in_progress")
        return DeploymentStatus(deployment_id="dep", status="finished")

    monkeypatch.setattr(client, "get_deployment_status", fake_status)
    status = asyncio.run(client.wait_for_deploy("dep", timeout_seconds=2, poll_interval=0))
    assert status.status == "finished"


def test_wait_for_deploy_failure_raises(monkeypatch):
    client = CoolifyClient(api_key="k", base_url="http://coolify")

    async def fake_status(_deployment_id):
        return DeploymentStatus(deployment_id="dep", status="failed", error="boom")

    monkeypatch.setattr(client, "get_deployment_status", fake_status)
    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(client.wait_for_deploy("dep", timeout_seconds=2, poll_interval=0))
