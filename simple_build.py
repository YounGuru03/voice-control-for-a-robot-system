#!/usr/bin/env python3
"""
Simple Build Script
===================

Streamlined build script for creating standalone executable
with minimal dependencies and optimal size.
"""

import sys
import os
import shutil
from pathlib import Path
import subprocess

def check_requirements():
    """Check if build requirements are available"""
    try:
        import PyInstaller
        print("✅ PyInstaller available")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def create_spec_file():
    """Create PyInstaller spec file for optimized build"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['voice_control.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'numpy',
        'whisper',
        'scipy',
        'watchdog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude heavy visualization
        'PIL',         # Exclude image processing
        'cv2',         # Exclude computer vision
        'torch.nn',    # Exclude unused torch components
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceControlRobot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('voice_control.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created optimized spec file")

def build_executable():
    """Build the standalone executable"""
    print("🔨 Building executable...")
    
    try:
        # Use the spec file for optimized build
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'voice_control.spec'
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print("❌ Build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def optimize_build():
    """Perform post-build optimizations"""
    dist_dir = Path('dist')
    
    if not dist_dir.exists():
        return
    
    print("⚡ Optimizing build...")
    
    # Find the executable
    exe_files = list(dist_dir.glob('*.exe')) + list(dist_dir.glob('VoiceControlRobot*'))
    
    if exe_files:
        exe_file = exe_files[0]
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"📦 Executable size: {size_mb:.1f} MB")
        
        if size_mb > 200:
            print("⚠️  Large executable size - consider removing unused dependencies")

def create_readme():
    """Create a simple README for the build"""
    readme_content = """# Voice Control Robot - Standalone Executable

## Quick Start
1. Double-click `VoiceControlRobot.exe` to run
2. Click "🎤 Start Listening" 
3. Speak robot commands clearly

## System Requirements
- Windows 10/11 (64-bit)
- Microphone access
- 2+ GB available RAM

## Supported Commands
- "open main" - Open main application
- "start robot" - Start robot system  
- "open lamp" - Control lamp
- "emergency stop" - Emergency stop
- "open camera 1-4" - Camera controls
- And many more...

## Troubleshooting
- Ensure microphone permissions are granted
- Close other audio applications if needed
- Run as administrator if file access issues occur

Built with Python and optimized for performance.
"""
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    
    print("📄 Created user README")

def main():
    """Main build process"""
    print("🚀 Voice Control Robot - Build Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create optimized spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Optimize and document
    optimize_build()
    create_readme()
    
    print("\n🎉 Build completed successfully!")
    print("📁 Check the 'dist' folder for your executable")
    
    return 0

if __name__ == "__main__":
    exit(main())