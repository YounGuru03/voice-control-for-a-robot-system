# ============================================================================
# main_voice_app.py
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import time
from datetime import datetime

# 导入优化模块
from optimized_audio_processor import OptimizedAudioProcessor
from speaker_manager import SpeakerManager

# 简化的颜色配置
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
    """简化的语音控制应用 - 修复转义符和时间间隔问题"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Control System")
        self.root.geometry("800x700")
        self.root.configure(bg=COLORS["bg"])
        
        # 状态变量
        self.STATE_IDLE = "IDLE"
        self.STATE_LISTEN_WAKE = "LISTEN_WAKE"
        self.STATE_CMD_MODE = "CMD_MODE"
        self.state = self.STATE_IDLE
        self.is_listening = False
        self.fail_count = 0
        
        # 线程控制
        self.recognition_thread = None
        self._stop_flag = threading.Event()
        
        # 初始化管理器
        print("[INIT] Loading system components...")
        self.spk_mgr = SpeakerManager()
        self.audio = None
        
        # 构建UI
        self._build_ui()
        
        # 初始化音频处理器
        self._init_audio()
    
    def _build_ui(self):
        """构建简化的用户界面"""
        # 标题栏
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="Voice Control System", 
                              font=("Arial", 16, "bold"), 
                              bg=COLORS["primary"], fg="white")
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 状态指示器
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = tk.Label(header, textvariable=self.status_var,
                               font=("Arial", 10), bg=COLORS["primary"], fg="white")
        status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 主界面标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 识别标签页
        self.tab_recognition = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_recognition, text="Recognition")
        
        # 命令标签页
        self.tab_commands = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_commands, text="Commands")
        
        # 训练标签页
        self.tab_training = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_training, text="Training")
        
        # 说话人标签页
        self.tab_speakers = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_speakers, text="Speakers")
        
        # 系统标签页
        self.tab_system = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.tab_system, text="System")
        
        # 构建各个标签页
        self._build_recognition_tab()
        self._build_commands_tab()
        self._build_training_tab()
        self._build_speakers_tab()
        self._build_system_tab()
    
    def _build_recognition_tab(self):
        """构建识别标签页"""
        # 标题
        tk.Label(self.tab_recognition, text="Voice Recognition", 
                font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        
        # 状态信息框
        status_info_frame = tk.LabelFrame(self.tab_recognition, text="System Status", 
                                        font=("Arial", 11, "bold"), bg=COLORS["bg"])
        status_info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.detailed_status_var = tk.StringVar(value="System initializing...")
        detailed_status_label = tk.Label(status_info_frame, textvariable=self.detailed_status_var,
                                        font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["dark"],
                                        justify=tk.LEFT, wraplength=600)
        detailed_status_label.pack(padx=10, pady=5)
        
        # 控制按钮
        btn_frame = tk.Frame(self.tab_recognition, bg=COLORS["bg"])
        btn_frame.pack(pady=20)
        
        self.btn_start = tk.Button(btn_frame, text="▶ Start Listening", 
                                  font=("Arial", 12, "bold"),
                                  bg=COLORS["success"], fg="white", 
                                  width=18, height=2, 
                                  command=self._start_listening,
                                  state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(btn_frame, text="⏹ Stop", 
                                 font=("Arial", 12, "bold"),
                                 bg=COLORS["danger"], fg="white", 
                                 width=18, height=2,
                                 command=self._stop_listening,
                                 state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(self.tab_recognition, text="Recognition Results", 
                                   font=("Arial", 11, "bold"), bg=COLORS["bg"])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 结果文本区域
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                   font=("Consolas", 10),
                                                   bg="white", height=12, 
                                                   wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 清除按钮
        clear_btn = tk.Button(result_frame, text="Clear Results", 
                            bg=COLORS["secondary"], fg="white",
                            command=lambda: self.result_text.delete("1.0", tk.END))
        clear_btn.pack(pady=5)
    
    def _build_commands_tab(self):
        """构建命令标签页"""
        tk.Label(self.tab_commands, text="Command Management", 
                font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        
        # 添加命令区域
        add_frame = tk.Frame(self.tab_commands, bg=COLORS["bg"])
        add_frame.pack(pady=10)
        
        tk.Label(add_frame, text="New Command:", 
                font=("Arial", 11), bg=COLORS["bg"]).pack(side=tk.LEFT, padx=5)
        
        self.cmd_entry = tk.Entry(add_frame, font=("Arial", 11), width=30)
        self.cmd_entry.pack(side=tk.LEFT, padx=5)
        self.cmd_entry.bind("<Return>", lambda e: self._add_command())
        
        tk.Button(add_frame, text="Add Command", 
                 bg=COLORS["success"], fg="white",
                 command=self._add_command).pack(side=tk.LEFT, padx=5)
        
        # 命令列表
        list_frame = tk.LabelFrame(self.tab_commands, text="Commands List", 
                                 font=("Arial", 11, "bold"), bg=COLORS["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.cmd_listbox = tk.Listbox(list_frame, font=("Arial", 10), height=15)
        self.cmd_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 命令操作按钮
        cmd_btn_frame = tk.Frame(list_frame, bg=COLORS["bg"])
        cmd_btn_frame.pack(pady=5)
        
        tk.Button(cmd_btn_frame, text="Delete Selected", 
                 bg=COLORS["danger"], fg="white",
                 command=self._delete_command).pack(side=tk.LEFT, padx=5)
        
        tk.Button(cmd_btn_frame, text="Refresh List", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_commands).pack(side=tk.LEFT, padx=5)
        
        self._refresh_commands()
    
    def _build_training_tab(self):
        """构建训练标签页"""
        tk.Label(self.tab_training, text="Command Training", 
                font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        
        tk.Label(self.tab_training, text="Select a command and click Train to improve recognition", 
                font=("Arial", 10), bg=COLORS["bg"]).pack(pady=5)
        
        # 训练列表
        train_frame = tk.LabelFrame(self.tab_training, text="Training Progress", 
                                  font=("Arial", 11, "bold"), bg=COLORS["bg"])
        train_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.train_tree = ttk.Treeview(train_frame, 
                                     columns=("Command", "Count", "Weight"), 
                                     show="headings", height=15)
        
        self.train_tree.heading("Command", text="Command")
        self.train_tree.heading("Count", text="Training Count")
        self.train_tree.heading("Weight", text="Recognition Weight")
        
        self.train_tree.column("Command", width=250)
        self.train_tree.column("Count", width=100)
        self.train_tree.column("Weight", width=120)
        
        self.train_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 训练按钮
        train_btn = tk.Button(train_frame, text="Train Selected Command", 
                            font=("Arial", 11, "bold"),
                            bg=COLORS["warning"], fg="black",
                            command=self._train_command)
        train_btn.pack(pady=10)
        
        tk.Button(train_frame, text="Refresh Training Data", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_training).pack(pady=5)
        
        self._refresh_training()
    
    def _build_speakers_tab(self):
        """构建说话人标签页"""
        tk.Label(self.tab_speakers, text="Speaker Management", 
                font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        
        # 添加说话人
        add_spk_frame = tk.Frame(self.tab_speakers, bg=COLORS["bg"])
        add_spk_frame.pack(pady=10)
        
        tk.Label(add_spk_frame, text="Speaker Name:", 
                font=("Arial", 11), bg=COLORS["bg"]).pack(side=tk.LEFT, padx=5)
        
        self.spk_entry = tk.Entry(add_spk_frame, font=("Arial", 11), width=25)
        self.spk_entry.pack(side=tk.LEFT, padx=5)
        self.spk_entry.bind("<Return>", lambda e: self._add_speaker())
        
        tk.Button(add_spk_frame, text="Add Speaker", 
                 bg=COLORS["success"], fg="white",
                 command=self._add_speaker).pack(side=tk.LEFT, padx=5)
        
        # 说话人列表
        spk_frame = tk.LabelFrame(self.tab_speakers, text="Speakers List", 
                                font=("Arial", 11, "bold"), bg=COLORS["bg"])
        spk_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.spk_tree = ttk.Treeview(spk_frame, columns=("ID", "Name"), 
                                   show="headings", height=15)
        
        self.spk_tree.heading("ID", text="Speaker ID")
        self.spk_tree.heading("Name", text="Name")
        
        self.spk_tree.column("ID", width=120)
        self.spk_tree.column("Name", width=200)
        
        self.spk_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 说话人操作按钮
        spk_btn_frame = tk.Frame(spk_frame, bg=COLORS["bg"])
        spk_btn_frame.pack(pady=5)
        
        tk.Button(spk_btn_frame, text="Delete Selected", 
                 bg=COLORS["danger"], fg="white",
                 command=self._delete_speaker).pack(side=tk.LEFT, padx=5)
        
        tk.Button(spk_btn_frame, text="Refresh List", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_speakers).pack(side=tk.LEFT, padx=5)
        
        self._refresh_speakers()
    
    def _build_system_tab(self):
        """构建系统标签页"""
        tk.Label(self.tab_system, text="System Information", 
                font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(pady=15)
        
        # 系统状态显示
        status_frame = tk.LabelFrame(self.tab_system, text="System Status", 
                                   font=("Arial", 11, "bold"), bg=COLORS["bg"])
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.system_status_text = tk.Text(status_frame, 
                                        font=("Consolas", 9), 
                                        height=20, state=tk.DISABLED,
                                        bg="white")
        self.system_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 系统操作按钮
        sys_btn_frame = tk.Frame(status_frame, bg=COLORS["bg"])
        sys_btn_frame.pack(pady=10)
        
        tk.Button(sys_btn_frame, text="Refresh Status", 
                 bg=COLORS["primary"], fg="white",
                 command=self._refresh_system_status).pack(side=tk.LEFT, padx=5)
        
        tk.Button(sys_btn_frame, text="Save System Log", 
                 bg=COLORS["secondary"], fg="white",
                 command=self._save_system_log).pack(side=tk.LEFT, padx=5)
        
        self._refresh_system_status()
    
    def _init_audio(self):
        """初始化音频处理器"""
        def worker():
            try:
                self.audio = OptimizedAudioProcessor(
                    model_size="base",
                    language="en", 
                    device="cpu"
                )
                
                self.root.after(0, lambda: self._update_status("System Ready"))
                self.root.after(0, lambda: self._update_detailed_status("System initialized successfully. Ready to start listening."))
                self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
                self.root.after(0, lambda: self._append_result("✅ Voice Control System initialized successfully"))
                
            except Exception as e:
                error_msg = f"System initialization failed: {e}"
                self.root.after(0, lambda: self._update_status("Initialization Failed"))
                self.root.after(0, lambda: self._update_detailed_status(f"Initialization error: {e}"))
                self.root.after(0, lambda: self._append_result(f"❌ {error_msg}"))
                print(f"❌ Audio initialization error: {e}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _start_listening(self):
        """开始监听（修复业务逻辑）"""
        if not self.audio or self.is_listening:
            return
        
        # 重置状态
        self._stop_flag.clear()
        self.is_listening = True
        self.fail_count = 0
        self.state = self.STATE_LISTEN_WAKE
        
        # 更新UI
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self._update_status("Listening for wake word 'susie'...")
        self._update_detailed_status("System is listening for the wake word 'susie'. Speak clearly into your microphone.")
        
        # 清除输出文件
        self._clear_output()
        
        # 记录日志（修复转义符问题）
        ts = datetime.now().strftime('%H:%M:%S')
        self._append_result(f"🎤 Voice recognition started at {ts}")
        self._append_result("💡 Say 'susie' to activate command mode")
        
        # TTS播报开始
        if self.audio.tts_mgr:
            self.audio.tts_mgr.speak_status("start")
        
        # 启动识别线程
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()
    
    def _stop_listening(self):
        """停止监听（修复清理逻辑）"""
        print("🔄 Stopping recognition...")
        
        # 设置停止标志
        self._stop_flag.set()
        self.is_listening = False
        
        # 重置音频处理器状态
        if self.audio:
            self.audio.reset_wake_state()
        
        # 更新状态
        self.state = self.STATE_IDLE
        
        # 更新UI
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self._update_status("System Ready")
        self._update_detailed_status("Recognition stopped. System is ready to start listening again.")
        
        # 记录日志
        ts = datetime.now().strftime('%H:%M:%S')
        self._append_result(f"⏹ Voice recognition stopped at {ts}")
        
        # TTS播报停止
        if self.audio and self.audio.tts_mgr:
            self.audio.tts_mgr.speak_status("stop")
        
        # 等待识别线程结束
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2.0)
        
        print("✅ Recognition stopped successfully")
    
    def _recognition_loop(self):
        """识别循环（修复时间间隔和输出格式）"""
        try:
            print("🔄 Starting recognition loop...")
            
            while self.is_listening and not self._stop_flag.is_set():
                try:
                    # 阶段1：等待唤醒词
                    if self.state == self.STATE_LISTEN_WAKE:
                        self.root.after(0, lambda: self._update_detailed_status("Listening for wake word 'susie'..."))
                        
                        print("🔍 Recording for wake word detection...")
                        audio = self.audio.record_audio(duration=3)
                        
                        if audio is None or self._stop_flag.is_set():
                            continue
                        
                        # 检测"susie"
                        if self.audio.detect_wake_word(audio, "susie"):
                            # 激活命令模式
                            self.audio.set_wake_state(self.audio.WAKE_STATE_ACTIVE)
                            self.state = self.STATE_CMD_MODE
                            self.fail_count = 0
                            
                            ts = datetime.now().strftime("%H:%M:%S")
                            self.root.after(0, lambda: self._update_status("Command mode - Speak your command"))
                            self.root.after(0, lambda: self._update_detailed_status("Wake word detected! Command mode activated. Speak your command clearly."))
                            self.root.after(0, lambda: self._append_result(f"[{ts}] 🎯 Wake word detected - Command mode activated"))
                        
                        # 添加间隔，防止过快检测
                        time.sleep(1.0)
                    
                    # 阶段2：命令识别模式
                    elif self.state == self.STATE_CMD_MODE:
                        self.root.after(0, lambda: self._update_detailed_status(f"Command mode active. Listening for commands... (Failures: {self.fail_count}/5)"))
                        
                        print("🔍 Recording for command recognition...")
                        audio = self.audio.record_audio(duration=5)  # 稍长一点确保完整录音
                        
                        if audio is None or self._stop_flag.is_set():
                            continue
                        
                        # 转写音频
                        text = self.audio.transcribe(audio)
                        
                        if not text or not isinstance(text, str):
                            print("⚠️ No transcription result")
                            time.sleep(1.0)  # 添加间隔
                            continue
                        
                        text = text.strip()
                        if not text:
                            print("⚠️ Empty transcription")
                            time.sleep(1.0)  # 添加间隔
                            continue
                        
                        print(f"✅ Transcribed: '{text}'")
                        
                        # 匹配命令
                        commands = self.audio.get_all_commands()
                        matched_cmd = self.audio.match_command(text, commands)
                        
                        ts = datetime.now().strftime("%H:%M:%S")
                        
                        if matched_cmd:
                            # 命令匹配成功（简化输出格式）
                            self.fail_count = 0
                            if self._write_output(matched_cmd):
                                msg = f"[{ts}] Command: '{matched_cmd}' ✅→ Saved to output.txt"
                                self.root.after(0, lambda: self._update_detailed_status(f"Command executed successfully: '{matched_cmd}'"))
                            else:
                                msg = f"[{ts}] Command: '{matched_cmd}' ❌→ File save failed"
                                self.root.after(0, lambda: self._update_detailed_status(f"Command recognized but file save failed: '{matched_cmd}'"))
                        else:
                            # 命令未匹配
                            self.fail_count += 1
                            msg = f"[{ts}] ❌ '{text}' → No matching command (Failures: {self.fail_count}/5)"
                            self.root.after(0, lambda: self._update_detailed_status(f"No matching command found for: '{text}' (Failures: {self.fail_count}/5)"))
                        
                        self.root.after(0, lambda m=msg: self._append_result(m))
                        
                        # 检查失败次数
                        if self.fail_count >= 5:
                            print("⚠️ Too many failures, returning to wake word mode")
                            self.state = self.STATE_LISTEN_WAKE
                            self.fail_count = 0
                            self.audio.reset_wake_state()
                            self.root.after(0, lambda: self._update_status("Listening for wake word 'susie'..."))
                            self.root.after(0, lambda: self._update_detailed_status("Too many unmatched commands. Returned to wake word mode. Say 'susie' again."))
                            self.root.after(0, lambda: self._append_result("⚠️ Too many unmatched commands. Returned to wake word mode."))
                        
                        # 添加间隔，防止识别过快
                        time.sleep(2.0)
                
                except Exception as e:
                    print(f"❌ Recognition loop error: {e}")
                    self.root.after(0, lambda: self._append_result(f"❌ Recognition error: {e}"))
                    time.sleep(2.0)  # 出错后增加更长间隔
                    continue
        
        except Exception as e:
            print(f"❌ Critical recognition loop error: {e}")
            self.root.after(0, lambda: self._append_result(f"❌ Critical error: {e}"))
        finally:
            print("🔄 Recognition loop ended")
            if self.is_listening:
                self.root.after(0, self._stop_listening)
    
    def _add_command(self):
        """添加命令"""
        if not self.audio:
            return
            
        cmd = self.cmd_entry.get().strip()
        if cmd and self.audio.add_command(cmd):
            self.cmd_entry.delete(0, tk.END)
            self._refresh_commands()
            self._refresh_training()
            messagebox.showinfo("Success", f"Command '{cmd}' added successfully")
    
    def _delete_command(self):
        """删除命令"""
        if not self.audio:
            return
            
        selection = self.cmd_listbox.curselection()
        if selection:
            cmd = self.cmd_listbox.get(selection[0])
            if messagebox.askyesno("Confirm", f"Delete command '{cmd}'?"):
                if self.audio.remove_command(cmd):
                    self._refresh_commands()
                    self._refresh_training()
    
    def _refresh_commands(self):
        """刷新命令列表"""
        if not self.audio:
            return
            
        self.cmd_listbox.delete(0, tk.END)
        commands = self.audio.get_all_commands()
        for cmd in commands:
            self.cmd_listbox.insert(tk.END, cmd)
    
    def _train_command(self):
        """训练命令"""
        if not self.audio:
            return
            
        selection = self.train_tree.selection()
        if selection:
            item = self.train_tree.item(selection[0])
            cmd = item["values"][0]
            weight = self.audio.train_command(cmd)
            self._refresh_training()
            messagebox.showinfo("Training", f"Command '{cmd}' trained. New weight: {weight:.2f}")
    
    def _refresh_training(self):
        """刷新训练数据"""
        if not self.audio:
            return
            
        for item in self.train_tree.get_children():
            self.train_tree.delete(item)
        
        commands = self.audio.get_all_commands()
        for cmd in commands:
            count = self.audio.get_training_count(cmd)
            cmd_info = self.audio.cmd_hotword_mgr.get_command_info(cmd)
            weight = cmd_info.get("weight", 1.0)
            
            self.train_tree.insert("", tk.END, values=(cmd, count, f"{weight:.2f}"))
    
    def _add_speaker(self):
        """添加说话人"""
        name = self.spk_entry.get().strip()
        if name and self.spk_mgr.add(name):
            self.spk_entry.delete(0, tk.END)
            self._refresh_speakers()
    
    def _delete_speaker(self):
        """删除说话人"""
        selection = self.spk_tree.selection()
        if selection:
            item = self.spk_tree.item(selection[0])
            spk_id = item["values"][0]
            if self.spk_mgr.remove(spk_id):
                self._refresh_speakers()
    
    def _refresh_speakers(self):
        """刷新说话人列表"""
        for item in self.spk_tree.get_children():
            self.spk_tree.delete(item)
        
        speakers = self.spk_mgr.get_all()
        for spk_id, spk_data in speakers.items():
            name = spk_data.get("name", "Unknown") if isinstance(spk_data, dict) else spk_data
            self.spk_tree.insert("", tk.END, values=(spk_id, name))
    
    def _refresh_system_status(self):
        """刷新系统状态"""
        if not self.audio:
            status_text = "Audio processor not initialized"
        else:
            try:
                status = self.audio.get_system_status()
                
                status_text = "=== VOICE CONTROL SYSTEM STATUS ===\n\n"
                status_text += f"System State: {self.state}\n"
                status_text += f"Wake State: {status['wake_state']}\n"
                status_text += f"Processing: {status['processing']}\n"
                status_text += f"Is Listening: {self.is_listening}\n"
                status_text += f"Model: {status['model_size']} ({status['backend']})\n"
                status_text += f"Model Loaded: {status['model_loaded']}\n\n"
                
                status_text += "Features:\n"
                for feature, enabled in status['features'].items():
                    status_text += f"  {feature}: {'✅ Enabled' if enabled else '❌ Disabled'}\n"
                
                status_text += f"\nCommands: {status['commands']['total']} total\n"
                
                if status['commands']['most_used']:
                    status_text += "Most Used Commands:\n"
                    for cmd, count in status['commands']['most_used']:
                        status_text += f"  '{cmd}': {count} times\n"
                
                status_text += f"\nTTS Engine: {status['tts']['engine_type']}\n"
                status_text += f"TTS Running: {status['tts']['running']}\n"
                status_text += f"TTS Speaking: {status['tts']['speaking']}\n"
                
                status_text += f"\nLocal Models:\n"
                status_text += f"Offline Mode: {status['local_models']['offline_mode']}\n"
                status_text += f"Available Models: {len(status['local_models']['available'])}\n"
                status_text += f"Total Size: {status['local_models']['total_size']}\n"
                status_text += f"Models: {', '.join(status['local_models']['available'])}\n"
                
            except Exception as e:
                status_text = f"Error getting system status: {e}"
        
        self.system_status_text.config(state=tk.NORMAL)
        self.system_status_text.delete("1.0", tk.END)
        self.system_status_text.insert("1.0", status_text)
        self.system_status_text.config(state=tk.DISABLED)
    
    def _save_system_log(self):
        """保存系统日志"""
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
        """更新状态显示"""
        self.status_var.set(status)
    
    def _update_detailed_status(self, status):
        """更新详细状态显示"""
        self.detailed_status_var.set(status)
    
    def _append_result(self, text):
        """添加结果文本（修复转义符问题）"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
    
    def _clear_output(self):
        """清除输出文件"""
        try:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"Clear output error: {e}")
    
    def _write_output(self, text):
        """写入输出文件"""
        try:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"Write output error: {e}")
            return False
    
    def on_closing(self):
        """关闭应用时的清理"""
        print("🔄 Closing application...")
        
        # 停止监听
        if self.is_listening:
            self._stop_listening()
        
        # 关闭音频处理器
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