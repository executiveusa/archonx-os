"""
OAuth 2.0 Server
================
Single Sign-In OAuth 2.0 server for ArchonX ecosystem.

Supports:
- Authorization Code Flow
- Client Credentials Flow
- Refresh Token Flow
- JWT Token issuance
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import uuid

import httpx

logger = logging.getLogger("archonx.auth.oauth")


class GrantType(Enum):
    """OAuth grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class OAuthClient:
    """Registered OAuth client."""
    client_id: str
    client_secret: str
    name: str
    redirect_uris: list[str]
    scopes: list[str] = field(default_factory=lambda: ["read", "write"])
    is_confidential: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "name": self.name,
            "redirect_uris": self.redirect_uris,
            "scopes": self.scopes,
            "is_confidential": self.is_confidential
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OAuthClient:
        return cls(
            client_id=data["client_id"],
            client_secret=data["client_secret"],
            name=data["name"],
            redirect_uris=data["redirect_uris"],
            scopes=data.get("scopes", ["read", "write"]),
            is_confidential=data.get("is_confidential", True)
        )


@dataclass
class AuthorizationCode:
    """Authorization code for OAuth flow."""
    code: str
    client_id: str
    redirect_uri: str
    user_id: str
    scopes: list[str]
    expires_at: float
    used: bool = False

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


