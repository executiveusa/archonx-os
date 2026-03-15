# 🤖 JARVIS Universal Agent Layer v2.0

**Voice-Controlled Autonomous Computer Agent System**

Transform any project into a Jarvis-style voice-controlled AI that can manipulate files, control your browser, execute code, and orchestrate complex workflows - all running on your laptop.

---

## 🎯 What Is This?

A **universal meta-layer** that adds autonomous agent capabilities to any AI system. Inject this prompt into Claude, GPT-4, Llama, or any LLM to enable:

- 🎤 **Voice Control** - "Hey JARVIS, find all my design files"
- 🖥️ **Computer Control** - Automates files, browser, system tasks
- 🧠 **Multi-Agent Orchestration** - Complex tasks split across specialized agents
- 💡 **Local-First** - Runs on lightweight models (Llama 3.2, Phi-3)
- 🔒 **Safety Guardrails** - Asks permission before destructive actions
- 📱 **Surface Optimized** - Works on tablets and low-resource devices

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- 8GB RAM minimum
- Microphone and speakers
- macOS, Windows, or Linux

### One-Command Install

```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/jarvis/main/setup.sh | bash
```

### Manual Install

```bash
# 1. Install Ollama (for local models)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Install Python dependencies
pip install faster-whisper pyttsx3 pyaudio playwright anthropic chromadb psutil

# 3. Install Playwright browsers
playwright install chromium

# 4. Pull local AI models
ollama pull llama3.2:3b
ollama pull phi-3-mini
ollama pull nomic-embed-text

# 5. Create JARVIS directory
mkdir -p ~/.jarvis/{memory,logs,cache,tools}

# 6. Copy configuration files
cp JARVIS_UNIVERSAL_AGENT_LAYER.xml ~/.jarvis/
cp jarvis_config.json ~/.jarvis/config.json

# 7. Set up environment variables (optional)
export JARVIS_HOME="$HOME/.jarvis"
export OPENROUTER_API_KEY="your_key_here"  # Optional
```

---

## 🚀 Usage

### Starting JARVIS

```bash
# Method 1: Direct Python
python jarvis_agent.py

# Method 2: Command alias (after setup)
jarvis

# Method 3: Voice-activated (starts listening on boot)
jarvis --voice --auto
```

### Voice Commands

**File Operations:**
```
"Hey JARVIS, find all my design files from last month"
"Open that proposal I was working on yesterday"
"Organize my downloads folder by file type"
"Show me all PDFs in my Documents"
```

**Browser Control:**
```
"Open GitHub and show me my notifications"
"Research AI agent frameworks and summarize them"
"Check if my website is running"
"Take a screenshot of this page"
```

**Development Tasks:**
```
"Set up a new React project called 'my-dashboard'"
"Run the build script in my current project"
"Check for errors in my code"
"Deploy this to Vercel"
```

**System Management:**
```
"What's using all my memory?"
"Show me my calendar for today"
"Read my latest emails"
"What's the weather like?"
```

**Multi-Agent Tasks:**
```
"Build me a landing page with conversion-optimized copy"
"Create a presentation about AI trends"
"Analyze this dataset and create visualizations"
```

---

## 🛠️ Configuration

### Model Selection

Edit `~/.jarvis/config.json`:

```json
{
  "llm": {
    "provider": "openrouter",
    "models": {
      "high_resource": "anthropic/claude-sonnet-4-20250514",
      "medium_resource": "anthropic/claude-3-haiku",
      "low_resource": "ollama/llama3.2:3b"
    }
  }
}
```

### Voice Customization

```json
{
  "voice": {
    "wake_words": ["hey jarvis", "computer"],
    "output": {
      "engine": "pyttsx3",
      "rate": 175,
      "voice_gender": "male"
    }
  }
}
```

### Safety Settings

```json
{
  "safety": {
    "mode": "supervised",
    "require_approval_for": [
      "delete_files",
      "send_emails",
      "system_shutdown"
    ]
  }
}
```

---

## 🎨 Integration with Existing Projects

### Option 1: System Prompt Injection

If you have an existing AI project (Claude, GPT, etc.), simply add the JARVIS system prompt:

