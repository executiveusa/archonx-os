"""
ArchonX Authentication Module
=============================
Single Sign-In (SSO) system for the ArchonX ecosystem.

Components:
- OAuthServer: OAuth 2.0 authorization server
- SessionManager: User session tracking
- RBACManager: Role-based access control

Usage:
    from archonx.auth import OAuthServer, SessionManager, RBACManager, Role, Permission
    
    # OAuth
    oauth = OAuthServer()
    client = oauth.register_client("My App", ["http://localhost:3000/callback"])
    
    # Sessions
    sessions = SessionManager()
    session = sessions.create_session(user, access_token)
    
    # RBAC
    rbac = RBACManager()
    rbac.assign_role(user_id, Role.WHITE_QUEEN)
    if rbac.has_permission(user_id, Permission.TASK_WRITE):
        # Allow action
        pass
"""

from archonx.auth.oauth_server import (
    OAuthServer,
    OAuthClient,
    Token,
    AuthorizationCode,
    GrantType,
    get_server as get_oauth_server
)

from archonx.auth.session_manager import (
    SessionManager,
    Session,
    User,
    get_session_manager
)

from archonx.auth.rbac import (
    RBACManager,
    Role,
    Permission,
    UserRole,
    ROLE_PERMISSIONS,
    get_rbac_manager
)

__all__ = [
    # OAuth
    "OAuthServer",
    "OAuthClient",
    "Token",
    "AuthorizationCode",
    "GrantType",
    "get_oauth_server",
    
    # Session
    "SessionManager",
    "Session",
    "User",
    "get_session_manager",
    
    # RBAC
    "RBACManager",
    "Role",
    "Permission",
    "UserRole",
    "ROLE_PERMISSIONS",
    "get_rbac_manager",
]
