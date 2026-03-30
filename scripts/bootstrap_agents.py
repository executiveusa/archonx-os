"""
ARCHON-X Agent Bootstrap Script
Loads 38 agent souls from .agent-souls/ YAML into Supabase.
Run once on fresh deployment or after DB reset.

Usage:
    python scripts/bootstrap_agents.py
    python scripts/bootstrap_agents.py --reset  # wipe and re-seed
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("bootstrap")

REPO_ROOT = Path(__file__).parent.parent
SOULS_DIR = REPO_ROOT / ".agent-souls"

# Default roles to insert
DEFAULT_ROLES = [
    {
        "name": "admin",
        "description": "Full system access",
        "permissions": ["read:*", "write:*", "admin:*"],
    },
    {
        "name": "agent",
        "description": "Agent task execution",
        "permissions": ["read:tasks", "write:tasks", "read:agents"],
    },
    {
        "name": "viewer",
        "description": "Read-only dashboard access",
        "permissions": ["read:tasks", "read:agents", "read:theater"],
    },
    {
        "name": "cockpit",
        "description": "Cockpit/operator access",
        "permissions": ["read:*", "write:tasks", "write:agents"],
    },
]

# Default cron jobs
DEFAULT_CRON_JOBS = [
    {
        "name": "sync_notion_tasks",
        "description": "Sync pending Notion tasks to agent queue",
        "schedule": "*/15 * * * *",
        "handler_path": "archonx.jobs.notion.sync_tasks",
        "enabled": True,
    },
    {
        "name": "cleanup_ws_sessions",
        "description": "Remove stale WebSocket sessions older than 1 hour",
        "schedule": "0 * * * *",
        "handler_path": "archonx.jobs.cleanup.prune_ws_sessions",
        "enabled": True,
    },
    {
        "name": "cost_daily_report",
        "description": "Send daily cost summary via Popebot",
        "schedule": "0 9 * * *",
        "handler_path": "archonx.jobs.reporting.daily_cost_report",
        "enabled": True,
    },
    {
        "name": "secret_health_check",
        "description": "Verify all API keys are valid",
        "schedule": "0 6 * * *",
        "handler_path": "archonx.jobs.secrets.health_check",
        "enabled": True,
    },
    {
        "name": "agent_metrics_snapshot",
        "description": "Snapshot agent performance metrics",
        "schedule": "*/5 * * * *",
        "handler_path": "archonx.jobs.metrics.snapshot",
        "enabled": True,
    },
    {
        "name": "theater_heartbeat",
        "description": "Broadcast agent status to Chess Theater", 
        "schedule": "* * * * *",
        "handler_path": "archonx.jobs.theater.heartbeat",
        "enabled": True,
    },
]


def parse_soul_file(path: Path) -> dict | None:
    """Parse a .soul.md file with YAML front-matter."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        log.warning(f"Cannot read {path}: {e}")
        return None

    # Extract YAML front-matter between --- delimiters
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        # Try to extract key:value pairs directly from the file
        data: dict = {"soul_id": path.stem}
        for line in content.split("\n")[:30]:
            if ":" in line and not line.startswith("#"):
                k, _, v = line.partition(":")
                data[k.strip().lower()] = v.strip()
        return _normalize_soul(data, path)

    try:
        import yaml
        data = yaml.safe_load(fm_match.group(1)) or {}
    except Exception:
        data = {}

    data["soul_id"] = path.stem
    return _normalize_soul(data, path)


def _normalize_soul(data: dict, path: Path) -> dict:
    """Normalize soul data to DB columns."""
    soul_id = data.get("soul_id", path.stem)

    # Determine team from directory structure
    team = "white" if "white" in str(path.parent) else "black"

    # Avatar color: try color field, or assign by team
    color = data.get("color", data.get("avatar_color", ""))
    if not color:
        color = "#d4af37" if team == "white" else "#1a1a2e"

    return {
        "soul_id": soul_id,
        "name": data.get("name", soul_id.replace("_", " ").title()),
        "role": data.get("role", data.get("title", "Agent")),
        "team": team,
        "status": "idle",
        "avatar_color": color[:7] if color else "#888888",
        "voice_id": data.get("voice_id", data.get("elevenlabs_voice_id", "")),
        "system_prompt": data.get("system_prompt", data.get("prompt", "")),
        "capabilities": json.dumps(data.get("capabilities", data.get("skills", []))),
        "metadata": json.dumps({
            "soul_file": str(path.relative_to(REPO_ROOT)),
            "locale": data.get("locale", "en-US"),
            "personality": data.get("personality", ""),
            "chess_piece": data.get("chess_piece", soul_id.split("_")[-1]),
        }),
    }


