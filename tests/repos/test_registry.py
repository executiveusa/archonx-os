"""Tests for RepoRegistry."""

import tempfile
from pathlib import Path
import pytest

from archonx.repos.registry import RepoRegistry
from archonx.repos.models import Repo, DomainType, RepoVisibility, RepoKind


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_repos.db"
        yield db_path


@pytest.fixture
def temp_yaml():
    """Create a temporary YAML file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "test_index.yaml"
        yaml_content = """
archonx_repo_index_spec:
  version: "1.0.0"
  mode: "index_only"
  do_not_clone: true
  do_not_vendor: true
  do_not_mirror: true

  teams:
    - id: test_team
      display: "Test Team"
      owners: [test_user]
      regions: [Global]

  domain_types:
    - id: saas
      description: "SaaS"

  repos:
    - {id: 1, name: "test-repo-1", url: "https://github.com/test/repo-1", vis: public, kind: orig, team_id: test_team, domain_type_id: saas}
    - {id: 2, name: "test-repo-2", url: "https://github.com/test/repo-2", vis: private, kind: fork, team_id: test_team, domain_type_id: saas}
"""
        yaml_path.write_text(yaml_content, encoding="utf-8")
        yield yaml_path


class TestRepoRegistry:
    """Test RepoRegistry functionality."""

    def test_init_creates_db(self, temp_db):
        """Test that init creates database file."""
        registry = RepoRegistry(temp_db)
        assert temp_db.exists()
        registry.close()

    def test_schema_created(self, temp_db):
        """Test that schema is created on init."""
        registry = RepoRegistry(temp_db)
        conn = registry._get_conn()
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        assert "teams" in tables
        assert "domain_types" in tables
        assert "repos" in tables
        assert "ingest_history" in tables

        registry.close()

    def test_ingest_yaml(self, temp_db, temp_yaml):
        """Test YAML ingestion."""
        registry = RepoRegistry(temp_db)
        result = registry.ingest_yaml(temp_yaml, mode="index_only")

        assert result["status"] in ["success", "partial"]
        assert result["repo_count"] == 2
        assert "file_hash" in result

        registry.close()

    def test_ingest_invalid_yaml(self, temp_db):
        """Test ingestion of invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = Path(tmpdir) / "bad.yaml"
            bad_yaml.write_text("invalid: yaml: content:", encoding="utf-8")

            registry = RepoRegistry(temp_db)
            with pytest.raises(ValueError):
                registry.ingest_yaml(bad_yaml)
            registry.close()

    def test_ingest_missing_do_not_clone(self, temp_db):
        """Test that ingest fails if do_not_clone is not true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = Path(tmpdir) / "bad.yaml"
            bad_yaml.write_text("""
archonx_repo_index_spec:
  version: "1.0.0"
  mode: "index_only"
  do_not_clone: false
""", encoding="utf-8")

            registry = RepoRegistry(temp_db)
            with pytest.raises(ValueError, match="do_not_clone"):
                registry.ingest_yaml(bad_yaml)
            registry.close()

    def test_get_repo(self, temp_db, temp_yaml):
        """Test getting a single repo."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        repo = registry.get_repo(1)
        assert repo is not None
        assert repo.id == 1
        assert repo.name == "test-repo-1"
        assert repo.visibility == RepoVisibility.PUBLIC
        assert repo.kind == RepoKind.ORIGINAL

        registry.close()

    def test_get_repo_not_found(self, temp_db):
        """Test getting a non-existent repo."""
        registry = RepoRegistry(temp_db)
        repo = registry.get_repo(999)
        assert repo is None
        registry.close()

    def test_get_repos_filter_team(self, temp_db, temp_yaml):
        """Test filtering repos by team."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        repos = registry.get_repos(team_id="test_team")
        assert len(repos) == 2

        repos = registry.get_repos(team_id="nonexistent")
        assert len(repos) == 0

        registry.close()

    def test_get_repos_filter_visibility(self, temp_db, temp_yaml):
        """Test filtering repos by visibility."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        public = registry.get_repos(visibility="public")
        assert len(public) == 1
        assert public[0].id == 1

        private = registry.get_repos(visibility="private")
        assert len(private) == 1
        assert private[0].id == 2

        registry.close()

    def test_get_repos_filter_kind(self, temp_db, temp_yaml):
        """Test filtering repos by kind."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        orig = registry.get_repos(kind="orig")
        assert len(orig) == 1
        assert orig[0].id == 1

        fork = registry.get_repos(kind="fork")
        assert len(fork) == 1
        assert fork[0].id == 2

        registry.close()

    def test_get_team(self, temp_db, temp_yaml):
        """Test getting team metadata."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        team = registry.get_team("test_team")
        assert team is not None
        assert team.display == "Test Team"
        assert "test_user" in team.owners

        registry.close()

    def test_ingest_history(self, temp_db, temp_yaml):
        """Test ingest history tracking."""
        registry = RepoRegistry(temp_db)
        registry.ingest_yaml(temp_yaml)

        history = registry.get_ingest_history(limit=10)
        assert len(history) > 0
        assert history[0].repo_count == 2
        assert history[0].status in ["success", "partial"]

        registry.close()

    def test_ingest_idempotency(self, temp_db, temp_yaml):
        """Test that ingesting same file twice is idempotent."""
        registry = RepoRegistry(temp_db)

        result1 = registry.ingest_yaml(temp_yaml)
        result2 = registry.ingest_yaml(temp_yaml)

        # Second ingest should be skipped (same hash)
        assert result2["status"] == "skipped"
        assert result1["file_hash"] == result2["file_hash"]

        registry.close()

    def test_upsert_repo_idempotency(self, temp_db):
        """Test that upserting repos is idempotent."""
        registry = RepoRegistry(temp_db)

        repo1 = Repo(
            id=1,
            name="test-repo",
            url="https://github.com/test/repo",
            visibility=RepoVisibility.PUBLIC,
            kind=RepoKind.ORIGINAL,
            team_id="test_team",
            domain_type_id=DomainType.SAAS,
        )

        registry._upsert_repo(repo1)
        repos_before = registry.get_repos()

        registry._upsert_repo(repo1)  # Same repo again
        repos_after = registry.get_repos()

        assert len(repos_before) == len(repos_after)

        registry.close()
