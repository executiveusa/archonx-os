import asyncio

from archonx.tools.deploy import DeploymentTool


class _FakeStatus:
    def __init__(self, status="finished"):
        self.status = status


class _FakeHealth:
    def __init__(self, status="running", url="https://app"):
        self.status = status
        self.url = url


def test_deploy_success(monkeypatch):
    tool = DeploymentTool()
    monkeypatch.setattr(tool, "_load_coolify_config", lambda: {"app_uuid": "app-1", "base_url": "http://c"})

    class FakeClient:
        def __init__(self, base_url=""):
            self.base_url = base_url

        async def trigger_deploy(self, app_uuid, force=False):
            assert app_uuid == "app-1"
            return "dep-1"

        async def wait_for_deploy(self, deployment_id, timeout_seconds=300):
            assert deployment_id == "dep-1"
            return _FakeStatus("finished")

        async def check_health(self, app_uuid):
            return _FakeHealth()

    class FakeNotifier:
        async def notify(self, _result):
            return None

    monkeypatch.setattr("archonx.tools.deploy.CoolifyClient", FakeClient)
    monkeypatch.setattr("archonx.tools.deploy.Notifier", FakeNotifier)

    result = asyncio.run(tool.execute({"action": "deploy", "repo": "owner/repo", "environment": "staging"}))
    assert result.status == "success"
    assert result.data["deployment_id"] == "dep-1"


def test_status_unconfigured(monkeypatch):
    tool = DeploymentTool()
    monkeypatch.setattr(tool, "_load_coolify_config", lambda: {"app_uuid": "", "base_url": ""})
    result = asyncio.run(tool._status("owner/repo", "staging"))
    assert result["health"] == "unconfigured"
