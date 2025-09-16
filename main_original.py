#!/usr/bin/env python3
"""
Offline Windows Voice Command Tool
==================================

A lightweight voice recognition system that:
1. Uses Whisper-small for local speech-to-text conversion
2. Processes text with NLP to extract commands
3. Provides a responsive Tkinter GUI
4. Monitors output file with watchdog
5. Runs offline without GPU/cloud dependencies

Requirements: Windows 10/11 x64, 4GB RAM, <2s latency
"""

import sys
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import json
from pathlib import Path

# Import custom modules
from voice_processor import VoiceProcessor
from nlp_processor import NLPProcessor
from file_monitor import FileMonitor

class VoiceCommandApp:
    """Main application class for the voice command tool."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Command Tool v1.0")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Initialize components
        self.voice_processor = VoiceProcessor()
        self.nlp_processor = NLPProcessor()
        self.file_monitor = FileMonitor("text.txt")
        
        # Application state
        self.is_recording = False
        self.last_command = "None"
        self.recording_thread = None
        
        # Create GUI
        self.create_widgets()
        self.setup_file_monitoring()
        
        # Load settings
        self.load_settings()
        
    def create_widgets(self):
        """Create the main GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Command Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Start/Stop button
        self.start_button = ttk.Button(main_frame, text="Start Listening", 
                                      command=self.toggle_recording,
                                      width=15)
        self.start_button.grid(row=1, column=0, pady=5, padx=(0, 10))
        
        # Status indicator
        self.status_label = ttk.Label(main_frame, text="Status: Ready", 
                                     foreground="green")
        self.status_label.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Last command section
        ttk.Label(main_frame, text="Last Command:").grid(row=2, column=0, 
                                                          sticky=tk.W, pady=(20, 5))
        
        self.command_var = tk.StringVar(value="None")
        self.command_label = ttk.Label(main_frame, textvariable=self.command_var,
                                      font=("Arial", 12, "bold"),
                                      foreground="blue")
        self.command_label.grid(row=2, column=1, sticky=tk.W, pady=(20, 5))
        
        # Log display
        ttk.Label(main_frame, text="Activity Log:").grid(row=3, column=0, 
                                                          columnspan=2, sticky=tk.W, 
                                                          pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=50)
        self.log_text.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(4, weight=1)
        
        # Settings button
        settings_button = ttk.Button(main_frame, text="Settings", 
                                    command=self.open_settings)
        settings_button.grid(row=5, column=0, pady=(10, 0))
        
        # Clear log button
        clear_button = ttk.Button(main_frame, text="Clear Log", 
                                 command=self.clear_log)
        clear_button.grid(row=5, column=1, pady=(10, 0), sticky=tk.E)
        
    def setup_file_monitoring(self):
        """Setup file monitoring for text.txt updates."""
        self.file_monitor.on_file_change = self.on_file_change
        self.file_monitor.start_monitoring()
        
    def toggle_recording(self):
        """Toggle voice recording on/off."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start voice recording in a separate thread."""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.start_button.config(text="Stop Listening")
        self.status_label.config(text="Status: Listening...", foreground="red")
        self.log("Started listening for voice commands")
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self.record_and_process, daemon=True)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop voice recording."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.start_button.config(text="Start Listening")
        self.status_label.config(text="Status: Ready", foreground="green")
        self.log("Stopped listening")
        
    def record_and_process(self):
        """Record audio and process it with Whisper and NLP."""
        while self.is_recording:
            try:
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Status: Recording...", foreground="orange"))
                
                # Record audio (3 second chunks)
                audio_data = self.voice_processor.record_audio(duration=3)
                
                if not self.is_recording:
                    break
                    
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Status: Processing...", foreground="blue"))
                
                # Convert speech to text
                transcript = self.voice_processor.speech_to_text(audio_data)
                
                if transcript and transcript.strip():
                    self.log(f"Transcript: {transcript}")
                    
                    # Process with NLP
                    command = self.nlp_processor.process_text(transcript)
                    
                    if command:
                        self.log(f"Command: {command}")
                        self.update_command(command)
                        
                        # Save to text.txt
                        self.save_command_to_file(command)
                        
                # Update status back to listening
                if self.is_recording:
                    self.root.after(0, lambda: self.status_label.config(text="Status: Listening...", foreground="red"))
                    
            except Exception as e:
                self.log(f"Error: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
    def update_command(self, command):
        """Update the last command display."""
        self.last_command = command
        self.root.after(0, lambda: self.command_var.set(command))
        
    def save_command_to_file(self, command):
        """Save the command to text.txt file."""
        try:
            with open("text.txt", "w", encoding="utf-8") as f:
                f.write(command)
        except Exception as e:
            self.log(f"Error saving command: {str(e)}")
            
    def on_file_change(self, filepath):
        """Handle file changes from the file monitor."""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    self.log(f"File updated: {content}")
        except Exception as e:
            self.log(f"Error reading file: {str(e)}")
            
    def log(self, message):
        """Add a message to the activity log."""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            
        self.root.after(0, update_log)
        
    def clear_log(self):
        """Clear the activity log."""
        self.log_text.delete(1.0, tk.END)
        
    def open_settings(self):
        """Open the settings dialog."""
        settings_window = SettingsWindow(self.root, self)
        
    def load_settings(self):
        """Load settings from config file."""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    settings = json.load(f)
                    # Apply settings to processors
                    if "confidence_threshold" in settings:
                        self.nlp_processor.confidence_threshold = settings["confidence_threshold"]
        except Exception as e:
            self.log(f"Error loading settings: {str(e)}")
            
    def save_settings(self, settings):
        """Save settings to config file."""
        try:
            with open("config.json", "w") as f:
                json.dump(settings, f, indent=2)
            self.log("Settings saved")
        except Exception as e:
            self.log(f"Error saving settings: {str(e)}")
            
    def cleanup(self):
        """Clean up resources before closing."""
        self.stop_recording()
        self.file_monitor.stop_monitoring()


class SettingsWindow:
    """Settings dialog window."""
    
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create settings widgets."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Confidence threshold setting
        ttk.Label(main_frame, text="Confidence Threshold:").pack(anchor=tk.W, pady=(0, 5))
        
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(main_frame, from_=0.1, to=1.0, 
                                   variable=self.confidence_var, orient=tk.HORIZONTAL)
        confidence_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Whisper model setting
        ttk.Label(main_frame, text="Whisper Model:").pack(anchor=tk.W, pady=(0, 5))
        
        self.model_var = tk.StringVar(value="small")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var,
                                  values=["tiny", "base", "small"])
        model_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def save_settings(self):
        """Save the current settings."""
        settings = {
            "confidence_threshold": self.confidence_var.get(),
            "whisper_model": self.model_var.get()
        }
        
        self.app.save_settings(settings)
        self.app.load_settings()  # Reload settings
        self.window.destroy()


def main():
    """Main entry point."""
    # Create main window
    root = tk.Tk()
    
    # Create application
    app = VoiceCommandApp(root)
    
    # Handle window closing
    def on_closing():
        app.cleanup()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()