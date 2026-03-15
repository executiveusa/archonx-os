# Open Brain + ARCHON-X Deployment Guide
## Coolify Deployment on Hostinger VPS (31.220.58.212)

**Status:** Ready for immediate deployment  
**Timeline:** 30 minutes to full integration  
**Downtime:** Zero (rolling deployment)  
**Rollback:** 5 minutes (previous container)

---

## PRE-DEPLOYMENT CHECKLIST

- [x] Supabase running @ 31.220.58.212:5434 (verified)
- [x] PostgreSQL + pgvector healthy
- [x] `second_brain` database created with schema
- [x] MCP server code ready (`open_brain_mcp_server.py`)
- [x] Agent integration code ready (`archonx_open_brain_integration.py`)
- [x] All ARCHON-X agents can be updated (Pauli, Synthia, Darya, Devika, Lightning)
- [ ] **REQUIRED:** Update `.env` files with Open Brain credentials
- [ ] **REQUIRED:** Deploy MCP server to Coolify
- [ ] **REQUIRED:** Update ARCHON-X agents to use Open Brain client
- [ ] **REQUIRED:** Wire MCP server to Claude Desktop config

---

## STEP 1: Prepare Environment Variables

SSH into VPS and create `.env` file for Open Brain services:

```bash
ssh -i ~/.ssh/bambu_key root@31.220.58.212

# Create environment file
cat > /opt/archonx/open_brain.env << 'EOF'
# Open Brain Database
OPEN_BRAIN_HOST=31.220.58.212
OPEN_BRAIN_PORT=5434
OPEN_BRAIN_DB=second_brain
OPEN_BRAIN_USER=postgres
OPEN_BRAIN_PASSWORD=072090156d28a9df6502d94083e47990

# Supabase API (for REST client)
SUPABASE_URL=http://31.220.58.212:8001
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzcyNzc2NjczLCJleHAiOjE5MzA0NTY2NzN9.rl1mc-GgpG6nQArbEfFAKOcMvzL7rrgzPFT-LlCiCy4
SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3NzI3NzY2NzMsImV4cCI6MTkzMDQ1NjY3M30.ns9wbGi2xeS2zbZ1foj6fj4NSa4JxSmJKAedmlShF3w

# Anthropic API
ANTHROPIC_API_KEY=sk-[your-api-key]

# Logging
LOG_LEVEL=INFO
EOF

chmod 600 /opt/archonx/open_brain.env
```

---

## STEP 2: Deploy MCP Server to Coolify

### Option A: Docker Container (Recommended)

Create `Dockerfile` for MCP server:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    asyncpg==0.29.0 \
    anthropic==0.25.0 \
    python-dotenv==1.0.0

# Copy MCP server code
COPY open_brain_mcp_server.py /app/

# Set environment
ENV PYTHONUNBUFFERED=1

# Run server in stdio mode (for MCP clients)
CMD ["python", "open_brain_mcp_server.py", "stdio"]
```

Deploy to Coolify:

```bash
cd /opt/archonx

# Build image
docker build -f Dockerfile.mcp -t archonx/open-brain-mcp:latest .

# Tag for registry
docker tag archonx/open-brain-mcp:latest 31.220.58.212:5000/archonx/open-brain-mcp:latest

# Deploy via Coolify (if using Docker Hub or private registry)
# Or use docker-compose:

cat > docker-compose.open-brain.yml << 'EOF'
version: '3.8'

services:
  open-brain-mcp:
    image: archonx/open-brain-mcp:latest
    container_name: archonx-open-brain-mcp
    restart: always
    env_file:
      - open_brain.env
    networks:
      - archonx-network
    labels:
      - "com.coolify.managed=true"

networks:
  archonx-network:
    external: true
EOF

# Start service
docker compose -f docker-compose.open-brain.yml up -d
```

### Option B: Python Service (Direct)

```bash
# Install dependencies
pip install asyncpg anthropic python-dotenv

# Create systemd service
cat > /etc/systemd/system/open-brain-mcp.service << 'EOF'
[Unit]
Description=ARCHON-X Open Brain MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/archonx
EnvironmentFile=/opt/archonx/open_brain.env
ExecStart=/usr/bin/python3 /opt/archonx/open_brain_mcp_server.py stdio
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable open-brain-mcp
systemctl start open-brain-mcp
systemctl status open-brain-mcp
```

### Verify Deployment

```bash
# Check service health
systemctl status open-brain-mcp

