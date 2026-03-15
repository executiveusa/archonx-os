"""
Tests — OpenClaw (backend, sessions, channels)
"""

import pytest

from archonx.openclaw.backend import OpenClawBackend, OpenClawConfig
from archonx.openclaw.sessions import ClientSession, SessionManager
from archonx.openclaw.channels import (
    ChannelRouter,
    OutgoingMessage,
    WhatsAppHandler,
)


# --- Sessions ---

def test_session_create() -> None:
    mgr = SessionManager()
    session = mgr.create_session("client-1", "Acme Corp")
    assert session.client_id == "client-1"
    assert session.active is True
    assert mgr.active_count == 1


def test_session_close() -> None:
    mgr = SessionManager()
    session = mgr.create_session("client-2")
    mgr.close_session(session.session_id)
    assert session.active is False
    assert mgr.active_count == 0


def test_session_get_by_client() -> None:
    mgr = SessionManager()
    mgr.create_session("c1")
    mgr.create_session("c1")
    mgr.create_session("c2")
    assert len(mgr.get_by_client("c1")) == 2
    assert len(mgr.get_by_client("c2")) == 1


# --- Channels ---

@pytest.mark.asyncio
async def test_whatsapp_send() -> None:
    handler = WhatsAppHandler()
    msg = OutgoingMessage(
        channel="whatsapp",
        client_id="c1",
        recipient="+1234567890",
        text="Deployment complete!",
    )
    result = await handler.send(msg)
    assert result["status"] == "sent"
    assert result["channel"] == "whatsapp"


@pytest.mark.asyncio
async def test_channel_router_outgoing() -> None:
    router = ChannelRouter()
    router.register_defaults()
    msg = OutgoingMessage(
        channel="slack",
        client_id="c1",
        recipient="#deployments",
        text="Site is live!",
    )
    result = await router.route_outgoing(msg)
    assert result["status"] == "sent"


@pytest.mark.asyncio
async def test_channel_router_unknown() -> None:
    router = ChannelRouter()
    router.register_defaults()
    msg = OutgoingMessage(
        channel="discord",
        client_id="c1",
        recipient="channel",
        text="hello",
    )
    with pytest.raises(ValueError, match="No handler for channel"):
        await router.route_outgoing(msg)


# --- OpenClaw Backend ---

@pytest.mark.asyncio
async def test_backend_start_stop() -> None:
    backend = OpenClawBackend()
    await backend.start()
    assert backend._running is True
    await backend.stop()
    assert backend._running is False


@pytest.mark.asyncio
async def test_backend_send_message() -> None:
    backend = OpenClawBackend()
    result = await backend.send_message("whatsapp", "clientx", "Hello!")
    assert result["status"] == "sent"


@pytest.mark.asyncio
async def test_backend_unsupported_channel() -> None:
    backend = OpenClawBackend()
    result = await backend.send_message("discord", "clientx", "Hello!")
    assert result["status"] == "error"
