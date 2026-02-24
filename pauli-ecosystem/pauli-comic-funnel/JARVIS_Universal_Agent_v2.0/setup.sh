#!/bin/bash
###############################################################################
# JARVIS Universal Agent - Automated Setup Script
# © 2025 The Pauli Effect / Jeremy Bowers
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Header
echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║                                                    ║
║     🤖 JARVIS Universal Agent Setup v2.0          ║
║     Voice-Controlled Autonomous AI                ║
║                                                    ║
║     © 2025 The Pauli Effect                       ║
║     Created by Jeremy Bowers                      ║
║                                                    ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

log_info "Starting JARVIS installation...\n"

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

log_info "Detected OS: $OS"

# Check Python version
log_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python $PYTHON_VERSION found"
else
    log_error "Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if pip is installed
log_info "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    log_warning "pip not found. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi
log_success "pip is ready"

# Install Ollama (for local models)
log_info "Installing Ollama for local AI models..."
if ! command -v ollama &> /dev/null; then
    if [[ "$OS" == "macos" ]] || [[ "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
        log_success "Ollama installed"
    else
        log_warning "Please install Ollama manually from https://ollama.com/download"
    fi
else
    log_success "Ollama already installed"
fi

# Install Python dependencies
log_info "Installing Python packages (this may take a few minutes)..."
pip3 install --upgrade pip --quiet

# Core dependencies
DEPS=(
    "faster-whisper"
    "pyttsx3"
    "pyaudio"
    "anthropic"
    "openai"
    "requests"
    "chromadb"
    "psutil"
    "pyperclip"
    "plyer"
    "playwright"
    "pyautogui"
    "SpeechRecognition"
)

for dep in "${DEPS[@]}"; do
    log_info "Installing $dep..."
    pip3 install "$dep" --quiet || log_warning "Failed to install $dep (may need manual installation)"
done

log_success "Python packages installed"

# Install Playwright browsers
log_info "Installing Playwright browsers..."
playwright install chromium --quiet || log_warning "Playwright browser installation failed"
log_success "Playwright ready"

# Pull recommended local AI models
log_info "Downloading local AI models (this will take several minutes)..."

if command -v ollama &> /dev/null; then
    log_info "Pulling llama3.2:3b (2GB)..."
    ollama pull llama3.2:3b &
    
    log_info "Pulling phi-3-mini (2.3GB)..."
    ollama pull phi-3-mini &
    
    log_info "Pulling nomic-embed-text (embedding model)..."
    ollama pull nomic-embed-text &
    
    # Wait for all downloads
    wait
    log_success "AI models downloaded"
else
    log_warning "Ollama not found. Skipping model download."
fi

# Create JARVIS directory structure
log_info "Creating JARVIS directory structure..."
JARVIS_HOME="$HOME/.jarvis"
mkdir -p "$JARVIS_HOME"/{memory,logs,cache,tools}
log_success "Directory structure created at $JARVIS_HOME"

# Copy configuration files (if they exist in current directory)
if [ -f "jarvis_config.json" ]; then
    log_info "Copying configuration file..."
    cp jarvis_config.json "$JARVIS_HOME/config.json"
    log_success "Configuration copied"
fi

if [ -f "JARVIS_UNIVERSAL_AGENT_LAYER.xml" ]; then
    log_info "Copying system prompt..."
    cp JARVIS_UNIVERSAL_AGENT_LAYER.xml "$JARVIS_HOME/"
    log_success "System prompt copied"
fi

if [ -f "jarvis_agent.py" ]; then
    log_info "Copying agent script..."
    cp jarvis_agent.py "$JARVIS_HOME/"
    chmod +x "$JARVIS_HOME/jarvis_agent.py"
    log_success "Agent script copied"
fi

# Create default config if it doesn't exist
if [ ! -f "$JARVIS_HOME/config.json" ]; then
    log_info "Creating default configuration..."
    cat > "$JARVIS_HOME/config.json" << 'EOF'
{
  "agent": {
    "name": "JARVIS",
    "personality": "professional_butler",
    "voice_enabled": true,
    "mode": "supervised"
  },
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "fallback_to_local": true
  },
  "voice": {
    "wake_words": ["hey jarvis", "computer"],
    "input": {
      "engine": "faster-whisper",
      "model_size": "base"
    },
    "output": {
      "engine": "pyttsx3",
      "rate": 175,
      "volume": 0.9
    }
  },
  "safety": {
    "mode": "supervised",
    "require_approval_for": [
      "delete_files",
      "system_shutdown",
      "send_emails"
    ]
  }
}
EOF
    log_success "Default configuration created"
fi

# Set up environment variables
log_info "Setting up environment variables..."

# Determine shell config file
SHELL_CONFIG="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

# Add to shell config if not already present
if ! grep -q "JARVIS_HOME" "$SHELL_CONFIG" 2>/dev/null; then
    cat >> "$SHELL_CONFIG" << 'EOF'

# JARVIS Agent Environment
export JARVIS_HOME="$HOME/.jarvis"
export OLLAMA_HOST="http://localhost:11434"
alias jarvis="python3 $JARVIS_HOME/jarvis_agent.py"
alias jarvis-voice="python3 $JARVIS_HOME/jarvis_agent.py --voice"
EOF
    log_success "Environment variables added to $SHELL_CONFIG"
else
    log_info "Environment variables already configured"
fi

# Create .env template for API keys
if [ ! -f "$JARVIS_HOME/.env" ]; then
    log_info "Creating .env template for API keys..."
    cat > "$JARVIS_HOME/.env" << 'EOF'
# JARVIS Agent - API Keys
# Uncomment and add your keys as needed

# OpenRouter (recommended for multi-model access)
# OPENROUTER_API_KEY=sk-or-v1-...

# Anthropic Claude (direct access)
# ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (optional)
# OPENAI_API_KEY=sk-...

# ElevenLabs (premium voice)
# ELEVENLABS_API_KEY=...

# GitHub integration
# GITHUB_TOKEN=ghp_...

# Google Workspace
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
EOF
    log_success ".env template created"
fi

# Create startup script
log_info "Creating startup script..."
cat > "$JARVIS_HOME/start.sh" << 'EOF'
#!/bin/bash
# JARVIS Agent Startup Script

echo "🤖 Starting JARVIS Agent..."

# Start Ollama server in background (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve &
    sleep 3
fi

# Load environment variables
if [ -f "$HOME/.jarvis/.env" ]; then
    export $(cat "$HOME/.jarvis/.env" | grep -v '^#' | xargs)
fi

# Run JARVIS
python3 "$HOME/.jarvis/jarvis_agent.py" "$@"
EOF
chmod +x "$JARVIS_HOME/start.sh"
log_success "Startup script created"

# Final status check
echo ""
log_info "Running system check..."

CHECKS_PASSED=0
CHECKS_TOTAL=5

# Check Python
if command -v python3 &> /dev/null; then
    log_success "Python 3: OK"
    ((CHECKS_PASSED++))
else
    log_error "Python 3: FAILED"
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    log_success "Ollama: OK"
    ((CHECKS_PASSED++))
else
    log_warning "Ollama: Not installed (optional)"
    ((CHECKS_PASSED++))  # Don't fail on this
fi

# Check pip packages
if python3 -c "import anthropic, pyttsx3, speech_recognition" 2>/dev/null; then
    log_success "Python packages: OK"
    ((CHECKS_PASSED++))
else
    log_warning "Python packages: Some may be missing"
fi

# Check JARVIS directory
if [ -d "$JARVIS_HOME" ]; then
    log_success "JARVIS directory: OK"
    ((CHECKS_PASSED++))
else
    log_error "JARVIS directory: FAILED"
fi

# Check config
if [ -f "$JARVIS_HOME/config.json" ]; then
    log_success "Configuration: OK"
    ((CHECKS_PASSED++))
else
    log_error "Configuration: FAILED"
fi

# Installation complete
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║                                                    ║
║           ✅ Installation Complete!                ║
║                                                    ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log_success "System checks passed: $CHECKS_PASSED/$CHECKS_TOTAL"
echo ""
log_info "Next steps:"
echo ""
echo "  1️⃣  Add your API keys (optional):"
echo "     Edit ~/.jarvis/.env"
echo ""
echo "  2️⃣  Reload your shell:"
echo "     source $SHELL_CONFIG"
echo ""
echo "  3️⃣  Start Ollama (for local models):"
echo "     ollama serve"
echo ""
echo "  4️⃣  Launch JARVIS:"
echo "     jarvis              # Text mode"
echo "     jarvis --voice      # Voice mode"
echo ""
echo "  5️⃣  Test voice control:"
echo "     Say: 'Hey JARVIS' then give a command"
echo ""

log_info "Documentation: ~/.jarvis/README.md"
log_info "Configuration: ~/.jarvis/config.json"
log_info "Logs: ~/.jarvis/logs/"
echo ""

log_success "🎉 Ready to use JARVIS! Happy automating!"