# Check logs
journalctl -u open-brain-mcp -f

# Test connection to database
docker exec archonx-open-brain-mcp python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://postgres:PASS@31.220.58.212:5434/second_brain')
    result = await conn.fetchval('SELECT 1')
    print(f'✅ Connected: {result}')
    await conn.close()
asyncio.run(test())
"
```

---

## STEP 3: Update ARCHON-X Agents

Update each agent to use Open Brain client:

### For Pauli (pauli_brain_persona.py)

```python
# Add at top of file
from archonx_open_brain_integration import PauliBrainWithMemory, OpenBrainAgentClient

class PauliBrainPersona:
    """Updated Pauli with Open Brain integration"""
    
    def __init__(self):
        self.pauli = PauliBrainWithMemory()  # New: with memory
        self.expertise = {}
    
    async def initialize(self):
        await self.pauli.initialize()  # Connect to Open Brain
    
    async def think(self, task: str, category: str = "ARCHON-X OS"):
        """Execute task with full context from Open Brain"""
        result = await self.pauli.analyze(task, category=category)
        return result

# Usage:
# pauli = PauliBrainPersona()
# await pauli.initialize()
# result = await pauli.think("Analyze deployment status")
```

### For Synthia (synthia_persona.py)

```python
from archonx_open_brain_integration import SynthiaWithMemory

class SynthiaPersona:
    """Updated Synthia with Open Brain integration"""
    
    def __init__(self):
        self.synthia = SynthiaWithMemory()
    
    async def initialize(self):
        await self.synthia.initialize()
    
    async def synthesize(self, task: str, category: str = "Strategy"):
        """Synthesize with full context"""
        result = await self.synthia.synthesize(
            task,
            output_format="narrative",
            category=category
        )
        return result
```

### For Guardian Fleet Coordinator

```python
from archonx_open_brain_integration import GuardianFleetCoordinator

class GuardianFleetWithMemory:
    """Updated Guardian Fleet with shared Open Brain memory"""
    
    def __init__(self):
        self.coordinator = GuardianFleetCoordinator()
    
    async def initialize(self):
        await self.coordinator.initialize()
    
    async def execute_mission(self, project: str):
        """All guardians coordinate through shared memory"""
        coordination = await self.coordinator.coordinate_project(project)
        # All guardians now have access to same context from Open Brain
        return coordination
```

### Deploy Updated Agents

```bash
# Update code in repository
cd /opt/archonx/archonx/agents

# Commit changes
git add pauli_brain_persona.py synthia_persona.py archon_x_guardian_fleet.py
git commit -m "integrate Open Brain memory system for agents"
git push

# Coolify will auto-deploy on push (if configured)
# Or manually trigger:
curl -X POST http://31.220.58.212:8000/api/deploy/archonx-os
```

---

## STEP 4: Wire MCP Server to Claude Desktop

### On Your Local Machine (Mac/Windows)

Update Claude Desktop config:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `C:\Users\[YourUser]\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "python3",
      "args": ["/opt/archonx/open_brain_mcp_server.py"],
      "env": {
        "OPEN_BRAIN_HOST": "31.220.58.212",
        "OPEN_BRAIN_PORT": "5434",
        "OPEN_BRAIN_DB": "second_brain",
        "OPEN_BRAIN_USER": "postgres",
        "OPEN_BRAIN_PASSWORD": "072090156d28a9df6502d94083e47990",
        "ANTHROPIC_API_KEY": "sk-[your-key]"
      }
    }
  }
}
```

**Or** use SSH tunnel if you want to keep DB private:

```bash
# Create tunnel on local machine
ssh -i ~/.ssh/bambu_key -L 5434:31.220.58.212:5434 root@31.220.58.212 -N

# Then update config to use localhost:5434
```

**Restart Claude Desktop** and test:

```
User: "Search my Open Brain for decisions about Auth0"

Claude should respond with:
✅ Found 3 relevant memories from Open Brain
- "Auth0 migration decision"
- "Budget constraints for rollout"
- "Team feedback on implementation"
```

---

## STEP 5: Run Integration Tests

### Test 1: MCP Server Health

```bash
# SSH into VPS
ssh -i ~/.ssh/bambu_key root@31.220.58.212

