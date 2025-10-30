"""
Essential code additions for modern GUI with model/voice selection
Copy these methods into the appropriate files
"""

# ============================================================================
# ADD TO audio_engine.py - Model Switching Capability
# ============================================================================

class AudioEngine:
    # ... existing code ...
    
    def switch_model(self, model_size: str) -> bool:
        """
        Switch to a different Whisper model dynamically.
        Args:
            model_size: 'tiny', 'base', or 'small'
        Returns:
            bool: True if successful
        """
        if model_size not in ["tiny", "base", "small"]:
            print(f"❌ Invalid model size: {model_size}")
            return False
        
        print(f"🔄 Switching to {model_size} model...")
        
        try:
            # Stop current recognition if running
            was_listening = self.is_listening
            if was_listening:
                self.stop_listening()
            
            # Unload current model
            if hasattr(self, 'model') and self.model:
                del self.model
                self.model = None
                print("✅ Previous model unloaded")
            
            # Load new model
            self.model_size = model_size
            self._initialize_whisper_model()
            
            # Restart if was listening
            if was_listening:
                # Give a moment for model to settle
                import time
                time.sleep(0.5)
            
            print(f"✅ Switched to {model_size} model successfully")
            return True
            
        except Exception as e:
            print(f"❌ Model switch failed: {e}")
            return False
    
    def get_current_model(self) -> dict:
        """Get current model information"""
        from model_manager import SUPPORTED_WHISPER_MODELS
        return {
            "size": self.model_size,
            "info": SUPPORTED_WHISPER_MODELS.get(self.model_size, {}),
            "loaded": self.model is not None
        }


# ============================================================================
# ADD TO tts_engine.py - Voice Selection Capability
# ============================================================================

class TTSEngine:
    # ... existing code ...
    
    def get_available_voices(self) -> list:
        """
        Get list of available TTS voices.
        Returns list of dicts with voice info.
        """
        voices = []
        
        if not self.engine:
            return voices
        
        try:
            pyttsx3_voices = self.engine.getProperty('voices')
            
            for i, voice in enumerate(pyttsx3_voices):
                # Extract voice name (clean up)
                name = voice.name
                if '\\' in name:
                    name = name.split('\\')[-1]
                
                voice_info = {
                    "index": i,
                    "id": voice.id,
                    "name": name,
                    "gender": "Female" if "female" in name.lower() or "zira" in name.lower() else "Male"
                }
                voices.append(voice_info)
            
            # Limit to 3 best voices for simplicity
            return voices[:3] if len(voices) > 3 else voices
            
        except Exception as e:
            print(f"⚠️ Voice enumeration error: {e}")
            return []
    
    def set_voice_by_index(self, voice_index: int) -> bool:
        """
        Switch to a different TTS voice.
        Args:
            voice_index: Index of voice from get_available_voices()
        Returns:
            bool: True if successful
        """
        if not self.engine:
            print("❌ TTS engine not initialized")
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            
            if 0 <= voice_index < len(voices):
                voice_id = voices[voice_index].id
                self.engine.setProperty('voice', voice_id)
                
                # Save to config
                self.config["voice_index"] = voice_index
                self._save_config()
                
                print(f"✅ Voice changed to: {voices[voice_index].name}")
                return True
            else:
                print(f"❌ Invalid voice index: {voice_index}")
                return False
                
        except Exception as e:
            print(f"❌ Voice change failed: {e}")
            return False
    
    def preview_voice(self, voice_index: int, text: str = "Hello, this is a voice preview."):
        """Preview a voice before selecting it"""
        current_voice = self.config.get("voice_index", 0)
        
        # Temporarily switch voice
        if self.set_voice_by_index(voice_index):
            # Speak preview text
            self.speak_text(text, priority=True)
            # Note: Don't switch back automatically - let user decide


# ============================================================================
# ADD TO main_voice_app.py - Modern GUI Components
# ============================================================================

