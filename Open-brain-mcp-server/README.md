# Open Brain MCP Server

Shared pgvector-backed memory layer for ArchonX agents. Implements token-efficient code retrieval via jcodemunch integration.

## Architecture

- **Database**: PostgreSQL with pgvector extension (Supabase)
- **Memory Types**: Thoughts, Entities, Repositories, Telemetry Events
- **Token Efficiency**: jcodemunch symbol-level retrieval (80-99% token savings)
- **Protocol**: Model Context Protocol (MCP) for agent integration

## Directory Structure

```
Open-brain-mcp-server/
├── .env                      # Configuration (secrets from vault)
├── open_brain_mcp_server.py # Main MCP server
├── schema_check.py           # Database schema verification
├── requirements.txt          # Python dependencies
├── start_open_brain.sh       # Linux/Mac startup script
├── start_open_brain.bat      # Windows startup script
├── tests/
│   ├── __init__.py
│   └── test_open_brain.py    # Comprehensive test suite
└── README.md                 # This file
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- Network access to Supabase instance

### 2. Configuration

Copy environment variables to `.env`:

```bash
# .env
SUPABASE_HOST=31.220.58.212
SUPABASE_PORT=5434
SUPABASE_DB=second_brain
SUPABASE_USER=postgres
SUPABASE_PASSWORD=<from vault>
SUPABASE_URL=http://31.220.58.212:8001
SUPABASE_KEY=<from vault>
SERVICE_ROLE_KEY=<from vault>
ANTHROPIC_API_KEY=<from vault>
JCODEMUNCH_ENABLED=true
JCODEMUNCH_INDEX=.jcodemunch/index.db
```

### 3. Start Server

**Linux/Mac:**
```bash
./start_open_brain.sh
```

**Windows:**
```cmd
start_open_brain.bat
```

This will:
1. Validate `.env` file
2. Install dependencies
3. Verify database schema
4. Start the MCP server

## Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `thoughts` | Agent memories/notes | id, agent_id, content, embedding, memory_type |
| `entities` | People, places, concepts | id, agent_id, entity_name, entity_type |
| `github_repos` | Linked repositories | id, agent_id, repo_url, repo_name |
| `memories` | Linked memory summaries | id, agent_id, thought_id, importance_score |
| `agent_telemetry` | Event tracking & token logs | id, agent_id, event_type, tokens_saved |
| `lightning_events` | Agent lifecycle events | id, agent_id, event_type, event_data |

### Indexes

- `thoughts(agent_id, created_at DESC)` - Recent memory lookup
- `thoughts(embedding)` - Vector similarity search
- `entities(agent_id)` - Entity filtering
- `agent_telemetry(agent_id, event_type, created_at)` - Event tracking

## MCP Tools

### store_memory

Store a memory/thought with optional embedding.

```json
{
  "agent_id": "agent_1",
  "content": "Meeting notes from standup",
  "memory_type": "meeting",
  "metadata": {"attendees": ["alice", "bob"]}
}
```

Memory types: `note`, `decision`, `insight`, `meeting`, `person`, `project`

### search_memories

Search memories using vector similarity (requires embedding computation).

```json
{
  "agent_id": "agent_1",
  "query": "recent project updates",
  "limit": 5
}
```

### list_recent

List most recent memories, optionally filtered by agent.

```json
{
  "agent_id": "agent_1",
  "limit": 10
}
```

### get_stats

Get aggregate statistics across memory tables.

```json
{
  "agent_id": "agent_1"
}
```

### store_entity

Store an entity (person, place, concept).

```json
{
  "agent_id": "agent_1",
  "entity_name": "Alice Chen",
  "entity_type": "person",
  "description": "Senior engineer, project lead"
}
```

### link_repo

Link a GitHub repository to agent memory.

```json
{
  "agent_id": "agent_1",
  "repo_url": "https://github.com/example/repo",
  "repo_name": "example-repo",
  "description": "Main project repository"
}
```

## Agent Protocol

All agents using Open Brain MUST follow this protocol:

### Before Starting Task
```python
# Retrieve relevant context from memory
memories = await call_tool("search_memories", {
    "agent_id": "your_agent_id",
    "query": "task context",
    "limit": 5
})
```

### After Completing Task
```python
# Store completion result and insights
await call_tool("store_memory", {
    "agent_id": "your_agent_id",
    "content": "Task completion notes",
    "memory_type": "decision",
    "metadata": {"status": "completed"}
})
```

### Logging Events
```python
# Log significant events for telemetry
await call_tool("log_event", {
    "agent_id": "your_agent_id",
    "event_type": "task_complete",
    "event_data": {"duration": 125}
})
```

## Token Efficiency (jcodemunch)

When enabled, jcodemunch reduces code-reading tokens by 80-99%:

- **Symbol retrieval** instead of full file reads
- **Byte-offset seeking** for efficient navigation
- **Token savings** logged to `agent_telemetry` table

Environment variables:
```
JCODEMUNCH_ENABLED=true
JCODEMUNCH_INDEX=.jcodemunch/index.db
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_open_brain.py -v

