# VS CODE COPILOT — BUILD ARCHONX OS
**Paste this into VS Code Copilot Chat to build the autonomous system**

---

```
You are building ArchonX OS - a 64-agent autonomous operating system based on IndyDevDan's 12 Principles of Agentic Coding and the OpenClaw Flywheel architecture.

PROJECT STRUCTURE:
C:\archonx-os-main\
├── agents\                    # 64 agent definitions (32 White, 32 Black)
├── orchestrator\              # Master coordinator
├── paulis-place\             # Central hub (FastAPI + React)
├── skills\                    # Templates and workflows
├── memory\                    # Persistent storage (expertise, KPIs, cache)
├── .beads\                    # Task tracking (git-backed)
├── .mcp-agent-mail\          # Inter-agent messaging
├── config\                    # System configuration
└── docs\                      # Documentation

CORE DEPENDENCIES TO INSTALL:
1. MCP Agent Mail
   curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/scripts/install.sh | bash -s -- --yes

2. Beads Rust + Beads Viewer
   curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
   (Beads Viewer auto-installs with Agent Mail)

3. OpenClaw Gateway (TypeScript)
   npm install -g openclaw@latest

4. Python dependencies
   pip install fastapi uvicorn anthropic openai google-generativeai elevenlabs

ARCHITECTURE TO BUILD:

1. AGENT FRAMEWORK (agents/base_agent.py)
   Create base class that ALL 64 agents inherit from:
   - Pre-task protocol (Beads check, Agent Mail check, expertise search)
   - Post-task protocol (self-validation, improvement filing, learning)
   - Agent Mail integration (send/receive)
   - Beads integration (create/update/close tasks)
   - Expertise file management (Act → Learn → Reuse)
   - KPI tracking

2. ORCHESTRATOR (orchestrator/main.py)
   Master coordinator that:
   - Receives tasks (from OpenClaw or direct)
   - Decomposes into subtasks
   - Assigns to specialized agents (via Agent Mail)
   - Monitors progress (via Beads Viewer robot API)
   - Aggregates results
   - Handles failures (retry, reassign, escalate)

3. PAULIS PLACE HUB (paulis-place/)
   Backend:
   - FastAPI server (port 8000)
   - Endpoints: /agents, /tasks, /status, /kpis
   - WebSocket for real-time updates
   - Agent Mail server integration (port 8765)
   - Beads Viewer dashboard proxy (port 8766)
   
   Frontend:
   - React + Vite + shadcn/ui
   - Dashboard showing:
     * 64 agents (chess board visualization)
     * Active tasks (Beads graph)
     * Agent Mail threads
     * KPI metrics
     * Deployment status

4. SPECIALIZED AGENTS (agents/)
   Create these key agents following the 12 principles:
   
   WHITE CREW (Constructive):
   - white_e1_orchestrator.py (King - coordinates)
   - white_d1_synthia.py (Queen - design/frontend)
   - white_b1_claudecode.py (Bishop - architecture)
   - white_c1_mcp_builder.py (Bishop - tool creation)
   - white_g1_switchblade.py (Knight - deployment)
   - white_a1_database_architect.py (Rook - infrastructure)
   - white_pawns_1-8.py (Feature developers)
   
   BLACK CREW (Adversarial):
   - black_e8_adversarial_orchestrator.py (King - attacks White plans)
   - black_d8_security_tester.py (Queen - penetration testing)
   - black_b8_brenner_critic.py (Bishop - adversarial review)
   - black_c8_chaos_engineer.py (Bishop - break things)
   - black_g8_load_tester.py (Knight - stress testing)
   - black_h8_edge_case_hunter.py (Rook - find bugs)
   - black_pawns_1-8.py (Specialized testers)

5. SKILL TEMPLATES (skills/)
   Create templates for common tasks:
   - skills/design/landing_page_template.md
   - skills/development/nextjs_app_template.md
   - skills/deployment/coolify_deploy_template.md
   - skills/testing/security_audit_template.md
   - Each template includes:
     * Problem it solves
     * Input parameters
     * Step-by-step workflow
     * Validation criteria
     * Example usage

6. MEMORY SYSTEM (memory/)
   - memory/expertise/<agent_id>/<task_id>.json (learning files)
   - memory/kpis/<agent_id>/daily_summary.json (performance tracking)
   - memory/cache/ (frequently accessed patterns)
   - memory/plans/ (generated plans for review)
   - memory/errors/ (failure logs)

7. INTEGRATION LAYER
   - config/openclaw_bridge.py (connect to OpenClaw gateway :18789)
   - config/brennerbot_integration.py (3-model research orchestration)
   - config/elevenlabs_voice.py (SYNTHIA voice in ES/EN/HI/SR)
   - config/deployment_targets.py (Coolify, Vercel endpoints)

THE 12 PRINCIPLES IMPLEMENTATION CHECKLIST:

For EACH agent you create, wire in:

✓ Principle 1 (Out of Loop): 
  - Autonomous task execution (no blocking on human approval)
  - Continuous operation (30-second cycle checking Beads)

✓ Principle 2 (Core Four): 
  - Context window management (<70% usage)
  - Model selection logic (GPT/Claude/Gemini for different roles)
  - Prompt templating (load from /skills)
  - Tool integration (MCP Agent Mail, Beads, OpenClaw)

✓ Principle 3 (Your Way):
  - Read AGENTS.md before every task
  - Follow quality gates (Lighthouse >90, WCAG AA, 0 TS errors)
  - Update learnings after tasks

✓ Principle 4 (Templating):
  - Check for existing template before coding
  - Extract template after solving new problem
  - Save to /skills/<role>/templates/

✓ Principle 5 (Success is Planned):
  - Generate plan before execution
  - Log to /memory/plans/<task_id>.md
  - If HIGH_PRIORITY, send to Orchestrator for review

✓ Principle 6 (Close Loops):
  - Self-validation (tests run automatically)
  - Self-correction (fix bugs, rerun tests)
  - Self-documentation (generate docs from code)

✓ Principle 7 (Specialized):
  - Each agent has clear domain
  - Agents coordinate via Agent Mail
  - No agent does everything

✓ Principle 8 (Learning):
  - Act → record decisions
  - Learn → analyze results
  - Reuse → search expertise before starting new tasks

✓ Principle 9 (Orchestration):
  - Orchestrator receives complex tasks
  - Decomposes → assigns to specialists
  - Monitors → aggregates → delivers

✓ Principle 10 (Context Engineering):
  - Load only relevant files
  - Use summaries instead of full content
  - Reference architecture docs by anchor

✓ Principle 11 (Measure):
  - Track: completion rate, time, self-corrections, plan velocity
  - Update daily at 3 AM
  - Dashboard displays trends

✓ Principle 12 (ZTE):
  - Start: in-loop (human approves everything)
  - Week 4: out-loop (human reviews final only)
  - Week 12: ZTE (human defines goals, system executes)

IMPLEMENTATION ORDER:

PHASE 1 (Week 1): Foundation
1. Install dependencies (MCP Agent Mail, Beads, OpenClaw)
2. Create base agent framework (agents/base_agent.py)
3. Create simple Orchestrator (orchestrator/main.py)
4. Test with 2 agents (White-e1 Orchestrator + White-d1 SYNTHIA)
5. Verify Agent Mail communication works
6. Verify Beads task creation/closing works

PHASE 2 (Week 2): Core Agents
1. Add ClaudeCode (White-b1)
2. Add Switchblade (White-g1)
3. Add Security Tester (Black-d8)
4. Wire OpenClaw gateway integration
5. Test end-to-end: WhatsApp message → agents → deploy → response

PHASE 3 (Week 3): Templating & Learning
1. Create 5 core skill templates
2. Implement Agent Expert files (Act → Learn → Reuse)
3. Add self-improvement cycle (3 AM daily)
4. Test learning: Run same task 3 times, verify speed improvement

PHASE 4 (Week 4): Full Fleet
1. Complete all 64 agents (32 White, 32 Black)
2. Add competitive scoring (White vs Black)
3. Build Paulis Place dashboard (React frontend)
4. Wire BrennerBot research integration

PHASE 5 (Week 5-6): Production Hardening
1. Add failure recovery protocols
2. Implement rollback strategies
3. Add comprehensive logging
4. Load testing (Black crew stress tests)
5. Security hardening (Black crew penetration tests)

PHASE 6 (Week 7-8): Revenue Flows
1. Wire Latin American client onboarding (WhatsApp/Telegram ES)
2. Autonomous site deployment pipeline (SYNTHIA → ClaudeCode → Switchblade)
3. Payment integration (Stripe/crypto via BTCPay)
4. Client notification system (OpenClaw channels)

CRITICAL FILES TO CREATE FIRST:

1. agents/base_agent.py
   (Base class with 12 principles baked in)

2. orchestrator/main.py
   (Master coordinator)

3. config/system_behavior.json
   (12 principles as configuration)

4. skills/README.md
   (Template library documentation)

5. memory/README.md
   (Learning system documentation)

6. paulis-place/backend/main.py
   (FastAPI server)

7. paulis-place/frontend/src/App.tsx
   (React dashboard)

EXAMPLE AGENT STRUCTURE:

```python
# agents/white_d1_synthia.py

