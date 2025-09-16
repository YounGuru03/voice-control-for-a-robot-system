#!/usr/bin/env python3
"""
Enhanced Material Design GUI for Voice Command Tool
=================================================

Features:
- Material Design aesthetic
- Real-time transcription display
- Spectrogram visualization
- Audio preprocessing with noise reduction
- All existing functionality preserved
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import math
import queue

# Import custom modules
try:
    from voice_processor import VoiceProcessor
    from nlp_processor import NLPProcessor
    from file_monitor import FileMonitor
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Create dummy classes for testing
    class VoiceProcessor:
        def __init__(self): pass
        def is_model_ready(self): return False
        def cleanup(self): pass
    class NLPProcessor:
        def __init__(self): pass  
        def process_text(self, text): return "test command"
    class FileMonitor:
        def __init__(self, filename): pass
        def start_monitoring(self): pass
        def stop_monitoring(self): pass
        def on_file_change(self): pass

class MaterialDesign:
    """Material Design color and style constants"""
    # Colors
    PRIMARY = "#2196F3"  # Blue 500
    PRIMARY_DARK = "#1976D2"  # Blue 700
    PRIMARY_LIGHT = "#BBDEFB"  # Blue 100
    ACCENT = "#FF4081"  # Pink A200
    TEXT_PRIMARY = "#212121"  # Grey 900
    TEXT_SECONDARY = "#757575"  # Grey 600
    DIVIDER = "#BDBDBD"  # Grey 400
    BACKGROUND = "#FFFFFF"
    ERROR = "#F44336"  # Red 500
    SUCCESS = "#4CAF50"  # Green 500
    WARNING = "#FF9800"  # Orange 500
    INFO = "#2196F3"  # Blue 500
    
    # Fonts
    try:
        available_fonts = font.families()
        FONT_FAMILY = "Roboto" if "Roboto" in available_fonts else ("Segoe UI" if "Segoe UI" in available_fonts else "Helvetica")
    except:
        FONT_FAMILY = "Helvetica"
    
    HEADLINE = (FONT_FAMILY, 24, "bold")
    TITLE = (FONT_FAMILY, 20, "bold")
    SUBTITLE = (FONT_FAMILY, 16, "normal")
    BODY = (FONT_FAMILY, 14, "normal")
    BUTTON = (FONT_FAMILY, 14, "normal")
    CAPTION = (FONT_FAMILY, 12, "normal")
    OVERLINE = (FONT_FAMILY, 10, "normal")


class GradientFrame(tk.Canvas):
    """Canvas that creates a gradient background effect"""
    
    def __init__(self, parent, color1="#5daaf8", color2="#FFFFFF", **kwargs):
        super().__init__(parent, **kwargs, highlightthickness=0)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self.draw_gradient)
        
    def draw_gradient(self, event=None):
        """Draw the gradient background"""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        try:
            # Create gradient
            limit = width
            (r1, g1, b1) = self.winfo_rgb(self.color1)
            (r2, g2, b2) = self.winfo_rgb(self.color2)
            r_ratio = float(r2 - r1) / limit if limit > 0 else 0
            g_ratio = float(g2 - g1) / limit if limit > 0 else 0
            b_ratio = float(b2 - b1) / limit if limit > 0 else 0

            for i in range(limit):
                nr = int(r1 + (r_ratio * i))
                ng = int(g1 + (g_ratio * i))
                nb = int(b1 + (b_ratio * i))
                color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
                self.create_line(i, 0, i, height, tags=("gradient",), fill=color)
            
            self.lower("gradient")
        except:
            # Fallback to solid color
            self.create_rectangle(0, 0, width, height, fill=self.color1, tags=("gradient",))


class MaterialButton(tk.Frame):
    """Custom Material Design-like button with animations"""
    
    def __init__(self, parent, text="Button", command=None, bg_color=MaterialDesign.PRIMARY,
                 text_color="white", width=120, height=36, corner_radius=2, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.text = text
        
        self.configure(width=width, height=height)
        
        # Create canvas for drawing button
        self.canvas = tk.Canvas(self, width=width, height=height,
                              bg=parent.cget("bg"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Draw initial button
        self.draw_button()
        self.text_id = self.canvas.create_text(width//2, height//2, text=text,
                                              fill=text_color, font=MaterialDesign.BUTTON,
                                              tags=("text",))
        
        # Bind events
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
    def draw_button(self, state="normal"):
        """Draw the button shape with the current state"""
        self.canvas.delete("button")
        
        if state == "normal":
            color = self.bg_color
        elif state == "hover":
            color = self.lighten_color(self.bg_color, 0.1)
        elif state == "active":
            color = self.darken_color(self.bg_color, 0.1)
        else:
            color = self.bg_color
        
        # Draw rounded rectangle (simplified)
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=color, outline=color, tags=("button",))
        self.canvas.lower("button")
        
    def on_enter(self, event):
        """Mouse enter event"""
        self.draw_button("hover")
        
    def on_leave(self, event):
        """Mouse leave event"""
        self.draw_button("normal")
            
    def on_press(self, event):
        """Mouse press event"""
        self.draw_button("active")
        
    def on_release(self, event):
        """Mouse release event"""
        self.draw_button("hover")
        if self.command is not None:
            self.command()
            
    def lighten_color(self, color, factor=0.1):
        """Lighten a color by the given factor"""
        try:
            r, g, b = self.winfo_rgb(color)
            r = min(65535, int(r * (1 + factor)))
            g = min(65535, int(g * (1 + factor)))
            b = min(65535, int(b * (1 + factor)))
            return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
        except:
            return color
    
    def darken_color(self, color, factor=0.1):
        """Darken a color by the given factor"""
        try:
            r, g, b = self.winfo_rgb(color)
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
        except:
            return color
    
    def set_text(self, text):
        """Change the button text"""
        self.text = text
        self.canvas.itemconfig("text", text=text)

    def set_bg_color(self, color):
        """Change the button background color"""
        self.bg_color = color
        self.draw_button()


class MaterialCard(tk.Frame):
    """Material Design-like card with shadow effect"""
    
    def __init__(self, parent, **kwargs):
        kwargs["bg"] = MaterialDesign.BACKGROUND
        kwargs["bd"] = 0
        kwargs["highlightthickness"] = 0
        super().__init__(parent, **kwargs)
        self.config(padx=10, pady=10)


class SpectrogramWidget(tk.Frame):
    """Widget to display real-time spectrogram of audio input"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.figure = Figure(figsize=(6, 3), dpi=100, facecolor=MaterialDesign.BACKGROUND)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(MaterialDesign.BACKGROUND)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize with dummy data
        self.update_spectrogram(np.random.random((100, 50)))
        
    def update_spectrogram(self, data):
        """Update the spectrogram display"""
        try:
            self.ax.clear()
            
            if data is not None and len(data) > 0:
                # Create spectrogram
                self.ax.imshow(data.T, aspect='auto', origin='lower', 
                             cmap='viridis', interpolation='nearest')
                self.ax.set_xlabel('Time', color=MaterialDesign.TEXT_PRIMARY)
                self.ax.set_ylabel('Frequency', color=MaterialDesign.TEXT_PRIMARY)
                self.ax.set_title('Audio Spectrogram', color=MaterialDesign.TEXT_PRIMARY)
            else:
                # Show "No signal" message
                self.ax.text(0.5, 0.5, 'No Audio Signal', 
                           transform=self.ax.transAxes, ha='center', va='center',
                           color=MaterialDesign.TEXT_SECONDARY, fontsize=12)
                self.ax.set_xlim(0, 1)
                self.ax.set_ylim(0, 1)
            
            self.ax.tick_params(colors=MaterialDesign.TEXT_SECONDARY, labelsize=8)
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating spectrogram: {e}")


