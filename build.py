"""
============================================================================
build.py - Executable Packaging Script for Voice Control System
============================================================================

This script packages the Voice Control System into a standalone Windows executable
using PyInstaller, including all dependencies and the Faster-Whisper model.

TEAM MEMBERS: How to modify model packaging
--------------------------------------------
To package different Whisper models or add additional models:

1. CHANGE DEFAULT MODEL SIZE:
   - Modify MODEL_SIZE variable below (options: 'tiny', 'base', 'small')
   - Default is 'base' (74MB, balanced performance)

2. ADD MULTIPLE MODELS:
   - Add model names to MODELS_TO_BUNDLE list
   - Models will be pre-downloaded and bundled in the executable

3. ADD VOSK OR OTHER STT MODELS:
   - Download model to local_models/vosk/ directory
   - Add --add-data line in pyinstaller_args for the model directory
   - Example: f'local_models/vosk{os.pathsep}local_models/vosk'

4. CUSTOM MODEL PATH:
   - If using custom model location, update CUSTOM_MODEL_PATH
   - Uncomment and modify the custom model --add-data line below

Usage:
    python build.py

Output:
    dist/VoiceControl.exe - Standalone executable with bundled models
============================================================================
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ============================================================================
# CONFIGURATION - Modify these variables to change packaging behavior
# ============================================================================

# Model configuration
MODEL_SIZE = 'base'  # Options: 'tiny', 'base', 'small', 'medium', 'large'
MODELS_TO_BUNDLE = ['base']  # List of models to pre-download and bundle

# Custom model path (uncomment if using custom models)
# CUSTOM_MODEL_PATH = 'path/to/custom/model'

# Application metadata
APP_NAME = 'VoiceControl'
VERSION = '1.0.0'
AUTHOR = 'Your Team Name'
DESCRIPTION = 'Offline Voice Control System with Faster-Whisper'

# Icon file (optional - create a .ico file for Windows)
ICON_FILE = None  # Set to 'app_icon.ico' if you have an icon

# ============================================================================
# Build Configuration
# ============================================================================

class VoiceControlBuilder:
    """Handles the build process for Voice Control System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        self.models_dir = self.project_root / 'local_models'
        
    def pre_download_models(self):
        """Pre-download Whisper models before packaging"""
        print("=" * 70)
        print("STEP 1: Pre-downloading Whisper models...")
        print("=" * 70)
        
        try:
            from model_manager import ModelManager
            
            model_mgr = ModelManager()
            
            for model_name in MODELS_TO_BUNDLE:
                print(f"\n📥 Downloading model: Systran/faster-whisper-{model_name}")
                success = model_mgr.download_model(f"Systran/faster-whisper-{model_name}")
                
                if success:
                    print(f"✅ Model '{model_name}' downloaded successfully")
                else:
                    print(f"⚠️  Model '{model_name}' may already exist or download failed")
            
            print(f"\n✅ Model pre-download completed")
            return True
            
        except Exception as e:
            print(f"❌ Model download error: {e}")
            print("⚠️  Continuing without pre-downloaded models...")
            return False
    
    def clean_build(self):
        """Clean previous build artifacts"""
        print("\n" + "=" * 70)
        print("STEP 2: Cleaning previous build artifacts...")
        print("=" * 70)
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                print(f"🧹 Removing: {dir_path}")
                shutil.rmtree(dir_path)
        
        # Remove spec file if exists
        spec_file = self.project_root / f'{APP_NAME}.spec'
        if spec_file.exists():
            spec_file.unlink()
            print(f"🧹 Removed: {spec_file}")
        
        print("✅ Cleanup completed\n")
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("=" * 70)
        print("STEP 3: Building executable with PyInstaller...")
        print("=" * 70)
        
        # Base PyInstaller arguments
        pyinstaller_args = [
            'main_voice_app.py',  # Main entry point
            f'--name={APP_NAME}',
            '--onefile',  # Single executable file
            '--windowed',  # No console window (GUI mode)
            '--clean',
            
            # Add application metadata
            f'--version-file=None',  # Can create version file separately
            
            # Hidden imports (modules that PyInstaller might miss)
            '--hidden-import=numpy',
            '--hidden-import=pyaudio',
            '--hidden-import=pyttsx3',
            '--hidden-import=faster_whisper',
            '--hidden-import=tkinter',
            '--hidden-import=queue',
            '--hidden-import=threading',
            
            # Add data files
            f'--add-data=commands_hotwords.json{os.pathsep}.',
            f'--add-data=requirements.txt{os.pathsep}.',
            
            # Add local models directory (including downloaded Whisper models)
            f'--add-data=local_models{os.pathsep}local_models',
            
            # Collect all required packages
            '--collect-all=faster_whisper',
            '--collect-all=pyttsx3',
            '--collect-submodules=faster_whisper',
            
            # Exclude unnecessary modules to reduce size
            '--exclude-module=matplotlib',
            '--exclude-module=scipy',
            '--exclude-module=pandas',
            '--exclude-module=PIL',
        ]
        
        # Add icon if specified
        if ICON_FILE and Path(ICON_FILE).exists():
            pyinstaller_args.append(f'--icon={ICON_FILE}')
        
        # CUSTOM MODEL PATH: Uncomment and modify if using custom models
        # if CUSTOM_MODEL_PATH and Path(CUSTOM_MODEL_PATH).exists():
        #     pyinstaller_args.append(
        #         f'--add-data={CUSTOM_MODEL_PATH}{os.pathsep}local_models/custom'
        #     )
        
        print(f"\n🔨 Building {APP_NAME}.exe...")
        print(f"   Model size: {MODEL_SIZE}")
        print(f"   Bundled models: {', '.join(MODELS_TO_BUNDLE)}")
        print(f"   Output: dist/{APP_NAME}.exe\n")
        
        try:
            # Run PyInstaller
            result = subprocess.run(
                ['pyinstaller'] + pyinstaller_args,
                check=True,
                capture_output=False
            )
            
            print(f"\n✅ Build completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Build failed with error code {e.returncode}")
            return False
        except FileNotFoundError:
            print("\n❌ PyInstaller not found!")
            print("   Install it with: pip install pyinstaller")
            return False
    
    def post_build_info(self):
        """Display post-build information"""
        print("\n" + "=" * 70)
        print("BUILD SUMMARY")
        print("=" * 70)
        
        exe_path = self.dist_dir / f'{APP_NAME}.exe'
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Executable created successfully!")
            print(f"   Location: {exe_path}")
            print(f"   Size: {size_mb:.1f} MB")
            print(f"\n📦 Bundled components:")
            print(f"   - Faster-Whisper model: {MODEL_SIZE}")
            print(f"   - Python runtime and dependencies")
            print(f"   - Audio processing engines")
            print(f"   - TTS engine (pyttsx3)")
            print(f"   - Command database")
            
            print(f"\n📋 Deployment notes:")
            print(f"   1. The executable is completely standalone")
            print(f"   2. No Python installation required on target machine")
            print(f"   3. Works offline after first run")
            print(f"   4. User data saved in: %APPDATA%\\{APP_NAME}")
            
            print(f"\n🚀 To distribute:")
            print(f"   - Share the single {APP_NAME}.exe file")
            print(f"   - Users need: Windows 10/11, microphone, speakers")
            print(f"   - Optional: Include README.md for user guidance")
            
        else:
            print(f"\n❌ Executable not found at: {exe_path}")
            print(f"   Check build logs above for errors")
        
        print("\n" + "=" * 70)
    
    def run(self):
        """Execute the complete build process"""
        print("\n" + "=" * 70)
        print(f"VOICE CONTROL SYSTEM - BUILD SCRIPT")
        print(f"Version: {VERSION}")
        print("=" * 70 + "\n")
        
        # Step 1: Pre-download models
        self.pre_download_models()
        
        # Step 2: Clean previous builds
        self.clean_build()
        
        # Step 3: Build executable
        success = self.build_executable()
        
        # Step 4: Display results
        if success:
            self.post_build_info()
        
        return success


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    print("\n🏗️  Voice Control System - Executable Builder")
    print("=" * 70 + "\n")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found!")
        print("\nPlease install it first:")
        print("   pip install pyinstaller")
        sys.exit(1)
    
    # Create builder and run
    builder = VoiceControlBuilder()
    success = builder.run()
    
    if success:
        print("\n✅ Build process completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Build process failed!")
        print("   Review the error messages above")
        sys.exit(1)
