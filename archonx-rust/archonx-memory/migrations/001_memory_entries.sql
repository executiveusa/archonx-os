-- Memory entries table — replaces Python file-based memory storage.
-- Requires pgvector extension for semantic search embeddings.

-- Enable pgvector (must be installed via CREATE EXTENSION if not already)
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memory_entries (
    id           TEXT        PRIMARY KEY,
    agent_id     TEXT        NOT NULL,
    content      TEXT        NOT NULL,
    tags         TEXT[]      NOT NULL DEFAULT '{}',
    -- Optional pgvector embedding (1536 dims for OpenAI text-embedding-3-small)
    -- Nullable so the table works without pgvector installed.
    embedding    vector(1536),
    layer        TEXT        NOT NULL DEFAULT 'project_local',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_entries_agent_id ON memory_entries(agent_id);
CREATE INDEX IF NOT EXISTS idx_memory_entries_layer    ON memory_entries(layer);
CREATE INDEX IF NOT EXISTS idx_memory_entries_tags     ON memory_entries USING GIN(tags);

-- Semantic search index (cosine distance) — only if pgvector available
-- CREATE INDEX IF NOT EXISTS idx_memory_entries_embedding
--     ON memory_entries
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

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
