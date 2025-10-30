# ============================================================================
# main_voice_app.py
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import time
from datetime import datetime

# Import core modules
from audio_engine import AudioEngine
from model_manager import ModelManager

# Simplified color configuration
COLORS = {
    "bg": "#F8F9FA",
    "primary": "#007BFF", 
    "success": "#28A745",
    "danger": "#DC3545",
    "warning": "#FFC107",
    "secondary": "#6C757D",
    "light": "#F8F9FA",
    "dark": "#343A40"
}

class VoiceControlApp:
    """
    Offline Voice Control System - Faster-Whisper Based Intelligent Voice Recognition
    
    Features:
    - Two-stage working mode: Standby → Wake Word → Command Recognition
    - Wake word: 'susie' - Activates command recognition mode
    - Automatic hotword boost for improved recognition accuracy
    - Dynamic weight adjustment based on usage frequency and training
    - Full offline operation with local Faster-Whisper models
    - Comprehensive TTS feedback for all system states
    - Four functional modules: Recognition, Commands, Training, System
    - Automatic JSON data persistence for commands and training data
    - Multi-threaded architecture for responsive UI and audio processing
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Offline Voice Control System - Faster-Whisper Based")
        self.root.geometry("800x700")
        self.root.configure(bg=COLORS["bg"])
        
        # State variables
        self.STATE_IDLE = "IDLE"
        self.STATE_LISTEN_WAKE = "LISTEN_WAKE"
        self.STATE_CMD_MODE = "CMD_MODE"
        self.state = self.STATE_IDLE
        self.is_listening = False
        self.fail_count = 0
        
        # Thread control
        self.recognition_thread = None
        self._stop_flag = threading.Event()
        
        # Initialize managers
        print("[INIT] Loading system components...")
        self.model_mgr = ModelManager()
        self.audio = None
        
        # Build UI
        self._build_ui()
        
        # Initialize audio processor
        self._init_audio()
    
    def _build_ui(self):
        """Build simplified user interface"""
        # Header
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_label = tk.Label(header, text="Voice Control", 
                  font=("Arial", 16, "bold"), 
                  bg=COLORS["primary"], fg="white")
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Status indicator
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = tk.Label(header, textvariable=self.status_var,
                               font=("Arial", 10), bg=COLORS["primary"], fg="white")
        status_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # Main tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_recognition = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_recognition, text="Listen")

        self.tab_commands = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_commands, text="Commands")

        self.tab_training = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_training, text="Train")

        self.tab_system = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_system, text="System")

        # Build each tab
        self._build_recognition_tab()
        self._build_commands_tab()
        self._build_training_tab()
        self._build_system_tab()
    
    def _build_recognition_tab(self):
        """Build recognition tab"""
        # Title
        tk.Label(self.tab_recognition, text="Listen", 
            font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)

        # Status info
        status_info_frame = tk.LabelFrame(self.tab_recognition, text="Status", 
                                        font=("Arial", 11, "bold"), bg=COLORS["bg"])
        status_info_frame.pack(fill=tk.X, padx=20, pady=10)

        self.detailed_status_var = tk.StringVar(value="Starting...")
        detailed_status_label = tk.Label(status_info_frame, textvariable=self.detailed_status_var,
                                        font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["dark"],
                                        justify=tk.LEFT, wraplength=600)
        detailed_status_label.pack(padx=10, pady=5)

        # Control buttons
        btn_frame = tk.Frame(self.tab_recognition, bg=COLORS["bg"])
        btn_frame.pack(pady=20)

        self.btn_start = tk.Button(btn_frame, text="Start", 
                      font=("Arial", 12, "bold"),
                      bg=COLORS["success"], fg="white", 
                      width=12, height=2, 
                      command=self._start_listening,
                      state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="Stop", 
                     font=("Arial", 12, "bold"),
                     bg=COLORS["danger"], fg="white", 
                     width=12, height=2,
                     command=self._stop_listening,
                     state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        # Results area
        result_frame = tk.LabelFrame(self.tab_recognition, text="Results", 
                                   font=("Arial", 11, "bold"), bg=COLORS["bg"])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Results text
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                   font=("Consolas", 10),
                                                   bg="white", height=12, 
                                                   wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Clear button
        clear_btn = tk.Button(result_frame, text="Clear", 
                            bg=COLORS["secondary"], fg="white",
                            command=lambda: self.result_text.delete("1.0", tk.END))
        clear_btn.pack(pady=5)
    
    def _build_commands_tab(self):
        """Build commands tab"""
        tk.Label(self.tab_commands, text="Commands", 
            font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)

        # Add command
        add_frame = tk.Frame(self.tab_commands, bg=COLORS["bg"])
        add_frame.pack(pady=10)

        tk.Label(add_frame, text="New", 
            font=("Arial", 11), bg=COLORS["bg"]).pack(side=tk.LEFT, padx=5)

        self.cmd_entry = tk.Entry(add_frame, font=("Arial", 11), width=30)
        self.cmd_entry.pack(side=tk.LEFT, padx=5)
        self.cmd_entry.bind("<Return>", lambda e: self._add_command())

        tk.Button(add_frame, text="Add", 
             bg=COLORS["success"], fg="white",
             command=self._add_command).pack(side=tk.LEFT, padx=5)

        # Command list
        list_frame = tk.LabelFrame(self.tab_commands, text="All Commands", 
                     font=("Arial", 11, "bold"), bg=COLORS["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.cmd_listbox = tk.Listbox(list_frame, font=("Arial", 10), height=15)
        self.cmd_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Command buttons
        cmd_btn_frame = tk.Frame(list_frame, bg=COLORS["bg"])
        cmd_btn_frame.pack(pady=5)

        tk.Button(cmd_btn_frame, text="Refresh", 
             bg=COLORS["primary"], fg="white",
             command=self._refresh_commands).pack(side=tk.LEFT, padx=5)

        tk.Button(cmd_btn_frame, text="Delete", 
             bg=COLORS["danger"], fg="white",
             command=self._delete_command).pack(side=tk.LEFT, padx=5)

        self._refresh_commands()
    
    def _build_training_tab(self):
        """Build training tab"""
        tk.Label(self.tab_training, text="Train", 
            font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)

        # Training list
        train_frame = tk.LabelFrame(self.tab_training, text="Progress", 
                      font=("Arial", 11, "bold"), bg=COLORS["bg"])
        train_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.train_tree = ttk.Treeview(train_frame, 
                                     columns=("Command", "Count", "Weight"), 
                                     show="headings", height=15)

        self.train_tree.heading("Command", text="Command")
        self.train_tree.heading("Count", text="Count")
        self.train_tree.heading("Weight", text="Weight")

        self.train_tree.column("Command", width=250)
        self.train_tree.column("Count", width=100)
        self.train_tree.column("Weight", width=120)

        self.train_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Training buttons
        train_btn_frame = tk.Frame(train_frame, bg=COLORS["bg"])
        train_btn_frame.pack(pady=10)

        tk.Button(train_btn_frame, text="Refresh", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_training).pack(side=tk.LEFT, padx=5)

        tk.Button(train_btn_frame, text="Train", 
                 bg=COLORS["warning"], fg="black",
                 command=self._train_command).pack(side=tk.LEFT, padx=5)

        self._refresh_training()
    
    def _build_system_tab(self):
        """Build system tab"""
        # All widgets must be created after tab_system is defined
        label = tk.Label(self.tab_system, text="System", 
            font=("Arial", 14, "bold"), bg=COLORS["bg"])
        label.pack(pady=15)

        # System status
        status_frame = tk.LabelFrame(self.tab_system, text="Status", 
                                   font=("Arial", 11, "bold"), bg=COLORS["bg"])
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.system_status_text = tk.Text(status_frame, 
                                        font=("Consolas", 9), 
                                        height=20, state=tk.DISABLED,
                                        bg="white")
        self.system_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # System buttons
        sys_btn_frame = tk.Frame(status_frame, bg=COLORS["bg"])
        sys_btn_frame.pack(pady=10)

        tk.Button(sys_btn_frame, text="Refresh Status", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_system_status).pack(side=tk.LEFT, padx=5)

        tk.Button(sys_btn_frame, text="Refresh Commands", 
                 bg=COLORS["success"], fg="white",
                 command=self._refresh_commands).pack(side=tk.LEFT, padx=5)

        tk.Button(sys_btn_frame, text="Refresh Training", 
                 bg=COLORS["warning"], fg="black",
                 command=self._refresh_training).pack(side=tk.LEFT, padx=5)

        tk.Button(sys_btn_frame, text="Save Log", 
                 bg=COLORS["secondary"], fg="white",
                 command=self._save_system_log).pack(side=tk.LEFT, padx=5)

        self._refresh_system_status()
    
    def _init_audio(self):
        """Initialize audio processor"""
        def worker():
            try:
                print("🔄 Initializing audio engine...")
                self.audio = AudioEngine(
                    model_size="base",
                    language="en", 
                    device="cpu"
                )
                self.root.after(0, lambda: self._update_status("System Ready"))
                self.root.after(0, lambda: self._update_detailed_status("System initialized successfully. Ready to start listening."))
                self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
                self.root.after(0, lambda: self._append_result("✅ Voice Control System initialized successfully"))
                # Auto-refresh commands, training, and system status after audio loads
                self.root.after(0, self._refresh_commands)
                self.root.after(0, self._refresh_training)
                self.root.after(0, self._refresh_system_status)
                # TTS announce system ready
                if self.audio and self.audio.tts_mgr:
                    time.sleep(1.0)  # Wait for TTS to fully initialize
                    self.audio.tts_mgr.speak_status("ready")
            except Exception as e:
                error_msg = f"System initialization failed: {e}"
                self.root.after(0, lambda: self._update_status("Initialization Failed"))
                self.root.after(0, lambda: self._update_detailed_status(f"Initialization error: {e}"))
                self.root.after(0, lambda: self._append_result(f"❌ {error_msg}"))
                # Auto-refresh system status on error
                self.root.after(0, self._refresh_system_status)
                print(f"❌ Audio initialization error: {e}")
                # TTS announce error
                if self.audio and self.audio.tts_mgr:
                    self.audio.tts_mgr.speak_status("error")
        threading.Thread(target=worker, daemon=True).start()
    
    def _start_listening(self):
        """Start listening (Fixed business logic)"""
        if not self.audio or self.is_listening:
            return
        
        # Reset state
        self._stop_flag.clear()
        self.is_listening = True
        self.fail_count = 0
        self.state = self.STATE_LISTEN_WAKE
        
        # Update UI
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self._update_status("Listening for wake word 'susie'...")
        self._update_detailed_status("System is listening for the wake word 'susie'. Speak clearly into your microphone.")
        
        # Clear output file
        self._clear_output()
        
        # Log entry (Fixed escape character issue)
        ts = datetime.now().strftime('%H:%M:%S')
        self._append_result(f"🎤 Voice recognition started at {ts}")
        self._append_result("💡 Say 'susie' to activate command mode")
        
        # TTS announce start
        if self.audio.tts_mgr:
            self.audio.tts_mgr.speak_status("start")
            time.sleep(0.5)
            self.audio.tts_mgr.speak_status("listening")
        
        # Start recognition thread
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()
    
    def _stop_listening(self):
        """Stop listening (Fixed cleanup logic)"""
        print("🔄 Stopping recognition...")
        
        # Set stop flag
        self._stop_flag.set()
        self.is_listening = False
        
        # Reset audio processor state
        if self.audio:
            self.audio.reset_wake_state()
        
        # Update state
        self.state = self.STATE_IDLE
        
        # Update UI
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self._update_status("System Ready")
        self._update_detailed_status("Recognition stopped. System is ready to start listening again.")
        
        # Log entry
        ts = datetime.now().strftime('%H:%M:%S')
        self._append_result(f"⏹ Voice recognition stopped at {ts}")
        
        # TTS announce stop
        if self.audio and self.audio.tts_mgr:
            self.audio.tts_mgr.speak_status("stop")
        
        # Wait for recognition thread to end
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2.0)
        
        print("✅ Recognition stopped successfully")
    
    def _recognition_loop(self):
        """
        Main recognition loop implementing two-stage voice control
        
        Stage 1: Standby Mode - Listen for wake word 'susie'
        Stage 2: Command Mode - Recognize and execute voice commands
        
        The system automatically returns to standby after 5 consecutive failed recognitions.
        All recognition results are written to output.txt with timestamps.
        TTS provides real-time feedback for all states and actions.
        """
        try:
            print("🔄 Starting recognition loop...")
            
            while self.is_listening and not self._stop_flag.is_set():
                try:
                    # ===== STAGE 1: STANDBY MODE - Wake Word Detection =====
                    if self.state == self.STATE_LISTEN_WAKE:
                        self.root.after(0, lambda: self._update_detailed_status("Listening for wake word 'susie'..."))
                        
                        print("🔍 Recording for wake word detection...")
                        audio = self.audio.record_audio(duration=3) if self.audio is not None and hasattr(self.audio, 'record_audio') else None
                        
                        if audio is None or self._stop_flag.is_set():
                            continue
                        
                        # Detect "susie"
                        if self.audio is not None and hasattr(self.audio, 'detect_wake_word') and self.audio.detect_wake_word(audio, "susie"):
                            # Activate command mode
                            if self.audio is not None and hasattr(self.audio, 'set_wake_state') and hasattr(self.audio, 'WAKE_STATE_ACTIVE'):
                                self.audio.set_wake_state(self.audio.WAKE_STATE_ACTIVE)
                            self.state = self.STATE_CMD_MODE
                            self.fail_count = 0
                            
                            ts = datetime.now().strftime("%H:%M:%S")
                            self.root.after(0, lambda: self._update_status("Command mode - Speak your command"))
                            self.root.after(0, lambda: self._update_detailed_status("Wake word detected! Command mode activated. Speak your command clearly."))
                            self.root.after(0, lambda: self._append_result(f"[{ts}] 🎯 Wake word detected - Command mode activated"))
                            
                            # TTS announce command mode activated (already announced "please speak" in detect_wake_word)
                            time.sleep(0.5)
                        
                        # Cooldown interval to prevent excessive processing
                        time.sleep(1.0)
                    
                    # ===== STAGE 2: COMMAND MODE - Voice Command Recognition =====
                    elif self.state == self.STATE_CMD_MODE:
                        self.root.after(0, lambda: self._update_detailed_status(f"Command mode active. Listening for commands... (Failures: {self.fail_count}/5)"))
                        
                        print("🔍 Recording for command recognition...")
                        audio = self.audio.record_audio(duration=5) if self.audio is not None and hasattr(self.audio, 'record_audio') else None  # Slightly longer to ensure complete recording
                        
                        if audio is None or self._stop_flag.is_set():
                            continue
                        
                        # Transcribe audio
                        text = self.audio.transcribe(audio) if self.audio is not None and hasattr(self.audio, 'transcribe') else None
                        
                        if not text or not isinstance(text, str):
                            print("⚠️ No transcription result")
                            time.sleep(1.0)  # Add interval
                            continue
                        
                        text = text.strip()
                        if not text:
                            print("⚠️ Empty transcription")
                            time.sleep(1.0)  # Add interval
                            continue
                        
                        print(f"✅ Transcribed: '{text}'")
                        
                        # TTS announce processing
                        if self.audio is not None and hasattr(self.audio, 'tts_mgr') and self.audio.tts_mgr:
                            self.audio.tts_mgr.speak_status("processing")
                        
                        # Match command
                        commands = self.audio.get_all_commands() if self.audio is not None and hasattr(self.audio, 'get_all_commands') else []
                        matched_cmd = self.audio.match_command(text, commands) if self.audio is not None and hasattr(self.audio, 'match_command') else None
                        
                        ts = datetime.now().strftime("%H:%M:%S")
                        
                        if matched_cmd:
                            # ===== COMMAND MATCHED SUCCESSFULLY =====
                            self.fail_count = 0
                            
                            # Write command to output.txt for robot execution
                            if self._write_output(matched_cmd):
                                msg = f"[{ts}] ✅ Command: '{matched_cmd}' → Saved to output.txt"
                                self.root.after(0, lambda cmd=matched_cmd: self._update_detailed_status(f"Command executed successfully: '{cmd}' → Written to output.txt"))
                                
                                # TTS confirmation: speak the matched command
                                if self.audio is not None and hasattr(self.audio, 'tts_mgr') and self.audio.tts_mgr:
                                    self.audio.tts_mgr.speak_command(matched_cmd)
                            else:
                                msg = f"[{ts}] ⚠️ Command: '{matched_cmd}' → File write failed"
                                self.root.after(0, lambda cmd=matched_cmd: self._update_detailed_status(f"Command recognized but file write failed: '{cmd}'"))
                                
                                # TTS error announcement
                                if self.audio is not None and hasattr(self.audio, 'tts_mgr') and self.audio.tts_mgr:
                                    self.audio.tts_mgr.speak_status("error")
                        else:
                            # ===== COMMAND NOT MATCHED =====
                            self.fail_count += 1
                            msg = f"[{ts}] ❌ '{text}' → No matching command (Failures: {self.fail_count}/5)"
                            self.root.after(0, lambda t=text, fc=self.fail_count: self._update_detailed_status(f"No matching command found for: '{t}' (Failures: {fc}/5)"))
                            
                            # TTS feedback: command not recognized
                            if self.audio is not None and hasattr(self.audio, 'tts_mgr') and self.audio.tts_mgr:
                                self.audio.tts_mgr.speak_status("not match")
                        
                        self.root.after(0, lambda m=msg: self._append_result(m))
                        
                        # ===== AUTO RETURN TO STANDBY AFTER 5 FAILURES =====
                        if self.fail_count >= 5:
                            print("⚠️ Maximum failures reached (5/5), returning to standby mode")
                            
                            # Reset to standby mode
                            self.state = self.STATE_LISTEN_WAKE
                            self.fail_count = 0
                            
                            # Reset audio processor wake state
                            if self.audio is not None and hasattr(self.audio, 'reset_wake_state'):
                                self.audio.reset_wake_state()
                            
                            # Update UI with clear feedback
                            self.root.after(0, lambda: self._update_status("Listening for wake word 'susie'..."))
                            self.root.after(0, lambda: self._update_detailed_status("5 consecutive failures detected. System returned to standby mode. Say 'susie' to reactivate."))
                            self.root.after(0, lambda: self._append_result("⚠️ [Auto-Reset] 5 consecutive failures → Returned to standby mode"))
                            
                            time.sleep(1.0)
                        
                        # Add interval to prevent too fast recognition
                        time.sleep(2.0)
                
                except Exception as e:
                    print(f"❌ Recognition loop error: {e}")
                    self.root.after(0, lambda: self._append_result(f"❌ Recognition error: {e}"))
                    time.sleep(2.0)  # Add longer interval after error
                    continue
        
        except Exception as e:
            print(f"❌ Critical recognition loop error: {e}")
            self.root.after(0, lambda: self._append_result(f"❌ Critical error: {e}"))
        finally:
            print("🔄 Recognition loop ended")
            if self.is_listening:
                self.root.after(0, self._stop_listening)
    
    def _add_command(self):
        """Add command"""
        if not self.audio:
            return
            
        cmd = self.cmd_entry.get().strip()
        if cmd and self.audio.add_command(cmd):
            self.cmd_entry.delete(0, tk.END)
            self._refresh_commands()
            self._refresh_training()
            self._refresh_system_status()
            messagebox.showinfo("Success", f"Command '{cmd}' added successfully")
    
    def _delete_command(self):
        """Delete command"""
        if not self.audio:
            return
            
        selection = self.cmd_listbox.curselection()
        if selection:
            cmd = self.cmd_listbox.get(selection[0])
            if messagebox.askyesno("Confirm", f"Delete command '{cmd}'?"):
                if self.audio.remove_command(cmd):
                    self._refresh_commands()
                    self._refresh_training()
                    self._refresh_system_status()
    
    def _refresh_commands(self):
        """Refresh command list"""
        if not self.audio:
            return
            
        self.cmd_listbox.delete(0, tk.END)
        commands = self.audio.get_all_commands()
        if not commands or not isinstance(commands, (list, tuple)):
            commands = []
        for cmd in commands:
            self.cmd_listbox.insert(tk.END, cmd)
    
    def _train_command(self):
        """Train command"""
        if not self.audio:
            return
            
        selection = self.train_tree.selection()
        if selection:
            item = self.train_tree.item(selection[0])
            cmd = item["values"][0]
            weight = self.audio.train_command(cmd)
            self._refresh_training()
            self._refresh_commands()
            self._refresh_system_status()
            messagebox.showinfo("Training", f"Command '{cmd}' trained. New weight: {weight:.2f}")
    
    def _refresh_training(self):
        """Refresh training data"""
        if not self.audio:
            return
            
        for item in self.train_tree.get_children():
            self.train_tree.delete(item)
        
        commands = self.audio.get_all_commands()
        if not commands or not isinstance(commands, (list, tuple)):
            commands = []
        for cmd in commands:
            count = self.audio.get_training_count(cmd)
            cmd_info = self.audio.cmd_hotword_mgr.get_command_info(cmd)
            weight = cmd_info.get("weight", 1.0)
            self.train_tree.insert("", tk.END, values=(cmd, count, f"{weight:.2f}"))
    
    def _refresh_system_status(self):
        """Refresh system status"""
        if not self.audio:
            status_text = "Audio processor not initialized.\n\nPlease check your model and audio device."
        else:
            try:
                status = self.audio.get_system_status()
                status_text = "=== VOICE CONTROL SYSTEM STATUS ===\n\n"
                status_text += f"System State: {self.state}\n"
                status_text += f"Wake State: {status['wake_state']}\n"
                status_text += f"Processing: {status['processing']}\n"
                status_text += f"Is Listening: {self.is_listening}\n"
                status_text += f"Model: {status['model_size']} ({status['backend']})\n"
                status_text += f"Model Loaded: {status['model_loaded']}\n"
                status_text += f"Model Path: {status.get('model_path', 'N/A')}\n"
                status_text += f"Model Error: {status.get('model_error', 'None')}\n"
                status_text += f"\nFeatures:\n"
                features = status.get('features', {})
                if not features or not isinstance(features, dict):
                    features = {}
                for feature, enabled in features.items():
                    status_text += f"  {feature}: {'✅ Enabled' if enabled else '❌ Disabled'}\n"
                status_text += f"\nCommands: {status['commands']['total']} total\n"
                most_used = status.get('commands', {}).get('most_used', [])
                if not most_used or not isinstance(most_used, (list, tuple)):
                    most_used = []
                if most_used:
                    status_text += "Most Used Commands:\n"
                    for cmd, count in most_used:
                        status_text += f"  '{cmd}': {count} times\n"
                status_text += f"\nTTS Engine: {status['tts']['engine_type']}\n"
                status_text += f"TTS Running: {status['tts']['running']}\n"
                status_text += f"TTS Speaking: {status['tts']['speaking']}\n"
                status_text += f"TTS Error: {status['tts'].get('error', 'None')}\n"
                status_text += f"\nLocal Models:\n"
                status_text += f"Offline Mode: {status['local_models']['offline_mode']}\n"
                status_text += f"Available Models: {len(status['local_models']['available'])}\n"
                status_text += f"Total Size: {status['local_models']['total_size']}\n"
                status_text += f"Models: {', '.join(status['local_models']['available'])}\n"
                status_text += f"Model Load Error: {status['local_models'].get('error', 'None')}\n"
                status_text += f"\nLast Success: {status.get('last_success', 'N/A')}\n"
                status_text += f"Last Error: {status.get('last_error', 'None')}\n"
            except Exception as e:
                status_text = f"Error getting system status: {e}"

        self.system_status_text.config(state=tk.NORMAL)
        self.system_status_text.delete("1.0", tk.END)
        self.system_status_text.insert("1.0", status_text)
        self.system_status_text.config(state=tk.DISABLED)
    
    def _save_system_log(self):
        """Save system log"""
        try:
            log_content = self.result_text.get("1.0", tk.END)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_control_log_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            messagebox.showinfo("Success", f"System log saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def _update_status(self, status):
        """Update status display"""
        self.status_var.set(status)
    
    def _update_detailed_status(self, status):
        """Update detailed status display"""
        self.detailed_status_var.set(status)
    
    def _append_result(self, text):
        """Append result text (Fixed escape character issue)"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
    
    def _clear_output(self):
        """Clear output file"""
        try:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"Clear output error: {e}")
    
    def _write_output(self, text):
        """Write command to output.txt with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_content = f"[{timestamp}] Command: {text}\n"
            
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(output_content)
            
            print(f"✅ Command written to output.txt: {text}")
            return True
        except Exception as e:
            print(f"❌ Write output error: {e}")
            return False
    
    def on_closing(self):
        """Cleanup when closing application"""
        print("🔄 Closing application...")
        
        # Stop listening
        if self.is_listening:
            self._stop_listening()
        
        # Close audio processor
        if self.audio:
            self.audio.shutdown()
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VoiceControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()