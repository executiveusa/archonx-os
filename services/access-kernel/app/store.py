import sqlite3
from pathlib import Path
from typing import Any


class Store:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                  id TEXT PRIMARY KEY,
                  principal TEXT NOT NULL,
                  principal_type TEXT NOT NULL,
                  expires_at TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS secrets (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  encrypted_payload TEXT NOT NULL,
                  metadata_json TEXT,
                  created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS grants (
                  id TEXT PRIMARY KEY,
                  principal TEXT NOT NULL,
                  principal_type TEXT NOT NULL,
                  work_item_id TEXT NOT NULL,
                  resource TEXT NOT NULL,
                  action TEXT NOT NULL,
                  duration_minutes INTEGER NOT NULL,
                  status TEXT NOT NULL,
                  approval_required INTEGER NOT NULL,
                  approved_by TEXT,
                  created_at TEXT NOT NULL,
                  expires_at TEXT
                );
                """
            )

    def execute(self, query: str, params: tuple[Any, ...]) -> None:
        with self._connect() as conn:
            conn.execute(query, params)

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def fetchone(self, query: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None