from agents.base_agent import BaseAgent
import asyncio

class SYNTHIAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="white_d1_synthia",
            role="design_frontend",
            position="White-d1",
            crew="white",
            specialization="Awwwards-level design, Lighthouse optimization"
        )
    
    async def execute_task(self, task):
        # PRE-TASK PROTOCOL (inherited from BaseAgent)
        await self.pre_task_check(task)
        
        # LOAD TEMPLATE
        template = self.load_template("design/landing_page_template.md")
        
        # GENERATE PLAN
        plan = await self.generate_plan(task, template)
        if task.priority == "high":
            await self.send_plan_for_review(plan)
        
        # EXECUTE
        design = await self.create_design_system(task.requirements)
        components = await self.generate_components(design)
        
        # SELF-VALIDATE (Principle 6: Close Loops)
        lighthouse_score = await self.run_lighthouse_audit(components)
        if lighthouse_score < 90:
            components = await self.optimize_performance(components)
            lighthouse_score = await self.run_lighthouse_audit(components)
        
        # POST-TASK PROTOCOL (inherited from BaseAgent)
        await self.post_task_actions(task, result={
            "design": design,
            "components": components,
            "lighthouse_score": lighthouse_score
        })
        
        return {
            "status": "complete",
            "artifacts": components,
            "metrics": {"lighthouse": lighthouse_score}
        }
