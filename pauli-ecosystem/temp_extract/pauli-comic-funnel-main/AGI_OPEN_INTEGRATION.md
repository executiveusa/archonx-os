# AGI Open (Lux) Integration Documentation

## 🎯 Overview

**AGI Open** (https://agiopen.org/) provides **Lux**, the world's best foundation computer-use model that enables AI agents to automate desktop and web-based tasks. This document outlines the integration of Lux into the Pauli Effect project for computer use automation capabilities.

## 📊 Platform Information

### What is Lux?

Lux is a foundation computer-use model developed by the OpenAGI Foundation, created by researchers from MIT, CMU, and UIUC. It enables AI agents to:
- Control desktop applications
- Automate web-based tasks
- Execute multi-step workflows
- Perform complex automation scenarios

### Performance Metrics

Lux achieved **83.6 on the Online-Mind2Web benchmark**, outperforming:
- Google Gemini CUA: 69.0
- OpenAI Operator: 61.3
- Anthropic Claude Sonnet 4: 61.0

**Key Advantages:**
- ⚡ Executes actions in ~1 second per step
- 💰 Costs 10× less than competing models
- 🎯 Built specifically for computer use (not a general model repurposed)

## 🛠️ Integration Architecture

### Three Execution Modes

1. **Actor Mode**
   - Fastest execution (~1 second per step)
   - Best for clearly specified tasks
   - Direct action execution

2. **Thinker Mode**
   - Handles vague, multi-step goals
   - Breaks down complex requests into actionable tasks
   - Autonomous planning and execution

3. **Tasker Mode**
   - Maximum control
   - Accepts Python list of predefined steps
   - Deterministic execution

### Use Cases for Pauli Effect

1. **Automated Testing**
   - UI/UX testing
   - Cross-browser compatibility
   - Regression testing

2. **Content Management**
   - Automated content publishing
   - Social media management
   - Bulk operations

3. **Data Operations**
   - Data entry automation
   - Form filling
   - Spreadsheet operations

4. **Development Workflows**
   - Code generation and testing
   - Build automation
   - Deployment tasks

## 📦 SDK and API Access

### Python SDK (OAGI)

**Installation:**
```bash
pip install oagi
# or
pip install oagi-core
```

**Package Information:**
- **Name:** `oagi` or `oagi-core`
- **PyPI:** https://pypi.org/project/oagi/
- **GitHub:** https://github.com/agiopen-org/oagi-python
- **Documentation:** https://developer.agiopen.org/

### TypeScript SDK

**GitHub:** https://github.com/agiopen-org/oagi-typescript

### API Authentication

**Get API Key:**
- Visit: https://developer.agiopen.org/
- Register for developer account
- Generate API key
- Store in environment variable: `AGI_OPEN_API_KEY`

## 🔧 Integration Plan for Pauli Effect

### Phase 1: Backend Integration

1. **Install Dependencies**
   ```bash
   npm install @agiopen/sdk
   # or for Python backend
   pip install oagi-core
   ```

2. **Configure Environment**
   ```bash
   AGI_OPEN_API_KEY=your_api_key_here
   AGI_OPEN_ENDPOINT=https://api.agiopen.org/v1
   ```

3. **Create Service Layer**
   - Location: `server/services/agi-open.ts`
   - Purpose: Centralized Lux integration
   - Modes: Actor, Thinker, Tasker

### Phase 2: API Endpoints

1. **Computer Use Automation Endpoint**
   - `POST /api/agi-open/execute`
   - Accepts task description
   - Returns execution result

2. **Task Planning Endpoint**
   - `POST /api/agi-open/plan`
   - Uses Thinker mode
   - Returns task breakdown

3. **Status Monitoring**
   - `GET /api/agi-open/status/:taskId`
   - Real-time task status
   - Progress tracking

### Phase 3: LibreChat Integration

1. **Internal-Only Access**
   - Authentication required
   - Team email whitelist
   - Session-based control

2. **Chat Commands**
   - `/automate [task]` - Execute automation
   - `/plan [goal]` - Plan multi-step tasks
   - `/status [taskId]` - Check task status

3. **UI Components**
   - Task execution panel
   - Real-time logs
   - Result visualization

### Phase 4: CopilotKit Integration

1. **Mandatory Usage System**
   - All UI generation routes through CopilotKit
   - Lux handles backend automation
   - Combined agent-driven workflow

2. **Agent Coordination**
   - CopilotKit: Frontend generation
   - Lux: Backend automation
   - Unified agent system

## 🔐 Security Considerations

### API Key Protection

```typescript
// Secure key storage
const agiOpenConfig = {
  apiKey: process.env.AGI_OPEN_API_KEY,
  endpoint: process.env.AGI_OPEN_ENDPOINT,
  maxRetries: 3,
  timeout: 30000,
};

// Validate on startup
if (!process.env.AGI_OPEN_API_KEY) {
  console.error('⚠️  AGI_OPEN_API_KEY not configured');
}
```

### Access Control

- **Internal Only:** LibreChat accessible only to team
- **Whitelist:** Team emails configured in `.env`
- **Authentication:** Session-based auth required
- **Rate Limiting:** Prevent abuse of automation endpoints

### Sandboxing

- Lux executes in isolated environment
- Limited scope per task
- Audit logging for all automation
- User confirmation for destructive actions

## 📋 Technical Requirements

### Dependencies

**Node.js:**
```json
{
  "@agiopen/sdk": "latest",
  "@agiopen/typescript": "latest"
}
```

**Python (if needed):**
```
oagi-core>=1.0.0
```

### Environment Variables

```bash
# AGI Open Configuration
AGI_OPEN_API_KEY=your_api_key
AGI_OPEN_ENDPOINT=https://api.agiopen.org/v1
AGI_OPEN_MODE=actor # or thinker/tasker

# LibreChat Configuration
LIBRECHAT_ENABLED=true
LIBRECHAT_TEAM_EMAILS=team@example.com,admin@example.com
LIBRECHAT_AUTH_SECRET=your_secret_here
```

### System Requirements

- Node.js 18+
- TypeScript 5+
- Express server (already available)
- Redis (for task queue, optional)

## 🚀 Implementation Steps

### Step 1: Install SDK

```bash
npm install @agiopen/sdk --save
```

### Step 2: Create Service

```typescript
// server/services/agi-open.ts
import { LuxClient } from '@agiopen/sdk';

export class AGIOpenService {
  private client: LuxClient;

  constructor() {
    this.client = new LuxClient({
      apiKey: process.env.AGI_OPEN_API_KEY,
    });
  }

  async executeTask(task: string, mode: 'actor' | 'thinker' | 'tasker' = 'actor') {
    // Implementation
  }
}
```

### Step 3: Create API Routes

```typescript
// server/agi-open-routes.ts
router.post('/execute', async (req, res) => {
  const { task, mode } = req.body;
  const result = await agiOpenService.executeTask(task, mode);
  res.json(result);
});
```

### Step 4: Integrate with LibreChat

```typescript
// LibreChat command handler
if (message.startsWith('/automate')) {
  const task = message.replace('/automate', '').trim();
  const result = await agiOpenService.executeTask(task);
  return result;
}
```

## 📊 Expected Outcomes

### For Pauli Effect Project

1. **Automated Testing:**
   - UI components tested automatically
   - Regression tests on every deploy
   - Cross-browser validation

2. **Content Automation:**
   - Automated comic upload
   - Social media posting
   - Newsletter generation

3. **Development Workflow:**
   - Automated builds
   - Deployment automation
   - Database migrations

4. **Team Productivity:**
   - Bulk operations via chat
   - Automated reporting
   - Data collection tasks

### Performance Targets

- Task execution: < 2 seconds per step
- API response time: < 500ms
- Automation success rate: > 95%
- Cost reduction: 10× vs manual processes

## 📚 Resources

### Official Documentation

- **Main Website:** https://agiopen.org/
- **Developer Portal:** https://developer.agiopen.org/
- **Python SDK:** https://github.com/agiopen-org/oagi-python
- **TypeScript SDK:** https://github.com/agiopen-org/oagi-typescript
- **PyPI Package:** https://pypi.org/project/oagi/
- **Samples:** https://github.com/agiopen-org/oagi-lux-samples

### Blog Posts

- [Introducing Lux](https://www.agiopen.org/blog)
- [OpenAGI's Lux: The First Foundation Model for Computer Use](https://medium.com/@meshuggah22/openagis-lux-the-first-foundation-model-built-specifically-for-computer-use-0057bb0ee9af)
- [Lux Launch Coverage](https://www.marktechpost.com/2025/12/05/openagi-foundation-launches-lux-a-foundation-computer-use-model-that-tops-online-mind2web-with-osgym-at-scale/)

### Community

- **GitHub Organization:** https://github.com/agiopen-org
- **Issue Tracker:** https://github.com/agiopen-org/oagi-python/issues

## 🔄 Next Steps

1. ✅ Document AGI Open capabilities (F002)
2. ⏳ Install and configure Lux SDK (F003)
3. ⏳ Create API endpoints for automation (F003)
4. ⏳ Integrate with LibreChat (F005)
5. ⏳ Create Claude skill for agent access (F007)
6. ⏳ Test and verify integration (F008)

## 📝 Notes

- **Launch Date:** December 2025 (very recent)
- **Model Type:** Foundation model for computer use
- **Training:** Trained on OSGym dataset at scale
- **Team:** MIT, CMU, UIUC researchers
- **License:** Check official documentation for licensing details
- **Pricing:** 10× cheaper than competitors (exact pricing TBD)

---

**Last Updated:** 2025-12-31
**Document Version:** 1.0
**Author:** Pauli Effect Development Team
