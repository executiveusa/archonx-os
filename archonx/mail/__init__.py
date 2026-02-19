"""
ArchonX Mail Module
===================
WebSocket-based Agent Mail server for inter-agent communication.

Components:
- AgentMailServer: WebSocket server on port 8765
- ConnectionManager: WebSocket connection handling
- Message routing and delivery

Usage:
    from archonx.mail import AgentMailServer
    
    server = AgentMailServer(port=8765)
    await server.start()
"""

from archonx.mail.server import (
    AgentMailServer,
    ConnectionManager,
    WebSocketConnection,
    get_mail_server
)

__all__ = [
    "AgentMailServer",
    "ConnectionManager",
    "WebSocketConnection",
    "get_mail_server",
]