```

CODE GENERATION INSTRUCTIONS:

When I ask you to generate code, follow this pattern:
1. Show file path clearly (e.g., "File: agents/white_d1_synthia.py")
2. Include all imports at top
3. Add docstrings explaining purpose
4. Wire in relevant principles from the 12
5. Include error handling
6. Add logging statements
7. Include example usage at bottom (in __main__ block)

TESTING INSTRUCTIONS:

For each agent, create a test file:
- tests/test_<agent_name>.py
- Mock Beads, Agent Mail, OpenClaw
- Test pre-task protocol
- Test post-task protocol
- Test failure recovery
- Test learning (expertise file updates)

START COMMAND FOR YOU:

Once I say "Build it", you will:
1. Ask me which phase to start with (1-6)
2. Generate the core files for that phase
3. Show installation commands
4. Provide testing instructions
5. Ask if I want to proceed to next phase

REMEMBER:
- Every agent follows the 12 principles
- Quality gates: Lighthouse >90, WCAG AA, 0 errors
- All coordination via Agent Mail
- All tasks tracked in Beads
- All learning saved to expertise files
- Daily self-improvement at 3 AM
- Chess board metaphor for agent positions
- White (constructive) vs Black (adversarial) creates quality through competition

Ready to build ArchonX OS. Waiting for your "Build it" command.
```

---

## QUICK START (PASTE THIS NEXT)

```
Build it. Start with Phase 1. Generate:
1. agents/base_agent.py (with all 12 principles)
2. orchestrator/main.py (simple version)
3. config/system_behavior.json (12 principles config)
4. Installation script (install_archonx.sh)
5. README.md (setup guide)
```
