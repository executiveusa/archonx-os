"""
Tests — Deployment Orchestrator & Client Deployer
"""

import pytest

from archonx.deploy.orchestrator import DeploymentOrchestrator, DeployStage
from archonx.deploy.client_deployer import ClientDeployer


@pytest.mark.asyncio
async def test_deployment_plan_staging_first() -> None:
    orch = DeploymentOrchestrator()
    plan = orch.create_plan(
        deployment_id="deploy-001",
        client_id="clientx",
        target="e-commerce",
        repo="clientx/ecommerce",
        mode="staging_first",
    )
    assert len(plan.stages) == 7
    assert plan.stages[0] == DeployStage.INIT
    assert plan.stages[-1] == DeployStage.COMPLETE


@pytest.mark.asyncio
async def test_deployment_plan_direct_mode() -> None:
    orch = DeploymentOrchestrator()
    plan = orch.create_plan(
        deployment_id="deploy-002",
        client_id="clienty",
        target="api",
        repo="clienty/api",
        mode="direct",
    )
    assert len(plan.stages) == 4  # init, deploy, verify, complete


@pytest.mark.asyncio
async def test_execute_plan_succeeds() -> None:
    orch = DeploymentOrchestrator()
    orch.create_plan(
        deployment_id="deploy-003",
        client_id="clientz",
        target="site",
        repo="clientz/site",
    )
    result = await orch.execute_plan("deploy-003")
    assert result.current_stage == DeployStage.COMPLETE
    assert result.completed_at is not None
    assert len(result.results) > 0


@pytest.mark.asyncio
async def test_execute_plan_not_found() -> None:
    orch = DeploymentOrchestrator()
    with pytest.raises(ValueError):
        await orch.execute_plan("nonexistent")


@pytest.mark.asyncio
async def test_client_deployer() -> None:
    deployer = ClientDeployer()
    instance = await deployer.deploy_client(
        client_id="acme",
        client_name="Acme Corp",
        competitive_mode=True,
        white_label={"brand_name": "AcmeAI"},
        integrations=["whatsapp", "slack"],
    )
    assert instance.status == "active"
    assert instance.client_name == "Acme Corp"
    assert instance.agent_count == 64
    assert "archonx-acme-" in instance.instance_id


@pytest.mark.asyncio
async def test_client_deployer_list() -> None:
    deployer = ClientDeployer()
    await deployer.deploy_client(client_id="c1", client_name="Client 1")
    await deployer.deploy_client(client_id="c2", client_name="Client 2")
    assert len(deployer.list_instances()) == 2


@pytest.mark.asyncio
async def test_client_decommission() -> None:
    deployer = ClientDeployer()
    await deployer.deploy_client(client_id="temp", client_name="Temp Client")
    await deployer.decommission("temp")
    assert deployer.get_instance("temp") is None
