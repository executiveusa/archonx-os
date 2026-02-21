#!/usr/bin/env python3
"""
Orgo Desktop Controller
=======================

This script creates an Orgo desktop instance and executes autonomous tasks.
Run this script to start the AI agency build process.

Usage:
    python orgo_controller.py

Requirements:
    pip install requests pillow
"""

import requests
import time
import json
import base64
from datetime import datetime
from pathlib import Path
import os

# Configuration
API_TOKEN = os.environ.get("ORGO_API_TOKEN", "")
BASE_URL = "https://api.orgo.ai/v1"
DESKTOP_OS = "windows"  # or "linux" or "mac"
DESKTOP_DURATION = 7200  # 2 hours

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

class OrgoController:
    def __init__(self):
        self.desktop_id = None
        self.stream_url = None
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def create_desktop(self):
        """Create a new desktop instance."""
        print("🖥️  Creating Orgo desktop instance...")
        
        response = requests.post(
            f"{BASE_URL}/desktops",
            headers=HEADERS,
            json={
                "os": DESKTOP_OS,
                "duration": DESKTOP_DURATION
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.desktop_id = data.get("desktop_id")
            self.stream_url = data.get("stream_url")
            print(f"✅ Desktop created: {self.desktop_id}")
            print(f"📺 Stream URL: {self.stream_url}")
            return True
        else:
            print(f"❌ Failed to create desktop: {response.text}")
            return False
    
    def send_command(self, action, **kwargs):
        """Send a command to the desktop."""
        if not self.desktop_id:
            print("❌ No desktop ID. Create a desktop first.")
            return None
        
        payload = {"action": action, **kwargs}
        
        response = requests.post(
            f"{BASE_URL}/desktops/{self.desktop_id}/command",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Command failed: {response.text}")
            return None
    
    def wait(self, seconds):
        """Wait for specified seconds."""
        print(f"⏳ Waiting {seconds} seconds...")
        time.sleep(seconds)
    
    def screenshot(self, save=True):
        """Take a screenshot."""
        result = self.send_command("screenshot")
        if result and save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.screenshots_dir / f"screenshot_{timestamp}.png"
            
            # Save screenshot if base64 data is returned
            if "image" in result:
                image_data = base64.b64decode(result["image"])
                with open(filepath, "wb") as f:
                    f.write(image_data)
                print(f"📸 Screenshot saved: {filepath}")
        
        return result
    
    def open_url(self, url):
        """Open a URL in the browser."""
        print(f"🌐 Opening URL: {url}")
        return self.send_command("open_url", url=url)
    
    def click(self, x, y):
        """Click at coordinates."""
        print(f"🖱️  Clicking at ({x}, {y})")
        return self.send_command("click", x=x, y=y)
    
    def type_text(self, text):
        """Type text."""
        print(f"⌨️  Typing: {text[:50]}...")
        return self.send_command("type", text=text)
    
    def press_key(self, key):
        """Press a keyboard key."""
        print(f"🔑 Pressing key: {key}")
        return self.send_command("press_key", key=key)
    
    def run_terminal_command(self, command):
        """Run a terminal command."""
        print(f"💻 Running command: {command}")
        return self.send_command("run_command", command=command)
    
    def read_file(self, filepath):
        """Read a file from the desktop."""
        return self.send_command("read_file", filepath=filepath)
    
    def write_file(self, filepath, content):
        """Write a file to the desktop."""
        return self.send_command("write_file", filepath=filepath, content=content)


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 ORGO AUTONOMOUS AGENT CONTROLLER")
    print("=" * 60)
    print()
    
    # Initialize controller
    controller = OrgoController()
    
    # Step 1: Create desktop
    if not controller.create_desktop():
        return
    
    # Wait for desktop to initialize
    controller.wait(15)
    
    # Step 2: Take initial screenshot
    print("\n📸 Taking initial screenshot...")
    controller.screenshot()
    
    # Step 3: Open VS Code Web
    print("\n🌐 Opening VS Code Web...")
    controller.open_url("https://vscode.dev")
    controller.wait(10)
    controller.screenshot()
    
    # Step 4: Open a new terminal in VS Code
    print("\n💻 Opening terminal...")
    controller.press_key("ctrl+shift+`")  # VS Code terminal shortcut
    controller.wait(3)
    
    # Step 5: Clone the repository
    print("\n📦 Cloning repository...")
    controller.type_text("git clone https://github.com/executiveusa/archonx-os.git")
    controller.press_key("enter")
    controller.wait(30)
    controller.screenshot()
    
    # Step 6: Navigate to project
    print("\n📁 Navigating to project...")
    controller.type_text("cd archonx-os")
    controller.press_key("enter")
    controller.wait(2)
    
    # Step 7: Open the orgo-agent folder
    print("\n📂 Opening orgo-agent folder...")
    controller.type_text("code orgo-agent/")
    controller.press_key("enter")
    controller.wait(5)
    controller.screenshot()
    
    # Step 8: Read the handoff prompt
    print("\n📖 Reading handoff prompt...")
    controller.type_text("cat HANDOFF_PROMPT.md")
    controller.press_key("enter")
    controller.wait(2)
    controller.screenshot()
    
    print("\n" + "=" * 60)
    print("✅ INITIAL SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n📺 Watch the desktop at: {controller.stream_url}")
    print("\nNext steps:")
    print("1. The desktop is ready for autonomous operation")
    print("2. Send additional commands via the API")
    print("3. Or use MCP integration for AI control")
    print("\nDesktop ID:", controller.desktop_id)
    print("\nTo continue, run more commands or use the MCP server.")


if __name__ == "__main__":
    main()
