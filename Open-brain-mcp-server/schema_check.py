#!/usr/bin/env python3
"""
Database schema verification script for Open Brain MCP Server
Ensures all required pgvector tables exist on the Supabase PostgreSQL instance
"""

import asyncio
import os
import sys
import logging
from typing import Dict, List

import asyncpg
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Expected tables schema
TABLES = {
    "thoughts": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("content", "TEXT NOT NULL"),
            ("embedding", "vector(1536)"),
            ("memory_type", "VARCHAR(50)"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
    "entities": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("entity_name", "VARCHAR(255) NOT NULL"),
            ("entity_type", "VARCHAR(50)"),
            ("description", "TEXT"),
            ("embedding", "vector(1536)"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
    "github_repos": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("repo_url", "VARCHAR(255) NOT NULL"),
            ("repo_name", "VARCHAR(255)"),
            ("description", "TEXT"),
            ("embedding", "vector(1536)"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
    "memories": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("thought_id", "BIGINT"),
            ("memory_summary", "TEXT"),
            ("importance_score", "FLOAT DEFAULT 0.5"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
    "agent_telemetry": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("event_type", "VARCHAR(100)"),
            ("tokens_saved", "INT DEFAULT 0"),
            ("tokens_used", "INT DEFAULT 0"),
            ("action", "VARCHAR(255)"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
    "lightning_events": {
        "columns": [
            ("id", "BIGSERIAL PRIMARY KEY"),
            ("agent_id", "VARCHAR(255) NOT NULL"),
            ("event_type", "VARCHAR(100) NOT NULL"),
            ("event_data", "JSONB"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("metadata", "JSONB"),
        ]
    },
}


async def connect_database() -> asyncpg.Connection:
    """Establish connection to PostgreSQL database"""
    try:
        conn = await asyncpg.connect(
            host=os.getenv("SUPABASE_HOST", "localhost"),
            port=int(os.getenv("SUPABASE_PORT", 5434)),
            database=os.getenv("SUPABASE_DB", "second_brain"),
            user=os.getenv("SUPABASE_USER", "postgres"),
            password=os.getenv("SUPABASE_PASSWORD", ""),
            timeout=10
        )
        logger.info(f"✓ Connected to {os.getenv('SUPABASE_HOST')}:{os.getenv('SUPABASE_PORT')}")
        return conn
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise


async def enable_vector_extension(conn: asyncpg.Connection) -> bool:
    """Enable pgvector extension if not already enabled"""
    try:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("✓ pgvector extension enabled")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to enable pgvector: {e}")
        return False


async def check_table_exists(conn: asyncpg.Connection, table_name: str) -> bool:
    """Check if a table exists in the database"""
    try:
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = $1
            );
        """, table_name)
        return result
    except Exception as e:
        logger.error(f"✗ Error checking table {table_name}: {e}")
        return False


async def create_table(conn: asyncpg.Connection, table_name: str, columns: List) -> bool:
    """Create a table with specified columns"""
    try:
        column_defs = ", ".join([f"{name} {dtype}" for name, dtype in columns])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
        await conn.execute(query)
        logger.info(f"✓ Table '{table_name}' created/verified")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create table {table_name}: {e}")
        return False


async def create_indexes(conn: asyncpg.Connection) -> bool:
    """Create performance indexes"""
    try:
        indexes = [
            """CREATE INDEX IF NOT EXISTS idx_thoughts_agent_created
               ON thoughts(agent_id, created_at DESC);""",
            """CREATE INDEX IF NOT EXISTS idx_thoughts_embedding
               ON thoughts USING ivfflat (embedding vector_cosine_ops);""",
            """CREATE INDEX IF NOT EXISTS idx_entities_agent
               ON entities(agent_id);""",
            """CREATE INDEX IF NOT EXISTS idx_agent_telemetry_event
               ON agent_telemetry(agent_id, event_type, created_at DESC);""",
        ]

        for index_query in indexes:
            await conn.execute(index_query)

        logger.info("✓ Indexes created/verified")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create indexes: {e}")
        return False


async def verify_schema() -> int:
    """Main schema verification routine"""
    logger.info("=" * 60)
    logger.info("Open Brain MCP Server - Database Schema Verification")
    logger.info("=" * 60)

    # Connect to database
    try:
        conn = await connect_database()
    except Exception:
        logger.error("Failed to connect to database. Check .env configuration.")
        return 1

    # Enable vector extension
    if not await enable_vector_extension(conn):
        logger.warning("Could not enable pgvector, continuing...")

    # Verify all tables
    results = {}
    for table_name, config in TABLES.items():
        logger.info(f"\nVerifying table: {table_name}")

        # Check if exists
        exists = await check_table_exists(conn, table_name)

        if exists:
            logger.info(f"✓ Table '{table_name}' exists")
            results[table_name] = "✓"
        else:
            logger.info(f"Creating table: {table_name}")
            success = await create_table(conn, table_name, config["columns"])
            results[table_name] = "✓" if success else "✗"

    # Create indexes
    await create_indexes(conn)

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Schema Verification Summary")
    logger.info("=" * 60)

    all_passed = True
    for table_name, status in results.items():
        logger.info(f"{status} {table_name}")
        if status == "✗":
            all_passed = False

    # Check table counts
    logger.info("\nTable Row Counts:")
    for table_name in TABLES.keys():
        try:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name};")
            logger.info(f"  {table_name}: {count} rows")
        except Exception as e:
            logger.warning(f"  {table_name}: Error counting rows - {e}")

    await conn.close()

    if all_passed:
        logger.info("\n✓ All schema checks passed!")
        return 0
    else:
        logger.error("\n✗ Some schema checks failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(verify_schema())
    sys.exit(exit_code)
