#!/usr/bin/env python3
"""
Setup script for Accommodation Search Agent
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_chrome():
    """Check if Chrome is installed"""
    system = platform.system().lower()
    
    if system == "linux":
        # Check for Chrome or Chromium
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✅ Chrome/Chromium found: {path}")
                return True
        print("⚠️  Chrome/Chromium not found. Please install:")
        print("   sudo apt-get install chromium-browser")
        return False
        
    elif system == "darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            print("✅ Chrome found on macOS")
            return True
        print("⚠️  Chrome not found. Please install via Homebrew:")
        print("   brew install --cask google-chrome")
        return False
        
    elif system == "windows":
        # Windows Chrome is usually in Program Files
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                print("✅ Chrome found on Windows")
                return True
        print("⚠️  Chrome not found. Please download from:")
        print("   https://www.google.com/chrome/")
        return False
    
    return False

def create_data_directory():
    """Create data directory for output files"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")

def make_executable():
    """Make CLI script executable on Unix systems"""
    if platform.system().lower() != "windows":
        try:
            os.chmod("cli_interface.py", 0o755)
            print("✅ CLI script made executable")
        except Exception as e:
            print(f"⚠️  Could not make CLI executable: {e}")

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    try:
        import selenium
        import pandas
        import numpy
        import undetected_chromedriver
        import fake_useragent
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🏨 Accommodation Search Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed - import test failed")
        sys.exit(1)
    
    # Check Chrome
    chrome_ok = check_chrome()
    
    # Create data directory
    create_data_directory()
    
    # Make executable
    make_executable()
    
    print("\n🎉 Setup completed!")
    
    if chrome_ok:
        print("\n🚀 You can now run the agent:")
        print("   python cli_interface.py")
        print("   python cli_interface.py --quick")
    else:
        print("\n⚠️  Please install Chrome browser before running the agent")
    
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
