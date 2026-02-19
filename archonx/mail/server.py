"""
Agent Mail WebSocket Server
===========================
WebSocket server for inter-agent communication on port 8765.

Features:
- Real-time message delivery
- Agent presence tracking
- Crew broadcasts
- Thread management
- Message history

BEAD-002: Agent Mail Server Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger("archonx.mail.server")


class MessageType(str, Enum):
    """Message types for agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ALERT = "alert"
    FLYWHEEL = "flywheel"
    COMMAND = "command"
    HEARTBEAT = "heartbeat"
    STATUS = "status"


@dataclass
class AgentMessage:
    """Message structure for agent communication."""
    id: str
    sender: str
    recipient: str
    message_type: MessageType
    subject: str
    payload: dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    thread_id: Optional[str] = None
    priority: int = 0  # 0=normal, 1=high, 2=critical

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "subject": self.subject,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp,
            "thread_id": self.thread_id,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentMessage:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data.get("message_type", "request")),
            subject=data.get("subject", ""),
            payload=data.get("payload", {}),
            reply_to=data.get("reply_to"),
            timestamp=data.get("timestamp", time.time()),
            thread_id=data.get("thread_id"),
            priority=data.get("priority", 0)
        )


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection from an agent."""
    agent_id: str
    websocket: WebSocketServerProtocol
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    subscriptions: set[str] = field(default_factory=set)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()


class ConnectionManager:
    """
    Manages WebSocket connections for all agents.
    
    Features:
    - Connection tracking by agent_id
    - Presence detection
    - Subscription management
    """

    def __init__(self) -> None:
        self._connections: dict[str, WebSocketConnection] = {}
        self._websocket_to_agent: dict[WebSocketServerProtocol, str] = {}

    async def register(
        self,
        websocket: WebSocketServerProtocol,
        agent_id: str
    ) -> WebSocketConnection:
        """Register a new WebSocket connection."""
        # Close existing connection for this agent if any
        if agent_id in self._connections:
            old_conn = self._connections[agent_id]
            try:
                await old_conn.websocket.close(code=4000, reason="Replaced by new connection")
            except Exception:
                pass
        
        connection = WebSocketConnection(
            agent_id=agent_id,
            websocket=websocket
        )
        
        self._connections[agent_id] = connection
        self._websocket_to_agent[websocket] = agent_id
        
        logger.info(f"Agent {agent_id} connected")
        return connection

    async def unregister(self, websocket: WebSocketServerProtocol) -> Optional[str]:
        """Unregister a WebSocket connection."""
        agent_id = self._websocket_to_agent.pop(websocket, None)
        if agent_id:
            self._connections.pop(agent_id, None)
            logger.info(f"Agent {agent_id} disconnected")
        return agent_id

    def get_connection(self, agent_id: str) -> Optional[WebSocketConnection]:
        """Get connection for an agent."""
        return self._connections.get(agent_id)

    def get_all_connections(self) -> list[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())

    def get_connected_agents(self) -> list[str]:
        """Get list of connected agent IDs."""
        return list(self._connections.keys())

    def is_connected(self, agent_id: str) -> bool:
        """Check if an agent is connected."""
        return agent_id in self._connections

    async def subscribe(self, agent_id: str, channel: str) -> bool:
        """Subscribe an agent to a channel."""
        conn = self._connections.get(agent_id)
        if conn:
            conn.subscriptions.add(channel)
            logger.debug(f"Agent {agent_id} subscribed to {channel}")
            return True
        return False

    async def unsubscribe(self, agent_id: str, channel: str) -> bool:
        """Unsubscribe an agent from a channel."""
        conn = self._connections.get(agent_id)
        if conn and channel in conn.subscriptions:
            conn.subscriptions.remove(channel)
            logger.debug(f"Agent {agent_id} unsubscribed from {channel}")
            return True
        return False


class MessageStore:
    """
    Persistent message storage for agent mail.
    
    Features:
    - Message history
    - Thread tracking
    - Unread counts
    """

    def __init__(self, store_path: Optional[Path] = None) -> None:
        self.store_path = store_path or Path.home() / ".archonx" / "mail_store.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._messages: dict[str, list[AgentMessage]] = defaultdict(list)
        self._threads: dict[str, list[str]] = defaultdict(list)  # thread_id -> [message_ids]
        self._counter = 0
        
        self._load_messages()

    def _load_messages(self) -> None:
        """Load messages from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._counter = data.get("counter", 0)
                    for agent_id, msgs in data.get("messages", {}).items():
                        self._messages[agent_id] = [
                            AgentMessage.from_dict(m) for m in msgs
                        ]
                logger.info(f"Loaded {sum(len(v) for v in self._messages.values())} messages")
            except Exception as e:
                logger.warning(f"Failed to load messages: {e}")

    def _save_messages(self) -> None:
        """Save messages to disk."""
        data = {
            "counter": self._counter,
            "messages": {
                agent_id: [m.to_dict() for m in msgs]
                for agent_id, msgs in self._messages.items()
            }
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def store(self, message: AgentMessage) -> AgentMessage:
        """Store a message and return it with ID assigned."""
        self._counter += 1
        if not message.id:
            message.id = f"mail-{self._counter:06d}"
        
        # Store in recipient's inbox
        self._messages[message.recipient].append(message)
        
        # Track thread
        if message.thread_id:
            self._threads[message.thread_id].append(message.id)
        
        self._save_messages()
        return message

    def get_messages(
        self,
        agent_id: str,
        unread_only: bool = False,
        limit: int = 100
    ) -> list[AgentMessage]:
        """Get messages for an agent."""
        msgs = self._messages.get(agent_id, [])
        if unread_only:
            msgs = [m for m in msgs if not m.payload.get("_read", False)]
        return msgs[-limit:]

    def mark_read(self, agent_id: str, message_id: str) -> bool:
        """Mark a message as read."""
        msgs = self._messages.get(agent_id, [])
        for msg in msgs:
            if msg.id == message_id:
                msg.payload["_read"] = True
                self._save_messages()
                return True
        return False

    def get_thread(self, thread_id: str) -> list[AgentMessage]:
        """Get all messages in a thread."""
        message_ids = set(self._threads.get(thread_id, []))
        messages = []
        for msgs in self._messages.values():
            for msg in msgs:
                if msg.id in message_ids:
                    messages.append(msg)
        return sorted(messages, key=lambda m: m.timestamp)

    def get_stats(self) -> dict[str, Any]:
        """Get message statistics."""
        total = sum(len(msgs) for msgs in self._messages.values())
        unread = sum(
            1 for msgs in self._messages.values()
            for m in msgs if not m.payload.get("_read", False)
        )
        return {
            "total_messages": self._counter,
            "stored_messages": total,
            "unread_messages": unread,
            "active_inboxes": len(self._messages),
            "active_threads": len(self._threads)
        }


class AgentMailServer:
    """
    WebSocket server for Agent Mail on port 8765.
    
    Features:
    - Real-time message delivery
    - Agent presence tracking
    - Crew broadcasts (crew:white, crew:black)
    - Global broadcasts
    - Thread management
    - Message history
    
    Usage:
        server = AgentMailServer(port=8765)
        await server.start()
        
        # Send message
        await server.send_message(
            sender="white-queen",
            recipient="black-king",
            subject="Test",
            payload={"text": "Hello!"}
        )
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        auth_handler: Optional[Callable[[str], Awaitable[bool]]] = None
    ) -> None:
        """
        Initialize the Agent Mail server.
        
        Args:
            host: Host to bind to
            port: Port to listen on (default: 8765)
            auth_handler: Optional async function to validate agent tokens
        """
        self.host = host
        self.port = port
        self.auth_handler = auth_handler
        
        self.connections = ConnectionManager()
        self.messages = MessageStore()
        self._server = None
        self._running = False
        
        # Crew membership
        self._crew_membership: dict[str, set[str]] = {
            "white": set(),
            "black": set()
        }
        
        logger.info(f"Agent Mail Server initialized on {host}:{port}")

    async def start(self) -> None:
        """Start the WebSocket server."""
        if self._running:
            logger.warning("Server already running")
            return
        
        self._running = True
        self._server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10
        )
        
        logger.info(f"Agent Mail Server started on ws://{self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if not self._running:
            return
        
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        logger.info("Agent Mail Server stopped")

    async def _handle_connection(
        self,
        websocket: WebSocketServerProtocol,
        path: str = "/"
    ) -> None:
        """Handle a WebSocket connection."""
        agent_id = None
        
        try:
            # Wait for authentication message
            auth_msg = await asyncio.wait_for(
                websocket.recv(),
                timeout=30.0
            )
            
            auth_data = json.loads(auth_msg)
            agent_id = auth_data.get("agent_id")
            token = auth_data.get("token")
            
            if not agent_id:
                await websocket.close(code=4001, reason="Missing agent_id")
                return
            
            # Validate auth if handler provided
            if self.auth_handler and token:
                if not await self.auth_handler(token):
                    await websocket.close(code=4003, reason="Authentication failed")
                    return
            
            # Register connection
            conn = await self.connections.register(websocket, agent_id)
            
            # Determine crew from agent_id
            if agent_id.startswith("white-"):
                self._crew_membership["white"].add(agent_id)
            elif agent_id.startswith("black-"):
                self._crew_membership["black"].add(agent_id)
            
            # Send welcome message
            await self._send_welcome(conn)
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(conn, message)
                
        except asyncio.TimeoutError:
            logger.warning("Connection timeout - no auth message received")
            await websocket.close(code=4002, reason="Authentication timeout")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON received: {e}")
            
        except websockets.exceptions.ConnectionClosed:
            pass
            
        except Exception as e:
            logger.exception(f"Error handling connection: {e}")
            
        finally:
            # Cleanup
            if agent_id:
                await self.connections.unregister(websocket)
                if agent_id.startswith("white-"):
                    self._crew_membership["white"].discard(agent_id)
                elif agent_id.startswith("black-"):
                    self._crew_membership["black"].discard(agent_id)

    async def _send_welcome(self, conn: WebSocketConnection) -> None:
        """Send welcome message to newly connected agent."""
        welcome = {
            "type": "welcome",
            "agent_id": conn.agent_id,
            "timestamp": time.time(),
            "unread_count": len([
                m for m in self.messages.get_messages(conn.agent_id)
                if not m.payload.get("_read", False)
            ])
        }
        await conn.websocket.send(json.dumps(welcome))

    async def _handle_message(
        self,
        conn: WebSocketConnection,
        raw_message: str
    ) -> None:
        """Handle an incoming message from an agent."""
        conn.touch()
        
        try:
            data = json.loads(raw_message)
            
            # Handle different message types
            msg_type = data.get("type", "message")
            
            if msg_type == "heartbeat":
                await self._handle_heartbeat(conn, data)
            elif msg_type == "subscribe":
                await self._handle_subscribe(conn, data)
            elif msg_type == "unsubscribe":
                await self._handle_unsubscribe(conn, data)
            elif msg_type == "message":
                await self._handle_agent_message(conn, data)
            elif msg_type == "read":
                await self._handle_mark_read(conn, data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from {conn.agent_id}")
        except Exception as e:
            logger.exception(f"Error handling message: {e}")

    async def _handle_heartbeat(
        self,
        conn: WebSocketConnection,
        data: dict[str, Any]
    ) -> None:
        """Handle heartbeat message."""
        response = {
            "type": "heartbeat_ack",
            "timestamp": time.time()
        }
        await conn.websocket.send(json.dumps(response))

    async def _handle_subscribe(
        self,
        conn: WebSocketConnection,
        data: dict[str, Any]
    ) -> None:
        """Handle subscription request."""
        channel = data.get("channel")
        if channel:
            await self.connections.subscribe(conn.agent_id, channel)
            response = {
                "type": "subscribed",
                "channel": channel,
                "timestamp": time.time()
            }
            await conn.websocket.send(json.dumps(response))

    async def _handle_unsubscribe(
        self,
        conn: WebSocketConnection,
        data: dict[str, Any]
    ) -> None:
        """Handle unsubscription request."""
        channel = data.get("channel")
        if channel:
            await self.connections.unsubscribe(conn.agent_id, channel)
            response = {
                "type": "unsubscribed",
                "channel": channel,
                "timestamp": time.time()
            }
            await conn.websocket.send(json.dumps(response))

    async def _handle_agent_message(
        self,
        conn: WebSocketConnection,
        data: dict[str, Any]
    ) -> None:
        """Handle agent-to-agent message."""
        message = AgentMessage.from_dict(data.get("message", data))
        message.sender = conn.agent_id  # Ensure sender is correct
        
        # Store message
        stored = self.messages.store(message)
        
        # Deliver to recipient(s)
        await self._deliver_message(stored)

    async def _handle_mark_read(
        self,
        conn: WebSocketConnection,
        data: dict[str, Any]
    ) -> None:
        """Handle mark as read request."""
        message_id = data.get("message_id")
        if message_id:
            self.messages.mark_read(conn.agent_id, message_id)

    async def _deliver_message(self, message: AgentMessage) -> None:
        """Deliver a message to its recipient(s)."""
        recipient = message.recipient
        
        # Handle broadcast
        if recipient == "broadcast":
            await self._broadcast(message)
            return
        
        # Handle crew broadcast
        if recipient.startswith("crew:"):
            crew = recipient.split(":")[1]
            await self._crew_broadcast(crew, message)
            return
        
        # Direct message
        conn = self.connections.get_connection(recipient)
        if conn:
            try:
                await conn.websocket.send(json.dumps({
                    "type": "message",
                    "message": message.to_dict()
                }))
                logger.debug(f"Delivered message {message.id} to {recipient}")
            except Exception as e:
                logger.warning(f"Failed to deliver to {recipient}: {e}")

    async def _broadcast(self, message: AgentMessage) -> None:
        """Broadcast message to all connected agents."""
        raw = json.dumps({
            "type": "message",
            "message": message.to_dict()
        })
        
        for conn in self.connections.get_all_connections():
            if conn.agent_id != message.sender:
                try:
                    await conn.websocket.send(raw)
                except Exception as e:
                    logger.warning(f"Failed to broadcast to {conn.agent_id}: {e}")

    async def _crew_broadcast(self, crew: str, message: AgentMessage) -> None:
        """Broadcast message to a specific crew."""
        raw = json.dumps({
            "type": "message",
            "message": message.to_dict()
        })
        
        members = self._crew_membership.get(crew, set())
        for agent_id in members:
            if agent_id != message.sender:
                conn = self.connections.get_connection(agent_id)
                if conn:
                    try:
                        await conn.websocket.send(raw)
                    except Exception as e:
                        logger.warning(f"Failed to broadcast to {agent_id}: {e}")

    # Public API methods

    async def send_message(
        self,
        sender: str,
        recipient: str,
        subject: str,
        payload: dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        thread_id: Optional[str] = None,
        priority: int = 0
    ) -> AgentMessage:
        """
        Send a message from one agent to another.
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID, "broadcast", or "crew:white"/"crew:black"
            subject: Message subject
            payload: Message payload
            message_type: Type of message
            thread_id: Optional thread ID for grouping
            priority: Message priority (0=normal, 1=high, 2=critical)
            
        Returns:
            The created message
        """
        message = AgentMessage(
            id="",
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            subject=subject,
            payload=payload,
            thread_id=thread_id,
            priority=priority
        )
        
        stored = self.messages.store(message)
        await self._deliver_message(stored)
        
        return stored

    def get_agent_messages(
        self,
        agent_id: str,
        unread_only: bool = False
    ) -> list[AgentMessage]:
        """Get messages for an agent."""
        return self.messages.get_messages(agent_id, unread_only)

    def get_connected_agents(self) -> list[str]:
        """Get list of connected agent IDs."""
        return self.connections.get_connected_agents()

    def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        return {
            "server": {
                "host": self.host,
                "port": self.port,
                "running": self._running
            },
            "connections": {
                "total": len(self.connections.get_connected_agents()),
                "agents": self.connections.get_connected_agents()
            },
            "crews": {
                "white": list(self._crew_membership["white"]),
                "black": list(self._crew_membership["black"])
            },
            "messages": self.messages.get_stats()
        }


# Singleton instance
_server: Optional[AgentMailServer] = None


def get_mail_server() -> AgentMailServer:
    """Get the singleton AgentMailServer."""
    global _server
    if _server is None:
        _server = AgentMailServer()
    return _server
