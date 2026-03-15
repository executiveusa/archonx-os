"""Repository registry — SQLite-based metadata storage."""

import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone

import yaml

from archonx.repos.models import (
    Team,
    Repo,
    DomainType,
    RepoVisibility,
    RepoKind,
    RepoPlacement,
    IngestHistory,
)


class RepoRegistry:
    """SQLite-backed repository metadata registry."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize registry.

        Args:
            db_path: Path to SQLite database. Defaults to archonx/.archonx/repos.db
        """
        if db_path is None:
            db_path = Path(__file__).resolve().parents[2] / ".archonx" / "repos.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                display TEXT NOT NULL,
                owners_json TEXT,
                regions_json TEXT,
                created_at TEXT
            )
        """)

        # Domain types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS domain_types (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL
            )
        """)

        # Repos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL UNIQUE,
                visibility TEXT NOT NULL,
                kind TEXT NOT NULL,
                team_id TEXT NOT NULL,
                domain_type_id TEXT NOT NULL,
                placement TEXT NOT NULL DEFAULT 'unknown',
                runtime_model TEXT,
                installed_under TEXT,
                capability_tags_json TEXT,
                called_by_json TEXT,
                calls_json TEXT,
                required_env_categories_json TEXT,
                created_at TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (domain_type_id) REFERENCES domain_types(id)
            )
        """)
        self._ensure_repo_columns(cursor)

        # Ingest history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingest_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingested_at_utc TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                repo_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                error TEXT,
                created_at TEXT
            )
        """)

        # Populate domain types if empty
        cursor.execute("SELECT COUNT(*) FROM domain_types")
        if cursor.fetchone()[0] == 0:
            for domain_type in DomainType:
                cursor.execute(
                    "INSERT OR IGNORE INTO domain_types (id, description) VALUES (?, ?)",
                    (domain_type.value, f"Domain type: {domain_type.value}"),
                )

        conn.commit()

    def _ensure_repo_columns(self, cursor: sqlite3.Cursor) -> None:
        """Ensure newer repo metadata columns exist on older databases."""
        cursor.execute("PRAGMA table_info(repos)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {
            "placement": "TEXT NOT NULL DEFAULT 'unknown'",
            "runtime_model": "TEXT",
            "installed_under": "TEXT",
            "capability_tags_json": "TEXT",
            "called_by_json": "TEXT",
            "calls_json": "TEXT",
            "required_env_categories_json": "TEXT",
        }
        for column_name, ddl in expected_columns.items():
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE repos ADD COLUMN {column_name} {ddl}")

    def ingest_yaml(self, yaml_path: Path, mode: str = "index_only") -> dict:
        """Ingest repos from YAML file.

        Args:
            yaml_path: Path to repos.index.yaml
            mode: Operating mode (index_only is the only supported mode)

        Returns:
            dict with ingest results

        Raises:
            ValueError: If schema is invalid or mode is not supported
        """
        if mode != "index_only":
            raise ValueError(f"Mode '{mode}' not supported. Only 'index_only' is allowed.")

        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        # Load and parse YAML
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        # Validate schema
        if not isinstance(data, dict) or "archonx_repo_index_spec" not in data:
            raise ValueError("Invalid schema: missing 'archonx_repo_index_spec' key")

        spec = data["archonx_repo_index_spec"]
        if spec.get("mode") != "index_only":
            raise ValueError(f"Spec mode must be 'index_only', got '{spec.get('mode')}'")

        # Check do_not_clone flag
        if not spec.get("do_not_clone"):
            raise ValueError("Spec must have do_not_clone: true")

        # Calculate file hash
        file_hash = hashlib.sha256(yaml_path.read_bytes()).hexdigest()

        # Check if already ingested
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ingest_history WHERE file_hash = ? ORDER BY created_at DESC LIMIT 1",
            (file_hash,),
        )
        existing = cursor.fetchone()
        if existing and existing["status"] == "success":
            return {
                "status": "skipped",
                "message": "File already ingested",
                "file_hash": file_hash,
                "repo_count": existing["repo_count"],
            }

        # Ingest teams
        teams = spec.get("teams", [])
        for team_data in teams:
            self._upsert_team(
                Team(
                    id=team_data["id"],
                    display=team_data["display"],
                    owners=team_data.get("owners", []),
                    regions=team_data.get("regions", []),
                )
            )

        # Ingest repos
        repos = spec.get("repos", [])
        repo_count = 0
        errors = []

        for repo_data in repos:
            try:
                repo = Repo(
                    id=repo_data["id"],
                    name=repo_data["name"],
                    url=repo_data["url"],
                    visibility=RepoVisibility(repo_data["vis"]),
                    kind=RepoKind(repo_data["kind"]),
                    team_id=repo_data["team_id"],
                    domain_type_id=DomainType(repo_data["domain_type_id"]),
                    placement=RepoPlacement(
                        repo_data.get("placement", RepoPlacement.UNKNOWN.value)
                    ),
                    runtime_model=repo_data.get("runtime_model"),
                    installed_under=repo_data.get("installed_under"),
                    capability_tags=repo_data.get("capability_tags", []),
                    called_by=repo_data.get("called_by", []),
                    calls=repo_data.get("calls", []),
                    required_env_categories=repo_data.get(
                        "required_env_categories", []
                    ),
                )
                self._upsert_repo(repo)
                repo_count += 1
            except (KeyError, ValueError) as e:
                errors.append(f"Repo {repo_data.get('id', '?')}: {e}")

        # Record ingest history
        status = "success" if not errors else "partial"
        error_msg = "; ".join(errors) if errors else None

        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """INSERT INTO ingest_history
               (ingested_at_utc, file_hash, repo_count, status, error, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (now, file_hash, repo_count, status, error_msg, now),
        )
        conn.commit()

        return {
            "status": status,
            "repo_count": repo_count,
            "file_hash": file_hash,
            "errors": errors if errors else None,
            "ingested_at": now,
        }

    def _upsert_team(self, team: Team) -> None:
        """Upsert a team record."""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """INSERT OR REPLACE INTO teams (id, display, owners_json, regions_json, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                team.id,
                team.display,
                json.dumps(team.owners),
                json.dumps(team.regions),
                now,
            ),
        )
        conn.commit()

    def _upsert_repo(self, repo: Repo) -> None:
        """Upsert a repo record."""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """INSERT OR REPLACE INTO repos
               (id, name, url, visibility, kind, team_id, domain_type_id, placement,
                runtime_model, installed_under, capability_tags_json, called_by_json,
                calls_json, required_env_categories_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                repo.id,
                repo.name,
                repo.url,
                repo.visibility.value,
                repo.kind.value,
                repo.team_id,
                repo.domain_type_id.value,
                repo.placement.value,
                repo.runtime_model,
                repo.installed_under,
                json.dumps(repo.capability_tags),
                json.dumps(repo.called_by),
                json.dumps(repo.calls),
                json.dumps(repo.required_env_categories),
                now,
            ),
        )
        conn.commit()

    def get_repo(self, repo_id: int) -> Optional[Repo]:
        """Get a single repo by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repos WHERE id = ?", (repo_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_repo(row)

    def get_repos(
        self,
        team_id: Optional[str] = None,
        domain_type_id: Optional[str] = None,
        visibility: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> List[Repo]:
        """Query repos with optional filters."""
        conn = self._get_conn()
        cursor = conn.cursor()

        query = "SELECT * FROM repos WHERE 1=1"
        params = []

        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
        if domain_type_id:
            query += " AND domain_type_id = ?"
            params.append(domain_type_id)
        if visibility:
            query += " AND visibility = ?"
            params.append(visibility)
        if kind:
            query += " AND kind = ?"
            params.append(kind)

        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        return [self._row_to_repo(row) for row in cursor.fetchall()]

    def get_team(self, team_id: str) -> Optional[Team]:
        """Get a single team by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Team(
            id=row["id"],
            display=row["display"],
            owners=json.loads(row["owners_json"] or "[]"),
            regions=json.loads(row["regions_json"] or "[]"),
        )

    def list_teams(self) -> List[Team]:
        """List all teams."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams ORDER BY id ASC")
        return [
            Team(
                id=row["id"],
                display=row["display"],
                owners=json.loads(row["owners_json"] or "[]"),
                regions=json.loads(row["regions_json"] or "[]"),
            )
            for row in cursor.fetchall()
        ]

    def get_ingest_history(self, limit: int = 10) -> List[IngestHistory]:
        """Get recent ingest history."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ingest_history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [
            IngestHistory(
                ingested_at_utc=row["ingested_at_utc"],
                file_hash=row["file_hash"],
                repo_count=row["repo_count"],
                status=row["status"],
                error=row["error"],
            )
            for row in cursor.fetchall()
        ]

    def _row_to_repo(self, row) -> Repo:
        """Convert database row to Repo object."""
        return Repo(
            id=row["id"],
            name=row["name"],
            url=row["url"],
            visibility=RepoVisibility(row["visibility"]),
            kind=RepoKind(row["kind"]),
            team_id=row["team_id"],
            domain_type_id=DomainType(row["domain_type_id"]),
            placement=RepoPlacement(row["placement"] or RepoPlacement.UNKNOWN.value),
            runtime_model=row["runtime_model"],
            installed_under=row["installed_under"],
            capability_tags=json.loads(row["capability_tags_json"] or "[]"),
            called_by=json.loads(row["called_by_json"] or "[]"),
            calls=json.loads(row["calls_json"] or "[]"),
            required_env_categories=json.loads(
                row["required_env_categories_json"] or "[]"
            ),
        )

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