async def run_bootstrap(database_url: str, reset: bool = False) -> None:
    try:
        import asyncpg
    except ImportError:
        log.error("asyncpg not installed. Run: pip install asyncpg")
        sys.exit(1)

    log.info(f"Connecting to database...")
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5, command_timeout=60)

    async with pool.acquire() as conn:
        # Run schema migrations first
        migration_path = REPO_ROOT / "migrations" / "001_init_agents_schema.sql"
        if migration_path.exists():
            log.info("Running schema migration...")
            sql = migration_path.read_text()
            # Execute each statement separately
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                try:
                    await conn.execute(stmt)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        log.warning(f"Migration warning: {e}")
            log.info("Schema migration complete")

        if reset:
            log.warning("RESET mode: clearing agents, tasks, roles, cron_jobs...")
            await conn.execute("DELETE FROM goal_evaluations")
            await conn.execute("DELETE FROM agent_metrics")
            await conn.execute("DELETE FROM execution_logs")
            await conn.execute("DELETE FROM agent_skills")
            await conn.execute("DELETE FROM tasks")
            await conn.execute("DELETE FROM agents")
            await conn.execute("DELETE FROM roles")
            await conn.execute("DELETE FROM cron_jobs")

        # Insert default roles
        log.info("Seeding roles...")
        for role in DEFAULT_ROLES:
            await conn.execute(
                """
                INSERT INTO roles (name, description, permissions)
                VALUES ($1, $2, $3)
                ON CONFLICT (name) DO UPDATE
                  SET description = EXCLUDED.description,
                      permissions = EXCLUDED.permissions
                """,
                role["name"],
                role["description"],
                json.dumps(role["permissions"]),
            )
        log.info(f"  ✓ {len(DEFAULT_ROLES)} roles seeded")

        # Insert cron jobs
        log.info("Seeding cron jobs...")
        for job in DEFAULT_CRON_JOBS:
            await conn.execute(
                """
                INSERT INTO cron_jobs (name, description, schedule, handler_path, enabled)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (name) DO UPDATE
                  SET schedule = EXCLUDED.schedule,
                      handler_path = EXCLUDED.handler_path,
                      enabled = EXCLUDED.enabled,
                      updated_at = NOW()
                """,
                job["name"],
                job["description"],
                job["schedule"],
                job["handler_path"],
                job["enabled"],
            )
        log.info(f"  ✓ {len(DEFAULT_CRON_JOBS)} cron jobs seeded")

        # Load and insert agent souls
        log.info(f"Loading souls from {SOULS_DIR}...")
        soul_files = list(SOULS_DIR.rglob("*.soul.md")) if SOULS_DIR.exists() else []
        log.info(f"  Found {len(soul_files)} soul files")

        inserted = 0
        skipped = 0
        for soul_path in sorted(soul_files):
            soul = parse_soul_file(soul_path)
            if not soul:
                skipped += 1
                continue

            try:
                await conn.execute(
                    """
                    INSERT INTO agents (soul_id, name, role, team, status, avatar_color, 
                                        voice_id, system_prompt, capabilities, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10::jsonb)
                    ON CONFLICT (soul_id) DO UPDATE
                      SET name = EXCLUDED.name,
                          role = EXCLUDED.role,
                          team = EXCLUDED.team,
                          avatar_color = EXCLUDED.avatar_color,
                          voice_id = EXCLUDED.voice_id,
                          system_prompt = EXCLUDED.system_prompt,
                          capabilities = EXCLUDED.capabilities,
                          metadata = EXCLUDED.metadata,
                          updated_at = NOW()
                    """,
                    soul["soul_id"],
                    soul["name"],
                    soul["role"],
                    soul["team"],
                    soul["status"],
                    soul["avatar_color"],
                    soul["voice_id"],
                    soul["system_prompt"],
                    soul["capabilities"],
                    soul["metadata"],
                )
                log.info(f"  ✓ {soul['team']:5} | {soul['soul_id']}")
                inserted += 1
            except Exception as e:
                log.error(f"  ✗ {soul['soul_id']}: {e}")
                skipped += 1

        log.info(f"\nBootstrap complete: {inserted} agents inserted/updated, {skipped} skipped")

        # Verify counts
        agent_count = await conn.fetchval("SELECT COUNT(*) FROM agents")
        role_count = await conn.fetchval("SELECT COUNT(*) FROM roles")
        job_count = await conn.fetchval("SELECT COUNT(*) FROM cron_jobs")
        log.info(f"DB state: {agent_count} agents | {role_count} roles | {job_count} cron_jobs")

    await pool.close()


def main():
    parser = argparse.ArgumentParser(description="Bootstrap ARCHON-X agents into Supabase")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Try to build from parts
        host = os.environ.get("PG_HOST", "31.220.58.212")
        port = os.environ.get("PG_PORT", "5434")
        db = os.environ.get("PG_DATABASE", "second_brain")
        user = os.environ.get("PG_USER", "postgres")
        password = os.environ.get("PG_PASSWORD", "")
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    if not db_url or "PASSWORD" not in db_url.upper() and ":" not in db_url:
        log.error("DATABASE_URL not set. Export it or set PG_HOST/PG_PORT/PG_DATABASE/PG_USER/PG_PASSWORD")
        sys.exit(1)

    asyncio.run(run_bootstrap(db_url, reset=args.reset))


if __name__ == "__main__":
    main()
