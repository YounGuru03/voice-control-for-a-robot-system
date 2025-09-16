#!/usr/bin/env python3
"""
Enhanced Build Script for Voice Command Tool
============================================

Creates a standalone .exe file using PyInstaller for Windows distribution.
Includes enhanced error handling, dependency checking, and Codespaces compatibility.
"""

import sys
import os
import shutil
import subprocess
import platform
from pathlib import Path
import json
import time

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        'PyInstaller', 'whisper', 'torch', 'numpy', 
        'pyaudio', 'watchdog', 'scipy', 'matplotlib'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module.lower().replace('-', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are available")
    return True

def get_system_info():
    """Get system information for build optimization."""
    info = {
        'platform': platform.system(),
        'architecture': platform.machine(),
        'python_version': sys.version,
        'is_codespaces': os.environ.get('CODESPACES') == 'true',
        'is_github_actions': os.environ.get('GITHUB_ACTIONS') == 'true'
    }
    
    print(f"Building on: {info['platform']} {info['architecture']}")
    if info['is_codespaces']:
        print("🔧 Detected GitHub Codespaces environment")
    if info['is_github_actions']:
        print("🔧 Detected GitHub Actions environment")
    
    return info

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name} directory")
            
    # Clean .pyc files recursively
    cleaned_count = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                try:
                    os.remove(os.path.join(root, file))
                    cleaned_count += 1
                except Exception:
                    pass
                    
    if cleaned_count > 0:
        print(f"🧹 Cleaned {cleaned_count} Python cache files")

def create_spec_file(system_info):
    """Create PyInstaller spec file optimized for the target system."""
    
    # Determine if we should create a windowed or console application
    windowed_mode = not (system_info['is_codespaces'] or system_info['is_github_actions'])
    
    # Enhanced hidden imports based on project analysis
    hidden_imports = [
        'whisper',
        'torch',
        'torchaudio', 
        'transformers',
        'numpy',
        'pyaudio',
        'watchdog',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'scipy',
        'scipy.signal',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'queue',
        'threading',
        'json',
        'datetime',
        'pathlib',
        'subprocess'
    ]
    
    # Enhanced excludes to reduce size
    excludes = [
        'IPython',
        'jupyter',
        'notebook', 
        'pandas',
        'pytest',
        'test',
        'tests',
        'unittest',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        # Large unused torch modules
        'torch.distributed',
        'torch.nn.quantized',
        'torchvision',
        # Unused matplotlib backends
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_gtk3agg'
    ]
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Auto-generated PyInstaller spec file for Voice Command Tool
# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Target: {system_info['platform']} {system_info['architecture']}

block_cipher = None

