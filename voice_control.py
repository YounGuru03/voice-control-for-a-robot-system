#!/usr/bin/env python3
"""
Voice Control for Robot System
==============================

A streamlined voice recognition system for robot control with a clean, 
simple interface and optimized performance.

Features:
- Lightweight voice recognition using Whisper
- Clean, responsive GUI
- Real-time command processing
- Minimal dependencies for better performance
- Designed for GitHub Codespaces compatibility
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from simple_voice_processor import create_voice_processor
    from simple_nlp_processor import create_nlp_processor  
    from simple_file_monitor import create_file_monitor
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Running in demo mode - voice recognition disabled")
    MODULES_AVAILABLE = False

class VoiceControlApp:
    """Main application class for the voice control system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Control for Robot System v2.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Application state
        self.is_listening = False
        self.voice_processor = None
        self.nlp_processor = None
        self.file_monitor = None
        
        # Initialize components
        self.setup_ui()
        self.setup_processors()
        
        # Configuration
        self.config_file = "config.json"
        self.output_file = "text.txt"
        self.load_config()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Control System", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Last Command:").grid(row=1, column=0, sticky=tk.W)
        self.command_label = ttk.Label(status_frame, text="None")
        self.command_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="🎤 Start Listening", 
                                     command=self.toggle_listening, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.show_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Open Output", 
                  command=self.open_output_file).pack(side=tk.LEFT)
        
        # Transcription display
        transcription_frame = ttk.LabelFrame(main_frame, text="Live Transcription", padding="10")
        transcription_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        transcription_frame.columnconfigure(0, weight=1)
        transcription_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        self.transcription_text = scrolledtext.ScrolledText(transcription_frame, height=8, wrap=tk.WORD)
        self.transcription_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Activity log
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize with welcome message
        self.log_message("Voice Control System started", "INFO")
        self.log_message("Click 'Start Listening' to begin voice recognition", "INFO")
        
    def setup_processors(self):
        """Initialize voice and NLP processors"""
        try:
            if MODULES_AVAILABLE:
                self.voice_processor = create_voice_processor()
                self.nlp_processor = create_nlp_processor()
                self.file_monitor = create_file_monitor(self.output_file)
                self.log_message("All processors initialized successfully", "SUCCESS")
            else:
                self.log_message("Running in demo mode - limited functionality", "WARNING")
        except Exception as e:
            self.log_message(f"Processor initialization failed: {str(e)}", "ERROR")
            self.log_message("Running in demo mode", "WARNING")
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "confidence_threshold": 0.7,
            "whisper_model": "small",
            "recording_duration": 3.0,
            "noise_reduction": True,
            "audio_filter": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            self.config = default_config
            self.log_message(f"Config load failed, using defaults: {str(e)}", "WARNING")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_message(f"Config save failed: {str(e)}", "ERROR")
    
    def toggle_listening(self):
        """Start or stop voice listening"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start voice recognition in background thread"""
        if not self.voice_processor:
            messagebox.showerror("Error", "Voice processor not available. Please check dependencies.")
            return
            
        self.is_listening = True
        self.start_button.config(text="⏹️ Stop Listening")
        self.status_label.config(text="Listening...", foreground="orange")
        self.log_message("Started voice recognition", "INFO")
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        self.start_button.config(text="🎤 Start Listening")
        self.status_label.config(text="Ready", foreground="green")
        self.log_message("Stopped voice recognition", "INFO")
    
    def listen_loop(self):
        """Main listening loop (runs in background thread)"""
        while self.is_listening:
            try:
                # Record audio
                audio_text = self.voice_processor.record_and_transcribe()
                
                if audio_text and audio_text.strip():
                    # Update transcription display
                    self.root.after(0, lambda: self.update_transcription(audio_text))
                    
                    # Process command
                    command = self.nlp_processor.process_text(audio_text)
                    
                    if command != "None":
                        self.root.after(0, lambda: self.handle_command(command, audio_text))
                        
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"Listening error: {str(e)}", "ERROR"))
                break
                
            time.sleep(0.1)  # Small delay to prevent CPU overload
    
    def update_transcription(self, text):
        """Update the transcription display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transcription_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.transcription_text.see(tk.END)
    
    def handle_command(self, command, original_text):
        """Process and execute a recognized command"""
        self.command_label.config(text=command)
        self.log_message(f"Command recognized: {command} (from: '{original_text}')", "COMMAND")
        
        # Write command to output file
        try:
            with open(self.output_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp}: {command}\n")
        except Exception as e:
            self.log_message(f"Failed to write command to file: {str(e)}", "ERROR")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Settings frame
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration options
        ttk.Label(frame, text="Whisper Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_var = tk.StringVar(value=self.config.get("whisper_model", "small"))
        ttk.Combobox(frame, textvariable=model_var, values=["tiny", "base", "small"], 
                    state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Confidence Threshold:").grid(row=1, column=0, sticky=tk.W, pady=5)
        confidence_var = tk.DoubleVar(value=self.config.get("confidence_threshold", 0.7))
        ttk.Scale(frame, from_=0.1, to=1.0, variable=confidence_var, 
                 orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Recording Duration (s):").grid(row=2, column=0, sticky=tk.W, pady=5)
        duration_var = tk.DoubleVar(value=self.config.get("recording_duration", 3.0))
        ttk.Scale(frame, from_=1.0, to=10.0, variable=duration_var, 
                 orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Checkboxes
        noise_var = tk.BooleanVar(value=self.config.get("noise_reduction", True))
        ttk.Checkbutton(frame, text="Enable Noise Reduction", 
                       variable=noise_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        filter_var = tk.BooleanVar(value=self.config.get("audio_filter", True))
        ttk.Checkbutton(frame, text="Enable Audio Filter", 
                       variable=filter_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        def save_settings():
            self.config.update({
                "whisper_model": model_var.get(),
                "confidence_threshold": confidence_var.get(),
                "recording_duration": duration_var.get(),
                "noise_reduction": noise_var.get(),
                "audio_filter": filter_var.get()
            })
            self.save_config()
            self.log_message("Settings saved successfully", "SUCCESS")
            settings_window.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT)
    
    def open_output_file(self):
        """Open the output file in system default editor"""
        import subprocess
        import sys
        
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w') as f:
                f.write("# Voice Control Commands\n")
        
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['open', self.output_file])
            elif sys.platform.startswith('win'):  # Windows
                os.startfile(self.output_file)
            else:  # Linux
                subprocess.call(['xdg-open', self.output_file])
        except Exception as e:
            messagebox.showinfo("Output File", f"Commands are saved to: {os.path.abspath(self.output_file)}")
    
    def log_message(self, message, level="INFO"):
        """Add a message to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "blue",
            "SUCCESS": "green", 
            "WARNING": "orange",
            "ERROR": "red",
            "COMMAND": "purple"
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        
        # Color the last line
        line_start = self.log_text.index("end-1c linestart")
        line_end = self.log_text.index("end-1c lineend")
        
        if level in color_map:
            self.log_text.tag_add(level, line_start, line_end)
            self.log_text.tag_config(level, foreground=color_map[level])
        
        self.log_text.see(tk.END)
    
    def run(self):
        """Start the application"""
        try:
            # Set up proper cleanup on close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Clean up and close the application"""
        if self.is_listening:
            self.stop_listening()
        
        if self.voice_processor:
            self.voice_processor.cleanup()
        
        self.root.destroy()

def main():
    """Main entry point"""
    print("Voice Control for Robot System v2.0")
    print("=" * 40)
    
    app = VoiceControlApp()
    app.run()

if __name__ == "__main__":
    main()