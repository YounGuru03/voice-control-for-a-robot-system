#!/usr/bin/env python3
"""
Build Script for Voice Command Tool
===================================

Creates a standalone .exe file using PyInstaller for Windows distribution.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")
            
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_spec_file():
    """Create PyInstaller spec file for better control."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'whisper',
        'torch',
        'torchaudio',
        'transformers',
        'numpy',
        'pyaudio',
        'watchdog',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
        'pandas',
        'scipy.spatial.distance',
        'test',
        'tests',
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
    name='VoiceCommandTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
    version='version_info.txt'  # Add version info if needed
)
'''
    
    with open('voice_command_tool.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")

def build_executable():
    """Build the standalone executable."""
    try:
        print("Building standalone executable...")
        
        # Use the spec file for building
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'voice_command_tool.spec'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Build successful!")
            print("Executable created in dist/ directory")
            
            # List the contents of dist directory
            if os.path.exists('dist'):
                print("\nBuild output:")
                for item in os.listdir('dist'):
                    item_path = os.path.join('dist', item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path) / (1024 * 1024)
                        print(f"  {item} ({size:.1f} MB)")
                    else:
                        print(f"  {item}/ (directory)")
        else:
            print("Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"Error during build: {str(e)}")
        return False
        
    return True

def copy_resources():
    """Copy necessary resource files to dist directory."""
    if not os.path.exists('dist'):
        return
        
    resources = ['README.md', 'LICENSE']
    
    for resource in resources:
        if os.path.exists(resource):
            try:
                shutil.copy2(resource, 'dist/')
                print(f"Copied {resource} to dist/")
            except Exception as e:
                print(f"Warning: Could not copy {resource}: {str(e)}")

def create_installer_info():
    """Create information file for the installer."""
    info_content = """Voice Command Tool v1.0
=========================

This is a standalone Windows application for offline voice command recognition.

Requirements:
- Windows 10/11 x64
- 4GB RAM minimum
- Microphone access

Features:
- Offline speech recognition using Whisper-small
- No GPU or internet required
- Lightweight GUI
- Real-time command processing
- File monitoring capabilities

Usage:
1. Run VoiceCommandTool.exe
2. Click "Start Listening"
3. Speak commands clearly
4. Commands are saved to text.txt

For support or issues, please refer to the project repository.
"""
    
    if os.path.exists('dist'):
        with open('dist/README.txt', 'w') as f:
            f.write(info_content)
        print("Created README.txt in dist/")

def main():
    """Main build process."""
    print("Starting build process for Voice Command Tool...")
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Create spec file
    create_spec_file()
    
    # Step 3: Build executable
    if not build_executable():
        print("Build process failed!")
        sys.exit(1)
    
    # Step 4: Copy resources
    copy_resources()
    
    # Step 5: Create installer info
    create_installer_info()
    
    print("\nBuild process completed successfully!")
    print("The standalone executable is ready in the 'dist' directory.")
    print("\nTo test the build:")
    print("1. Navigate to the 'dist' directory")
    print("2. Run 'VoiceCommandTool.exe'")
    
if __name__ == "__main__":
    main()