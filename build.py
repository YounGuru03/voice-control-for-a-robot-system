# Build Script for EXE Packaging
# Creates standalone Windows executable

import os
import sys
import shutil
import subprocess


def build_exe():
    """Package application as EXE"""

    print("=" * 60)
    print("VOICE CONTROL SYSTEM - EXE BUILDER")
    print("=" * 60)
    print()

    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")

    if os.path.exists('VoiceControl.spec'):
        os.remove('VoiceControl.spec')
        print("   Removed VoiceControl.spec")

    print("✅ Clean complete\n")

    # Build command
    print("📦 Building EXE...")
    print()

    cmd = [
        'pyinstaller',
        '--name=VoiceControl',
        '--onefile',
        '--windowed',
        '--add-data=NTU.png;.' if os.path.exists('NTU.png') else '--noupx',
        '--hidden-import=faster_whisper',
        '--hidden-import=pyaudio',
        '--hidden-import=PIL',
        '--hidden-import=numpy',
        '--hidden-import=tkinter',
        'main_app.py'
    ]

    # Remove empty args
    cmd = [arg for arg in cmd if arg and arg != '--noupx']

    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, shell=True)

    print()
    print("=" * 60)

    if result.returncode == 0:
        print("✅ BUILD SUCCESSFUL!")
        print()
        print("📁 Output location:")
        print(f"   {os.path.abspath('dist/VoiceControl.exe')}")
        print()
        print("📋 Deployment checklist:")
        print("   ✓ Copy dist/VoiceControl.exe")
        print("   ✓ Copy NTU.png (if exists)")
        print("   ✓ Optionally copy commands.json")
        print("   ✓ Optionally copy speakers.json")
        print()
        print("⚠️  First run requires internet to download Whisper model (~141MB)")
        print("   Model will be cached to %LOCALAPPDATA%")
    else:
        print("❌ BUILD FAILED!")
        print()
        print("Common fixes:")
        print("   1. Ensure PyInstaller is installed: pip install pyinstaller")
        print("   2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   3. Check for missing imports in main_app.py")
        print("   4. Try running: python main_app.py first to verify it works")
        sys.exit(1)

    print("=" * 60)


if __name__ == '__main__':
    build_exe()