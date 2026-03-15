"""
Role-Based Access Control (RBAC)
================================
Permission management for ArchonX ecosystem.

Provides:
- Role definitions
- Permission checking
- Resource access control
- Role assignment
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("archonx.auth.rbac")


class Permission(Enum):
    """System permissions."""
    # Agent permissions
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_DELETE = "agent:delete"
    AGENT_DEPLOY = "agent:deploy"
    
    # Task permissions
    TASK_READ = "task:read"
    TASK_WRITE = "task:write"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"
    
    # Skill permissions
    SKILL_READ = "skill:read"
    SKILL_WRITE = "skill:write"
    SKILL_EXECUTE = "skill:execute"
    
    # Tool permissions
    TOOL_READ = "tool:read"
    TOOL_WRITE = "tool:write"
    TOOL_EXECUTE = "tool:execute"
    
    # Memory permissions
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    MEMORY_DELETE = "memory:delete"
    
    # Billing permissions
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_ROLES = "admin:roles"
    
    # Crew permissions
    CREW_WHITE = "crew:white"
    CREW_BLACK = "crew:black"
    
    # Orchestrator permissions
    ORCHESTRATOR_COMMAND = "orchestrator:command"
    ORCHESTRATOR_STATUS = "orchestrator:status"


class Role(Enum):
    """System roles with predefined permissions."""
    ADMIN = "admin"
    ORCHESTRATOR = "orchestrator"
    WHITE_QUEEN = "white_queen"
    WHITE_KING = "white_king"
    WHITE_ROOK = "white_rook"
    WHITE_BISHOP = "white_bishop"
    WHITE_KNIGHT = "white_knight"
    WHITE_PAWN = "white_pawn"
    BLACK_QUEEN = "black_queen"
    BLACK_KING = "black_king"
    BLACK_ROOK = "black_rook"
    BLACK_BISHOP = "black_bishop"
    BLACK_KNIGHT = "black_knight"
    BLACK_PAWN = "black_pawn"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    SERVICE = "service"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        # Admins have all permissions
        *Permission
    },
    Role.ORCHESTRATOR: {
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.AGENT_DEPLOY,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.TASK_ASSIGN,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.ORCHESTRATOR_COMMAND,
        Permission.ORCHESTRATOR_STATUS,
        Permission.CREW_WHITE,
        Permission.CREW_BLACK,
    },
    Role.WHITE_QUEEN: {
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.TASK_ASSIGN,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.CREW_WHITE,
        Permission.ORCHESTRATOR_STATUS,
    },
    Role.WHITE_KING: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.CREW_WHITE,
        Permission.ORCHESTRATOR_STATUS,
    },
    Role.WHITE_ROOK: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.CREW_WHITE,
    },
    Role.WHITE_BISHOP: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.CREW_WHITE,
    },
    Role.WHITE_KNIGHT: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.CREW_WHITE,
    },
    Role.WHITE_PAWN: {
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.CREW_WHITE,
    },
    Role.BLACK_QUEEN: {
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.AGENT_DELETE,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.TASK_DELETE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.MEMORY_DELETE,
        Permission.CREW_BLACK,
        Permission.ORCHESTRATOR_STATUS,
    },
    Role.BLACK_KING: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.TASK_DELETE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_DELETE,
        Permission.CREW_BLACK,
        Permission.ORCHESTRATOR_STATUS,
    },
    Role.BLACK_ROOK: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.TASK_DELETE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.CREW_BLACK,
    },
    Role.BLACK_BISHOP: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.CREW_BLACK,
    },
    Role.BLACK_KNIGHT: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.CREW_BLACK,
    },
    Role.BLACK_PAWN: {
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.CREW_BLACK,
    },
    Role.DEVELOPER: {
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.SKILL_READ,
        Permission.SKILL_WRITE,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_WRITE,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.BILLING_READ,
    },
    Role.VIEWER: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.SKILL_READ,
        Permission.TOOL_READ,
        Permission.MEMORY_READ,
    },
    Role.SERVICE: {
        Permission.AGENT_READ,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.TOOL_READ,
        Permission.TOOL_EXECUTE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
    },
}


@dataclass
class UserRole:
    """User role assignment."""
    user_id: str
    role: Role
    assigned_by: Optional[str] = None
    assigned_at: str = ""
    expires_at: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.assigned_at:
            from datetime import datetime, timezone
            self.assigned_at = datetime.now(timezone.UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserRole:
        return cls(
            user_id=data["user_id"],
            role=Role(data["role"]),
            assigned_by=data.get("assigned_by"),
            assigned_at=data.get("assigned_at", ""),
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {})
        )


class RBACManager:
    """
    Role-Based Access Control manager.
    
    Features:
    - Role assignment
    - Permission checking
    - Resource access control
    - Role hierarchy
    
    Usage:
        rbac = RBACManager()
        
        # Assign role
        rbac.assign_role(user_id, Role.WHITE_QUEEN)
        
        # Check permission
        if rbac.has_permission(user_id, Permission.TASK_WRITE):
            # Allow action
            pass
    """

    def __init__(self, roles_file: Optional[Path] = None):
        """
        Initialize RBAC manager.
        
        Args:
            roles_file: File to persist role assignments
        """
        self.roles_file = roles_file or Path.home() / ".archonx" / "user_roles.json"
        self.roles_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._user_roles: dict[str, list[UserRole]] = {}
        
        # Load roles
        self._load_roles()
        
        logger.info(f"RBAC manager initialized")

    def _load_roles(self) -> None:
        """Load role assignments from file."""
        if self.roles_file.exists():
            try:
                with open(self.roles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for user_id, roles in data.get("user_roles", {}).items():
                        self._user_roles[user_id] = [
                            UserRole.from_dict(r) for r in roles
                        ]
                logger.info(f"Loaded roles for {len(self._user_roles)} users")
            except Exception as e:
                logger.warning(f"Failed to load roles: {e}")

    def _save_roles(self) -> None:
        """Save role assignments to file."""
        data = {
            "user_roles": {
                user_id: [r.to_dict() for r in roles]
                for user_id, roles in self._user_roles.items()
            }
        }
        with open(self.roles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def assign_role(
        self,
        user_id: str,
        role: Role,
        assigned_by: Optional[str] = None,
        expires_at: Optional[str] = None
    ) -> UserRole:
        """
        Assign a role to a user.
        
        Args:
            user_id: The user ID
            role: The role to assign
            assigned_by: ID of user who assigned the role
            expires_at: Optional expiration timestamp
            
        Returns:
            The created UserRole
        """
        # Check if role already assigned
        existing = self.get_user_roles(user_id)
        for ur in existing:
            if ur.role == role:
                logger.debug(f"User {user_id} already has role {role.value}")
                return ur
        
        user_role = UserRole(
            user_id=user_id,
            role=role,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        self._user_roles[user_id].append(user_role)
        
        self._save_roles()
        
        logger.info(f"Assigned role {role.value} to user {user_id}")
        return user_role

    def revoke_role(self, user_id: str, role: Role) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: The user ID
            role: The role to revoke
            
        Returns:
            True if revoked, False if not found
        """
        if user_id not in self._user_roles:
            return False
        
        for i, ur in enumerate(self._user_roles[user_id]):
            if ur.role == role:
                self._user_roles[user_id].pop(i)
                self._save_roles()
                logger.info(f"Revoked role {role.value} from user {user_id}")
                return True
        
        return False

    def get_user_roles(self, user_id: str) -> list[UserRole]:
        """
        Get all roles for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of UserRole objects
        """
        return self._user_roles.get(user_id, [])

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Set of permissions
        """
        permissions: set[Permission] = set()
        
        for user_role in self.get_user_roles(user_id):
            permissions.update(ROLE_PERMISSIONS.get(user_role.role, set()))
        
        return permissions

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: The user ID
            permission: The permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        return permission in self.get_user_permissions(user_id)

    def has_any_permission(self, user_id: str, permissions: set[Permission]) -> bool:
        """
        Check if a user has any of the specified permissions.
        
        Args:
            user_id: The user ID
            permissions: Set of permissions to check
            
        Returns:
            True if user has any permission, False otherwise
        """
        user_perms = self.get_user_permissions(user_id)
        return bool(user_perms & permissions)

    def has_all_permissions(self, user_id: str, permissions: set[Permission]) -> bool:
        """
        Check if a user has all of the specified permissions.
        
        Args:
            user_id: The user ID
            permissions: Set of permissions to check
            
        Returns:
            True if user has all permissions, False otherwise
        """
        user_perms = self.get_user_permissions(user_id)
        return permissions.issubset(user_perms)

    def check_resource_access(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if a user can access a resource.
        
        Args:
            user_id: The user ID
            resource: Resource type (agent, task, skill, etc.)
            action: Action (read, write, delete, execute)
            
        Returns:
            True if access allowed, False otherwise
        """
        permission_str = f"{resource}:{action}"
        
        try:
            permission = Permission(permission_str)
            return self.has_permission(user_id, permission)
        except ValueError:
            logger.warning(f"Unknown permission: {permission_str}")
            return False

    def get_users_with_role(self, role: Role) -> list[str]:
        """
        Get all users with a specific role.
        
        Args:
            role: The role to check
            
        Returns:
            List of user IDs
        """
        users = []
        for user_id, roles in self._user_roles.items():
            if any(ur.role == role for ur in roles):
                users.append(user_id)
        return users

    def get_users_with_permission(self, permission: Permission) -> list[str]:
        """
        Get all users with a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            List of user IDs
        """
        users = []
        for user_id in self._user_roles:
            if self.has_permission(user_id, permission):
                users.append(user_id)
        return users

    def clear_user_roles(self, user_id: str) -> int:
        """
        Clear all roles for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Number of roles cleared
        """
        if user_id not in self._user_roles:
            return 0
        
        count = len(self._user_roles[user_id])
        del self._user_roles[user_id]
        self._save_roles()
        
        logger.info(f"Cleared {count} roles for user {user_id}")
        return count


# Singleton instance
_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get the singleton RBACManager."""
    global _manager
    if _manager is None:
        _manager = RBACManager()
    return _manager
