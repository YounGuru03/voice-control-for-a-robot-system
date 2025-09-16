#!/usr/bin/env python3
"""
Voice Control System Launcher
=============================

Simple launcher for the voice control system with dependency checking
and clear error messages for better user experience.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_core_dependencies():
    """Check if core dependencies are available"""
    core_modules = ['tkinter']
    missing_modules = []
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} missing")
    
    if missing_modules:
        print("\n⚠️  Missing core dependencies. Try:")
        print("   sudo apt-get update")
        print("   sudo apt-get install python3-tk")
        return False
    
    return True

def check_optional_dependencies():
    """Check optional dependencies and provide guidance"""
    optional_modules = {
        'numpy': 'pip install numpy',
        'whisper': 'pip install openai-whisper',
        'scipy': 'pip install scipy',
        'watchdog': 'pip install watchdog'
    }
    
    available = []
    missing = []
    
    for module, install_cmd in optional_modules.items():
        try:
            __import__(module)
            available.append(module)
            print(f"✅ {module} available")
        except ImportError:
            missing.append((module, install_cmd))
            print(f"⚠️  {module} missing (voice recognition will be limited)")
    
    if missing:
        print("\n📦 To enable full functionality, install missing packages:")
        for module, cmd in missing:
            print(f"   {cmd}")
        print("   Or run: pip install -r requirements.txt")
    
    return len(available) > 0

def main():
    """Launch the voice control system"""
    print("🎤 Voice Control for Robot System v2.0")
    print("=" * 40)
    print("🔍 Checking system requirements...\n")
    
    # Check requirements
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    if not check_core_dependencies():
        input("\nPress Enter to exit...")
        return
    
    has_optional = check_optional_dependencies()
    
    if not has_optional:
        print("\n⚠️  Running with limited functionality (GUI only)")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            return
    
    print("\n🚀 Launching application...")
    
    # Import and launch main application
    try:
        from voice_control import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error importing main application: {e}")
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()