```python
import anthropic

# Load JARVIS prompt
with open('~/.jarvis/JARVIS_UNIVERSAL_AGENT_LAYER.xml', 'r') as f:
    jarvis_prompt = f.read()

# Inject into your system
client = anthropic.Anthropic(api_key="your_key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=jarvis_prompt,
    messages=[{"role": "user", "content": "Hey JARVIS, find my files"}]
)
```

### Option 2: MCP Server Layer

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jarvis": {
      "command": "python",
      "args": ["~/.jarvis/jarvis_mcp_server.py"]
    }
  }
}
```

### Option 3: Standalone Agent

Run as independent application:

```bash
python ~/.jarvis/jarvis_standalone.py
```

---

## 🧠 Architecture

```
┌─────────────────────────────────────┐
│   Voice Input (Whisper STT)        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   LLM Brain (Claude/Llama/OpenRouter)│
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Orchestration Layer               │
│   ├─ Intent Classification          │
│   ├─ Safety Checks                  │
│   ├─ Multi-Agent Coordination       │
│   └─ Memory Management              │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Tool Execution Layer              │
│   ├─ Filesystem (MCP)               │
│   ├─ Browser (Playwright)           │
│   ├─ System Control (PyAutoGUI)    │
│   ├─ Code Execution (Bash)         │
│   └─ APIs (GitHub, Google, etc.)   │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Voice Output (TTS)                │
└─────────────────────────────────────┘
```

---

## 🔧 Advanced Features

### Multi-Agent Orchestration

JARVIS automatically activates multiple specialized agents for complex tasks:

```
User: "Build me a nonprofit landing page"
  ↓
Coordinator Agent: Splits task into subtasks
  ↓
├─ Architect Agent: Designs system architecture
├─ Copywriter Agent: Creates P.A.S.S. structured copy
├─ Builder Agent: Implements code
└─ QA Agent: Tests and validates
  ↓
Final output delivered to user
```

### Long-Term Memory

JARVIS remembers your preferences:

```
User: "Remember that I save all projects in ~/Work/Projects"
JARVIS: "Got it. I'll default to that location from now on."

[Next day]
User: "Create a new React project"
JARVIS: "Creating project in ~/Work/Projects as per your preference."
```

### Context Awareness

```
User: "Open that file"
JARVIS: (searches conversation history)
       "Opening 'proposal-final-v3.docx' that we discussed 5 minutes ago."
```

---

## 📊 Resource Optimization

### For Surface Tablets / Low-Resource Devices

JARVIS automatically detects device capabilities and selects optimal models:

| Device RAM | Selected Model     | Speed  | Quality |
|------------|-------------------|--------|---------|
| 16GB+      | Claude Sonnet 4   | Medium | Excellent |
| 8-15GB     | Claude Haiku      | Fast   | Good |
| 4-7GB      | Llama 3.2 (3B)    | Fast   | Good |
| <4GB       | Phi-3 Mini        | Very Fast | Decent |

**Battery Optimization:**
- Automatically switches to smaller models on battery power
- Reduces processing frequency
- Caches responses
- Disables non-essential features

**Network Optimization:**
- Prefers local models when offline
- Caches API responses
- Batches API calls

---

## 🔒 Safety & Privacy

### Permission System

JARVIS asks before:
- Deleting files
- Sending emails
- Making purchases
- Modifying system files
- Executing potentially harmful code

### Audit Trail

All actions logged to `~/.jarvis/logs/audit.log`:

```json
{
  "timestamp": "2025-11-02T14:30:15Z",
  "action": "delete_file",
  "path": "~/Documents/old-file.txt",
  "approved_by": "user",
  "result": "success"
}
```

### Data Privacy

- All processing can happen locally (no internet required)
- API keys stored in environment variables only
- User data never leaves device unless explicitly requested
- Memory can be cleared anytime: `jarvis --clear-memory`

---

## 🌐 Integrations

### Supported Services

- **GitHub** - Repo management, PR creation, issue tracking
- **Google Workspace** - Gmail, Drive, Calendar
- **Stripe** - Payment processing (with approval)
- **Notion** - Note-taking and databases
- **Slack** - Team communication
- **Linear** - Issue tracking

### API Setup

```bash
# Add API keys to environment
export OPENROUTER_API_KEY="sk-..."
export GITHUB_TOKEN="ghp_..."
export GOOGLE_CLIENT_ID="..."

