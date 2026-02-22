"""
SQLite Memory Backend — Lightweight persistent memory with full-text search.

Uses SQLite with FTS5 for efficient text search across agent memory entries.
No external dependencies beyond the Python standard library.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.core.memory_sqlite")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT    NOT NULL,
    namespace   TEXT    NOT NULL DEFAULT 'default',
    key         TEXT    NOT NULL,
    value       TEXT    NOT NULL,
    metadata    TEXT,
    created_at  REAL    NOT NULL,
    updated_at  REAL    NOT NULL,
    UNIQUE(agent_id, namespace, key)
);

CREATE INDEX IF NOT EXISTS idx_memory_agent   ON memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_memory_ns      ON memory(agent_id, namespace);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    key, value, metadata,
    content='memory',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
    INSERT INTO memory_fts(rowid, key, value, metadata)
    VALUES (new.id, new.key, new.value, new.metadata);
END;

CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, key, value, metadata)
    VALUES ('delete', old.id, old.key, old.value, old.metadata);
END;

CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, key, value, metadata)
    VALUES ('delete', old.id, old.key, old.value, old.metadata);
    INSERT INTO memory_fts(rowid, key, value, metadata)
    VALUES (new.id, new.key, new.value, new.metadata);
END;
"""


@dataclass
class MemoryEntry:
    """A single memory record."""
    id: int
    agent_id: str
    namespace: str
    key: str
    value: str
    metadata: dict[str, Any]
    created_at: float
    updated_at: float


class SQLiteMemory:
    """
    SQLite-backed memory store with FTS5 full-text search.

    Usage:
        mem = SQLiteMemory("data/memory.db")
        mem.initialize()
        mem.put("agent-01", "context", "user_prefs", '{"theme":"dark"}')
        results = mem.search("agent-01", "dark")
        mem.close()
    """

    def __init__(self, db_path: str = "data/archonx_memory.db") -> None:
        self._db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def initialize(self) -> None:
        """Create the database and schema."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        logger.info("SQLite memory initialized at %s", self._db_path)

    def _ensure_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("SQLiteMemory not initialized — call initialize() first")
        return self._conn

    def put(
        self,
        agent_id: str,
        namespace: str,
        key: str,
        value: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Insert or update a memory entry. Returns the row ID."""
        conn = self._ensure_conn()
        now = time.time()
        meta_json = json.dumps(metadata) if metadata else None
        cursor = conn.execute(
            """
            INSERT INTO memory (agent_id, namespace, key, value, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id, namespace, key) DO UPDATE SET
                value = excluded.value,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
            """,
            (agent_id, namespace, key, value, meta_json, now, now),
        )
        conn.commit()
        return cursor.lastrowid or 0

    def get(self, agent_id: str, namespace: str, key: str) -> MemoryEntry | None:
        """Retrieve a single memory entry by exact key."""
        conn = self._ensure_conn()
        row = conn.execute(
            "SELECT id, agent_id, namespace, key, value, metadata, created_at, updated_at "
            "FROM memory WHERE agent_id = ? AND namespace = ? AND key = ?",
            (agent_id, namespace, key),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_entry(row)

    def delete(self, agent_id: str, namespace: str, key: str) -> bool:
        """Delete a single entry. Returns True if deleted."""
        conn = self._ensure_conn()
        cursor = conn.execute(
            "DELETE FROM memory WHERE agent_id = ? AND namespace = ? AND key = ?",
            (agent_id, namespace, key),
        )
        conn.commit()
        return cursor.rowcount > 0

    def list_keys(self, agent_id: str, namespace: str = "default") -> list[str]:
        """List all keys in a namespace for an agent."""
        conn = self._ensure_conn()
        rows = conn.execute(
            "SELECT key FROM memory WHERE agent_id = ? AND namespace = ? ORDER BY key",
            (agent_id, namespace),
        ).fetchall()
        return [r[0] for r in rows]

    def search(
        self,
        agent_id: str,
        query: str,
        namespace: str | None = None,
        limit: int = 20,
    ) -> list[MemoryEntry]:
        """Full-text search across memory entries for an agent."""
        conn = self._ensure_conn()
        if namespace:
            rows = conn.execute(
                """
                SELECT m.id, m.agent_id, m.namespace, m.key, m.value,
                       m.metadata, m.created_at, m.updated_at
                FROM memory m
                JOIN memory_fts f ON f.rowid = m.id
                WHERE m.agent_id = ? AND m.namespace = ? AND memory_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (agent_id, namespace, query, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT m.id, m.agent_id, m.namespace, m.key, m.value,
                       m.metadata, m.created_at, m.updated_at
                FROM memory m
                JOIN memory_fts f ON f.rowid = m.id
                WHERE m.agent_id = ? AND memory_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (agent_id, query, limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def clear_agent(self, agent_id: str) -> int:
        """Delete all memory for an agent. Returns count deleted."""
        conn = self._ensure_conn()
        cursor = conn.execute("DELETE FROM memory WHERE agent_id = ?", (agent_id,))
        conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("SQLite memory closed")

    @staticmethod
    def _row_to_entry(row: tuple[Any, ...]) -> MemoryEntry:
        return MemoryEntry(
            id=row[0],
            agent_id=row[1],
            namespace=row[2],
            key=row[3],
            value=row[4],
            metadata=json.loads(row[5]) if row[5] else {},
            created_at=row[6],
            updated_at=row[7],
        )
