-- Memory entries table — key/value model matching manager.rs db_upsert INSERT.
-- Replaced id/agent_id/content schema (mismatched) and removed pgvector dependency
-- (pgvector not in Cargo.toml; add as a separate migration when the dep is added).

CREATE TABLE IF NOT EXISTS memory_entries (
    key          TEXT        PRIMARY KEY,
    value        TEXT        NOT NULL,   -- JSON stored as text; matches sqlx .bind(&value_str)
    layer        TEXT        NOT NULL DEFAULT 'project_local',
    tags         TEXT[]      NOT NULL DEFAULT '{}',
    confidence   FLOAT       NOT NULL DEFAULT 1.0,
    access_count INTEGER     NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_layer ON memory_entries (layer);
CREATE INDEX IF NOT EXISTS idx_memory_tags  ON memory_entries USING GIN (tags);

-- Agent expertise — shares the same key/value schema (layer = 'team_shared')
-- Stored in memory_entries with the 'expertise' tag; separate table kept for
-- explicit querying and future indexing.
CREATE TABLE IF NOT EXISTS agent_expertise (
    key          TEXT        PRIMARY KEY,
    value        TEXT        NOT NULL,
    layer        TEXT        NOT NULL DEFAULT 'team_shared',
    tags         TEXT[]      NOT NULL DEFAULT '{}',
    confidence   FLOAT       NOT NULL DEFAULT 1.0,
    access_count INTEGER     NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expertise_tags ON agent_expertise USING GIN (tags);

-- Session memory table (session lifecycle tracking)
CREATE TABLE IF NOT EXISTS session_memory (
    session_id   TEXT        PRIMARY KEY,
    agent_id     TEXT        NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at     TIMESTAMPTZ,
    decisions    JSONB       NOT NULL DEFAULT '[]',
    tool_uses    JSONB       NOT NULL DEFAULT '[]',
    patterns     TEXT[]      NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_session_memory_agent_id ON session_memory (agent_id);