@dataclass
class Token:
    """OAuth token."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scopes: list[str] = field(default_factory=list)
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "created_at": self.created_at
        }
        if self.refresh_token:
            result["refresh_token"] = self.refresh_token
        if self.scopes:
            result["scope"] = " ".join(self.scopes)
        return result

    def is_expired(self) -> bool:
        return time.time() > (self.created_at + self.expires_in)


class OAuthServer:
    """
    OAuth 2.0 Authorization Server for ArchonX.
    
    Provides Single Sign-In across the ecosystem with:
    - Authorization Code Flow for web apps
    - Client Credentials Flow for services
    - Refresh Token Flow for long-lived sessions
    
    Usage:
        server = OAuthServer()
        
        # Register client
        client = server.register_client("My App", ["http://localhost:3000/callback"])
        
        # Authorization URL
        auth_url = server.get_authorization_url(client, "http://localhost:3000/callback")
        
        # Exchange code for token
        token = server.exchange_code(code, client)
    """

    def __init__(
        self,
        issuer: str = "https://auth.archonx.local",
        token_lifetime: int = 3600,
        refresh_lifetime: int = 86400 * 30,  # 30 days
        clients_file: Optional[Path] = None
    ):
        """
        Initialize OAuth server.
        
        Args:
            issuer: The issuer URL for tokens
            token_lifetime: Access token lifetime in seconds
            refresh_lifetime: Refresh token lifetime in seconds
            clients_file: File to store registered clients
        """
        self.issuer = issuer
        self.token_lifetime = token_lifetime
        self.refresh_lifetime = refresh_lifetime
        
        # Storage
        self.clients_file = clients_file or Path.home() / ".archonx" / "oauth_clients.json"
        self.clients_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._clients: dict[str, OAuthClient] = {}
        self._codes: dict[str, AuthorizationCode] = {}
        self._tokens: dict[str, Token] = {}
        self._refresh_tokens: dict[str, str] = {}  # refresh_token -> access_token
        
        # Load clients
        self._load_clients()
        
        logger.info(f"OAuth server initialized (issuer: {issuer})")

    def _load_clients(self) -> None:
        """Load registered clients from file."""
        if self.clients_file.exists():
            try:
                with open(self.clients_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for client_data in data.get("clients", []):
                        client = OAuthClient.from_dict(client_data)
                        self._clients[client.client_id] = client
                logger.info(f"Loaded {len(self._clients)} OAuth clients")
            except Exception as e:
                logger.warning(f"Failed to load clients: {e}")

    def _save_clients(self) -> None:
        """Save registered clients to file."""
        data = {
            "clients": [c.to_dict() for c in self._clients.values()]
        }
        with open(self.clients_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register_client(
        self,
        name: str,
        redirect_uris: list[str],
        scopes: Optional[list[str]] = None,
        is_confidential: bool = True
    ) -> OAuthClient:
        """
        Register a new OAuth client.
        
        Args:
            name: Client name
            redirect_uris: Allowed redirect URIs
            scopes: Allowed scopes
            is_confidential: Whether client is confidential
            
        Returns:
            The registered OAuthClient
        """
        client_id = f"archonx_{uuid.uuid4().hex[:16]}"
        client_secret = secrets.token_urlsafe(32) if is_confidential else ""
        
        client = OAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            name=name,
            redirect_uris=redirect_uris,
            scopes=scopes or ["read", "write"],
            is_confidential=is_confidential
        )
        
        self._clients[client_id] = client
        self._save_clients()
        
        logger.info(f"Registered OAuth client: {name} ({client_id})")
        return client

    def get_client(self, client_id: str) -> Optional[OAuthClient]:
        """Get a registered client by ID."""
        return self._clients.get(client_id)

    def get_authorization_url(
        self,
        client: OAuthClient,
        redirect_uri: str,
        state: Optional[str] = None,
        scopes: Optional[list[str]] = None
    ) -> str:
        """
        Generate authorization URL for Authorization Code Flow.
        
        Args:
            client: The OAuth client
            redirect_uri: Redirect URI (must be registered)
            state: Optional state parameter
            scopes: Requested scopes
            
        Returns:
            Authorization URL
        """
        if redirect_uri not in client.redirect_uris:
            raise ValueError(f"Redirect URI not registered: {redirect_uri}")
        
        scopes = scopes or client.scopes
        state = state or secrets.token_urlsafe(16)
        
        params = {
            "response_type": "code",
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.issuer}/authorize?{query}"

    def create_authorization_code(
        self,
        client: OAuthClient,
        redirect_uri: str,
        user_id: str,
        scopes: Optional[list[str]] = None
    ) -> str:
        """
        Create an authorization code.
        
        Args:
            client: The OAuth client
            redirect_uri: Redirect URI
            user_id: User ID granting authorization
            scopes: Granted scopes
            
        Returns:
            Authorization code
        """
        code = secrets.token_urlsafe(32)
        scopes = scopes or client.scopes
        
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=redirect_uri,
            user_id=user_id,
            scopes=scopes,
            expires_at=time.time() + 600  # 10 minutes
        )
        
        self._codes[code] = auth_code
        logger.debug(f"Created authorization code for user {user_id}")
        
        return code

    def exchange_code(
        self,
        code: str,
        client: OAuthClient,
        redirect_uri: str
    ) -> Optional[Token]:
        """
        Exchange authorization code for token.
        
        Args:
            code: Authorization code
            client: The OAuth client
            redirect_uri: Redirect URI
            
        Returns:
            Token if successful, None otherwise
        """
        auth_code = self._codes.get(code)
        
        if not auth_code:
            logger.warning(f"Invalid authorization code: {code[:8]}...")
            return None
        
        if auth_code.used:
            logger.warning(f"Authorization code already used: {code[:8]}...")
            return None
        
        if auth_code.is_expired():
            logger.warning(f"Authorization code expired: {code[:8]}...")
            del self._codes[code]
            return None
        
        if auth_code.client_id != client.client_id:
            logger.warning(f"Client ID mismatch for code: {code[:8]}...")
            return None
        
        if auth_code.redirect_uri != redirect_uri:
            logger.warning(f"Redirect URI mismatch for code: {code[:8]}...")
            return None
        
        # Mark code as used
        auth_code.used = True
        
        # Create token
        token = self._create_token(
            user_id=auth_code.user_id,
            client_id=client.client_id,
            scopes=auth_code.scopes
        )
        
        logger.info(f"Exchanged code for token (user: {auth_code.user_id})")
        return token

    def client_credentials_flow(
        self,
        client: OAuthClient,
        scopes: Optional[list[str]] = None
    ) -> Token:
        """
        Perform Client Credentials Flow.
        
        Args:
            client: The OAuth client
            scopes: Requested scopes
            
        Returns:
            Access token
        """
        scopes = scopes or client.scopes
        
        token = self._create_token(
            user_id=None,
            client_id=client.client_id,
            scopes=scopes,
            with_refresh=False
        )
        
        logger.info(f"Issued client credentials token for {client.name}")
        return token

    def refresh_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New token if successful, None otherwise
        """
        old_access_token = self._refresh_tokens.get(refresh_token)
        if not old_access_token:
            logger.warning(f"Invalid refresh token: {refresh_token[:8]}...")
            return None
        
        old_token = self._tokens.get(old_access_token)
        if not old_token:
            logger.warning(f"Token not found for refresh token")
            return None
        
        # Create new token
        new_token = self._create_token(
            user_id=old_token.user_id,
            client_id=old_token.client_id,
            scopes=old_token.scopes
        )
        
        # Invalidate old refresh token
        del self._refresh_tokens[refresh_token]
        
        logger.info(f"Refreshed token for user {old_token.user_id}")
        return new_token

    def validate_token(self, access_token: str) -> Optional[Token]:
        """
        Validate an access token.
        
        Args:
            access_token: The access token
            
        Returns:
            Token if valid, None otherwise
        """
        token = self._tokens.get(access_token)
        
        if not token:
            return None
        
        if token.is_expired():
            del self._tokens[access_token]
            return None
        
        return token

    def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            access_token: The access token
            
        Returns:
            True if revoked, False if not found
        """
        if access_token in self._tokens:
            del self._tokens[access_token]
            logger.info(f"Revoked token: {access_token[:8]}...")
            return True
        return False

    def _create_token(
        self,
        user_id: Optional[str],
        client_id: str,
        scopes: list[str],
        with_refresh: bool = True
    ) -> Token:
        """Create a new access token."""
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32) if with_refresh else None
        
        token = Token(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.token_lifetime,
            refresh_token=refresh_token,
            scopes=scopes,
            user_id=user_id,
            client_id=client_id
        )
        
        self._tokens[access_token] = token
        
        if refresh_token:
            self._refresh_tokens[refresh_token] = access_token
        
        return token

    def cleanup_expired(self) -> int:
        """
        Clean up expired codes and tokens.
        
        Returns:
            Number of items cleaned up
        """
        count = 0
        
        # Clean expired codes
        expired_codes = [
            code for code, auth in self._codes.items()
            if auth.is_expired() or auth.used
        ]
        for code in expired_codes:
            del self._codes[code]
            count += 1
        
        # Clean expired tokens
        expired_tokens = [
            token for token, t in self._tokens.items()
            if t.is_expired()
        ]
        for token in expired_tokens:
            del self._tokens[token]
            count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired items")
        
        return count


# Singleton instance
_server: Optional[OAuthServer] = None


def get_server() -> OAuthServer:
    """Get the singleton OAuth server."""
    global _server
    if _server is None:
        _server = OAuthServer()
    return _server
