# ============================================================================
# optimized_audio_processor.py
# ============================================================================

import warnings
warnings.filterwarnings("ignore")

import os
import sys
import re
import time
import threading
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pyaudio
from typing import Optional, List, Dict, Any

# Import optimized modules
from command_manager import CommandManager
from tts_engine import TTSEngine
from model_manager import ModelManager

# Whisper backend detection
BACKEND = None
try:
    from faster_whisper import WhisperModel
    BACKEND = "faster-whisper"
except ImportError:
    try:
        import whisper
        BACKEND = "openai-whisper"
    except ImportError:
        BACKEND = "none"
        print("❌ WARNING: No Whisper backend available")

class AudioEngine:
    """
    Core audio processing engine for offline voice control system.
    Handles wake word detection, speech recognition, and command execution.
    """
    
    # State definitions
    WAKE_STATE_INACTIVE = 0
    WAKE_STATE_ACTIVE = 1
    
    def __init__(self, model_size="base", language="en", device="cpu"):
        """Initialize audio engine with specified model and language"""
        
        # Basic configuration
        self.language = language
        self.wake_state = self.WAKE_STATE_INACTIVE
        self.model_size = model_size
        self.device = device
        self.model = None
        
        # State management
        self._lock = threading.Lock()
        self._processing = False
        self._last_command_time = 0
        self._command_cooldown = 3.0  # Increased to 3 seconds cooldown to prevent too fast recognition
        
        # Error and success tracking for diagnostics
        self._last_success_time = None
        self._last_error_message = None
        
        # Initialize managers
        print("🔄 Initializing audio engine...")
        
        # Command manager
        self.cmd_hotword_mgr = CommandManager()
        
        # TTS engine
        self.tts_mgr = TTSEngine()
        
        # Model manager
        self.model_mgr = ModelManager()
        
        # Initialize Whisper model
        self._initialize_whisper_model()
        
        print(f"✅ AudioEngine initialized")
        print(f"   Model: {model_size}, Backend: {BACKEND}")
    
    def _initialize_whisper_model(self):
        """Initialize Whisper model"""
        try:
            if BACKEND == "faster-whisper":
                # Use local model manager to load model
                print(f"🔄 Loading local model: {self.model_size}")
                self.model = self.model_mgr.load_model(self.model_size)
                
                if self.model:
                    print("✅ Using local faster-whisper model")
                else:
                    print("❌ Failed to load local model")
                    
            elif BACKEND == "openai-whisper":
                import whisper
                self.model = whisper.load_model(self.model_size, device=self.device)
                print("✅ Using openai-whisper model")
                
            else:
                print("❌ No Whisper backend available")
                self.model = None
                
        except Exception as e:
            print(f"❌ Model initialization error: {e}")
            self.model = None
    
    def set_wake_state(self, state):
        """Set wake state (thread-safe)"""
        if state not in [self.WAKE_STATE_INACTIVE, self.WAKE_STATE_ACTIVE]:
            return False
        
        with self._lock:
            self.wake_state = state
            
        state_name = "ACTIVE" if state == 1 else "INACTIVE"
        print(f"🔄 Wake state: {state_name}")
        return True
    
    def get_wake_state(self):
        """Get wake state"""
        with self._lock:
            return self.wake_state
    
    def is_active(self):
        """Check if active"""
        return self.get_wake_state() == self.WAKE_STATE_ACTIVE
    
    def is_processing(self):
        """Check if processing"""
        with self._lock:
            return self._processing
    
    def record_audio(self, duration=5, sample_rate=16000):
        """Record audio (reduced terminal output)"""
        chunk = 1024
        channels = 1
        
        try:
            p = pyaudio.PyAudio()
            
            # Find default input device (no device info output)
            default_device = p.get_default_input_device_info()
            # print(f"🎤 Using microphone: {default_device['name']}")  # Removed terminal output
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=default_device['index']
            )
            
            frames = []
            frames_to_read = int(sample_rate / chunk * duration)
            
            for i in range(frames_to_read):
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    # print(f"⚠️ Audio read warning: {e}")  # Reduced output
                    continue
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if not frames:
                print("❌ No audio data recorded")
                return None
            
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            # Check audio quality (simplified output)
            rms = np.sqrt(np.mean(audio_data**2))
            if rms < 0.001:  # Too quiet
                print("⚠️ Audio too quiet")
            
            # print(f"✅ Recorded {duration}s audio, RMS: {rms:.4f}")  # Reduced output
            return audio_data
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def detect_wake_word(self, audio_data, wake_word="susie"):
        """Detect wake word (enhanced processing)"""
        if audio_data is None or self.model is None:
            return False
        
        with self._lock:
            if self._processing:
                print("⚠️ Already processing, skipping wake word detection")
                return False
            self._processing = True
        
        try:
            # Get hotword boost
            boost_phrases = [wake_word] + self.cmd_hotword_mgr.get_boost_phrases(5)
            
            # print(f"🔍 Detecting wake word '{wake_word}'...")  # Reduced output
            
            # Transcribe audio
            if BACKEND == "faster-whisper":
                initial_prompt = ", ".join(boost_phrases)
                segments, _ = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=1,
                    vad_filter=True,
                    initial_prompt=initial_prompt
                )
                text = " ".join([seg.text for seg in segments])
                
            elif BACKEND == "openai-whisper":
                initial_prompt = ", ".join(boost_phrases)
                result = self.model.transcribe(
                    audio_data, 
                    language=self.language, 
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]
            else:
                return False
            
            text = text.strip().lower()
            detected = wake_word.lower() in text
            
            # print(f"🔍 Wake word detection result: '{text}' -> {detected}")  # Reduced output
            
            if detected:
                print(f"✅ Wake word '{wake_word}' detected")
                # TTS announce wake
                self.tts_mgr.speak_status("please speak")
            
            return detected
            
        except Exception as e:
            print(f"❌ Wake word detection error: {e}")
            return False
        finally:
            with self._lock:
                self._processing = False
    
    def transcribe(self, audio_data):
        """Transcribe audio (enhanced state check and error handling)"""
        # State check
        current_state = self.get_wake_state()
        if current_state != self.WAKE_STATE_ACTIVE:
            print(f"❌ Not in active state (current: {current_state}), skipping transcription")
            return None
        
        if audio_data is None or self.model is None:
            print("❌ No audio data or model not available")
            return None
        
        with self._lock:
            if self._processing:
                print("⚠️ Already processing, skipping transcription")
                return None
            self._processing = True
        
        try:
            # Get hotword boost phrases
            boost_phrases = self.cmd_hotword_mgr.get_boost_phrases(15)
            initial_prompt = ", ".join(boost_phrases) if boost_phrases else None
            
            print("🔄 Transcribing audio...")
            
            # Transcribe audio
            if BACKEND == "faster-whisper":
                segments, _ = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=3,  # Reduced beam_size for faster speed
                    vad_filter=True,
                    initial_prompt=initial_prompt
                )
                text = " ".join([seg.text for seg in segments])
                
            elif BACKEND == "openai-whisper":
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]
            else:
                return None
            
            text = text.strip()
            
            # Number formatting
            text = self._format_numbers(text)
            
            print(f"✅ Transcription result: '{text}'")
            
            # Track successful transcription
            from datetime import datetime
            self._last_success_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return text if text else None
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            
            # Track error for diagnostics
            from datetime import datetime
            self._last_error_message = f"Transcription error at {datetime.now().strftime('%H:%M:%S')}: {str(e)}"
            
            return None
        finally:
            with self._lock:
                self._processing = False
    
    def _format_numbers(self, text: str) -> str:
        """Format number output"""
        if not text:
            return text
        
        # English number words to Arabic numerals mapping
        number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
            'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
        }
        
        # Replace English numbers with Arabic numerals
        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?')
            if word_lower in number_words:
                words[i] = word.replace(word_lower, number_words[word_lower])
        
        return ' '.join(words)
    
    def match_command(self, text, commands):
        """Match command with intelligent matching algorithm and usage tracking"""
        if not text or not commands:
            return None
        
        # Check cooldown time to prevent duplicate recognition
        current_time = time.time()
        if current_time - self._last_command_time < self._command_cooldown:
            print(f"⚠️ Command cooldown active ({self._command_cooldown}s)")
            return None
        
        text_lower = text.lower().strip()
        matched_command = None
        
        # Priority 1: Exact match (highest priority)
        for cmd in commands:
            if cmd.lower().strip() == text_lower:
                matched_command = cmd
                break
        
        # Priority 2: Contains match (if exact match fails)
        if not matched_command:
            for cmd in commands:
                cmd_lower = cmd.lower().strip()
                if cmd_lower in text_lower or text_lower in cmd_lower:
                    matched_command = cmd
                    break
        
        # Record usage statistics for weight optimization
        if matched_command:
            self.cmd_hotword_mgr.record_usage(matched_command, success=True)
            self._last_command_time = current_time
            print(f"✅ Command matched: '{text}' -> '{matched_command}'")
        else:
            # Track partial matches for failed recognition analysis
            for word in text_lower.split():
                if word in [cmd.lower() for cmd in commands]:
                    self.cmd_hotword_mgr.record_usage(word, success=False)
            print(f"❌ No command match for: '{text}'")
        
        return matched_command
    
    def reset_wake_state(self):
        """Reset wake state"""
        with self._lock:
            self.wake_state = self.WAKE_STATE_INACTIVE
            self._processing = False
        
        print("🔄 Wake state reset to INACTIVE")
        # TTS announce state reset
        self.tts_mgr.speak_status("stand by")
    
    def add_command(self, text: str) -> bool:
        """Add command"""
        return self.cmd_hotword_mgr.add_command(text)
    
    def remove_command(self, text: str) -> bool:
        """Remove command"""
        return self.cmd_hotword_mgr.remove_command(text)
    
    def get_all_commands(self) -> List[str]:
        """Get all commands"""
        return self.cmd_hotword_mgr.get_all_commands()
    
    def train_command(self, text: str) -> float:
        """Train command"""
        return self.cmd_hotword_mgr.train_command(text)
    
    def get_training_count(self, text: str) -> int:
        """Get training count"""
        return self.cmd_hotword_mgr.get_training_count(text)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for monitoring and diagnostics"""
        with self._lock:
            current_wake_state = self.wake_state
            current_processing = self._processing
        
        # Wake state description for better UI display
        wake_state_desc = "ACTIVE - Command Mode" if current_wake_state == self.WAKE_STATE_ACTIVE else "INACTIVE - Standby Mode"
        
        status = {
            "wake_state": wake_state_desc,
            "wake_state_raw": current_wake_state,
            "processing": current_processing,
            "model_size": self.model_size,
            "backend": BACKEND,
            "model_loaded": self.model is not None,
            "model_path": "Local cache" if self.model else "Not loaded",
            "model_error": "None" if self.model else "Model not initialized",
            "features": {
                "tts_enabled": True,
                "hotwords_enabled": True,
                "embedded_models": True,
                "offline_mode": True,
                "dynamic_weights": True
            }
        }
        
        # Command statistics with detailed metrics
        cmd_stats = self.cmd_hotword_mgr.get_statistics()
        status["commands"] = {
            "total": cmd_stats["total"],
            "most_used": cmd_stats["most_used"][:5],  # Show top 5
            "highest_weight": cmd_stats.get("highest_weight", [])[:3]
        }
        
        # TTS engine status with error tracking
        tts_info = self.tts_mgr.get_engine_info()
        status["tts"] = {
            "engine_type": tts_info["engine_type"],
            "enabled": tts_info["enabled"],
            "running": tts_info["running"],
            "speaking": tts_info["speaking"],
            "error": tts_info.get("error", "None")
        }
        
        # Local model manager status
        model_info = self.model_mgr.get_system_info()
        status["local_models"] = {
            "offline_mode": model_info["offline_mode"],
            "available": model_info["available_models"],
            "total_size": model_info["total_size"],
            "error": model_info.get("error", "None")
        }
        
        # Add timestamps for last success/error
        status["last_success"] = getattr(self, '_last_success_time', 'N/A')
        status["last_error"] = getattr(self, '_last_error_message', 'None')
        
        return status
    
    def shutdown(self):
        """Shutdown processor"""
        print("🔄 Shutting down audio processor...")
        
        # Reset state
        with self._lock:
            self.wake_state = self.WAKE_STATE_INACTIVE
            self._processing = False
        
        # Stop TTS
        if self.tts_mgr:
            self.tts_mgr.stop()
        
        print("✅ Audio processor shutdown complete")