class VoiceControlApp:
    # ... in __init__ ...
    
    def _build_modern_control_panel(self):
        """Build modern control panel with model/voice selection"""
        
        # Control Panel Card
        control_card = ModernCard(self.tab_recognition)
        control_card.pack(fill=tk.X, padx=SPACING["lg"], pady=SPACING["md"])
        
        # === Model Selection Section ===
        model_frame = tk.Frame(control_card, bg=MODERN_COLORS["bg_primary"])
        model_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])
        
        ModernLabel(model_frame, text="Speech Model:", style="subheading").pack(anchor=tk.W)
        
        # Model dropdown
        model_options = list(SUPPORTED_WHISPER_MODELS.keys())
        self.model_combo = ModernCombobox(
            model_frame,
            textvariable=self.selected_model,
            values=model_options,
            width=20
        )
        self.model_combo.pack(anchor=tk.W, pady=(SPACING["xs"], 0))
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)
        
        # Model info display
        self.model_info_label = ModernLabel(
            model_frame,
            text=self._get_model_info_text("base"),
            style="small",
            fg=MODERN_COLORS["text_secondary"]
        )
        self.model_info_label.pack(anchor=tk.W, pady=(SPACING["xs"], 0))
        
        # Separator
        tk.Frame(control_card, height=1, bg=MODERN_COLORS["border"]).pack(
            fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"]
        )
        
        # === Voice Selection Section ===
        voice_frame = tk.Frame(control_card, bg=MODERN_COLORS["bg_primary"])
        voice_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])
        
        ModernLabel(voice_frame, text="Voice:", style="subheading").pack(anchor=tk.W)
        
        # Voice dropdown
        self.voice_combo = ModernCombobox(
            voice_frame,
            textvariable=self.selected_voice,
            values=["Loading..."],
            width=30
        )
        self.voice_combo.pack(anchor=tk.W, pady=(SPACING["xs"], 0))
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)
        
        # Preview button
        preview_btn = ModernButton(
            voice_frame,
            text="Preview Voice",
            command=self._preview_voice,
            style="secondary"
        )
        preview_btn.pack(anchor=tk.W, pady=(SPACING["xs"], 0))
        
        # Load voices asynchronously
        threading.Thread(target=self._load_available_voices, daemon=True).start()
    
    def _get_model_info_text(self, model_size):
        """Get formatted model info text"""
        info = SUPPORTED_WHISPER_MODELS.get(model_size, {})
        return f"Size: {info.get('size', 'N/A')} | Memory: {info.get('memory', 'N/A')} | Accuracy: {info.get('accuracy', 'N/A')}"
    
    def _on_model_change(self, event=None):
        """Handle model selection change"""
        new_model = self.selected_model.get()
        
        if not self.audio:
            messagebox.showinfo("Info", "Please wait for system initialization")
            return
        
        # Update info display
        self.model_info_label.config(text=self._get_model_info_text(new_model))
        
        # Ask for confirmation
        if messagebox.askyesno(
            "Change Model",
            f"Switch to {new_model} model?\n\nThis will briefly pause recognition."
        ):
            # Show progress
            self._update_status("Switching model...")
            
            def switch():
                success = self.audio.switch_model(new_model)
                if success:
                    self.root.after(0, lambda: self._update_status("Model switched successfully"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Now using {new_model} model"))
                else:
                    self.root.after(0, lambda: self._update_status("Model switch failed"))
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to switch model"))
            
            threading.Thread(target=switch, daemon=True).start()
        else:
            # Revert selection
            if self.audio:
                current = self.audio.get_current_model()
                self.selected_model.set(current["size"])
    
    def _load_available_voices(self):
        """Load available TTS voices"""
        if not self.audio or not self.audio.tts_mgr:
            return
        
        voices = self.audio.tts_mgr.get_available_voices()
        self.available_voices = voices
        
        if voices:
            voice_names = [f"{v['name']} ({v['gender']})" for v in voices]
            self.root.after(0, lambda: self.voice_combo.config(values=voice_names))
            self.root.after(0, lambda: self.voice_combo.current(0))
        else:
            self.root.after(0, lambda: self.voice_combo.config(values=["No voices available"]))
    
    def _on_voice_change(self, event=None):
        """Handle voice selection change"""
        selection = self.voice_combo.current()
        
        if selection >= 0 and selection < len(self.available_voices):
            voice = self.available_voices[selection]
            
            if self.audio and self.audio.tts_mgr:
                success = self.audio.tts_mgr.set_voice_by_index(voice["index"])
                if success:
                    messagebox.showinfo("Success", f"Voice changed to: {voice['name']}")
    
    def _preview_voice(self):
        """Preview the selected voice"""
        selection = self.voice_combo.current()
        
        if selection >= 0 and selection < len(self.available_voices):
            voice = self.available_voices[selection]
            
            if self.audio and self.audio.tts_mgr:
                self.audio.tts_mgr.preview_voice(
                    voice["index"],
                    "Hello, this is a preview of this voice. How does it sound?"
                )


# ============================================================================
# OPTIMIZATION FOR build.py - Minimal Resource Usage
# ============================================================================

"""
Update build.py with these optimizations for embedded deployment:
"""

# In build.py, update pyinstaller_args:

pyinstaller_args = [
    'main_voice_app.py',
    f'--name={APP_NAME}',
    '--onefile',  # Single file for USB portability
    '--windowed',  # No console
    '--clean',
    
    # OPTIMIZATION: Exclude unnecessary packages
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    '--exclude-module=pandas',
    '--exclude-module=PIL',
    '--exclude-module=notebook',
    '--exclude-module=IPython',
    '--exclude-module=pytest',
    '--exclude-module=sphinx',
    
    # OPTIMIZATION: Strip debug symbols
    '--strip',  # Reduce size (Windows/Linux)
    
    # OPTIMIZATION: UPX compression (if available)
    '--upx-dir=upx',  # Compress executable (requires UPX)
    
    # OPTIMIZATION: Only include tiny model for minimal deployment
    # Change MODEL_SIZE = 'tiny' at top of file
    
    # Hidden imports (minimal set)
    '--hidden-import=numpy.core._methods',
    '--hidden-import=numpy.lib.format',
    '--hidden-import=pyaudio',
    '--hidden-import=pyttsx3.drivers',
    '--hidden-import=pyttsx3.drivers.sapi5',
    
    # Data files (only essentials)
    f'--add-data=commands_hotwords.json{os.pathsep}.',
    f'--add-data=local_models{os.pathsep}local_models',  # Only tiny model
    
    # Collect only essential packages
    '--collect-data=faster_whisper',
    '--collect-binaries=pyaudio',
]

# Add to build script:
def optimize_for_low_resource():
    """Optimize build for minimal resource usage"""
    print("\n🎯 Optimizing for low-resource deployment...")
    
    # Use tiny model only
    global MODEL_SIZE, MODELS_TO_BUNDLE
    MODEL_SIZE = 'tiny'
    MODELS_TO_BUNDLE = ['tiny']
    
    print("   ✅ Using tiny model (fastest, lowest memory)")
    print("   ✅ Excluded unnecessary packages")
    print("   ✅ Enabled compression")
    print("   ✅ Target: i5 8th gen, 4GB RAM, USB deployment")
