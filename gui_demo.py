#!/usr/bin/env python3
"""
GUI Demo for Voice Command Tool
==============================

Demonstrates the GUI interface without requiring all dependencies.
This can be used to preview the interface design.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import threading
from datetime import datetime

class DemoVoiceCommandApp:
    """Demo version of the voice command application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Command Tool v1.0 - Demo")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Demo state
        self.is_recording = False
        self.last_command = "None"
        self.demo_commands = [
            "move forward", "turn left", "stop", "go home", 
            "open main", "emergency stop", "status", "help"
        ]
        self.command_index = 0
        
        # Create GUI
        self.create_widgets()
        
        # Start demo log messages
        self.log("Voice Command Tool initialized (Demo Mode)")
        self.log("All components loaded successfully")
        
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
        
        # Demo notice
        demo_label = ttk.Label(main_frame, text="(Demo Mode - No Audio Processing)", 
                              font=("Arial", 10), foreground="orange")
        demo_label.grid(row=0, column=0, columnspan=2, pady=(25, 10))
        
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
        
    def toggle_recording(self):
        """Toggle demo recording on/off."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start demo recording."""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.start_button.config(text="Stop Listening")
        self.status_label.config(text="Status: Listening...", foreground="red")
        self.log("Started listening for voice commands")
        
        # Start demo processing in separate thread
        demo_thread = threading.Thread(target=self.demo_processing, daemon=True)
        demo_thread.start()
        
    def stop_recording(self):
        """Stop demo recording."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.start_button.config(text="Start Listening")
        self.status_label.config(text="Status: Ready", foreground="green")
        self.log("Stopped listening")
        
    def demo_processing(self):
        """Simulate voice processing with demo commands."""
        while self.is_recording:
            time.sleep(3)  # Simulate recording time
            
            if not self.is_recording:
                break
                
            # Simulate processing
            self.root.after(0, lambda: self.status_label.config(text="Status: Processing...", foreground="blue"))
            time.sleep(1)  # Simulate processing time
            
            if not self.is_recording:
                break
                
            # Generate demo transcript and command
            demo_transcript = f"Please {self.demo_commands[self.command_index]}"
            demo_command = self.demo_commands[self.command_index]
            self.command_index = (self.command_index + 1) % len(self.demo_commands)
            
            # Update GUI
            self.log(f"Transcript: {demo_transcript}")
            self.log(f"Command: {demo_command}")
            self.update_command(demo_command)
            
            # Simulate saving to file
            self.log(f"Saved command to text.txt: {demo_command}")
            
            # Update status back to listening
            if self.is_recording:
                self.root.after(0, lambda: self.status_label.config(text="Status: Listening...", foreground="red"))
                
    def update_command(self, command):
        """Update the last command display."""
        self.last_command = command
        self.root.after(0, lambda: self.command_var.set(command))
        
    def log(self, message):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            
        self.root.after(0, update_log)
        
    def clear_log(self):
        """Clear the activity log."""
        self.log_text.delete(1.0, tk.END)
        self.log("Activity log cleared")
        
    def open_settings(self):
        """Open the demo settings dialog."""
        settings_window = DemoSettingsWindow(self.root, self)


class DemoSettingsWindow:
    """Demo settings dialog window."""
    
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Demo")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create settings widgets."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Demo notice
        demo_label = ttk.Label(main_frame, text="Demo Mode - Settings Preview", 
                              font=("Arial", 12, "bold"), foreground="orange")
        demo_label.pack(pady=(0, 20))
        
        # Confidence threshold setting
        ttk.Label(main_frame, text="Confidence Threshold:").pack(anchor=tk.W, pady=(0, 5))
        
        self.confidence_var = tk.DoubleVar(value=0.7)
        confidence_scale = ttk.Scale(main_frame, from_=0.1, to=1.0, 
                                   variable=self.confidence_var, orient=tk.HORIZONTAL)
        confidence_scale.pack(fill=tk.X, pady=(0, 10))
        
        confidence_value_label = ttk.Label(main_frame, text="Current: 0.7")
        confidence_value_label.pack(anchor=tk.W, pady=(0, 10))
        
        def update_confidence_label(*args):
            confidence_value_label.config(text=f"Current: {self.confidence_var.get():.2f}")
        self.confidence_var.trace('w', update_confidence_label)
        
        # Whisper model setting
        ttk.Label(main_frame, text="Whisper Model:").pack(anchor=tk.W, pady=(0, 5))
        
        self.model_var = tk.StringVar(value="small")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var,
                                  values=["tiny", "base", "small"], state="readonly")
        model_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Audio settings
        ttk.Label(main_frame, text="Recording Duration (seconds):").pack(anchor=tk.W, pady=(10, 5))
        
        self.duration_var = tk.DoubleVar(value=3.0)
        duration_scale = ttk.Scale(main_frame, from_=1.0, to=10.0, 
                                  variable=self.duration_var, orient=tk.HORIZONTAL)
        duration_scale.pack(fill=tk.X, pady=(0, 10))
        
        duration_value_label = ttk.Label(main_frame, text="Current: 3.0s")
        duration_value_label.pack(anchor=tk.W, pady=(0, 10))
        
        def update_duration_label(*args):
            duration_value_label.config(text=f"Current: {self.duration_var.get():.1f}s")
        self.duration_var.trace('w', update_duration_label)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def save_settings(self):
        """Save the demo settings."""
        self.app.log("Settings saved (Demo Mode)")
        self.app.log(f"Confidence threshold: {self.confidence_var.get():.2f}")
        self.app.log(f"Whisper model: {self.model_var.get()}")
        self.app.log(f"Recording duration: {self.duration_var.get():.1f}s")
        self.window.destroy()


def main():
    """Main demo function."""
    print("Voice Command Tool - GUI Demo")
    print("=============================")
    print("Starting GUI demonstration...")
    
    # Create main window
    root = tk.Tk()
    
    # Create demo application
    app = DemoVoiceCommandApp(root)
    
    # Handle window closing
    def on_closing():
        if app.is_recording:
            app.stop_recording()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("GUI Demo started. Close the window to exit.")
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()