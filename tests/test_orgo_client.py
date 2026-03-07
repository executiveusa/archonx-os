import asyncio

from archonx.openclaw.orgo import OrgoClient


def test_orgo_simulated_mode():
    client = OrgoClient(api_key="")
    session = asyncio.run(client.create_session("visit example.com"))
    assert session.session_id.startswith("orgo-local-")

    action = asyncio.run(client.execute_action(session.session_id, {"type": "click"}))
    assert action["status"] == "completed"

    asyncio.run(client.close_session(session.session_id))


def test_orgo_http_mode(monkeypatch):
    client = OrgoClient(api_key="token")

    class _Resp:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _HTTP:
        async def post(self, path, json):
            if path == "/v1/sessions":
                return _Resp({"id": "sess-1", "status": "active", "url": "https://vm"})
            return _Resp({"status": "completed"})

        async def get(self, _path):
            return _Resp({"url": "https://shot"})

        async def delete(self, _path):
            return _Resp({})

        async def aclose(self):
            return None

    async def fake_http():
        return _HTTP()

    monkeypatch.setattr(client, "_http", fake_http)

    session = asyncio.run(client.create_session("live"))
    assert session.session_id == "sess-1"

    result = asyncio.run(client.execute_action("sess-1", {"type": "click"}))
    assert result["status"] == "completed"

    shot = asyncio.run(client.get_screenshot("sess-1"))
    assert shot == "https://shot"
