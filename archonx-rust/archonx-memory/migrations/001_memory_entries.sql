-- Memory entries table — replaces Python file-based memory storage.
-- Schema matches MemoryManager::db_upsert (key/value model).

CREATE TABLE IF NOT EXISTS memory_entries (
    key          TEXT        PRIMARY KEY,
    value        TEXT        NOT NULL,
    layer        TEXT        NOT NULL DEFAULT 'project_local',
    tags         TEXT[]      NOT NULL DEFAULT '{}',
    confidence   DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    access_count INTEGER     NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_entries_layer ON memory_entries(layer);
CREATE INDEX IF NOT EXISTS idx_memory_entries_tags  ON memory_entries USING GIN(tags);

-- Agent expertise table
CREATE TABLE IF NOT EXISTS agent_expertise (
    agent_id     TEXT        PRIMARY KEY,
    domains      TEXT[]      NOT NULL DEFAULT '{}',
    tools        TEXT[]      NOT NULL DEFAULT '{}',
    task_count   INTEGER     NOT NULL DEFAULT 0,
    success_rate DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Session memory table
CREATE TABLE IF NOT EXISTS session_memory (
    session_id   TEXT        PRIMARY KEY,
    agent_id     TEXT        NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at     TIMESTAMPTZ,
    decisions    JSONB       NOT NULL DEFAULT '[]',
    tool_uses    JSONB       NOT NULL DEFAULT '[]',
    patterns     TEXT[]      NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_session_memory_agent_id ON session_memory(agent_id);