# Check service
curl -s http://31.220.58.212:5434/ || echo "MCP server listening on 5434 (not HTTP)"

# Check Docker logs
docker logs -f archonx-open-brain-mcp | tail -20
```

Expected output:
```
2026-03-06T20:30:00 - open-brain-mcp - INFO - Connected to PostgreSQL @ 31.220.58.212:5434/second_brain
```

### Test 2: Agent Integration

Create test script on VPS:

```python
# /opt/archonx/test_open_brain_agents.py
import asyncio
from archonx_open_brain_integration import PauliBrainWithMemory, SynthiaWithMemory

async def test():
    # Test Pauli
    print("Testing Pauli...")
    pauli = PauliBrainWithMemory()
    await pauli.initialize()
    
    analysis = await pauli.analyze(
        "What is our current deployment status?",
        category="ARCHON-X OS"
    )
    print(f"✅ Pauli analysis: {analysis['analysis'][:100]}...")
    await pauli.open_brain.disconnect()
    
    # Test Synthia
    print("\nTesting Synthia...")
    synthia = SynthiaWithMemory()
    await synthia.initialize()
    
    strategy = await synthia.synthesize(
        "Create a client onboarding plan",
        category="Akash Engine"
    )
    print(f"✅ Synthia synthesis: {strategy['synthesis'][:100]}...")
    await synthia.open_brain.disconnect()

asyncio.run(test())
```

Run test:
```bash
cd /opt/archonx
python test_open_brain_agents.py
```

### Test 3: Claude Integration

In Claude Desktop:

```
Ask me 5 semantic search queries about ARCHON-X from Open Brain, 
then summarize what you found.
```

Expected flow:
```
Claude: "Searching Open Brain for ARCHON-X context..."
-> MCP tool call: semantic_search(query="ARCHON-X deployment status")
-> MCP tool call: semantic_search(query="Deployment pending items")
-> MCP tool call: semantic_search(query="Guardian Fleet coordination")
-> MCP tool call: semantic_search(query="Agent initialization")
-> MCP tool call: semantic_search(query="System health checks")

Claude: "Based on Open Brain searches, here's what I found:
1. ARCHON-X OS is production-ready pending 2 config items
2. coolify.app_uuid and coolify.base_url need to be set
3. All 15 tests passing with zero stubs
4. Agents are waiting for these config updates before final deployment
5. Guardian Fleet is coordinated through shared memory..."
```

---

## STEP 6: Production Validation

### Checklist Before Going Live

- [ ] MCP server running and healthy
- [ ] PostgreSQL connection pool working (2-10 connections)
- [ ] Claude Desktop can query Open Brain (all 7 MCP tools working)
- [ ] Pauli can analyze with context
- [ ] Synthia can synthesize with context
- [ ] Guardian Fleet coordinator active
- [ ] At least 1 memory stored from agent execution
- [ ] Semantic search finds stored memories
- [ ] Zero errors in logs (last 10 minutes)
- [ ] Database backups configured (Supabase handles this)
- [ ] Monitoring alerts set up (optional but recommended)

### Validation Script

```bash
# /opt/archonx/validate_open_brain.sh

echo "🔍 Validating Open Brain Deployment..."
echo ""

# 1. Check service status
echo "1. Service Status:"
systemctl status open-brain-mcp --no-pager | head -3

# 2. Check database connection
echo ""
echo "2. Database Connection:"
psql -h 31.220.58.212 -p 5434 -U postgres -d second_brain -c "SELECT COUNT(*) as memories FROM memories;" || echo "❌ Connection failed"

# 3. Check MCP tools available
echo ""
echo "3. MCP Tools:"
python3 -c "
import sys
sys.path.insert(0, '/opt/archonx')
from open_brain_mcp_server import create_server
import asyncio
async def check():
    server = create_server()
    tools = await server.list_tools()
    print(f'✅ {len(tools)} MCP tools available')
    for tool in tools:
        print(f'   - {tool.name}')
asyncio.run(check())
"

# 4. Check logs for errors
echo ""
echo "4. Recent Logs:"
journalctl -u open-brain-mcp -n 5 --no-pager | grep -i error || echo "✅ No errors found"

