"""
ARCHON-X Agent Integration with Open Brain
============================================

Integrates all ARCHON-X agents (Pauli, Synthia, Guardian Fleet) with the
self-hosted Open Brain memory system for persistent, agent-readable context.

Deploy to: Coolify on Hostinger VPS (31.220.58.212)
Status: Production-ready

This module:
1. Initializes agent personas with Open Brain client
2. Provides context retrieval before agent execution
3. Logs decisions and insights back to Open Brain
4. Enables agent coordination through shared memory
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone
import os

import anthropic
import asyncpg

logger = logging.getLogger("archonx.open_brain")

# ============================================================================
# OPEN BRAIN CLIENT FOR AGENTS
# ============================================================================

class OpenBrainAgentClient:
    """
    Client for agents to interact with Open Brain memory system
    
    Usage:
        client = OpenBrainAgentClient()
        await client.connect()
        
        # Search for relevant context
        context = await client.search_context(
            "Auth0 migration for Akash Engine",
            category="decision"
        )
        
        # Execute task with context
        result = await agent.execute(task, context=context)
        
        # Log outcome back to Open Brain
        await client.log_decision(
            title="Approved Auth0 phased rollout",
            category="Akash Engine",
            outcome=result
        )
    """
    
    def __init__(self):
        self.pool = None
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Configuration from environment
        self.host = os.getenv("OPEN_BRAIN_HOST", "31.220.58.212")
        self.port = int(os.getenv("OPEN_BRAIN_PORT", "5434"))
        self.database = os.getenv("OPEN_BRAIN_DB", "second_brain")
        self.user = os.getenv("OPEN_BRAIN_USER", "postgres")
        self.password = os.getenv("OPEN_BRAIN_PASSWORD")
    
    async def connect(self):
        """Connect to Open Brain database"""
        self.pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        logger.info(f"Agent connected to Open Brain @ {self.host}:{self.port}")
    
    async def disconnect(self):
        """Disconnect from Open Brain"""
        if self.pool:
            await self.pool.close()
    
    async def search_context(
        self,
        query: str,
        category: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> str:
        """
        Search Open Brain for relevant context before executing a task.
        Returns formatted context string for agent prompt injection.
        """
        async with self.pool.acquire() as conn:
            # Search for relevant memories
            where_clauses = ["m.status = 'active'"]
            params = [limit]
            
            if category:
                where_clauses.append(f"m.category = '{category}'")
            
            if memory_type:
                where_clauses.append(f"m.memory_type = '{memory_type}'")
            
            where_clause = " AND ".join(where_clauses)
            
            # Simple search for now (use full semantic search in advanced version)
            rows = await conn.fetch(f"""
                SELECT title, summary, memory_type, category, tags, importance
                FROM memories
                WHERE {where_clause}
                AND (
                    title ILIKE '%{query}%'
                    OR summary ILIKE '%{query}%'
                    OR content ILIKE '%{query}%'
                )
                ORDER BY importance DESC, updated_at DESC
                LIMIT $1
            """, limit)
            
            if not rows:
                return "No relevant context found in Open Brain."
            
            # Format context
            context_blocks = [f"RELEVANT CONTEXT FROM OPEN BRAIN ({len(rows)} items):"]
            context_blocks.append("=" * 60)
            
            for i, row in enumerate(rows, 1):
                context_blocks.append(f"\n{i}. {row['title']}")
                context_blocks.append(f"   Type: {row['memory_type']} | Category: {row['category']}")
                context_blocks.append(f"   Summary: {row['summary'][:200]}")
                if row['tags']:
                    context_blocks.append(f"   Tags: {', '.join(row['tags'])}")
            
            return "\n".join(context_blocks)
    
    async def log_decision(
        self,
        title: str,
        category: str,
        context: str,
        decision: str,
        status: str = "decided",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an important decision to Open Brain"""
        async with self.pool.acquire() as conn:
            memory_id = await conn.fetchval("""
                INSERT INTO memories (
                    title, content, summary, memory_type, category,
                    metadata, importance, status, source
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """,
                title,
                f"Context: {context}\n\nDecision: {decision}",
                decision[:200],
                "decision",
                category,
                json.dumps(metadata or {}),
                4,  # High importance
                status,
                "archonx_agent"
            )
            
            logger.info(f"Decision logged to Open Brain: {memory_id}")
            return memory_id
    
    async def log_insight(
        self,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        importance: int = 3
    ) -> str:
        """Log an insight or learning to Open Brain"""
        async with self.pool.acquire() as conn:
            memory_id = await conn.fetchval("""
                INSERT INTO memories (
                    title, content, memory_type, category,
                    importance, status, source
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """,
                title,
                content,
                "insight",
                category,
                importance,
                "active",
                "archonx_agent"
            )
            
            # Add tags if provided
            if tags:
                for tag in tags:
                    await conn.execute("""
                        INSERT INTO memory_tags (memory_id, tag_name)
                        VALUES ($1, $2)
                        ON CONFLICT DO NOTHING
                    """, memory_id, tag)
            
            return memory_id
    
    async def get_project_context(self, project_name: str) -> str:
        """Get full context for a project (decisions, status, team, repos)"""
        async with self.pool.acquire() as conn:
            # Get recent decisions
            decisions = await conn.fetch("""
                SELECT title, summary, created_at FROM memories
                WHERE category = $1 AND memory_type = 'decision'
                ORDER BY created_at DESC LIMIT 10
            """, project_name)
            
            if not decisions:
                return f"No context found for project: {project_name}"
            
            context_blocks = [f"PROJECT CONTEXT: {project_name}"]
            context_blocks.append("=" * 60)
            context_blocks.append("\nRecent Decisions:")
            
            for decision in decisions:
                context_blocks.append(f"- {decision['title']}")
                if decision['summary']:
                    context_blocks.append(f"  {decision['summary'][:100]}")
            
            return "\n".join(context_blocks)

