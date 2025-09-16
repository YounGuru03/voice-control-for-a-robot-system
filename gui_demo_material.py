#!/usr/bin/env python3
"""
GUI Demo for Voice Command Tool - Material Design Version
======================================================

Demonstrates the GUI interface with Google-inspired Material Design aesthetics
without requiring all dependencies.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import threading
from datetime import datetime
import math

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
    FONT_FAMILY = "Roboto" if "Roboto" in tk.font.families() else "Helvetica"
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
        
        # Create gradient
        limit = width
        (r1, g1, b1) = self.winfo_rgb(self.color1)
        (r2, g2, b2) = self.winfo_rgb(self.color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color)
        
        self.lower("gradient")


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
        
        self.configure(width=width, height=height)
        
        # Create canvas for drawing button
        self.canvas = tk.Canvas(self, width=width, height=height,
                              bg=parent["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Draw initial button
        self.draw_button()
        self.canvas.create_text(width//2, height//2, text=text,
                              fill=text_color, font=MaterialDesign.BUTTON,
                              tags=("text",))
        
        # Bind events
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Animation variables
        self.ripple = None
        self.ripple_id = None
        self.ripple_radius = 0
        self.animation_id = None
        
    def draw_button(self, state="normal"):
        """Draw the button shape with the current state"""
        self.canvas.delete("button")
        
        if state == "normal":
            color = self.bg_color
        elif state == "hover":
            # Slightly lighter color for hover
            color = self.lighten_color(self.bg_color, 0.1)
        elif state == "active":
            # Slightly darker color for press
            color = self.darken_color(self.bg_color, 0.1)
        
        # Draw rounded rectangle
        self.canvas.create_rectangle(
            self.corner_radius, 0,
            self.width - self.corner_radius, self.height,
            fill=color, outline=color, tags=("button",))
        self.canvas.create_rectangle(
            0, self.corner_radius,
            self.width, self.height - self.corner_radius,
            fill=color, outline=color, tags=("button",))
            
        # Draw corners
        self.canvas.create_arc(
            0, 0,
            2*self.corner_radius, 2*self.corner_radius,
            start=90, extent=90,
            fill=color, outline=color, tags=("button",))
        self.canvas.create_arc(
            self.width - 2*self.corner_radius, 0,
            self.width, 2*self.corner_radius,
            start=0, extent=90,
            fill=color, outline=color, tags=("button",))
        self.canvas.create_arc(
            0, self.height - 2*self.corner_radius,
            2*self.corner_radius, self.height,
            start=180, extent=90,
            fill=color, outline=color, tags=("button",))
        self.canvas.create_arc(
            self.width - 2*self.corner_radius, self.height - 2*self.corner_radius,
            self.width, self.height,
            start=270, extent=90,
            fill=color, outline=color, tags=("button",))
            
        self.canvas.lower("button")
        
    def on_enter(self, event):
        """Mouse enter event"""
        self.draw_button("hover")
        
    def on_leave(self, event):
        """Mouse leave event"""
        self.draw_button("normal")
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.canvas.delete("ripple")
            
    def on_press(self, event):
        """Mouse press event"""
        self.draw_button("active")
        
        # Create ripple effect
        self.ripple_x = event.x
        self.ripple_y = event.y
        self.ripple_radius = 0
        
        # Calculate maximum radius
        max_distance = max(
            math.sqrt(event.x**2 + event.y**2),
            math.sqrt((self.width - event.x)**2 + event.y**2),
            math.sqrt(event.x**2 + (self.height - event.y)**2),
            math.sqrt((self.width - event.x)**2 + (self.height - event.y)**2)
        )
        self.max_radius = max_distance
        
        # Start animation
        self.animate_ripple()
        
    def on_release(self, event):
        """Mouse release event"""
        self.draw_button("hover")
        
        # Execute command
        if self.command is not None:
            self.command()
            
    def animate_ripple(self):
        """Animate the ripple effect"""
        # Delete previous ripple
        self.canvas.delete("ripple")
        
        # Draw new ripple
        self.ripple = self.canvas.create_oval(
            self.ripple_x - self.ripple_radius,
            self.ripple_y - self.ripple_radius,
            self.ripple_x + self.ripple_radius,
            self.ripple_y + self.ripple_radius,
            fill="#ffffff33", outline="",
            tags=("ripple",)
        )
        
        # Increase radius
        self.ripple_radius += 3
        
        # Stop animation when ripple is large enough
        if self.ripple_radius < self.max_radius:
            self.animation_id = self.after(10, self.animate_ripple)
        else:
            self.after(100, lambda: self.canvas.delete("ripple"))
            
    def lighten_color(self, color, factor=0.1):
        """Lighten a color by the given factor"""
        r, g, b = self.winfo_rgb(color)
        r = min(65535, int(r * (1 + factor)))
        g = min(65535, int(g * (1 + factor)))
        b = min(65535, int(b * (1 + factor)))
        return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
    
    def darken_color(self, color, factor=0.1):
        """Darken a color by the given factor"""
        r, g, b = self.winfo_rgb(color)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
    
    def set_text(self, text):
        """Change the button text"""
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
        
        # Add shadow effect using layers
        self.shadow_size = 4
        self.shadow_color = "#22000000"
        
        # Configure to always have some padding
        self.config(padx=10, pady=10)
        
        # Bind resize events
        self.bind("<Configure>", self.update_shadow)
    
    def update_shadow(self, event=None):
        """Update the shadow effect when the widget is resized"""
        # This is just a placeholder - in a real implementation we would
        # redraw shadows here, but for simplicity we're not implementing it fully
        pass


class DemoVoiceCommandApp:
    """Demo version of the voice command application with Material Design."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Command Tool v1.0 - Material")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        
        # Demo state
        self.is_recording = False
        self.last_command = "None"
        self.demo_commands = [
            "move forward", "turn left", "stop", "go home", 
            "open main", "emergency stop", "status", "help"
        ]
        self.command_index = 0
        
        # Apply Material Design color scheme
        self.root.configure(bg=MaterialDesign.BACKGROUND)
        
        # Setup gradient background
        self.setup_background()
        
        # Create GUI
        self.create_widgets()
        
        # Start demo log messages
        self.log("Voice Command Tool initialized (Demo Mode)")
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
        
        title_label = tk.Label(title_frame, text="Voice Command Tool", 
                              font=MaterialDesign.TITLE, bg=MaterialDesign.BACKGROUND,
                              fg=MaterialDesign.TEXT_PRIMARY)
        title_label.pack(side="left", padx=10)
        
        demo_label = tk.Label(title_frame, text="(Demo Mode - No Audio Processing)", 
                            font=MaterialDesign.CAPTION, bg=MaterialDesign.BACKGROUND,
                            fg=MaterialDesign.WARNING)
        demo_label.pack(side="left", padx=10)
        
        # Main content - split into left and right panels
        content_frame = tk.Frame(self.main_container, bg=MaterialDesign.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls & Last Command
        left_panel = MaterialCard(content_frame)
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
        status_label.pack(side="left")
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=MaterialDesign.BODY, bg=MaterialDesign.BACKGROUND,
                                    fg=MaterialDesign.SUCCESS)
        self.status_label.pack(side="left", padx=5)
        
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
                                    fg=MaterialDesign.TEXT_PRIMARY)
        self.command_label.pack(anchor="w")
        
        # Right panel - Activity Log
        right_panel = MaterialCard(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        log_title_frame = tk.Frame(right_panel, bg=MaterialDesign.BACKGROUND)
        log_title_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        log_title = tk.Label(log_title_frame, text="Activity Log", 
                            font=MaterialDesign.SUBTITLE, bg=MaterialDesign.BACKGROUND,
                            fg=MaterialDesign.TEXT_PRIMARY)
        log_title.pack(side="left")
        
        # Clear log button
        self.clear_button = MaterialButton(log_title_frame, text="Clear Log",
                                         command=self.clear_log, width=100, height=30,
                                         bg_color=MaterialDesign.PRIMARY_LIGHT,
                                         text_color=MaterialDesign.TEXT_PRIMARY)
        self.clear_button.pack(side="right")
        
        # Log display
        log_frame = tk.Frame(right_panel, bg=MaterialDesign.BACKGROUND)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=40,
                                                font=MaterialDesign.BODY, bd=0,
                                                bg=MaterialDesign.BACKGROUND)
        self.log_text.pack(fill="both", expand=True)
        
        # Footer with settings button
        footer_frame = tk.Frame(self.main_container, bg=MaterialDesign.BACKGROUND)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_button = MaterialButton(footer_frame, text="Settings",
                                            command=self.open_settings, width=150, height=36,
                                            bg_color=MaterialDesign.PRIMARY_DARK)
        self.settings_button.pack(side="right")
        
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
        self.start_button.set_text("Stop Listening")
        self.start_button.set_bg_color(MaterialDesign.ERROR)
        self.status_label.config(text="Listening...", fg=MaterialDesign.ERROR)
        self.log("Started listening for voice commands")
        
        # Animate the command display
        self.pulse_command_display()
        
        # Start demo processing in separate thread
        demo_thread = threading.Thread(target=self.demo_processing, daemon=True)
        demo_thread.start()
        
    def stop_recording(self):
        """Stop demo recording."""
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
        r, g, b = self.root.winfo_rgb(color)
        r = min(65535, int(r * (1 + factor)))
        g = min(65535, int(g * (1 + factor)))
        b = min(65535, int(b * (1 + factor)))
        return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
            
    def demo_processing(self):
        """Simulate voice processing with demo commands."""
        while self.is_recording:
            time.sleep(3)  # Simulate recording time
            
            if not self.is_recording:
                break
                
            # Simulate processing
            self.root.after(0, lambda: self.status_label.config(text="Processing...", fg=MaterialDesign.INFO))
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
                self.root.after(0, lambda: self.status_label.config(text="Listening...", fg=MaterialDesign.ERROR))
                
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
        self.log("Activity log cleared")
        
    def open_settings(self):
        """Open the demo settings dialog."""
        settings_window = DemoSettingsWindow(self.root, self)


class DemoSettingsWindow:
    """Demo settings dialog window with Material Design."""
    
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Demo")
        self.window.geometry("450x400")
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
        
        subtitle_label = tk.Label(title_frame, text="Demo Mode - Settings Preview", 
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
        """Save the demo settings."""
        self.app.log("Settings saved (Demo Mode)")
        self.app.log(f"Confidence threshold: {self.confidence_var.get():.2f}")
        self.app.log(f"Whisper model: {self.model_var.get()}")
        self.app.log(f"Recording duration: {self.duration_var.get():.1f}s")
        self.window.destroy()


def main():
    """Main demo function."""
    print("Voice Command Tool - Material Design GUI Demo")
    print("============================================")
    print("Starting GUI demonstration...")
    
    # Create main window
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.configure("TButton", font=MaterialDesign.BUTTON)
    style.configure("TScale", background=MaterialDesign.BACKGROUND)
    
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