# Or add to ~/.jarvis/.env file
echo "OPENROUTER_API_KEY=sk-..." >> ~/.jarvis/.env
```

---

## 🎓 Use Cases

### For Developers
- "Set up my dev environment for a new project"
- "Find all TODO comments in my codebase"
- "Run tests and show me failures"
- "Deploy to production"

### For Nonprofits
- "Generate a donation page for our campaign"
- "Search for grants related to education"
- "Schedule volunteer shifts"
- "Create impact report"

### For Content Creators
- "Transcribe this video"
- "Generate social media posts from this article"
- "Schedule posts across platforms"
- "Analyze engagement metrics"

### For Researchers
- "Search academic papers about AI ethics"
- "Organize my research notes by topic"
- "Generate bibliography in APA format"
- "Summarize these 10 papers"

---

## 🐛 Troubleshooting

### Voice Not Working

```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Check audio permissions (macOS)
# System Preferences → Security & Privacy → Microphone → Enable for Terminal

# Test TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
```

### Model Not Loading

```bash
# Check Ollama is running
ollama list

# Pull models again
ollama pull llama3.2:3b

# Check model file size
ls -lh ~/.ollama/models/
```

### High Memory Usage

```bash
# Switch to smaller model
jarvis --model phi-3-mini

# Clear cache
rm -rf ~/.jarvis/cache/*

# Reduce context window
# Edit config.json: "short_term_max_tokens": 4000
```

---

## 📝 Command Reference

### CLI Options

```bash
jarvis [OPTIONS]

Options:
  --voice               Enable voice control
  --auto                Auto-start on boot
  --model MODEL         Specify LLM model
  --mode MODE           supervised|semi_autonomous|fully_autonomous
  --config PATH         Path to config file
  --log-level LEVEL     DEBUG|INFO|WARNING|ERROR
  --clear-memory        Clear long-term memory
  --reset               Reset to factory defaults
  --version             Show version
  --help                Show this help
```

### Keyboard Shortcuts

- `Ctrl+Space` - Push to talk (if voice activated)
- `Ctrl+C` - Stop current task
- `Ctrl+Shift+C` - Clear context
- `Ctrl+Shift+M` - Toggle microphone

---

## 🚧 Roadmap

### v2.1 (Coming Soon)
- [ ] Visual interface (Electron app)
- [ ] iOS/Android companion apps
- [ ] More language support (Spanish, French, etc.)
- [ ] Custom tool creation wizard

### v3.0 (Future)
- [ ] Multi-device sync
- [ ] Team collaboration features
- [ ] Marketplace for custom agents
- [ ] Plugin system

---

## 🤝 Contributing

This is a proprietary system developed for The Pauli Effect / ARCHON Platform. For licensing inquiries, contact:

**Jeremy Bowers**  
Email: bambu@thepaulieffect.com  
Platform: https://archon.ai

---

## 📄 License

© 2025 The Pauli Effect / Jeremy Bowers  
Licensed under ARCHON Platform Agreement

**Trademarks:**
- P.A.S.S.™ Framework
- Rockabye Baby™ Protocol
- JARVIS Universal Agent Layer™

---

## 🙏 Acknowledgments

Built with:
- Anthropic Claude
- OpenRouter
- Ollama
- Playwright
- Whisper AI
- The amazing open-source community

Special thanks to the nonprofit and social service organizations that inspired the ethical framework.

---

## 📞 Support

- **Documentation**: https://docs.thepaulieffect.com/jarvis
- **Discord**: https://discord.gg/paulieffect
- **Issues**: GitHub Issues (if open source)
- **Email**: support@thepaulieffect.com

---

**Ready to get started?**

```bash
jarvis --voice --auto
```

*Say: "Hey JARVIS" to activate your personal AI assistant!* 🎤✨