# Run specific test class
pytest tests/test_open_brain.py::TestDatabaseConnection -v

# Run with coverage
pytest tests/test_open_brain.py --cov=open_brain_mcp_server
```

### Test Coverage

- ✓ Database connectivity
- ✓ Schema completeness
- ✓ Memory CRUD operations
- ✓ Entity storage
- ✓ Repository linking
- ✓ Telemetry logging
- ✓ Data integrity
- ✓ pgvector extension

## Troubleshooting

### Database Connection Failed

**Check:**
1. PostgreSQL server is running
2. `.env` contains correct credentials
3. Network access to SUPABASE_HOST is available
4. Firewall not blocking port 5434

**Test:**
```bash
psql -h 31.220.58.212 -U postgres -d second_brain
```

### Missing pgvector Extension

```bash
# Connect to database and enable
psql -h 31.220.58.212 -U postgres -d second_brain
CREATE EXTENSION IF NOT EXISTS vector;
```

### Schema Check Failing

Run `schema_check.py` directly for detailed output:
```bash
python schema_check.py
```

### Tests Failing

Ensure:
1. Database is accessible
2. All tables exist (run `schema_check.py`)
3. `.env` is properly configured
4. Dependencies are installed: `pip install -r requirements.txt`

## Development

### Adding a New MCP Tool

1. **Define the tool** in `open_brain_mcp_server.py`:

```python
mcp_server.define_tool(
    Tool(
        name="my_tool",
        description="Tool description",
        inputSchema={
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    )
)
```

2. **Implement the handler**:

```python
async def my_tool(args: dict) -> TextContent:
    # Implementation
    return TextContent(type="text", text=json.dumps(result))
```

3. **Add to tool router** in `handle_call_tool()`.

4. **Add tests** in `tests/test_open_brain.py`.

## Performance Tuning

### Connection Pool Sizing

Adjust in `OpenBrainDB.connect()`:
```python
self.pool = await asyncpg.create_pool(
    ...,
    min_size=2,      # Minimum connections
    max_size=10,     # Maximum connections
)
```

### Vector Search Performance

Tune the IVFFlat index:
```sql
CREATE INDEX ON thoughts
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Production Deployment

1. Set up PostgreSQL with pgvector on production server
2. Use environment variables from secure vault
3. Enable connection pooling
4. Configure logging level to INFO
5. Run schema_check.py on startup
6. Monitor agent_telemetry table for anomalies

## Integration with ArchonX

Add to `archonx-config.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "python",
      "args": ["/path/to/open_brain_mcp_server.py"],
      "env": {
        "SUPABASE_HOST": "${SUPABASE_HOST}",
        "SUPABASE_PORT": "${SUPABASE_PORT}",
        "SUPABASE_DB": "${SUPABASE_DB}",
        "SUPABASE_USER": "${SUPABASE_USER}",
        "SUPABASE_PASSWORD": "${SUPABASE_PASSWORD}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "JCODEMUNCH_ENABLED": "true"
      }
    }
  }
}
```

## License

Part of ArchonX OS - Copyright 2024+

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test suite for usage examples
3. Check database schema with `schema_check.py`
4. Enable debug logging: `LOG_LEVEL=DEBUG`
