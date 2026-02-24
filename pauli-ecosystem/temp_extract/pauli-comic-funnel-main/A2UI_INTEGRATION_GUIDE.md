# A2UI + CopilotKit Integration Guide

## 🚀 Overview

This document describes the integration of **A2UI** (Agent-to-User Interface) and **CopilotKit** into the Pauli Effect project. This integration enables AI agents to dynamically generate secure, interactive user interfaces on-the-fly.

## 📚 What is A2UI?

**A2UI** is an open-source project by Google for agent-driven, cross-platform generative UI. It provides:

- **Security First**: Declarative data format (not executable code)
- **Framework Agnostic**: Works with React, Flutter, Angular, and more
- **LLM Friendly**: Optimized for AI agents to generate incrementally
- **Portable**: Same JSON payload renders across different platforms

### Key Concepts

- **Declarative Format**: Agents describe UI intent, clients render implementation
- **Component Catalog**: Pre-approved components ensure security
- **Progressive Rendering**: UIs can be built incrementally
- **Trust Boundaries**: Agents run remotely with controlled UI generation

## 🛠️ What is CopilotKit?

**CopilotKit** is a React framework for building in-app AI copilots and AI agents. Features include:

- AI chat interfaces
- Agent-driven actions
- Agentic workflows
- Native A2UI support

## 🎯 Integration Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                  │
│  ┌────────────────────────────────────────────────┐ │
│  │         PauliCopilotKitProvider                │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │           A2UIChat Component             │ │ │
│  │  │  - User input                            │ │ │
│  │  │  - Message display                       │ │ │
│  │  │  - A2UI rendering                        │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         ↕ HTTPS
┌─────────────────────────────────────────────────────┐
│                Backend (Express + Node)              │
│  ┌────────────────────────────────────────────────┐ │
│  │      CopilotKit API Routes                     │ │
│  │  - /api/copilotkit (main endpoint)            │ │
│  │  - /api/copilotkit/a2ui (A2UI generation)     │ │
│  │  - /api/copilotkit/health (health check)      │ │
│  └────────────────────────────────────────────────┘ │
│                      ↕                               │
│  ┌────────────────────────────────────────────────┐ │
│  │          Anthropic Claude API                  │ │
│  │  - claude-sonnet-4-20250514                    │ │
│  │  - Generates A2UI JSON                         │ │
│  │  - Processes user requests                     │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 📦 Installed Packages

### Frontend Dependencies

```json
{
  "@copilotkit/react-core": "~1.50.0",
  "@copilotkit/a2ui-renderer": "0.0.2",
  "@a2ui/lit": "^0.8.1",
  "@ag-ui/a2a": "0.00.6",
  "@a2a-js/sdk": "0.2.5"
}
```

### Backend Dependencies

```json
{
  "@copilotkit/runtime": "~1.50.0"
}
```

## 🏗️ Project Structure

```
pauli-comic-funnel/
├── src/
│   ├── integrations/
│   │   ├── a2ui/
│   │   │   ├── A2UIChat.tsx         # Main chat component
│   │   │   ├── theme.ts             # Pauli Effect theming
│   │   │   └── index.ts             # Exports
│   │   └── copilotkit/
│   │       ├── CopilotKitProvider.tsx  # Provider wrapper
│   │       └── index.ts             # Exports
│   └── pages/
│       └── A2UIDemo.tsx             # Demo page
├── server/
│   ├── copilotkit-routes.ts        # API endpoints
│   └── index.ts                    # Main server (updated)
├── a2ui-temp/                      # Cloned A2UI repo (reference)
├── copilotkit-a2ui-example/        # CopilotKit example (reference)
└── .claude/
    └── mcp.json                    # CopilotKit MCP config
```

## 🎨 Theming

The integration includes custom theming for the Pauli Effect brand in `src/integrations/a2ui/theme.ts`:

```typescript
export const pauliA2UITheme = {
  primaryColor: '#8B5CF6',      // Purple
  secondaryColor: '#3B82F6',    // Blue
  backgroundColor: '#0F172A',   // Dark slate
  surfaceColor: '#1E293B',      // Card background
  // ... more theme properties
};
```

## 🚀 Usage

### 1. Access the Demo

