"""
NullClaw Memory Synchronization Bridge
========================================

Bidirectional memory synchronization between:
- Central Franken-Claw distributed memory (backend: Redis/Postgres/custom)
- Edge NullClaw local SQLite memory (vector + FTS5)

Sync modes:
- broadcast: Central → all edges (on context change)
- pull: Edge asks central for memory (on startup)
- push: Edge sends local memories (on idle)
- migrate: Manual export/import of memory state

Memory format:
- Both systems normalize to {id, type, content, vector, tags, timestamp}
- Central stores compound index; edge stores local SQLite
- Hybrid search (vector cosine similarity + BM25 keyword)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import time

logger = logging.getLogger("archonx.openclaw.memory.nullclaw_sync")


class SyncMode(Enum):
    """Memory sync modes."""
    BROADCAST = "broadcast"  # Central → edges
    PULL = "pull"  # Edge ← central on startup
    PUSH = "push"  # Edge → central on idle
    MERGE = "merge"  # Bidirectional merge
    MANUAL = "manual"  # One-time export/import


@dataclass
class MemoryEntry:
    """
    Unified memory entry format.
    
    Used by both central and edge systems to normalize
    memory records. Allows seamless sync and merge.
    """
    id: str  # Unique ID (UUID or hash)
    type: str  # "conversation", "knowledge", "agent_state", "vector_embedding", etc.
    content: str  # Text content
    vector: list[float] = field(default_factory=list)  # Embedding vector (if available)
    tags: list[str] = field(default_factory=list)  # Search tags
    metadata: dict[str, Any] = field(default_factory=dict)  # Extra data
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: str | None = None  # For auto-purge
    gateway_id: str = ""  # Which edge created this (if synced from edge)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return asdict(self)
    
    def hash_id(self) -> str:
        """Generate or verify content hash."""
        content_hash = hashlib.sha256(
            (self.content + self.type).encode()
        ).hexdigest()
        return content_hash[:16]


@dataclass
class SyncCheckpoint:
    """Track sync state for consistency."""
    gateway_id: str
    mode: SyncMode
    direction: str  # "push" or "pull" or "bidirectional"
    last_sync_time: float = field(default_factory=time.time)
    last_sequence_number: int = 0
    entries_sent: int = 0
    entries_received: int = 0
    bytes_transferred: int = 0
    status: str = "success"  # "success", "in_progress", "failed"


class NullClawMemorySyncBridge:
    """
    Bidirectional memory sync between central and edge systems.
    
    Responsibilities:
    1. Normalize memory formats (central <-> edge)
    2. Detect conflicts + merge strategies
    3. Track sync state + checkpoints
    4. Handle offline/retry scenarios
    5. Implement multi-mode sync (broadcast/pull/push/merge)
    """
    
    def __init__(
        self,
        central_backend: Any,  # Central memory backend (Redis/Postgres/custom)
        edge_backends: dict[str, Any] | None = None,  # {gateway_id: edge_backend}
    ):
        """
        Args:
            central_backend: Central memory system (interface: get, set, delete, search)
            edge_backends: Map of edge gateways to their SQLite backends
        """
        self.central_backend = central_backend
        self.edge_backends = edge_backends or {}
        self.checkpoints: dict[str, SyncCheckpoint] = {}
        self.sync_locks: dict[str, asyncio.Lock] = {}
        self.merge_conflicts: list[dict[str, Any]] = []
        
        logger.info(
            "NullClawMemorySyncBridge initialized with %d edge backends",
            len(self.edge_backends),
        )
    
    async def broadcast_to_edge(
        self,
        gateway_id: str,
        memory_snapshot: list[MemoryEntry],
        mode: SyncMode = SyncMode.BROADCAST,
    ) -> dict[str, Any]:
        """
        Broadcast memory from central to edge gateway.
        
        Used when:
        - New agent spins up on edge
        - Context/policy changes require propagation
        - Full sync requested
        """
        if gateway_id not in self.edge_backends:
            logger.error("Unknown edge gateway: %s", gateway_id)
            return {
                "status": "error",
                "reason": "unknown_gateway",
            }
        
        # Acquire sync lock (prevent concurrent syncs)
        lock_key = f"{gateway_id}:broadcast"
        if lock_key not in self.sync_locks:
            self.sync_locks[lock_key] = asyncio.Lock()
        
        async with self.sync_locks[lock_key]:
            checkpoint = SyncCheckpoint(
                gateway_id=gateway_id,
                mode=mode,
                direction="push",
                status="in_progress",
            )
            
            try:
                edge_backend = self.edge_backends[gateway_id]
                entries_written = 0
                bytes_written = 0
                
                # Send entries in batches
                batch_size = 100
                for i in range(0, len(memory_snapshot), batch_size):
                    batch = memory_snapshot[i : i + batch_size]
                    
                    for entry in batch:
                        await edge_backend.set(entry.id, entry.to_dict())
                        entries_written += 1
                        bytes_written += len(json.dumps(entry.to_dict()).encode())
                
                checkpoint.entries_sent = entries_written
                checkpoint.bytes_transferred = bytes_written
                checkpoint.status = "success"
                
                logger.info(
                    "Broadcast %d memory entries to %s (%d bytes)",
                    entries_written,
                    gateway_id,
                    bytes_written,
                )
                
            except Exception as e:
                checkpoint.status = "failed"
                logger.error("Broadcast to %s failed: %s", gateway_id, e)
                return {
                    "status": "error",
                    "reason": str(e),
                }
            finally:
                self.checkpoints[f"{gateway_id}:broadcast"] = checkpoint
        
        return {
            "status": "success",
            "gateway_id": gateway_id,
            "entries_sent": checkpoint.entries_sent,
            "bytes_transferred": checkpoint.bytes_transferred,
        }
    
    async def sync_from_edge(
        self,
        gateway_id: str,
        edge_memory_export: list[MemoryEntry],
        mode: SyncMode = SyncMode.PUSH,
    ) -> dict[str, Any]:
        """
        Ingest memories from edge NullClaw.
        
        Used for:
        - After offline period: merge new memories
        - Agent failover: transfer context to central
        - Scheduled consolidation (e.g., daily 02:00 UTC)
        
        Merge strategy: last-write-wins with conflict tracking
        """
        lock_key = f"{gateway_id}:push"
        if lock_key not in self.sync_locks:
            self.sync_locks[lock_key] = asyncio.Lock()
        
        async with self.sync_locks[lock_key]:
            checkpoint = SyncCheckpoint(
                gateway_id=gateway_id,
                mode=mode,
                direction="pull",
                status="in_progress",
            )
            
            try:
                entries_merged = 0
                entries_skipped = 0
                conflicts = []
                
                for edge_entry in edge_memory_export:
                    # Check if entry already exists in central
                    try:
                        central_entry_dict = await self.central_backend.get(edge_entry.id)
                        central_entry = MemoryEntry(**central_entry_dict)
                    except Exception:
                        central_entry = None
                    
                    if central_entry is None:
                        # New entry: write to central
                        edge_entry.gateway_id = gateway_id
                        await self.central_backend.set(edge_entry.id, edge_entry.to_dict())
                        entries_merged += 1
                    
                    else:
                        # Conflict: both have entry
                        # Strategy: last-write-wins
                        edge_time = datetime.fromisoformat(edge_entry.updated_at)
                        central_time = datetime.fromisoformat(central_entry.updated_at)
                        
                        if edge_time > central_time:
                            # Edge is newer: use edge version
                            edge_entry.gateway_id = gateway_id
                            await self.central_backend.set(
                                edge_entry.id,
                                edge_entry.to_dict(),
                            )
                            entries_merged += 1
                        else:
                            # Central is newer: skip edge version
                            entries_skipped += 1
                            conflicts.append({
                                "entry_id": edge_entry.id,
                                "central_time": central_entry.updated_at,
                                "edge_time": edge_entry.updated_at,
                                "winner": "central",
                            })
                
                checkpoint.entries_received = entries_merged
                checkpoint.status = "success"
                
                if conflicts:
                    self.merge_conflicts.extend(conflicts)
                
                logger.info(
                    "Synced from %s: %d merged, %d skipped, %d conflicts",
                    gateway_id,
                    entries_merged,
                    entries_skipped,
                    len(conflicts),
                )
                
            except Exception as e:
                checkpoint.status = "failed"
                logger.error("Sync from %s failed: %s", gateway_id, e)
                return {
                    "status": "error",
                    "reason": str(e),
                }
            finally:
                self.checkpoints[f"{gateway_id}:push"] = checkpoint
        
        return {
            "status": "success",
            "gateway_id": gateway_id,
            "entries_merged": checkpoint.entries_received,
            "entries_skipped": entries_skipped,
            "conflicts": conflicts,
        }
    
    async def pull_from_central(
        self,
        gateway_id: str,
        since_timestamp: str | None = None,
    ) -> list[MemoryEntry]:
        """
        Pull memory from central for edge startup.
        
        Optionally filters by timestamp to get incremental updates.
        """
        try:
            # Query central backend for all entries
            # (or filtered if since_timestamp provided)
            entries = await self.central_backend.search("*")
            
            if since_timestamp:
                cutoff = datetime.fromisoformat(since_timestamp)
                entries = [
                    e for e in entries
                    if datetime.fromisoformat(e.updated_at) > cutoff
                ]
            
            logger.info(
                "Pulled %d memory entries from central for %s",
                len(entries),
                gateway_id,
            )
            
            return [MemoryEntry(**e) if isinstance(e, dict) else e for e in entries]
        
        except Exception as e:
            logger.error("Pull from central failed for %s: %s", gateway_id, e)
            return []
    
    async def migrate_from_openclaw(
        self,
        openclaw_export_path: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        Migrate memory state from OpenClaw to nullclaw format.
        
        OpenClaw export is typically markdown files or JSON dump.
        This converts to NullClaw SQLite format.
        
        Called by edge instance: nullclaw migrate openclaw --source PATH
        """
        try:
            # Read OpenClaw export
            with open(openclaw_export_path, "r") as f:
                openclaw_data = json.load(f)
            
            converted_entries = []
            
            for item in openclaw_data.get("memories", []):
                entry = MemoryEntry(
                    id=item.get("id", hashlib.md5(
                        item.get("content", "").encode()
                    ).hexdigest()[:16]),
                    type=item.get("type", "knowledge"),
                    content=item.get("content", ""),
                    vector=item.get("vector", []),
                    tags=item.get("tags", []),
                    created_at=item.get("created_at", datetime.utcnow().isoformat()),
                    updated_at=item.get("updated_at", datetime.utcnow().isoformat()),
                )
                converted_entries.append(entry)
            
            if not dry_run:
                # Write to NullClaw memory backend
                for entry in converted_entries:
                    if "edge_backends" in self.__dict__ and self.edge_backends:
                        edge_backend = next(iter(self.edge_backends.values()))
                        await edge_backend.set(entry.id, entry.to_dict())
            
            logger.info(
                "Migrated %d OpenClaw memories to NullClaw format (dry_run=%s)",
                len(converted_entries),
                dry_run,
            )
            
            return {
                "status": "success",
                "entries_migrated": len(converted_entries),
                "dry_run": dry_run,
            }
        
        except Exception as e:
            logger.error("Migration from OpenClaw failed: %s", e)
            return {
                "status": "error",
                "reason": str(e),
            }
    
    async def get_sync_status(self) -> dict[str, Any]:
        """Return overview of all sync operations and conflicts."""
        return {
            "checkpoints": {
                k: asdict(v) for k, v in self.checkpoints.items()
            },
            "merge_conflicts": self.merge_conflicts,
            "total_conflicts": len(self.merge_conflicts),
        }
    
    async def resolve_conflict(
        self,
        entry_id: str,
        winner: str,  # "central" or "edge"
    ) -> dict[str, Any]:
        """
        Manually resolve a conflict (last-write-wins default can be overridden).
        """
        conflict = next(
            (c for c in self.merge_conflicts if c["entry_id"] == entry_id),
            None,
        )
        
        if not conflict:
            return {
                "status": "error",
                "reason": "conflict_not_found",
            }
        
        conflict["resolved"] = True
        conflict["resolution"] = winner
        
        logger.info(
            "Resolved conflict for %s: winner=%s",
            entry_id,
            winner,
        )
        
        return {
            "status": "success",
            "entry_id": entry_id,
            "winner": winner,
        }


# Singleton instance
_bridge: NullClawMemorySyncBridge | None = None


def get_bridge(
    central_backend: Any | None = None,
    edge_backends: dict[str, Any] | None = None,
) -> NullClawMemorySyncBridge:
    """Get or create singleton bridge."""
    global _bridge
    if _bridge is None:
        _bridge = NullClawMemorySyncBridge(central_backend, edge_backends)
    return _bridge
