# Pauli Agent UI Skill

## Description
Build beautiful, interactive frontends using the Pauli Agent UI system (powered by CopilotKit & A2UI). This skill enables AI agents to create secure, declarative user interfaces with computer-use automation through AGI Open's Lux model.

## When to Use This Skill

Use this skill when:
- Building any frontend component or interface
- Creating forms, dashboards, or visualizations
- Generating UI from natural language descriptions
- Automating computer-use tasks
- Need agent-driven interface generation

## Technologies

- **CopilotKit** (rebranded as Pauli Agent UI): Frontend generation
- **A2UI**: Declarative UI protocol from Google
- **AGI Open Lux**: Computer-use automation
- **React + TypeScript**: UI framework
- **Tailwind CSS**: Styling

## API Endpoints

### Pauli Agent UI (CopilotKit)

```
POST /api/copilotkit
- Main endpoint for agent-driven UI generation
- Accepts natural language requests
- Returns A2UI JSON or React components

POST /api/copilotkit/a2ui
- Dedicated A2UI generation
- Returns declarative UI JSON
```

### AGI Open Computer Use

```
POST /api/agi-open/execute
- Execute computer-use automation tasks
- Modes: actor (fast), thinker (planning), tasker (controlled)

POST /api/agi-open/plan
- Plan multi-step automation workflows

GET /api/agi-open/status/:taskId
- Check automation task status
```

## Usage Examples

### Generate a Form Component

```typescript
// Request to Pauli Agent UI
POST /api/copilotkit/a2ui
{
  "prompt": "Create a user registration form with email, password, and name fields"
}

// Returns A2UI JSON that renders securely
```

### Automate a Task

```typescript
// Request to AGI Open
POST /api/agi-open/execute
{
  "task": "Take a screenshot of the dashboard and save it",
  "mode": "actor"
}
```

### Combined Workflow

1. Use AGI Open to gather data
2. Use Pauli Agent UI to generate visualization
3. Display in frontend automatically

## Mandatory Rules

1. **ALL frontend generation MUST use Pauli Agent UI**
   - Never generate UI code manually
   - Always route through /api/copilotkit
   - System will enforce this automatically

2. **Computer automation uses AGI Open Lux**
   - Browser automation: Use Lux Actor mode
   - Complex workflows: Use Lux Thinker mode
   - Scripted tasks: Use Lux Tasker mode

3. **Security First**
   - A2UI is declarative, not executable code
   - Only pre-approved components can render
   - All automation is logged and monitored

## Environment Variables Required

```bash
# CopilotKit Configuration
COPILOTKIT_API_KEY=ck_pub_fbf215dde8fa4552d50f5c965defbabe

# AGI Open Configuration
AGI_OPEN_API_KEY=your_key_here
AGI_OPEN_ENDPOINT=https://api.agiopen.org/v1

# Anthropic (for backend AI)
ANTHROPIC_API_KEY=your_key_here
```

## Demo and Testing

- Visit `/a2ui-demo` to see live examples
- Try prompts like:
  - "Create a contact form"
  - "Build a temperature converter"
  - "Design a task management widget"

## Integration with LibreChat

Internal team can access via LibreChat with commands:
- `/ui [description]` - Generate UI component
- `/automate [task]` - Execute automation
- `/plan [goal]` - Plan multi-step workflow

## Performance

- UI Generation: < 2 seconds
- Automation: ~1 second per step (Lux Actor mode)
- Cost: 10× cheaper than alternatives

## Documentation

- Integration Guide: `/A2UI_INTEGRATION_GUIDE.md`
- AGI Open Docs: `/AGI_OPEN_INTEGRATION.md`
- Live Demo: `/a2ui-demo`

## Notes

- System automatically enforces Pauli Agent UI usage
- Legacy UI endpoints redirect to new system
- All operations logged for monitoring
- Rebranded from CopilotKit for Pauli Effect architecture

---

**Always use this skill for frontend generation and computer-use automation in the Pauli Effect project.**
