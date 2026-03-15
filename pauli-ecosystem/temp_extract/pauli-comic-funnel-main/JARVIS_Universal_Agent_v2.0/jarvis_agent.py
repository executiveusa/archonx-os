#!/usr/bin/env python3
"""
JARVIS Universal Agent - Starter Implementation
================================================
A working example of the JARVIS voice-controlled autonomous agent.

This script demonstrates how to integrate the JARVIS system prompt
with actual computer control capabilities.

© 2025 The Pauli Effect / Jeremy Bowers
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, List

# Check dependencies
try:
    import speech_recognition as sr
    import pyttsx3
    from anthropic import Anthropic
    import psutil
    import pyautogui
    from playwright.sync_api import sync_playwright
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install faster-whisper pyttsx3 pyaudio anthropic psutil pyautogui playwright")
    sys.exit(1)


class JARVISAgent:
    """Main JARVIS agent controller"""
    
    def __init__(self, config_path: str = "~/.jarvis/config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.system_prompt = self.load_system_prompt()
        
        # Initialize components
        self.llm_client = self.init_llm()
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.conversation_history = []
        self.is_listening = False
        
        # Configure TTS
        self.tts_engine.setProperty('rate', self.config['voice']['output']['rate'])
        self.tts_engine.setProperty('volume', self.config['voice']['output']['volume'])
        
        print("✅ JARVIS initialized successfully")
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            print(f"⚠️  Config not found at {self.config_path}")
            print("Using default configuration...")
            return self.get_default_config()
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "agent": {
                "name": "JARVIS",
                "mode": "supervised",
                "voice_enabled": True
            },
            "llm": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514"
            },
            "voice": {
                "wake_words": ["hey jarvis", "computer"],
                "output": {
                    "rate": 175,
                    "volume": 0.9
                }
            },
            "safety": {
                "require_approval_for": [
                    "delete_files",
                    "system_shutdown",
                    "send_emails"
                ]
            }
        }
    
    def load_system_prompt(self) -> str:
        """Load JARVIS system prompt from XML file"""
        prompt_path = Path("~/.jarvis/JARVIS_UNIVERSAL_AGENT_LAYER.xml").expanduser()
        
        if not prompt_path.exists():
            # Fallback: use embedded abbreviated prompt
            return self.get_fallback_prompt()
        
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def get_fallback_prompt(self) -> str:
        """Abbreviated system prompt if XML not found"""
        return """You are JARVIS, a voice-controlled autonomous computer agent.

IDENTITY:
- Professional, efficient, proactive
- Speak naturally and concisely
- Explain what you're doing

CAPABILITIES:
- File operations (search, read, organize)
- Browser control (navigate, extract data)
- System commands (screenshot, process management)
- Code execution (Python, bash)

SAFETY:
- Always ask before deleting files
- Confirm before system changes
- Never execute untrusted code
- Be transparent about actions

RESPONSE FORMAT:
- Brief acknowledgment
- Action description
- Clear status updates
- Offer next steps