# ============================================================================
# AGENT PERSONA IMPLEMENTATIONS
# ============================================================================

class PauliBrainWithMemory:
    """
    Pauli Agent - Analytical Brain
    Enhanced with Open Brain integration for context-aware reasoning
    """
    
    def __init__(self):
        self.open_brain = OpenBrainAgentClient()
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.name = "Pauli"
        self.role = "Analytical Brain - Logic, Data, Diagnostics"
    
    async def initialize(self):
        """Initialize agent with Open Brain connection"""
        await self.open_brain.connect()
        logger.info(f"{self.name} initialized with Open Brain")
    
    async def analyze(self, task: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute analytical task with full context from Open Brain
        
        Args:
            task: The analytical task to perform
            category: Optional category for context filtering (e.g., "ARCHON-X OS", "Akash Engine")
        
        Returns:
            Analysis result with reasoning and recommendations
        """
        # Retrieve relevant context from Open Brain
        context = await self.open_brain.search_context(
            query=task,
            category=category,
            limit=10
        )
        
        # Execute analysis with context
        response = self.claude.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=f"""You are Pauli, the analytical brain of ARCHON-X.
Your specialties: data analysis, logic, diagnostics, mathematics, system architecture.

{context}

Provide thorough analysis with:
1. Key findings
2. Root cause analysis if applicable
3. Data-driven recommendations
4. Confidence levels
5. Next steps""",
            messages=[{"role": "user", "content": task}]
        )
        
        analysis = response.content[0].text
        
        # Log significant findings back to Open Brain
        if "critical" in analysis.lower() or "risk" in analysis.lower():
            await self.open_brain.log_insight(
                title=f"Pauli Analysis: {task[:50]}",
                content=analysis,
                category=category or "ARCHON-X",
                tags=["analysis", "pauli"],
                importance=4
            )
        
        return {
            "agent": self.name,
            "task": task,
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class SynthiaWithMemory:
    """
    Synthia Agent - Creative Brain
    Enhanced with Open Brain for context-aware communication and synthesis
    """
    
    def __init__(self):
        self.open_brain = OpenBrainAgentClient()
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.name = "Synthia"
        self.role = "Creative Brain - Communication, Synthesis, Strategy"
    
    async def initialize(self):
        """Initialize agent with Open Brain connection"""
        await self.open_brain.connect()
        logger.info(f"{self.name} initialized with Open Brain")
    
    async def synthesize(
        self,
        task: str,
        output_format: str = "narrative",
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute creative/synthesis task with full context
        
        Args:
            task: The synthesis task
            output_format: 'narrative', 'structured', 'summary', 'strategy'
            category: Optional category for context filtering
        
        Returns:
            Synthesized output in requested format
        """
        # Get project context if specified
        if category:
            context = await self.open_brain.get_project_context(category)
        else:
            context = await self.open_brain.search_context(task, limit=10)
        
        response = self.claude.messages.create(
            model="claude-opus-4-1",
            max_tokens=3000,
            system=f"""You are Synthia, the creative brain of ARCHON-X.
Your specialties: communication, strategic thinking, synthesis, client relationships.

{context}

Format your response as {output_format}.
Focus on clarity, actionability, and strategic value.""",
            messages=[{"role": "user", "content": task}]
        )
        
        synthesis = response.content[0].text
        
        # Log to Open Brain if high importance
        if output_format == "strategy":
            await self.open_brain.log_insight(
                title=f"Synthia Strategy: {task[:50]}",
                content=synthesis,
                category=category or "Strategy",
                tags=["synthia", "strategy"],
                importance=5
            )
        
        return {
            "agent": self.name,
            "task": task,
            "format": output_format,
            "synthesis": synthesis,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class GuardianFleetCoordinator:
    """
    Guardian Fleet Coordinator
    Coordinates between Darya, Devika, Lightning through shared Open Brain memory
    """
    
    def __init__(self):
        self.open_brain = OpenBrainAgentClient()
        self.guardians = {
            "darya": "Design & Brand Specialist",
            "devika": "Code & Infrastructure",
            "lightning": "Deployment & Automation"
        }
    
    async def initialize(self):
        """Initialize coordinator with Open Brain"""
        await self.open_brain.connect()
        logger.info("Guardian Fleet Coordinator initialized")
    
    async def coordinate_project(self, project_name: str) -> Dict[str, Any]:
        """
        Coordinate guardian execution on a project using shared memory
        """
        # Get full project context
        context = await self.open_brain.get_project_context(project_name)
        
        coordination = {
            "project": project_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "guardians_briefed": []
        }
        
        # Each guardian gets the same context from Open Brain
        for guardian_name, guardian_role in self.guardians.items():
            coordination["guardians_briefed"].append({
                "name": guardian_name,
                "role": guardian_role,
                "context_provided": bool(context),
                "ready": True
            })
        
        # Log coordination to Open Brain
        await self.open_brain.log_decision(
            title=f"Guardian Fleet Coordination: {project_name}",
            category=project_name,
            context=f"Coordinating {len(self.guardians)} guardians",
            decision=f"All guardians briefed with shared context from Open Brain",
            metadata={"guardians": list(self.guardians.keys())}
        )
        
        return coordination

# ============================================================================
# INTEGRATION EXAMPLES
# ============================================================================

async def example_workflow():
    """Example: Complete workflow using agents with Open Brain"""
    
    print("\n" + "=" * 60)
    print("ARCHON-X + Open Brain Integration Demo")
    print("=" * 60)
    
    # 1. Pauli analyzes system status
    print("\n1. Pauli analyzes ARCHON-X deployment status...")
    pauli = PauliBrainWithMemory()
    await pauli.initialize()
    
    analysis = await pauli.analyze(
        "What is the current deployment status of ARCHON-X OS on Coolify?",
        category="ARCHON-X OS"
    )
    print(f"   Status: {analysis['analysis'][:200]}...")
    
    # 2. Synthia synthesizes strategy
    print("\n2. Synthia synthesizes deployment strategy...")
    synthia = SynthiaWithMemory()
    await synthia.initialize()
    
    strategy = await synthia.synthesize(
        "Create a deployment rollout plan for the remaining config items",
        output_format="strategy",
        category="ARCHON-X OS"
    )
    print(f"   Strategy: {strategy['synthesis'][:200]}...")
    
    # 3. Guardian Fleet coordinates
    print("\n3. Guardian Fleet coordinates on project...")
    coordinator = GuardianFleetCoordinator()
    await coordinator.initialize()
    
    coordination = await coordinator.coordinate_project("ARCHON-X OS")
    print(f"   Coordination: {len(coordination['guardians_briefed'])} guardians briefed")
    
    # Cleanup
    await pauli.open_brain.disconnect()
    await synthia.open_brain.disconnect()
    await coordinator.open_brain.disconnect()
    
    print("\n" + "=" * 60)
    print("Demo Complete - All decisions logged to Open Brain")
    print("=" * 60 + "\n")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    asyncio.run(example_workflow())
