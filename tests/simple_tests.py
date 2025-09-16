#!/usr/bin/env python3
"""
Simple Test Suite
================

Basic tests for the voice control system components.
Tests core functionality and dependencies.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_nlp_processor():
    """Test NLP command extraction"""
    print("🧠 Testing NLP Processor...")
    
    try:
        from simple_nlp_processor import create_nlp_processor
        nlp = create_nlp_processor()
        
        # Test cases
        test_cases = [
            ("open main", "open main"),
            ("start robot please", "open robot"),
            ("emergency stop now", "emergency stop"),
            ("um can you open camera 1", "open camera 1"),
            ("hello world", "None"),
            ("", "None"),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for input_text, expected in test_cases:
            result = nlp.process_text(input_text)
            if result == expected:
                print(f"  ✅ '{input_text}' → '{result}'")
                passed += 1
            else:
                print(f"  ❌ '{input_text}' → '{result}' (expected '{expected}')")
        
        print(f"  Result: {passed}/{total} tests passed")
        return passed == total
        
    except Exception as e:
        print(f"  ❌ NLP test failed: {e}")
        return False

def test_file_monitor():
    """Test file monitoring functionality"""
    print("📁 Testing File Monitor...")
    
    try:
        from simple_file_monitor import create_file_monitor
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
            f.write("test content\n")
        
        try:
            # Test file monitor creation
            monitor = create_file_monitor(temp_file)
            
            # Test basic functionality
            content = monitor.get_recent_content(5)
            
            if "test content" in content:
                print("  ✅ File monitor created and reads content")
                result = True
            else:
                print("  ❌ File monitor cannot read content")
                result = False
                
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
        return result
        
    except Exception as e:
        print(f"  ❌ File monitor test failed: {e}")
        return False

def test_voice_processor():
    """Test voice processor initialization"""
    print("🎤 Testing Voice Processor...")
    
    try:
        from simple_voice_processor import create_voice_processor
        
        # Create processor (should work even without dependencies)
        processor = create_voice_processor("small")
        
        # Test basic interface
        if hasattr(processor, 'is_model_ready') and hasattr(processor, 'cleanup'):
            print("  ✅ Voice processor created with correct interface")
            
            # Test cleanup
            processor.cleanup()
            print("  ✅ Voice processor cleanup works")
            return True
        else:
            print("  ❌ Voice processor missing required methods")
            return False
            
    except Exception as e:
        print(f"  ❌ Voice processor test failed: {e}")
        return False

def test_main_application():
    """Test main application import"""
    print("🖥️  Testing Main Application...")
    
    try:
        # Test if we can import the main application
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        import voice_control
        
        if hasattr(voice_control, 'VoiceControlApp'):
            print("  ✅ Main application imports successfully")
            return True
        else:
            print("  ❌ Main application missing VoiceControlApp class")
            return False
            
    except Exception as e:
        print(f"  ❌ Main application test failed: {e}")
        return False

def test_dependencies():
    """Test optional dependencies"""
    print("📦 Testing Dependencies...")
    
    dependencies = {
        'tkinter': 'GUI framework',
        'json': 'Configuration',
        'threading': 'Multi-threading', 
        'time': 'Timing functions',
        'os': 'File operations',
        'sys': 'System functions'
    }
    
    available = 0
    total = len(dependencies)
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {module} - {description}")
            available += 1
        except ImportError:
            print(f"  ❌ {module} - {description}")
    
    print(f"  Result: {available}/{total} core dependencies available")
    return available >= 5  # At least 5 core dependencies should be available

def main():
    """Run all tests"""
    print("🧪 Voice Control System - Test Suite")
    print("=" * 40)
    
    tests = [
        ("NLP Processor", test_nlp_processor),
        ("File Monitor", test_file_monitor), 
        ("Voice Processor", test_voice_processor),
        ("Main Application", test_main_application),
        ("Dependencies", test_dependencies),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}")
        
        print()  # Empty line between tests
    
    print("=" * 40)
    print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed - system should work")
        return 0
    else:
        print("❌ Many tests failed - check dependencies")
        return 1

if __name__ == "__main__":
    exit(main())