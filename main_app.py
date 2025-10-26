# Main Application - PRODUCTION READY
# All bugs fixed + Enhanced recognition + Correct output.txt handling

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import shutil
from datetime import datetime
from PIL import Image, ImageTk

from audio_processor import AudioProcessor
from command_manager import CommandManager
from speaker_manager import SpeakerManager

THEME = {
    "bg": "#FFFFFF",
    "border_red": "#FF0000",
    "border_blue": "#0000FF",
    "text": "#000000",
    "button_green": "#00AA00",
    "button_red": "#FF0000",
    "button_blue": "#0066CC",
    "gray": "#CCCCCC",
    "light_gray": "#F5F5F5"
}


class VoiceCommandApp:
    """Main application - Production ready with all fixes"""

    def __init__(self, root):
        self.root = root
        self.root.title("Voice Control For A Robot System")
        self.root.geometry("850x800")
        self.root.configure(bg=THEME["bg"])

        self.audio_processor = None
        self.command_manager = CommandManager()
        self.speaker_manager = SpeakerManager()

        # STATE MACHINE
        self.STATE_IDLE = "IDLE"
        self.STATE_LISTENING_FOR_WAKE = "LISTENING_FOR_WAKE"
        self.STATE_COMMAND_MODE = "COMMAND_MODE"

        self.current_state = self.STATE_IDLE
        self.is_listening = False
        self.listen_thread = None
        self.failed_match_count = 0
        self.max_failed_matches = 5

        self.create_ui()
        self.init_audio()
        self.update_status_display()

    def load_logo(self):
        """Load NTU.png logo"""
        try:
            if os.path.exists("NTU.png"):
                img = Image.open("NTU.png")
                img = img.resize((180, 120), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"⚠️ Logo error: {e}")
        return None

    def show_easter_egg(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Provided by NTU EEE MSc Group 2025")

    def update_status_display(self):
        """Update status indicator"""
        status_map = {
            self.STATE_IDLE: ("⚪ Idle", THEME["gray"]),
            self.STATE_LISTENING_FOR_WAKE: ("🔴 Listening for 'susie'", "#FF6600"),
            self.STATE_COMMAND_MODE: ("🟢 Command Mode Ready", THEME["button_green"])
        }

        text, color = status_map.get(self.current_state, ("❓ Unknown", THEME["text"]))
        self.status_var.set(text)
        self.status_label.config(fg=color)

    def clear_output_file(self):
        """Clear output.txt - FIXED: No double extension"""
        output_path = "output.txt"
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("")
            print(f"📝 Cleared {output_path}")
            self.append_result("📝 Session started - output.txt cleared\n\n")
        except Exception as e:
            print(f"❌ Clear error: {e}")

    def write_to_output(self, command_text):
        """Write to output.txt - FIXED: Correct filename"""
        output_path = "output.txt"
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {command_text}\n")
            print(f"✅ Wrote to {output_path}: {command_text}")
            return True
        except Exception as e:
            print(f"❌ Write error: {e}")
            return False

    def clear_cache(self):
        """Clear cache"""
        try:
            cache_dirs = ["__pycache__", ".cache", "temp"]
            cleaned_size = 0

            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    for root_dir, dirs, files in os.walk(cache_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root_dir, file)
                                cleaned_size += os.path.getsize(file_path)
                                os.remove(file_path)
                            except:
                                pass
                    try:
                        shutil.rmtree(cache_dir)
                    except:
                        pass

            messagebox.showinfo("Success", f"Cleaned {cleaned_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def create_ui(self):
        """Create UI"""
        # HEADER
        header = tk.Frame(self.root, bg=THEME["bg"], height=70)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        logo_frame = tk.Frame(header, bg=THEME["bg"])
        logo_frame.pack(side=tk.LEFT, padx=15, pady=5)

        self.logo_photo = self.load_logo()
        if self.logo_photo:
            tk.Label(logo_frame, image=self.logo_photo, bg=THEME["bg"]).pack()
        else:
            tk.Label(logo_frame, text="NTU", font=("Arial", 20, "bold"), bg=THEME["bg"], fg=THEME["border_blue"]).pack()

        title_button = tk.Button(
            header, text="Voice Control For A Robot System",
            font=("Arial", 16, "bold"), bg=THEME["bg"], fg=THEME["text"],
            relief=tk.FLAT, bd=0, command=self.show_easter_egg, cursor="arrow"
        )
        title_button.pack(side=tk.LEFT, padx=30, pady=15)

        status_frame = tk.Frame(header, bg=THEME["bg"])
        status_frame.pack(side=tk.RIGHT, padx=15, pady=15)

        tk.Label(status_frame, text="Status:", font=("Arial", 10), bg=THEME["bg"]).pack(side=tk.LEFT, padx=3)

        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"),
                                     bg=THEME["bg"], fg=THEME["button_green"])
        self.status_label.pack(side=tk.LEFT, padx=3)

        tk.Frame(self.root, bg=THEME["border_red"], height=2).pack(fill=tk.X)

        # TABS
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tab_recognition = tk.Frame(notebook, bg=THEME["bg"])
        self.tab_commands = tk.Frame(notebook, bg=THEME["bg"])
        self.tab_training = tk.Frame(notebook, bg=THEME["bg"])
        self.tab_speakers = tk.Frame(notebook, bg=THEME["bg"])
        self.tab_guide = tk.Frame(notebook, bg=THEME["bg"])
        self.tab_maintenance = tk.Frame(notebook, bg=THEME["bg"])

        notebook.add(self.tab_recognition, text=" Recognition ")
        notebook.add(self.tab_commands, text=" Commands ")
        notebook.add(self.tab_training, text=" Training ")
        notebook.add(self.tab_speakers, text=" Speakers ")
        notebook.add(self.tab_guide, text=" Guide ")
        notebook.add(self.tab_maintenance, text=" Maintenance ")

        self.create_recognition_tab()
        self.create_commands_tab()
        self.create_training_tab()
        self.create_speakers_tab()
        self.create_guide_tab()
        self.create_maintenance_tab()

    def create_recognition_tab(self):
        """Recognition tab"""
        tk.Label(self.tab_recognition, text="Recognition", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=15)
        tk.Frame(self.tab_recognition, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        speaker_frame = tk.Frame(self.tab_recognition, bg=THEME["bg"])
        speaker_frame.pack(pady=12)

        tk.Label(speaker_frame, text="Speaker:", font=("Arial", 11), bg=THEME["bg"]).pack(side=tk.LEFT, padx=8)

        self.speaker_var = tk.StringVar(value="Auto")
        self.speaker_combo = ttk.Combobox(speaker_frame, textvariable=self.speaker_var, state="readonly", width=18)
        self.speaker_combo.pack(side=tk.LEFT, padx=8)
        self.update_speaker_combo()

        control_frame = tk.Frame(self.tab_recognition, bg=THEME["bg"])
        control_frame.pack(pady=15)

        self.btn_start = tk.Button(control_frame, text="▶ Start", font=("Arial", 12, "bold"), bg=THEME["button_green"],
                                   fg="white", width=18, height=2, command=self.start_listening, cursor="hand2")
        self.btn_start.grid(row=0, column=0, padx=8)

        self.btn_stop = tk.Button(control_frame, text="⏹ Stop", font=("Arial", 12, "bold"), bg=THEME["button_red"],
                                  fg="white", width=18, height=2, command=self.stop_listening, state=tk.DISABLED,
                                  cursor="hand2")
        self.btn_stop.grid(row=0, column=1, padx=8)

        tk.Frame(self.tab_recognition, bg=THEME["border_red"], height=2).pack(fill=tk.X, padx=15, pady=8)
        tk.Label(self.tab_recognition, text="Results", font=("Arial", 12, "bold"), bg=THEME["bg"]).pack(pady=8)

        self.result_text = scrolledtext.ScrolledText(self.tab_recognition, font=("Consolas", 10),
                                                     bg=THEME["light_gray"], height=12, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        action_frame = tk.Frame(self.tab_recognition, bg=THEME["bg"])
        action_frame.pack(pady=8)

        tk.Button(action_frame, text="Clear", font=("Arial", 9), bg=THEME["gray"], command=self.clear_results,
                  cursor="hand2").pack(side=tk.LEFT, padx=5)

    def create_commands_tab(self):
        """Commands tab"""
        tk.Label(self.tab_commands, text="Commands", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=15)
        tk.Frame(self.tab_commands, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        add_frame = tk.Frame(self.tab_commands, bg=THEME["bg"])
        add_frame.pack(pady=15)

        tk.Label(add_frame, text="New:", font=("Arial", 11), bg=THEME["bg"]).pack(side=tk.LEFT, padx=8)

        self.cmd_entry = tk.Entry(add_frame, font=("Arial", 11), width=25)
        self.cmd_entry.pack(side=tk.LEFT, padx=8)
        self.cmd_entry.bind("<Return>", lambda e: self.add_command())

        tk.Button(add_frame, text="Add", font=("Arial", 10, "bold"), bg=THEME["button_green"], fg="white",
                  command=self.add_command, cursor="hand2").pack(side=tk.LEFT, padx=8)

        tk.Frame(self.tab_commands, bg=THEME["border_red"], height=2).pack(fill=tk.X, padx=15, pady=8)
        tk.Label(self.tab_commands, text="Registered", font=("Arial", 12, "bold"), bg=THEME["bg"]).pack(pady=8)

        self.cmd_tree = ttk.Treeview(self.tab_commands, columns=("Command",), show="headings", height=13)
        self.cmd_tree.heading("Command", text="Command")
        self.cmd_tree.column("Command", width=600)
        self.cmd_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        btn_frame = tk.Frame(self.tab_commands, bg=THEME["bg"])
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Delete", font=("Arial", 9), bg=THEME["button_red"], fg="white",
                  command=self.delete_command, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", font=("Arial", 9), bg=THEME["button_blue"], fg="white",
                  command=self.refresh_commands, cursor="hand2").pack(side=tk.LEFT, padx=5)

        self.refresh_commands()

    def create_training_tab(self):
        """Training tab"""
        tk.Label(self.tab_training, text="Training", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=15)
        tk.Frame(self.tab_training, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        speaker_train_frame = tk.Frame(self.tab_training, bg=THEME["bg"])
        speaker_train_frame.pack(pady=10)

        tk.Label(speaker_train_frame, text="Speaker:", font=("Arial", 11), bg=THEME["bg"]).pack(side=tk.LEFT, padx=8)

        self.train_speaker_var = tk.StringVar(value="None")
        self.train_speaker_combo = ttk.Combobox(speaker_train_frame, textvariable=self.train_speaker_var,
                                                state="readonly", width=18)
        self.train_speaker_combo.pack(side=tk.LEFT, padx=8)
        self.update_train_speaker_combo()

        tk.Label(self.tab_training, text="Say 3-5 times", font=("Arial", 10), bg=THEME["bg"]).pack(pady=5)

        self.training_tree = ttk.Treeview(self.tab_training, columns=("Command", "Count", "Weight"), show="headings",
                                          height=12)
        self.training_tree.heading("Command", text="Command")
        self.training_tree.heading("Count", text="Count")
        self.training_tree.heading("Weight", text="Weight")
        self.training_tree.column("Command", width=250)
        self.training_tree.column("Count", width=120)
        self.training_tree.column("Weight", width=100)
        self.training_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        btn_frame = tk.Frame(self.tab_training, bg=THEME["bg"])
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Train", font=("Arial", 10, "bold"), bg=THEME["button_green"], fg="white",
                  command=self.train_command, cursor="hand2", width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", font=("Arial", 9), bg=THEME["button_blue"], fg="white",
                  command=self.refresh_training, cursor="hand2").pack(side=tk.LEFT, padx=5)

        self.refresh_training()

    def create_speakers_tab(self):
        """Speakers tab"""
        tk.Label(self.tab_speakers, text="Speakers", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=15)
        tk.Frame(self.tab_speakers, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        add_frame = tk.Frame(self.tab_speakers, bg=THEME["bg"])
        add_frame.pack(pady=15)

        tk.Label(add_frame, text="Name:", font=("Arial", 11), bg=THEME["bg"]).pack(side=tk.LEFT, padx=8)

        self.speaker_entry = tk.Entry(add_frame, font=("Arial", 11), width=20)
        self.speaker_entry.pack(side=tk.LEFT, padx=8)
        self.speaker_entry.bind("<Return>", lambda e: self.add_speaker())

        tk.Button(add_frame, text="Add", font=("Arial", 10, "bold"), bg=THEME["button_green"], fg="white",
                  command=self.add_speaker, cursor="hand2").pack(side=tk.LEFT, padx=8)

        tk.Frame(self.tab_speakers, bg=THEME["border_red"], height=2).pack(fill=tk.X, padx=15, pady=8)
        tk.Label(self.tab_speakers, text="Registered", font=("Arial", 12, "bold"), bg=THEME["bg"]).pack(pady=8)

        self.speaker_tree = ttk.Treeview(self.tab_speakers, columns=("ID", "Name"), show="headings", height=13)
        self.speaker_tree.heading("ID", text="ID")
        self.speaker_tree.heading("Name", text="Name")
        self.speaker_tree.column("ID", width=120)
        self.speaker_tree.column("Name", width=300)
        self.speaker_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        btn_frame = tk.Frame(self.tab_speakers, bg=THEME["bg"])
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Delete", font=("Arial", 9), bg=THEME["button_red"], fg="white",
                  command=self.delete_speaker, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", font=("Arial", 9), bg=THEME["button_blue"], fg="white",
                  command=self.refresh_speakers, cursor="hand2").pack(side=tk.LEFT, padx=5)

        self.refresh_speakers()

    def create_guide_tab(self):
        """Guide tab"""
        tk.Label(self.tab_guide, text="Guide", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=15)
        tk.Frame(self.tab_guide, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        guide_text = scrolledtext.ScrolledText(self.tab_guide, font=("Consolas", 9), bg=THEME["light_gray"],
                                               wrap=tk.WORD, height=20)
        guide_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        content = """HOW TO USE

1. ADD COMMANDS
   Commands → New → type "open door" → Add

2. START LISTENING
   Recognition → Speaker: Auto → Start

3. SAY "susie"
   Status turns green = Command Mode

4. SAY COMMANDS
   Say registered commands continuously
   ✅ = Saved to output.txt
   ❌ = Not registered

5. CHECK RESULTS
   Results box shows all transcriptions
   output.txt contains successful commands

6. TRAINING (Optional)
   Training → Select command → Train
   Say 3-5 times in 5 seconds
   Higher weight = better recognition

═══════════════════════════════════════

MIT LICENSE

Copyright (c) 2025 NTU EEE MSc Group

Permission granted to use, modify, distribute.
Software provided "as is" without warranty.

═══════════════════════════════════════

CREDITS

Built with:
→ OpenAI Whisper
→ Faster-Whisper
→ PyAudio
→ CTranslate2
→ Python Tkinter

Made with ❤️ + ☕
NTU EEE MSc Group 2025
Version: 1.0
"""

        guide_text.insert(tk.END, content)
        guide_text.config(state=tk.DISABLED)

    def create_maintenance_tab(self):
        """Maintenance tab"""
        tk.Label(self.tab_maintenance, text="Maintenance", font=("Arial", 15, "bold"), bg=THEME["bg"]).pack(pady=20)
        tk.Frame(self.tab_maintenance, bg=THEME["border_blue"], height=2).pack(fill=tk.X, padx=15, pady=5)

        tk.Label(self.tab_maintenance, text="Clear cache safely.\nData files preserved.", font=("Arial", 11),
                 bg=THEME["bg"]).pack(pady=20)

        tk.Button(self.tab_maintenance, text="🗑️ Clear Cache", font=("Arial", 12, "bold"), bg=THEME["button_red"],
                  fg="white", width=20, height=2, command=self.clear_cache, cursor="hand2").pack(pady=20)

    def init_audio(self):
        """Initialize audio processor"""

        def init_worker():
            try:
                self.audio_processor = AudioProcessor(model_size="base", language="en", device="cpu")
                self.root.after(0, lambda: self.update_status_display())
                self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Init failed:\n{e}"))

        threading.Thread(target=init_worker, daemon=True).start()

    def start_listening(self):
        """START - Core recognition logic with proper display"""
        if not self.audio_processor:
            messagebox.showerror("Error", "Not initialized")
            return

        if self.is_listening:
            return

        self.clear_output_file()

        self.is_listening = True
        self.failed_match_count = 0
        self.current_state = self.STATE_LISTENING_FOR_WAKE

        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.update_status_display()

        def listen_worker():
            try:
                while self.is_listening:
                    try:
                        # PHASE 1: Wake-word detection
                        wake_audio = self.audio_processor.record_audio(duration=3)

                        if wake_audio is None or not self.is_listening:
                            continue

                        if self.audio_processor.detect_wake_word(wake_audio, wake_word="susie"):
                            # ENTER COMMAND MODE
                            self.current_state = self.STATE_COMMAND_MODE
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            self.root.after(0,
                                            lambda: self.append_result(f"[{timestamp}]\n🎯 Command Mode Activated\n\n"))
                            self.root.after(0, lambda: self.update_status_display())

                            # PHASE 2: Command recognition
                            while self.is_listening and self.current_state == self.STATE_COMMAND_MODE:
                                try:
                                    cmd_audio = self.audio_processor.record_audio(duration=5)

                                    if cmd_audio is None or not self.is_listening:
                                        break

                                    boost_list = self.command_manager.get_boost_list()
                                    result = self.audio_processor.transcribe(cmd_audio, boost_phrases=boost_list)

                                    # CRITICAL: Validate result
                                    if result is None:
                                        continue
                                    if not isinstance(result, str):
                                        print(f"⚠️ Non-string result: {type(result)}")
                                        continue

                                    result = result.strip()
                                    if not result:
                                        continue

                                    # Check match
                                    matched = self.audio_processor.check_phrase_match(result,
                                                                                      self.command_manager.get_all_commands())

                                    timestamp = datetime.now().strftime("%H:%M:%S")

                                    # Get speaker
                                    speaker_label = ""
                                    if self.speaker_var.get() == "Auto" and matched:
                                        detected_speaker = self.command_manager.get_trained_speaker(matched)
                                        if detected_speaker:
                                            speaker_name = self.speaker_manager.get_all_speakers().get(detected_speaker,
                                                                                                       {}).get("name",
                                                                                                               "Unknown")
                                            speaker_label = f" [{speaker_name}]"

                                    if matched:
                                        # SUCCESS
                                        self.failed_match_count = 0
                                        write_success = self.write_to_output(result)

                                        if write_success:
                                            log_msg = f"[{timestamp}]{speaker_label}\n✅ {result}\n📝 Saved to output.txt\n\n"
                                        else:
                                            log_msg = f"[{timestamp}]{speaker_label}\n✅ {result}\n⚠️ Write failed\n\n"
                                    else:
                                        # NOT MATCHED
                                        self.failed_match_count += 1
                                        log_msg = f"[{timestamp}]\n❌ {result}\n⚠️ Not in command list\n\n"

                                    self.root.after(0, lambda m=log_msg: self.append_result(m))

                                    # Check failures
                                    if self.failed_match_count >= self.max_failed_matches:
                                        self.current_state = self.STATE_LISTENING_FOR_WAKE
                                        self.failed_match_count = 0
                                        self.root.after(0, lambda: self.append_result(
                                            "⚠️ Too many unmatched. Say 'susie' again.\n\n"))
                                        self.root.after(0, lambda: self.update_status_display())

                                except Exception as e:
                                    print(f"❌ Command error: {e}")
                                    continue

                    except Exception as e:
                        print(f"❌ Wake error: {e}")
                        continue

            except Exception as e:
                print(f"❌ Critical: {e}")
            finally:
                self.root.after(0, lambda: self.on_listening_stopped())

        self.listen_thread = threading.Thread(target=listen_worker, daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        """STOP"""
        self.is_listening = False
        self.current_state = self.STATE_IDLE

        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

        self.update_status_display()

    def on_listening_stopped(self):
        """Cleanup"""
        self.current_state = self.STATE_IDLE
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.update_status_display()

    def append_result(self, text):
        """Append to results"""
        try:
            self.result_text.insert(tk.END, text)
            self.result_text.see(tk.END)
            self.result_text.update()
        except Exception as e:
            print(f"⚠️ Display error: {e}")

    def clear_results(self):
        """Clear results"""
        self.result_text.delete("1.0", tk.END)

    def add_command(self):
        """Add command"""
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            messagebox.showwarning("Warning", "Enter command")
            return

        if self.command_manager.add_command(cmd):
            self.cmd_entry.delete(0, tk.END)
            self.refresh_commands()
            self.refresh_training()
            messagebox.showinfo("Success", f"Added: {cmd}")
        else:
            messagebox.showwarning("Warning", "Exists")

    def delete_command(self):
        """Delete command"""
        sel = self.cmd_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select")
            return

        cmd = self.cmd_tree.item(sel[0])["values"][0]

        if messagebox.askyesno("Confirm", f"Delete '{cmd}'?"):
            self.command_manager.remove_command(cmd)
            self.refresh_commands()
            self.refresh_training()

    def refresh_commands(self):
        """Refresh commands"""
        for item in self.cmd_tree.get_children():
            self.cmd_tree.delete(item)

        for cmd in self.command_manager.get_all_commands():
            self.cmd_tree.insert("", tk.END, values=(cmd,))

    def train_command(self):
        """Train command"""
        sel = self.training_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select")
            return

        cmd = self.training_tree.item(sel[0])["values"][0]

        if not self.audio_processor:
            messagebox.showerror("Error", "Not ready")
            return

        speaker_id = None
        speaker_name = self.train_speaker_var.get()
        if speaker_name != "None":
            for sid, info in self.speaker_manager.get_all_speakers().items():
                if info["name"] == speaker_name:
                    speaker_id = sid
                    break

        train_win = tk.Toplevel(self.root)
        train_win.title(f"Training: {cmd}")
        train_win.geometry("400x200")
        train_win.configure(bg=THEME["bg"])
        train_win.grab_set()

        tk.Label(train_win, text=f"Say '{cmd}' 3-5 times for 5 seconds", font=("Arial", 12), bg=THEME["bg"]).pack(
            pady=20)

        countdown_label = tk.Label(train_win, text="5", font=("Arial", 48, "bold"), bg=THEME["bg"],
                                   fg=THEME["button_blue"])
        countdown_label.pack(pady=20)

        def train_worker():
            import time
            try:
                for i in range(5, 0, -1):
                    train_win.after(0, lambda x=i: countdown_label.config(text=str(x)))
                    time.sleep(1)

                train_win.after(0, lambda: countdown_label.config(text="Recording..."))

                audio = self.audio_processor.record_audio(duration=5)

                if audio is not None:
                    result = self.audio_processor.transcribe(audio)

                    if result and isinstance(result, str):
                        count = result.lower().count(cmd.lower())

                        self.command_manager.add_training(cmd, speaker_id)
                        info = self.command_manager.get_command_info(cmd)

                        train_win.after(0, train_win.destroy)
                        self.root.after(0, self.refresh_training)

                        msg = f"Recognized {count} times\n\nCount: {info['training_count']}\nWeight: {info['weight']:.2f}x"
                        if speaker_id:
                            msg += f"\nSpeaker: {speaker_name}"

                        messagebox.showinfo("Complete", msg)
                    else:
                        train_win.after(0, train_win.destroy)
                        messagebox.showerror("Error", "Failed")
                else:
                    train_win.after(0, train_win.destroy)
                    messagebox.showerror("Error", "Record failed")
            except Exception as e:
                print(f"❌ Error: {e}")
                if train_win.winfo_exists():
                    train_win.after(0, train_win.destroy)
                messagebox.showerror("Error", str(e))

        threading.Thread(target=train_worker, daemon=True).start()

    def refresh_training(self):
        """Refresh training"""
        for item in self.training_tree.get_children():
            self.training_tree.delete(item)

        for cmd in self.command_manager.get_all_commands():
            info = self.command_manager.get_command_info(cmd)
            self.training_tree.insert("", tk.END, values=(cmd, info["training_count"], f"{info['weight']:.2f}x"))

    def add_speaker(self):
        """Add speaker"""
        name = self.speaker_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Enter name")
            return

        self.speaker_manager.add_speaker(name)
        self.speaker_entry.delete(0, tk.END)
        self.refresh_speakers()
        self.update_speaker_combo()
        self.update_train_speaker_combo()
        messagebox.showinfo("Success", f"Added: {name}")

    def delete_speaker(self):
        """Delete speaker"""
        sel = self.speaker_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select")
            return

        item = self.speaker_tree.item(sel[0])
        sid = item["values"][0]
        name = item["values"][1]

        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            self.speaker_manager.remove_speaker(sid)
            self.refresh_speakers()
            self.update_speaker_combo()
            self.update_train_speaker_combo()

    def refresh_speakers(self):
        """Refresh speakers"""
        for item in self.speaker_tree.get_children():
            self.speaker_tree.delete(item)

        for sid, info in self.speaker_manager.get_all_speakers().items():
            self.speaker_tree.insert("", tk.END, values=(sid, info["name"]))

    def update_speaker_combo(self):
        """Update speaker combo"""
        speakers = ["Auto", "None"] + [info["name"] for info in self.speaker_manager.get_all_speakers().values()]
        self.speaker_combo["values"] = speakers
        if self.speaker_var.get() not in speakers:
            self.speaker_combo.set("Auto")

    def update_train_speaker_combo(self):
        """Update train speaker combo"""
        speakers = ["None"] + [info["name"] for info in self.speaker_manager.get_all_speakers().values()]
        self.train_speaker_combo["values"] = speakers
        if self.train_speaker_var.get() not in speakers:
            self.train_speaker_combo.set("None")


def main():
    root = tk.Tk()
    app = VoiceCommandApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()