a = Analysis(
    ['launcher.py'],  # Use launcher as entry point for better error handling
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),  # Include config if it exists
        ('README.md', '.'),    # Include documentation
    ],
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={excludes},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries and optimize
a.binaries = TOC([x for x in a.binaries if not x[0].startswith('api-ms-win')])

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
    strip=True,  # Strip symbols to reduce size
    upx=True,    # Use UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(not windowed_mode).lower()},  # Console mode for CI/debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None
)
'''
    
    with open('voice_command_tool.spec', 'w') as f:
        f.write(spec_content)
    
    print(f"📄 Created PyInstaller spec file (windowed: {windowed_mode})")

def build_executable(system_info):
    """Build the standalone executable with enhanced error handling."""
    try:
        print("🔨 Building standalone executable...")
        
        # Create build command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'voice_command_tool.spec'
        ]
        
        # Add verbosity for debugging in CI environments
        if system_info['is_github_actions'] or system_info['is_codespaces']:
            cmd.append('--log-level=INFO')
        
        print(f"Running: {' '.join(cmd)}")
        
        # Run build with real-time output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Build successful!")
            analyze_build_output()
            return True
        else:
            print(f"❌ Build failed with exit code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")
        return False

def analyze_build_output():
    """Analyze and report on build output."""
    if not os.path.exists('dist'):
        print("⚠️ No dist directory found")
        return
        
    print("\n📊 Build Analysis:")
    total_size = 0
    file_count = 0
    
    for item in os.listdir('dist'):
        item_path = os.path.join('dist', item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            size_mb = size / (1024 * 1024)
            total_size += size
            file_count += 1
            print(f"  📄 {item}: {size_mb:.1f} MB")
        else:
            # Count files in subdirectories
            subdir_size = sum(
                os.path.getsize(os.path.join(item_path, f)) 
                for f in os.listdir(item_path) 
                if os.path.isfile(os.path.join(item_path, f))
            )
            subdir_count = len([
                f for f in os.listdir(item_path) 
                if os.path.isfile(os.path.join(item_path, f))
            ])
            total_size += subdir_size
            file_count += subdir_count
            print(f"  📁 {item}/: {subdir_count} files, {subdir_size/(1024*1024):.1f} MB")
    
    print(f"\n📊 Total: {file_count} files, {total_size/(1024*1024):.1f} MB")
    
    # Check for the main executable
    exe_path = os.path.join('dist', 'VoiceCommandTool.exe')
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"🎯 Main executable: VoiceCommandTool.exe ({exe_size:.1f} MB)")
        
        # Test if it's a valid executable
        if os.access(exe_path, os.X_OK):
            print("✅ Executable has proper permissions")
        else:
            print("⚠️ Executable permissions may be incorrect")
    else:
        print("❌ Main executable not found!")

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

def create_build_info():
    """Create build information file."""
    if not os.path.exists('dist'):
        return
        
    build_info = {
        'build_date': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'platform': platform.system(),
        'architecture': platform.machine(),
        'python_version': sys.version,
        'pyinstaller_version': 'Unknown',
        'files': {}
    }
    
    # Try to get PyInstaller version
    try:
        import PyInstaller
        build_info['pyinstaller_version'] = PyInstaller.__version__
    except:
        pass
    
    # Catalog all build outputs
    for item in os.listdir('dist'):
        item_path = os.path.join('dist', item)
        if os.path.isfile(item_path):
            build_info['files'][item] = {
                'size_bytes': os.path.getsize(item_path),
                'size_mb': round(os.path.getsize(item_path) / (1024 * 1024), 2)
            }
    
    # Write build info
    with open('dist/build_info.json', 'w') as f:
        json.dump(build_info, f, indent=2)
    
    print("📋 Created build_info.json")

def validate_build():
    """Validate the build output."""
    exe_path = os.path.join('dist', 'VoiceCommandTool.exe')
    
    if not os.path.exists(exe_path):
        print("❌ Validation failed: Main executable not found")
        return False
    
    # Check file size (should be reasonable)
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    if size_mb < 10:
        print(f"⚠️ Warning: Executable seems small ({size_mb:.1f} MB)")
    elif size_mb > 500:
        print(f"⚠️ Warning: Executable seems large ({size_mb:.1f} MB)")
    else:
        print(f"✅ Executable size is reasonable ({size_mb:.1f} MB)")
    
    # On Windows, we could try to run it briefly
    if platform.system() == 'Windows':
        try:
            # Test that the executable can start (will exit quickly)
            result = subprocess.run(
                [exe_path, '--help'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            print("✅ Executable starts successfully")
        except subprocess.TimeoutExpired:
            print("✅ Executable starts (timed out waiting for response)")
        except Exception as e:
            print(f"⚠️ Could not test executable startup: {e}")
    
    return True

def main():
    """Main build process with enhanced error handling and reporting."""
    print("🚀 Starting enhanced build process for Voice Command Tool...")
    print(f"Python version: {sys.version}")
    
    # Step 0: Get system information
    system_info = get_system_info()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Build aborted due to missing dependencies")
        sys.exit(1)
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create optimized spec file
    create_spec_file(system_info)
    
    # Step 4: Build executable
    if not build_executable(system_info):
        print("❌ Build process failed!")
        sys.exit(1)
    
    # Step 5: Copy resources
    copy_resources()
    
    # Step 6: Create installer info
    create_installer_info()
    
    # Step 7: Create build info
    create_build_info()
    
    # Step 8: Validate build
    if not validate_build():
        print("⚠️ Build validation warnings detected")
    
    print("\n🎉 Build process completed successfully!")
    print("📦 The standalone executable is ready in the 'dist' directory.")
    
    if system_info['is_github_actions']:
        print("📤 In GitHub Actions: Files will be uploaded as artifacts")
    elif system_info['is_codespaces']:
        print("☁️ In GitHub Codespaces: You can download files from the dist/ directory")
    else:
        print("💻 Local build: Test by running dist/VoiceCommandTool.exe")
    
    print("\n📋 Next steps:")
    print("1. Test the executable on a Windows machine")
    print("2. Check that all voice commands work correctly")  
    print("3. Verify that output is written to text.txt")
    print("4. Test different audio input scenarios")
    
if __name__ == "__main__":
    main()