Example: "On it. Searching your files for design documents now."
"""
    
    def init_llm(self) -> Anthropic:
        """Initialize LLM client"""
        api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            print("⚠️  No API key found. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY")
            print("Running in demo mode with simulated responses")
            return None
        
        return Anthropic(api_key=api_key)
    
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"🗣️  JARVIS: {text}")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"⚠️  TTS error: {e}")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input"""
        with sr.Microphone() as source:
            print("🎤 Listening...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You: {text}")
                return text.lower()
            
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("⚠️  Could not understand audio")
                return None
            except Exception as e:
                print(f"⚠️  Listen error: {e}")
                return None
    
    def check_wake_word(self, text: str) -> bool:
        """Check if wake word was spoken"""
        if not text:
            return False
        
        wake_words = self.config['voice']['wake_words']
        return any(wake_word in text for wake_word in wake_words)
    
    def process_command(self, command: str) -> str:
        """Process user command through LLM"""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": command
        })
        
        # If no LLM available, use demo mode
        if not self.llm_client:
            return self.demo_response(command)
        
        # Call LLM
        try:
            response = self.llm_client.messages.create(
                model=self.config['llm']['model'],
                max_tokens=2000,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            print(f"⚠️  LLM error: {e}")
            return f"I encountered an error: {str(e)}"
    
    def demo_response(self, command: str) -> str:
        """Generate demo responses when no API available"""
        command_lower = command.lower()
        
        if "find" in command_lower and "file" in command_lower:
            return "I would search your filesystem for matching files. In demo mode, I can't actually access your files. Set up API keys to enable full functionality."
        
        elif "open" in command_lower:
            return "I would open the requested application or file. Demo mode active."
        
        elif "search" in command_lower or "research" in command_lower:
            return "I would open a browser and research that topic for you. Demo mode active."
        
        else:
            return f"I understand you want me to: {command}. However, I'm running in demo mode. Configure API keys for full functionality."
    
    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool/capability"""
        
        tools = {
            'screenshot': self.tool_screenshot,
            'search_files': self.tool_search_files,
            'system_info': self.tool_system_info,
        }
        
        if tool_name in tools:
            return tools[tool_name](**kwargs)
        else:
            return f"Tool {tool_name} not implemented"
    
    def tool_screenshot(self, filename: Optional[str] = None):
        """Take a screenshot"""
        if filename is None:
            timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"screenshot-{timestamp}.png"
        
        try:
            screenshot = pyautogui.screenshot()
            save_path = Path.home() / "Desktop" / filename
            screenshot.save(save_path)
            return f"Screenshot saved to {save_path}"
        except Exception as e:
            return f"Screenshot failed: {e}"
    
    def tool_search_files(self, query: str, directory: str = "~"):
        """Search for files"""
        search_path = Path(directory).expanduser()
        matches = []
        
        try:
            for path in search_path.rglob(f"*{query}*"):
                if path.is_file():
                    matches.append(str(path))
                    if len(matches) >= 10:  # Limit results
                        break
            
            if matches:
                return f"Found {len(matches)} files:\n" + "\n".join(matches[:5])
            else:
                return f"No files found matching '{query}'"
        
        except Exception as e:
            return f"Search failed: {e}"
    
    def tool_system_info(self):
        """Get system information"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            info = f"""System Status:
- CPU Usage: {cpu_percent}%
- Memory: {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB ({memory.percent}%)
- Available: {memory.available / (1024**3):.1f}GB
"""
            return info
        except Exception as e:
            return f"Could not get system info: {e}"
    
    def run_voice_loop(self):
        """Main voice control loop"""
        self.speak(f"{self.config['agent']['name']} online and ready. Say {self.config['voice']['wake_words'][0]} to activate.")
        
        while True:
            try:
                # Listen for wake word
                text = self.listen()
                
                if not text:
                    continue
                
                # Check for wake word
                if self.check_wake_word(text):
                    self.speak("Yes?")
                    
                    # Listen for command
                    command = self.listen()
                    
                    if not command:
                        self.speak("I didn't catch that. Please try again.")
                        continue
                    
                    # Check for exit commands
                    if any(word in command for word in ['exit', 'quit', 'goodbye', 'stop']):
                        self.speak("Goodbye. Going offline.")
                        break
                    
                    # Process command
                    self.speak("On it.")
                    response = self.process_command(command)
                    self.speak(response)
            
            except KeyboardInterrupt:
                self.speak("Shutting down.")
                break
            except Exception as e:
                print(f"⚠️  Error in voice loop: {e}")
                self.speak("I encountered an error. Please try again.")
    
    def run_text_mode(self):
        """Run in text input mode (for testing)"""
        print(f"\n{'='*60}")
        print(f"{self.config['agent']['name']} - Text Mode")
        print(f"{'='*60}\n")
        print("Type your commands. Type 'exit' to quit.\n")
        
        while True:
            try:
                command = input("You: ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'goodbye']:
                    print("\n👋 Goodbye!")
                    break
                
                # Process command
                print(f"\n🤖 JARVIS: Processing...\n")
                response = self.process_command(command)
                print(f"🤖 JARVIS: {response}\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Universal Agent")
    parser.add_argument('--voice', action='store_true', help='Enable voice control')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode')
    
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════╗
║  🤖 JARVIS Universal Agent v2.0        ║
║  Voice-Controlled Autonomous AI        ║
║  © 2025 The Pauli Effect              ║
╚════════════════════════════════════════╝
    """)
    
    # Initialize agent
    config_path = args.config or "~/.jarvis/config.json"
    agent = JARVISAgent(config_path)
    
    # Run appropriate mode
    if args.voice:
        print("\n🎤 Voice mode activated")
        print(f"Say '{agent.config['voice']['wake_words'][0]}' to activate\n")
        agent.run_voice_loop()
    else:
        print("\n⌨️  Text mode (use --voice for voice control)")
        agent.run_text_mode()


if __name__ == "__main__":
    main()