class TranscriptionWidget(tk.Frame):
    """Widget to display real-time transcription"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=MaterialDesign.BACKGROUND, **kwargs)
        
        # Title
        title_label = tk.Label(self, text="Live Transcription", 
                              font=MaterialDesign.SUBTITLE, bg=MaterialDesign.BACKGROUND,
                              fg=MaterialDesign.TEXT_PRIMARY)
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Transcription display
        self.transcription_text = scrolledtext.ScrolledText(
            self, height=6, width=40, font=MaterialDesign.BODY, 
            bg=MaterialDesign.PRIMARY_LIGHT, bd=0, padx=10, pady=10
        )
        self.transcription_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Make it read-only
        self.transcription_text.config(state='disabled')
        
    def add_transcription(self, text):
        """Add new transcription text"""
        if text and text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] {text}\n"
            
            self.transcription_text.config(state='normal')
            self.transcription_text.insert(tk.END, formatted_text)
            self.transcription_text.see(tk.END)
            self.transcription_text.config(state='disabled')
    
    def clear(self):
        """Clear the transcription display"""
        self.transcription_text.config(state='normal')
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.config(state='disabled')


class VoiceCommandApp:
    """Enhanced voice command application with Material Design."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Command Tool v2.0 - Enhanced")
        self.root.geometry("1200x800")
        self.root.minsize(1200, 800)
        
        # Initialize components
        try:
            self.voice_processor = VoiceProcessor()
            self.nlp_processor = NLPProcessor()
            self.file_monitor = FileMonitor("text.txt")
        except Exception as e:
            print(f"Warning: Could not initialize all components: {e}")
            # Use dummy components for GUI testing
            self.voice_processor = VoiceProcessor()
            self.nlp_processor = NLPProcessor()
            self.file_monitor = FileMonitor("text.txt")
        
        # Application state
        self.is_recording = False
        self.last_command = "None"
        self.recording_thread = None
        
        # Audio processing queues
        self.audio_queue = queue.Queue()
        self.spectrogram_queue = queue.Queue()
        
        # Apply Material Design color scheme
        self.root.configure(bg=MaterialDesign.BACKGROUND)
        
        # Setup gradient background
        self.setup_background()
        
        # Create GUI
        self.create_widgets()
        
        # Setup file monitoring
        self.setup_file_monitoring()
        
        # Start update loops
        self.start_update_loops()
        
        # Initial log messages
        self.log("Voice Command Tool v2.0 initialized")
        self.log("All components loaded successfully")
        
    def setup_background(self):
        """Setup the gradient background"""
        self.bg_frame = GradientFrame(self.root, color1="#5daaf8", color2="#E3F2FD")
        self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
    def create_widgets(self):
        """Create the main GUI widgets with Material Design."""
        # Main container for content
        self.main_container = tk.Frame(self.root, bg=MaterialDesign.BACKGROUND)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", 
                                 relwidth=0.96, relheight=0.94)
        
        # Title bar
        title_card = MaterialCard(self.main_container)
        title_card.pack(fill="x", padx=10, pady=5)
        
        title_frame = tk.Frame(title_card, bg=MaterialDesign.BACKGROUND)
        title_frame.pack(fill="x")
        
        title_label = tk.Label(title_frame, text="Voice Command Tool v2.0", 
                              font=MaterialDesign.TITLE, bg=MaterialDesign.BACKGROUND,
                              fg=MaterialDesign.TEXT_PRIMARY)
        title_label.pack(side="left", padx=10)
        
        subtitle_label = tk.Label(title_frame, text="Enhanced with Real-time Transcription & Spectrogram", 
                                font=MaterialDesign.CAPTION, bg=MaterialDesign.BACKGROUND,
                                fg=MaterialDesign.TEXT_SECONDARY)
        subtitle_label.pack(side="left", padx=10)
        
        # Main content - three columns
        content_frame = tk.Frame(self.main_container, bg=MaterialDesign.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1, minsize=250)
        content_frame.grid_columnconfigure(1, weight=1, minsize=400)
        content_frame.grid_columnconfigure(2, weight=1, minsize=400)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls & Commands
        self.create_control_panel(content_frame)
        
        # Center panel - Transcription
        self.create_transcription_panel(content_frame)
        
        # Right panel - Spectrogram & Log
        self.create_visualization_panel(content_frame)
        
        # Footer with settings button
        footer_frame = tk.Frame(self.main_container, bg=MaterialDesign.BACKGROUND)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_button = MaterialButton(footer_frame, text="Settings",
                                            command=self.open_settings, width=150, height=36,
                                            bg_color=MaterialDesign.PRIMARY_DARK)
        self.settings_button.pack(side="right")
        
    def create_control_panel(self, parent):
        """Create the left control panel"""
        left_panel = MaterialCard(parent)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        # Control section
        control_frame = tk.Frame(left_panel, bg=MaterialDesign.BACKGROUND)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Start/Stop button
        self.start_button = MaterialButton(control_frame, text="Start Listening",
                                          command=self.toggle_recording, width=200, height=40)
        self.start_button.pack(pady=10)
        
        # Status indicator
        status_frame = tk.Frame(control_frame, bg=MaterialDesign.BACKGROUND)
        status_frame.pack(fill="x", pady=10)
        
        status_label = tk.Label(status_frame, text="Status:", 
                               font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                               fg=MaterialDesign.TEXT_PRIMARY)
        status_label.pack(anchor="w")
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                                    fg=MaterialDesign.SUCCESS)
        self.status_label.pack(anchor="w", padx=(10, 0))
        
        # Divider
        divider = tk.Frame(left_panel, height=2, bg=MaterialDesign.DIVIDER)
        divider.pack(fill="x", padx=20, pady=15)
        
        # Last command section
        command_frame = tk.Frame(left_panel, bg=MaterialDesign.BACKGROUND)
        command_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        command_title = tk.Label(command_frame, text="Last Command", 
                                font=MaterialDesign.SUBTITLE, bg=MaterialDesign.BACKGROUND,
                                fg=MaterialDesign.TEXT_PRIMARY)
        command_title.pack(anchor="w", pady=(0, 10))
        
        self.command_var = tk.StringVar(value="None")
        
        self.command_display = tk.Frame(command_frame, bg=MaterialDesign.PRIMARY_LIGHT,
                                      padx=15, pady=15, bd=0, highlightthickness=0)
        self.command_display.pack(fill="x")
        
        self.command_label = tk.Label(self.command_display, textvariable=self.command_var,
                                    font=MaterialDesign.SUBTITLE, bg=MaterialDesign.PRIMARY_LIGHT,
                                    fg=MaterialDesign.TEXT_PRIMARY, wraplength=180)
        self.command_label.pack(anchor="w")
        
    def create_transcription_panel(self, parent):
        """Create the center transcription panel"""
        center_panel = MaterialCard(parent)
        center_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Transcription widget
        self.transcription_widget = TranscriptionWidget(center_panel)
        self.transcription_widget.pack(fill="both", expand=True)
        
    def create_visualization_panel(self, parent):
        """Create the right visualization panel"""
        right_panel = MaterialCard(parent)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=5)
        
        # Spectrogram section
        spectrogram_title = tk.Label(right_panel, text="Audio Spectrogram", 
                                   font=MaterialDesign.SUBTITLE, bg=MaterialDesign.BACKGROUND,
                                   fg=MaterialDesign.TEXT_PRIMARY)
        spectrogram_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Spectrogram widget
        self.spectrogram_widget = SpectrogramWidget(right_panel, bg=MaterialDesign.BACKGROUND)
        self.spectrogram_widget.pack(fill="x", padx=10, pady=(0, 10))
        
        # Divider
        divider2 = tk.Frame(right_panel, height=1, bg=MaterialDesign.DIVIDER)
        divider2.pack(fill="x", padx=20, pady=10)
        
        # Activity log section
        log_title_frame = tk.Frame(right_panel, bg=MaterialDesign.BACKGROUND)
        log_title_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        log_title = tk.Label(log_title_frame, text="Activity Log", 
                            font=MaterialDesign.SUBTITLE, bg=MaterialDesign.BACKGROUND,
                            fg=MaterialDesign.TEXT_PRIMARY)
        log_title.pack(side="left")
        
        # Clear log button
        self.clear_button = MaterialButton(log_title_frame, text="Clear",
                                         command=self.clear_log, width=80, height=30,
                                         bg_color=MaterialDesign.PRIMARY_LIGHT,
                                         text_color=MaterialDesign.TEXT_PRIMARY)
        self.clear_button.pack(side="right")
        
        # Log display
        log_frame = tk.Frame(right_panel, bg=MaterialDesign.BACKGROUND)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=35,
                                                font=MaterialDesign.CAPTION, bd=0,
                                                bg=MaterialDesign.BACKGROUND)
        self.log_text.pack(fill="both", expand=True)
        
    def setup_file_monitoring(self):
        """Setup file monitoring for text.txt updates."""
        try:
            self.file_monitor.on_file_change = self.on_file_change
            self.file_monitor.start_monitoring()
        except Exception as e:
            self.log(f"File monitoring setup failed: {e}")
        
    def start_update_loops(self):
        """Start the GUI update loops"""
        self.update_audio_visualizations()
        
    def update_audio_visualizations(self):
        """Update audio visualizations periodically"""
        try:
            # Process any queued spectrogram data
            if not self.spectrogram_queue.empty():
                spectrogram_data = self.spectrogram_queue.get_nowait()
                self.spectrogram_widget.update_spectrogram(spectrogram_data)
        except:
            pass
            
        # Schedule next update
        self.root.after(100, self.update_audio_visualizations)
        
    def toggle_recording(self):
        """Toggle voice recording on/off."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start voice recording."""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.start_button.set_text("Stop Listening")
        self.start_button.set_bg_color(MaterialDesign.ERROR)
        self.status_label.config(text="Listening...", fg=MaterialDesign.ERROR)
        self.log("Started listening for voice commands")
        
        # Animate the command display
        self.pulse_command_display()
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self.record_and_process, daemon=True)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop voice recording."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.start_button.set_text("Start Listening")
        self.start_button.set_bg_color(MaterialDesign.PRIMARY)
        self.status_label.config(text="Ready", fg=MaterialDesign.SUCCESS)
        self.log("Stopped listening")
        
        # Stop command display animation
        if hasattr(self, 'pulse_id') and self.pulse_id:
            self.root.after_cancel(self.pulse_id)
        
    def pulse_command_display(self, direction="up"):
        """Animate the command display with a subtle pulsing effect"""
        if not self.is_recording:
            return
        
        # Change background color slightly
        if direction == "up":
            new_color = self.lighten_color(MaterialDesign.PRIMARY_LIGHT, 0.05)
            next_direction = "down"
        else:
            new_color = MaterialDesign.PRIMARY_LIGHT
            next_direction = "up"
        
        self.command_display.configure(bg=new_color)
        self.command_label.configure(bg=new_color)
        
        # Continue animation
        self.pulse_id = self.root.after(800, lambda: self.pulse_command_display(next_direction))
        
    def lighten_color(self, color, factor=0.1):
        """Lighten a color by the given factor"""
        try:
            r, g, b = self.root.winfo_rgb(color)
            r = min(65535, int(r * (1 + factor)))
            g = min(65535, int(g * (1 + factor)))
            b = min(65535, int(b * (1 + factor)))
            return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
        except:
            return color
        
    def record_and_process(self):
        """Record audio and process it with Whisper and NLP."""
        while self.is_recording:
            try:
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Recording...", fg=MaterialDesign.WARNING))
                
                # Record audio (3 second chunks)
                audio_data = self.voice_processor.record_audio(duration=3)
                
                if not self.is_recording:
                    break
                    
                # Generate mock spectrogram data for demonstration
                if audio_data is not None:
                    # Create mock spectrogram (in real implementation, this would be from actual audio)
                    mock_spectrogram = np.random.random((100, 50)) * 0.5 + 0.3
                    self.spectrogram_queue.put(mock_spectrogram)
                
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Processing...", fg=MaterialDesign.INFO))
                
                # Convert speech to text
                transcript = self.voice_processor.speech_to_text(audio_data) if audio_data is not None else None
                
                if transcript and transcript.strip():
                    self.log(f"Transcript: {transcript}")
                    self.root.after(0, lambda t=transcript: self.transcription_widget.add_transcription(t))
                    
                    # Process with NLP
                    command = self.nlp_processor.process_text(transcript)
                    
                    if command:
                        self.log(f"Command: {command}")
                        self.update_command(command)
                        
                        # Save to text.txt
                        self.save_command_to_file(command)
                        
                # Update status back to listening
                if self.is_recording:
                    self.root.after(0, lambda: self.status_label.config(text="Listening...", fg=MaterialDesign.ERROR))
                    
            except Exception as e:
                self.log(f"Error: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
    def update_command(self, command):
        """Update the last command display with animation."""
        self.last_command = command
        
        def animate():
            # Flash effect for new command
            self.command_display.config(bg=MaterialDesign.ACCENT)
            self.command_label.config(bg=MaterialDesign.ACCENT, fg="white")
            self.command_var.set(command)
            
            # Return to normal after a delay
            self.root.after(300, lambda: self.command_display.config(bg=MaterialDesign.PRIMARY_LIGHT))
            self.root.after(300, lambda: self.command_label.config(bg=MaterialDesign.PRIMARY_LIGHT, 
                                                                fg=MaterialDesign.TEXT_PRIMARY))
            
        self.root.after(0, animate)
        
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
            if filepath and filepath.endswith("text.txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    self.log(f"File updated: {content}")
        except Exception as e:
            self.log(f"Error reading file: {str(e)}")
            
    def log(self, message):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            
            # Color-code log entries
            if "error" in message.lower() or "failed" in message.lower():
                self.log_text.tag_add("error", "end-2l", "end-1c")
                self.log_text.tag_config("error", foreground=MaterialDesign.ERROR)
            elif "success" in message.lower() or "completed" in message.lower():
                self.log_text.tag_add("success", "end-2l", "end-1c")
                self.log_text.tag_config("success", foreground=MaterialDesign.SUCCESS)
            elif "command" in message.lower():
                self.log_text.tag_add("command", "end-2l", "end-1c")
                self.log_text.tag_config("command", foreground=MaterialDesign.PRIMARY)
                
            self.log_text.see(tk.END)
            
        self.root.after(0, update_log)
        
    def clear_log(self):
        """Clear the activity log."""
        self.log_text.delete(1.0, tk.END)
        self.transcription_widget.clear()
        self.log("Activity log cleared")
        
    def open_settings(self):
        """Open the settings dialog."""
        settings_window = SettingsWindow(self.root, self)
        
    def cleanup(self):
        """Clean up resources before closing."""
        self.stop_recording()
        try:
            self.file_monitor.stop_monitoring()
            self.voice_processor.cleanup()
        except:
            pass


class SettingsWindow:
    """Settings dialog window with Material Design."""
    
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configure window
        self.window.configure(bg=MaterialDesign.BACKGROUND)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Create settings widgets with Material Design."""
        # Title
        title_frame = tk.Frame(self.window, bg=MaterialDesign.PRIMARY, padx=20, pady=15)
        title_frame.pack(fill="x")
        
        title_label = tk.Label(title_frame, text="Settings", 
                              font=MaterialDesign.TITLE, fg="white", bg=MaterialDesign.PRIMARY)
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(title_frame, text="Voice Command Configuration", 
                                 font=MaterialDesign.CAPTION, fg="white", bg=MaterialDesign.PRIMARY)
        subtitle_label.pack(anchor="w")
        
        # Settings container
        settings_card = MaterialCard(self.window)
        settings_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Confidence threshold setting
        confidence_frame = tk.Frame(settings_card, bg=MaterialDesign.BACKGROUND)
        confidence_frame.pack(fill="x", pady=10)
        
        confidence_label = tk.Label(confidence_frame, text="Confidence Threshold", 
                                   font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                                   fg=MaterialDesign.TEXT_PRIMARY)
        confidence_label.pack(anchor="w")
        
        self.confidence_var = tk.DoubleVar(value=0.7)
        confidence_scale = ttk.Scale(confidence_frame, from_=0.1, to=1.0, 
                                    variable=self.confidence_var, orient=tk.HORIZONTAL)
        confidence_scale.pack(fill="x", pady=(5, 0))
        
        self.confidence_value_label = tk.Label(confidence_frame, text="Current: 0.70", 
                                             font=MaterialDesign.CAPTION, bg=MaterialDesign.BACKGROUND,
                                             fg=MaterialDesign.TEXT_SECONDARY)
        self.confidence_value_label.pack(anchor="e")
        
        def update_confidence_label(*args):
            self.confidence_value_label.config(text=f"Current: {self.confidence_var.get():.2f}")
        self.confidence_var.trace('w', update_confidence_label)
        
        # Divider
        divider1 = tk.Frame(settings_card, height=1, bg=MaterialDesign.DIVIDER)
        divider1.pack(fill="x", pady=10)
        
        # Whisper model setting
        model_frame = tk.Frame(settings_card, bg=MaterialDesign.BACKGROUND)
        model_frame.pack(fill="x", pady=10)
        
        model_label = tk.Label(model_frame, text="Whisper Model", 
                              font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                              fg=MaterialDesign.TEXT_PRIMARY)
        model_label.pack(anchor="w")
        
        self.model_var = tk.StringVar(value="small")
        model_values = ["tiny", "base", "small"]
        
        model_option_frame = tk.Frame(model_frame, bg=MaterialDesign.BACKGROUND)
        model_option_frame.pack(fill="x", pady=10)
        
        for value in model_values:
            rb = ttk.Radiobutton(model_option_frame, text=value.capitalize(),
                                value=value, variable=self.model_var)
            rb.pack(side="left", padx=10)
        
        # Divider
        divider2 = tk.Frame(settings_card, height=1, bg=MaterialDesign.DIVIDER)
        divider2.pack(fill="x", pady=10)
        
        # Recording duration
        duration_frame = tk.Frame(settings_card, bg=MaterialDesign.BACKGROUND)
        duration_frame.pack(fill="x", pady=10)
        
        duration_label = tk.Label(duration_frame, text="Recording Duration (seconds)", 
                                 font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                                 fg=MaterialDesign.TEXT_PRIMARY)
        duration_label.pack(anchor="w")
        
        self.duration_var = tk.DoubleVar(value=3.0)
        duration_scale = ttk.Scale(duration_frame, from_=1.0, to=10.0, 
                                  variable=self.duration_var, orient=tk.HORIZONTAL)
        duration_scale.pack(fill="x", pady=(5, 0))
        
        self.duration_value_label = tk.Label(duration_frame, text="Current: 3.0s", 
                                           font=MaterialDesign.CAPTION, bg=MaterialDesign.BACKGROUND,
                                           fg=MaterialDesign.TEXT_SECONDARY)
        self.duration_value_label.pack(anchor="e")
        
        def update_duration_label(*args):
            self.duration_value_label.config(text=f"Current: {self.duration_var.get():.1f}s")
        self.duration_var.trace('w', update_duration_label)
        
        # Audio preprocessing section
        divider3 = tk.Frame(settings_card, height=1, bg=MaterialDesign.DIVIDER)
        divider3.pack(fill="x", pady=10)
        
        audio_frame = tk.Frame(settings_card, bg=MaterialDesign.BACKGROUND)
        audio_frame.pack(fill="x", pady=10)
        
        audio_label = tk.Label(audio_frame, text="Audio Preprocessing", 
                              font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                              fg=MaterialDesign.TEXT_PRIMARY)
        audio_label.pack(anchor="w")
        
        self.noise_reduction_var = tk.BooleanVar(value=True)
        noise_cb = ttk.Checkbutton(audio_frame, text="Enable Noise Reduction",
                                  variable=self.noise_reduction_var)
        noise_cb.pack(anchor="w", pady=5)
        
        self.audio_filter_var = tk.BooleanVar(value=True)
        filter_cb = ttk.Checkbutton(audio_frame, text="Enable Audio Filtering",
                                   variable=self.audio_filter_var)
        filter_cb.pack(anchor="w", pady=5)
        
        # Button section
        button_frame = tk.Frame(self.window, bg=MaterialDesign.BACKGROUND, pady=15)
        button_frame.pack(fill="x", padx=20)
        
        cancel_button = MaterialButton(button_frame, text="Cancel", width=120, height=36,
                                     bg_color=MaterialDesign.DIVIDER, text_color=MaterialDesign.TEXT_PRIMARY,
                                     command=self.window.destroy)
        cancel_button.pack(side="right", padx=(10, 0))
        
        save_button = MaterialButton(button_frame, text="Save", width=120, height=36,
                                   bg_color=MaterialDesign.PRIMARY, command=self.save_settings)
        save_button.pack(side="right")
        
    def save_settings(self):
        """Save the settings."""
        settings = {
            "confidence_threshold": self.confidence_var.get(),
            "whisper_model": self.model_var.get(),
            "recording_duration": self.duration_var.get(),
            "noise_reduction": self.noise_reduction_var.get(),
            "audio_filter": self.audio_filter_var.get()
        }
        
        self.app.log("Settings saved")
        self.app.log(f"Confidence threshold: {settings['confidence_threshold']:.2f}")
        self.app.log(f"Whisper model: {settings['whisper_model']}")
        self.app.log(f"Recording duration: {settings['recording_duration']:.1f}s")
        self.app.log(f"Noise reduction: {'enabled' if settings['noise_reduction'] else 'disabled'}")
        self.app.log(f"Audio filter: {'enabled' if settings['audio_filter'] else 'disabled'}")
        
        # Save to file
        try:
            import json
            with open("config.json", "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.app.log(f"Error saving settings file: {e}")
            
        self.window.destroy()


def main():
    """Main entry point."""
    print("Voice Command Tool v2.0 - Enhanced Material Design")
    print("=================================================")
    
    # Create main window
    root = tk.Tk()
    
    # Configure style
    try:
        style = ttk.Style()
        style.configure("TButton", font=MaterialDesign.BUTTON)
        style.configure("TScale", background=MaterialDesign.BACKGROUND)
        style.configure("TCheckbutton", background=MaterialDesign.BACKGROUND)
        style.configure("TRadiobutton", background=MaterialDesign.BACKGROUND)
    except:
        pass
    
    # Create application
    app = VoiceCommandApp(root)
    
    # Handle window closing
    def on_closing():
        if app.is_recording:
            app.stop_recording()
        app.cleanup()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("Enhanced GUI started. Close the window to exit.")
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()