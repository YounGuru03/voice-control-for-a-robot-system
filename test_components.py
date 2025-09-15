#!/usr/bin/env python3
"""
Test Script for Voice Command Tool Components
=============================================

Tests the individual modules before packaging.
"""

import sys
import os
import time
import tempfile
import threading

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nlp_processor():
    """Test the NLP processor functionality."""
    print("=== Testing NLP Processor ===")
    
    try:
        from nlp_processor import NLPProcessor
        
        nlp = NLPProcessor()
        
        # Test cases
        test_cases = [
            "move forward please",
            "um, can you go left",
            "turn right now",
            "stop the robot",
            "open main application",
            "emergency stop",
            "help me please",
        ]
        
        print("Testing command extraction:")
        for test_text in test_cases:
            command = nlp.process_text(test_text)
            print(f"  '{test_text}' -> '{command}'")
        
        print("NLP Processor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"NLP Processor test failed: {str(e)}")
        return False

def test_file_monitor():
    """Test the file monitor functionality."""
    print("\n=== Testing File Monitor ===")
    
    try:
        from file_monitor import FileMonitor
        
        # Create temporary test file
        test_file = "test_monitor.txt"
        
        # Setup monitor
        monitor = FileMonitor(test_file)
        
        # Callback to track changes
        changes_detected = []
        
        def on_change(filepath):
            changes_detected.append(filepath)
            print(f"  File changed: {os.path.basename(filepath)}")
        
        monitor.on_file_change = on_change
        
        # Start monitoring
        monitor.start_monitoring()
        print("Started file monitoring...")
        
        # Test writing to file
        print("Writing to file...")
        monitor.write_file("test content")
        
        # Wait a bit for the event
        time.sleep(0.5)
        
        # Test appending to file
        print("Appending to file...")
        monitor.append_to_file("\nmore content")
        
        # Wait a bit for the event
        time.sleep(0.5)
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print(f"Detected {len(changes_detected)} file changes")
        print("File Monitor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"File Monitor test failed: {str(e)}")
        return False

def test_voice_processor_initialization():
    """Test voice processor initialization (without actually recording)."""
    print("\n=== Testing Voice Processor Initialization ===")
    
    try:
        from voice_processor import VoiceProcessor
        
        # Test initialization
        print("Initializing voice processor...")
        processor = VoiceProcessor(model_name="tiny")  # Use tiny model for faster testing
        
        # Wait a bit for model loading
        print("Waiting for model to load...")
        timeout = 30  # 30 seconds timeout
        start_time = time.time()
        
        while not processor.is_model_ready() and (time.time() - start_time) < timeout:
            time.sleep(1)
            print("  Still loading...")
        
        if processor.is_model_ready():
            print("Voice processor initialized successfully!")
            processor.cleanup()
            return True
        else:
            print("Voice processor failed to load model within timeout")
            processor.cleanup()
            return False
            
    except Exception as e:
        print(f"Voice Processor test failed: {str(e)}")
        return False

def test_gui_imports():
    """Test that GUI components can be imported."""
    print("\n=== Testing GUI Imports ===")
    
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext, messagebox
        
        # Test creating a simple window (don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test creating widgets
        frame = ttk.Frame(root)
        button = ttk.Button(frame, text="Test")
        label = ttk.Label(frame, text="Test")
        text = scrolledtext.ScrolledText(frame, height=5, width=20)
        
        # Clean up
        root.destroy()
        
        print("GUI imports and basic widget creation successful!")
        return True
        
    except Exception as e:
        print(f"GUI import test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Voice Command Tool - Component Tests")
    print("=" * 40)
    
    results = []
    
    # Run tests
    results.append(("NLP Processor", test_nlp_processor()))
    results.append(("File Monitor", test_file_monitor()))
    results.append(("GUI Imports", test_gui_imports()))
    results.append(("Voice Processor Init", test_voice_processor_initialization()))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The application should work correctly.")
    else:
        print("Some tests failed. Please check the error messages above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)