Navigate to `/a2ui-demo` in your browser to see the integration in action.

### 2. Using in Your Components

```typescript
import { PauliCopilotKitProvider } from '@/integrations/copilotkit';
import { A2UIChat } from '@/integrations/a2ui';

function MyComponent() {
  return (
    <PauliCopilotKitProvider>
      <A2UIChat placeholder="Ask me anything..." />
    </PauliCopilotKitProvider>
  );
}
```

### 3. Example Prompts

Try these prompts in the chat:

- "Create a user registration form"
- "Build a temperature converter"
- "Design a task management widget"
- "Make a color picker interface"
- "Create a data visualization dashboard"
- "Build a feedback survey"

## 🔧 API Endpoints

### POST /api/copilotkit

Main endpoint for CopilotKit communication.

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Create a contact form"
    }
  ]
}
```

**Response:**
```json
{
  "messages": [
    {
      "id": "msg-1234567890",
      "role": "assistant",
      "content": "I'll create a contact form for you...",
      "createdAt": "2025-12-31T14:00:00.000Z"
    }
  ]
}
```

### POST /api/copilotkit/a2ui

Dedicated endpoint for A2UI generation.

**Request:**
```json
{
  "prompt": "Create a user profile form"
}
```

**Response:**
```json
{
  "a2ui": "{\"components\": [...]}",
  "generatedAt": "2025-12-31T14:00:00.000Z"
}
```

### GET /api/copilotkit/health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "copilotkit",
  "features": ["chat", "a2ui", "agents"],
  "timestamp": "2025-12-31T14:00:00.000Z"
}
```

## 🔐 Security Considerations

1. **Declarative Format**: A2UI uses declarative JSON, not executable code
2. **Component Catalog**: Only pre-approved components can be rendered
3. **API Key Protection**: Anthropic API key stored in environment variables
4. **CORS Configuration**: Configured for your domain only
5. **Input Validation**: All user inputs are validated before processing

## 🌐 Environment Variables

Required environment variables:

```bash
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Server Configuration
PORT=3001

# Optional: Notion Integration
NOTION_API_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id
```

## 📖 Reference Documentation

- [A2UI Official Site](https://a2ui.org/)
- [A2UI GitHub](https://github.com/google/A2UI)
- [A2UI Quickstart](https://a2ui.org/quickstart/)
- [CopilotKit Official Site](https://www.copilotkit.ai/)
- [CopilotKit GitHub](https://github.com/CopilotKit/CopilotKit)
- [CopilotKit A2UI Integration](https://www.copilotkit.ai/blog/build-with-googles-new-a2ui-spec-agent-user-interfaces-with-a2ui-ag-ui)

## 🧪 Development

### Running the Demo Locally

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Start the backend:**
   ```bash
   npm run server
   ```

4. **Start the frontend:**
   ```bash
   npm run dev
   ```

5. **Access the demo:**
   Navigate to `http://localhost:5173/a2ui-demo`

## 🐛 Troubleshooting

### CopilotKit Not Connecting

- Verify backend is running on port 3001
- Check ANTHROPIC_API_KEY is set
- Verify CORS is properly configured

### A2UI Components Not Rendering

- Check browser console for errors
- Verify theme configuration is loaded
- Ensure proper component registration

### API Errors

- Check server logs: `npm run server`
- Verify Anthropic API key is valid
- Check network requests in browser DevTools

## 🔮 Future Enhancements

- [ ] Add custom A2UI components (charts, maps, etc.)
- [ ] Implement A2UI component library browser
- [ ] Add agent memory/context persistence
- [ ] Create reusable A2UI templates
- [ ] Implement A2UI state management
- [ ] Add A2UI export/import functionality
- [ ] Create visual A2UI builder tool

## 📝 License

This integration uses:
- **A2UI**: Apache 2.0 License
- **CopilotKit**: MIT License

## 🙏 Credits

- **A2UI** by Google
- **CopilotKit** by CopilotKit Team
- **Pauli Effect Project** - Custom integration and theming

## 📞 Support

For issues or questions:
- Create an issue on the project GitHub
- Check the documentation links above
- Review the demo implementation at `/a2ui-demo`

---

**Built with ❤️ for The Pauli Effect Project**
