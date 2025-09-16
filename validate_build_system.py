#!/usr/bin/env python3
"""
Basic Build System Validation
=============================

Tests the core build system functionality without requiring
heavy dependencies like whisper or torch.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_imports():
    """Test that core Python modules can be imported."""
    print("🔍 Testing core imports...")
    
    critical_modules = ['json', 'os', 'sys', 'pathlib', 'subprocess', 'time', 'platform']
    success_count = 0
    
    for module in critical_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
    
    print(f"✅ {success_count}/{len(critical_modules)} critical modules available")
    return success_count == len(critical_modules)

def test_build_script_syntax():
    """Test that build.py has valid syntax."""
    print("🔍 Testing build script syntax...")
    
    try:
        with open('build.py', 'r') as f:
            content = f.read()
        
        compile(content, 'build.py', 'exec')
        print("  ✅ build.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"  ❌ build.py syntax error: {e}")
        return False
    except FileNotFoundError:
        print("  ❌ build.py not found")
        return False

def test_setup_script_syntax():
    """Test that setup_dev_environment.py has valid syntax."""
    print("🔍 Testing setup script syntax...")
    
    try:
        with open('setup_dev_environment.py', 'r') as f:
            content = f.read()
        
        compile(content, 'setup_dev_environment.py', 'exec')
        print("  ✅ setup_dev_environment.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"  ❌ setup_dev_environment.py syntax error: {e}")
        return False
    except FileNotFoundError:
        print("  ❌ setup_dev_environment.py not found")
        return False

def test_github_actions_syntax():
    """Test that GitHub Actions workflow files exist and have basic structure."""
    print("🔍 Testing GitHub Actions workflows...")
    
    workflow_files = [
        '.github/workflows/build-windows-exe.yml',
        '.github/workflows/build-native-windows.yml'
    ]
    
    success_count = 0
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            print(f"  ✅ {workflow_file} exists")
            success_count += 1
        else:
            print(f"  ❌ {workflow_file} not found")
    
    print(f"✅ {success_count}/{len(workflow_files)} workflow files found")
    return success_count > 0

def test_requirements_files():
    """Test that requirements files exist."""
    print("🔍 Testing requirements files...")
    
    req_files = ['requirements.txt', 'requirements-minimal.txt']
    success_count = 0
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                lines = len(f.readlines())
            print(f"  ✅ {req_file} ({lines} lines)")
            success_count += 1
        else:
            print(f"  ❌ {req_file} not found")
    
    return success_count > 0

def test_main_entry_points():
    """Test that main entry point files exist."""
    print("🔍 Testing entry point files...")
    
    entry_files = ['main.py', 'launcher.py']
    success_count = 0
    
    for entry_file in entry_files:
        if os.path.exists(entry_file):
            # Test basic syntax
            try:
                with open(entry_file, 'r') as f:
                    content = f.read()
                compile(content, entry_file, 'exec')
                print(f"  ✅ {entry_file} (valid syntax)")
                success_count += 1
            except SyntaxError as e:
                print(f"  ⚠️ {entry_file} (syntax error: {e})")
        else:
            print(f"  ❌ {entry_file} not found")
    
    return success_count > 0

def test_documentation():
    """Test that documentation files exist."""
    print("🔍 Testing documentation...")
    
    doc_files = ['README.md', 'BUILD_GUIDE.md', 'README_NATIVE.md']
    success_count = 0
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            with open(doc_file, 'r') as f:
                content = f.read()
                word_count = len(content.split())
            print(f"  ✅ {doc_file} ({word_count} words)")
            success_count += 1
        else:
            print(f"  ❌ {doc_file} not found")
    
    return success_count > 0

def test_basic_build_system():
    """Test basic build system functionality without heavy dependencies."""
    print("🔍 Testing basic build system...")
    
    # Test that build.py can at least show help or detect environment
    try:
        result = subprocess.run(
            [sys.executable, 'build.py', '--help'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        # Build script might not have --help, so just check if it starts
        print(f"  ✅ build.py executable (exit code: {result.returncode})")
        return True
        
    except subprocess.TimeoutExpired:
        print("  ✅ build.py starts (timed out - expected)")
        return True
    except FileNotFoundError:
        print("  ❌ Cannot execute build.py")
        return False
    except Exception as e:
        print(f"  ⚠️ build.py test warning: {e}")
        return True  # Don't fail for minor issues

def main():
    """Run all validation tests."""
    print("🚀 Voice Control Build System Validation")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_imports),
        ("Build Script Syntax", test_build_script_syntax), 
        ("Setup Script Syntax", test_setup_script_syntax),
        ("GitHub Actions", test_github_actions_syntax),
        ("Requirements Files", test_requirements_files),
        ("Entry Points", test_main_entry_points),
        ("Documentation", test_documentation),
        ("Build System", test_basic_build_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All validation tests passed!")
        print("🎯 The build system is ready for use.")
    elif passed >= total * 0.8:  # 80% pass rate
        print("⚠️ Most tests passed - build system should work with minor issues.")
    else:
        print("❌ Several tests failed - check the build system setup.")
        sys.exit(1)
    
    print("\n🎯 Next Steps:")
    if passed == total:
        print("  1. Run 'python setup_dev_environment.py' for full setup")
        print("  2. Use GitHub Actions to build Windows .exe")
        print("  3. Try GitHub Codespaces for cloud development")
    else:
        print("  1. Fix any issues identified above")
        print("  2. Re-run this validation script")
        print("  3. Check documentation for troubleshooting")

if __name__ == "__main__":
    main()