echo ""
echo "✅ Validation Complete"
```

Run validation:
```bash
bash /opt/archonx/validate_open_brain.sh
```

---

## MONITORING & MAINTENANCE

### Daily Health Checks

```bash
# Monitor service (runs every 5 minutes via cron)
cat > /opt/archonx/monitor_open_brain.sh << 'EOF'
#!/bin/bash

# Check if service is running
if ! systemctl is-active --quiet open-brain-mcp; then
    echo "❌ Open Brain MCP service is DOWN"
    systemctl restart open-brain-mcp
    # Send alert
    curl -X POST https://hooks.slack.com/services/[your-webhook] \
      -d '{"text":"Open Brain MCP restarted on 31.220.58.212"}'
fi

# Check database
psql -h 31.220.58.212 -p 5434 -U postgres -d second_brain -c "SELECT 1" 2>/dev/null || {
    echo "❌ Database connection failed"
    # Send alert
}

# Check recent errors
ERROR_COUNT=$(journalctl -u open-brain-mcp -S "5 min ago" | grep -c "ERROR")
if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ $ERROR_COUNT errors in last 5 minutes"
fi
EOF

chmod +x /opt/archonx/monitor_open_brain.sh

# Add to crontab
crontab -e
# Add line: */5 * * * * /opt/archonx/monitor_open_brain.sh
```

### Log Rotation

```bash
# Configure logrotate for MCP service logs
cat > /etc/logrotate.d/open-brain-mcp << 'EOF'
/var/log/open-brain-mcp.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### Backup Open Brain Data

```bash
# Weekly backup of second_brain database
cat > /opt/archonx/backup_open_brain.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/open-brain"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Dump database
pg_dump -h 31.220.58.212 -p 5434 -U postgres -d second_brain > $BACKUP_DIR/second_brain_$TIMESTAMP.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "✅ Backup completed: second_brain_$TIMESTAMP.sql.gz"
EOF

chmod +x /opt/archonx/backup_open_brain.sh

# Run weekly via crontab
crontab -e
# Add: 0 2 * * 0 /opt/archonx/backup_open_brain.sh
```

---

## TROUBLESHOOTING

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| MCP server won't start | `journalctl -u open-brain-mcp -e` | Check env vars, DB connection, Python dependencies |
| Agents can't connect to Open Brain | `psql -h 31.220.58.212 -p 5434 -U postgres` | Verify network connectivity, firewall rules |
| Claude can't find MCP tools | Restart Claude Desktop, check config syntax | Verify JSON formatting in `claude_desktop_config.json` |
| Slow semantic search | Too many vectors? | Add HNSW indexes, check query plan with EXPLAIN |
| Memory table growing too large | Archival strategy needed | Implement TTL or archive old memories to cold storage |

---

## ROLLBACK PROCEDURE

If something goes wrong:

```bash
# Stop Open Brain MCP
systemctl stop open-brain-mcp

# Revert agent changes
cd /opt/archonx
git checkout -- archonx/agents/

# Restart ARCHON-X
systemctl restart archonx-os

# Keep Open Brain database safe (it has all the memories)
# Just update agents to not use Open Brain client
```

Rollback time: ~5 minutes. Data is never lost.

---

## SUCCESS METRICS

After deployment, you should see:

✅ **Day 1:**
- All 7 MCP tools working in Claude
- Agents can query Open Brain for context
- At least 10 memories captured

✅ **Week 1:**
- 100+ memories in Open Brain
- Semantic search finding relevant context
- Agents executing with 50% less re-explanation

✅ **Month 1:**
- 500+ memories
- Agent IQ improvement measurable
- Full knowledge graph built out
- Career-gap advantage: 6 months of context vs peers

---

## NEXT STEPS

1. **Deploy MCP server** (Step 1-2): 10 minutes
2. **Update agents** (Step 3): 5 minutes
3. **Test integration** (Step 5): 10 minutes
4. **Go live** (Step 6): 5 minutes validation

**Total: ~30 minutes to full production**

Once live, start capturing daily:
- Decisions (Pauli + Synthia log these automatically)
- Project updates (via Slack or manual entry)
- Meeting notes (auto-indexed with full-text search)

The compound advantage starts immediately. Every thought you capture makes the next agent execution smarter.

---

**Status:** Ready to deploy  
**Contact:** For issues, check logs or reach out to development team  
**Backup:** Open Brain data is your knowledge base. Keep it safe.

**One system. All agents. Full context. Zero vendor lock-in.**
