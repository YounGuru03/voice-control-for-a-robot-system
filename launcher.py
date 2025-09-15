#!/usr/bin/env python3
"""
Voice Command Tool Launcher
===========================

Entry point for the voice command application.
Handles initialization and error checking.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    # Check critical dependencies
    try:
        import whisper
    except ImportError:
        missing_deps.append("whisper (openai-whisper)")
    
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import torch
    except ImportError:
        missing_deps.append("torch")
    
    try:
        from watchdog.observers import Observer
    except ImportError:
        missing_deps.append("watchdog")
    
    return missing_deps

def show_error_dialog(title, message):
    """Show error dialog and exit."""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    messagebox.showerror(title, message)
    root.destroy()
    sys.exit(1)

def main():
    """Main launcher function."""
    print("Voice Command Tool v1.0")
    print("Starting application...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        show_error_dialog(
            "Python Version Error",
            "This application requires Python 3.8 or higher.\n"
            f"Current version: {sys.version}"
        )
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        deps_list = "\n".join(f"- {dep}" for dep in missing_deps)
        show_error_dialog(
            "Missing Dependencies",
            f"The following required packages are missing:\n\n{deps_list}\n\n"
            "Please install them using:\npip install -r requirements.txt"
        )
    
    # Import and run main application
    try:
        from main import main as run_main_app
        run_main_app()
    except Exception as e:
        show_error_dialog(
            "Application Error",
            f"Failed to start the application:\n\n{str(e)}\n\n"
            "Please check the console for detailed error information."
        )

if __name__ == "__main__":
    main()