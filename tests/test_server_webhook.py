from fastapi.testclient import TestClient

import archonx.server as server


class _FakeRegistry:
    def all(self):
        return []


class _FakeKernel:
    def __init__(self):
        self.registry = _FakeRegistry()
        self.theater = type("Theater", (), {"emit": lambda *a, **k: None})()

    async def boot(self):
        return None

    async def shutdown(self):
        return None

    async def execute_task(self, _task):
        return {"status": "ok"}


class _FakeResult:
    def __init__(self, task_id: str):
        self.success = True
        self.message = "ok"
        self.data = {"task_id": task_id}


class _FakeOrchestrator:
    async def initialize(self):
        return None

    async def create_task(self, title, task_type, priority=None, metadata=None):
        _ = (title, task_type, priority, metadata)
        return _FakeResult("task-123")


def test_webhook_and_status(monkeypatch):
    monkeypatch.setattr(server, "ArchonXKernel", _FakeKernel)
    monkeypatch.setattr(server, "Orchestrator", _FakeOrchestrator)

    app = server.create_app()
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        created = client.post("/webhook/task", json={"message": "do work"})
        assert created.status_code == 200
        task_id = created.json()["task_id"]
        assert task_id == "task-123"

        status = client.get(f"/status/{task_id}")
        assert status.status_code == 200
        assert status.json()["task_id"] == task_id
