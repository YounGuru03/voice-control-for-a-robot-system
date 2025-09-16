#!/usr/bin/env python3
"""
Development Environment Setup Script
====================================

Sets up the development environment for both local and Codespaces use.
Handles dependency installation, environment checking, and basic validation.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def get_environment_info():
    """Detect the current environment."""
    env_info = {
        'platform': platform.system(),
        'python_version': sys.version,
        'is_codespaces': os.environ.get('CODESPACES') == 'true',
        'is_github_actions': os.environ.get('GITHUB_ACTIONS') == 'true',
        'is_windows': platform.system() == 'Windows',
        'is_linux': platform.system() == 'Linux',
        'has_display': bool(os.environ.get('DISPLAY'))
    }
    
    print("🔍 Environment Detection:")
    for key, value in env_info.items():
        print(f"  {key}: {value}")
    
    return env_info

def install_system_dependencies(env_info):
    """Install system-level dependencies based on environment."""
    if env_info['is_linux'] and not env_info['is_github_actions']:
        print("📦 Installing Linux system dependencies...")
        
        commands = [
            ['sudo', 'apt-get', 'update'],
            ['sudo', 'apt-get', 'install', '-y', 'portaudio19-dev', 'python3-tk', 'ffmpeg']
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ Executed: {' '.join(cmd)}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Warning: {' '.join(cmd)} failed: {e}")
            except FileNotFoundError:
                print(f"⚠️ Warning: Command not found: {cmd[0]}")
    
    elif env_info['is_windows']:
        print("🪟 Windows detected - system dependencies should be handled by conda/pip")
    
    else:
        print("ℹ️ Skipping system dependencies (CI environment or unsupported platform)")

def install_python_dependencies(env_info, use_minimal=False):
    """Install Python dependencies with environment-specific handling."""
    
    requirements_file = 'requirements-minimal.txt' if use_minimal else 'requirements.txt'
    
    if not os.path.exists(requirements_file):
        print(f"⚠️ Requirements file {requirements_file} not found, skipping pip install")
        return False
    
    print(f"📦 Installing Python dependencies from {requirements_file}...")
    
    # Upgrade pip first
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ pip upgrade failed: {e}")
    
    # Install dependencies with retries for network issues
    max_retries = 3 if env_info['is_codespaces'] else 1
    
    for attempt in range(max_retries):
        try:
            cmd = [
                sys.executable, '-m', 'pip', 'install', 
                '--timeout', '300',
                '-r', requirements_file
            ]
            
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("⏳ Retrying in 30 seconds...")
                import time
                time.sleep(30)
    
    print(f"❌ Failed to install dependencies after {max_retries} attempts")
    return False

def validate_installation():
    """Validate that key components can be imported."""
    print("🔍 Validating installation...")
    
    critical_modules = ['json', 'os', 'sys', 'pathlib', 'subprocess']
    optional_modules = ['whisper', 'torch', 'pyaudio', 'numpy', 'watchdog']
    
    success_count = 0
    
    # Test critical modules
    print("  Critical modules:")
    for module in critical_modules:
        try:
            __import__(module)
            print(f"    ✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"    ❌ {module}: {e}")
    
    # Test optional modules
    print("  Optional modules:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"    ✅ {module}")
        except ImportError as e:
            print(f"    ⚠️  {module}: {e}")
    
    if success_count == len(critical_modules):
        print("✅ Core functionality should work")
        return True
    else:
        print("❌ Critical modules missing - some functionality may not work")
        return False

def create_sample_config():
    """Create a sample configuration file."""
    config = {
        "confidence_threshold": 0.7,
        "whisper_model": "small",
        "recording_duration": 3.0,
        "noise_reduction": True,
        "audio_filter": True,
        "output_file": "text.txt",
        "log_level": "INFO"
    }
    
    config_path = Path('config.json')
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Created sample config.json")
    else:
        print("ℹ️ config.json already exists")

def show_next_steps(env_info):
    """Show next steps based on environment."""
    print("\n🎯 Next Steps:")
    
    if env_info['is_codespaces']:
        print("☁️ GitHub Codespaces Environment:")
        print("  1. Dependencies should now be installed")
        print("  2. Test the build system: python build.py")
        print("  3. For full functionality, install complete dependencies:")
        print("     pip install -r requirements.txt")
        print("  4. Use the GitHub Actions workflow to build Windows exe")
    
    elif env_info['is_windows']:
        print("🪟 Windows Environment:")
        print("  1. Install complete dependencies: pip install -r requirements.txt")
        print("  2. Test the application: python launcher.py")
        print("  3. Build executable: python build.py")
        print("  4. Test the exe: dist/VoiceCommandTool.exe")
    
    else:
        print("🐧 Linux Environment:")
        print("  1. Install complete dependencies: pip install -r requirements.txt")
        print("  2. Test components: python test_components.py")
        print("  3. Use GitHub Actions for Windows exe building")
    
    print("\n📚 Documentation:")
    print("  - README.md: General information")
    print("  - README_NATIVE.md: Native Rust version info")
    print("  - Build logs will be in build-logs/ directory")

def main():
    """Main setup process."""
    print("🚀 Voice Control Development Environment Setup")
    print("=" * 50)
    
    # Step 1: Detect environment
    env_info = get_environment_info()
    
    # Step 2: Install system dependencies if needed
    install_system_dependencies(env_info)
    
    # Step 3: Install Python dependencies (use minimal for CI/testing)
    use_minimal = env_info['is_github_actions'] or env_info['is_codespaces']
    if not install_python_dependencies(env_info, use_minimal):
        print("⚠️ Continuing with partial setup...")
    
    # Step 4: Validate installation
    validate_installation()
    
    # Step 5: Create sample config
    create_sample_config()
    
    # Step 6: Show next steps
    show_next_steps(env_info)
    
    print("\n✅ Setup complete!")

if __name__ == "__main__":
    main()