# ============================================================================
# optimized_tts_manager.py
# ============================================================================

import os
import threading
import time
import queue
from typing import Optional, List, Dict, Any
from datetime import datetime

TTS_ENGINE = None
TTS_TYPE = None

try:
    import pyttsx3

    TTS_ENGINE = pyttsx3
    TTS_TYPE = "pyttsx3"
except ImportError:
    print("❌ pyttsx3 not available")


class TTSEngine:
    """
    Text-to-Speech engine with queue-based processing and fault tolerance.
    Provides non-blocking voice feedback for system status and command confirmation.
    """

    def __init__(self, config_file="tts_config.json"):
        """Initialize TTS engine with configuration"""
        self.config_file = os.path.abspath(config_file)
        self.config = self._load_config()

        # TTS queue and thread control
        self.tts_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.engine = None
        self._lock = threading.Lock()
        self._current_speaking = False

        # Enhanced fault tolerance control variables
        self._engine_error_count = 0
        self._max_error_count = 3
        self._last_engine_init_time = 0
        self._engine_init_cooldown = 5.0

        # Initialize engine
        self._initialize_engine()

        print(f"✅ TTSEngine initialized with {TTS_TYPE}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "enabled": True,
            "rate": 160,
            "volume": 0.9,
            "voice_index": 0
        }

        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception as e:
                print(f"⚠️ Config load error: {e}")

        return default_config

    def _initialize_engine(self):
        """Initialize TTS engine"""
        if not self.config["enabled"] or TTS_TYPE != "pyttsx3":
            return

        try:
            # Start worker thread
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
        except Exception as e:
            print(f"❌ TTS initialization error: {e}")

    def _init_pyttsx3_engine(self):
        """Initialize pyttsx3 engine (with fault tolerance)"""
        current_time = time.time()

        # Check cooldown time
        if current_time - self._last_engine_init_time < self._engine_init_cooldown:
            return False

        try:
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                self.engine = None

            # Reinitialize engine
            self.engine = pyttsx3.init()

            # Configure engine
            self.engine.setProperty('rate', self.config["rate"])
            self.engine.setProperty('volume', self.config["volume"])

            # Set voice
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > self.config["voice_index"]:
                voice_id = voices[self.config["voice_index"]].id
                self.engine.setProperty('voice', voice_id)

            self._engine_error_count = 0
            self._last_engine_init_time = current_time
            print("✅ TTS engine reinitialized successfully")
            return True

        except Exception as e:
            print(f"❌ Engine initialization error: {e}")
            self._engine_error_count += 1
            self._last_engine_init_time = current_time
            return False

    def _worker_loop(self):
        """TTS worker thread loop - Enhanced fault tolerance"""
        # Initialize engine
        if not self._init_pyttsx3_engine():
            print("❌ Failed to initialize TTS engine")
            return

        # Process TTS queue - Enhanced fault tolerance
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.is_running:
            try:
                # Get TTS task - Enhanced fault tolerance, won't break on empty queue
                try:
                    task = self.tts_queue.get(timeout=2.0)  # Increased timeout
                except queue.Empty:
                    # Continue waiting when queue is empty, don't exit
                    consecutive_errors = 0  # Reset consecutive error count
                    continue

                # Process stop signal
                if task is None:
                    print("🔄 TTS received stop signal")
                    break

                text = task.get("text", "")
                if not text:
                    consecutive_errors = 0
                    continue

                # Check engine status
                if not self.engine:
                    print("⚠️ Engine not available, attempting to reinitialize...")
                    if self._init_pyttsx3_engine():
                        print("✅ Engine reinitialized successfully")
                    else:
                        print("❌ Engine reinitialization failed, skipping task")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            print("❌ Too many consecutive errors, attempting full reset...")
                            time.sleep(3.0)
                            consecutive_errors = 0
                        continue

                # Execute TTS announcement
                try:
                    with self._lock:
                        self._current_speaking = True

                    print(f"🔊 Speaking: '{text[:50]}'")
                    print(f"   Text length: {len(text)}, ASCII-only: {all(ord(c) < 128 for c in text)}")
                    
                    self.engine.say(text)
                    self.engine.runAndWait()

                    print(f"✅ TTS completed successfully")
                    
                    # Reset error count on successful announcement
                    consecutive_errors = 0

                    # Brief pause after completion
                    time.sleep(0.5)

                except Exception as e:
                    print(f"❌ TTS speaking error: {e}")
                    print(f"   Failed text: '{text[:100]}'")
                    print(f"   Error type: {type(e).__name__}")
                    consecutive_errors += 1

                    # Attempt to reinitialize engine
                    if consecutive_errors >= 2:
                        print("⚠️ Multiple TTS errors, reinitializing engine...")
                        if self._init_pyttsx3_engine():
                            consecutive_errors = 0
                        else:
                            print("❌ Engine reinitialization failed")

                    # Pause if too many consecutive errors
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"❌ Too many consecutive TTS errors ({consecutive_errors}), pausing...")
                        time.sleep(5.0)
                        consecutive_errors = 0

                finally:
                    with self._lock:
                        self._current_speaking = False

                # Mark task as complete
                try:
                    self.tts_queue.task_done()
                except:
                    pass

            except Exception as e:
                print(f"❌ TTS worker loop error: {e}")
                consecutive_errors += 1

                # Pause and attempt recovery on critical error
                if consecutive_errors >= max_consecutive_errors:
                    print("❌ Critical TTS error, attempting recovery...")
                    time.sleep(3.0)

                    # Attempt to reinitialize engine
                    if self._init_pyttsx3_engine():
                        consecutive_errors = 0
                        print("✅ TTS recovery successful")
                    else:
                        print("❌ TTS recovery failed")

                continue

        # Clean up resources
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

        with self._lock:
            self._current_speaking = False

        print("✅ TTS worker loop ended")

    def speak_text(self, text: str, priority: bool = False) -> bool:
        """Speak (asynchronous, enhanced fault tolerance, supports priority)"""
        if not self.config["enabled"] or not text.strip():
            return False

        if not self.is_running:
            print("❌ TTS not running, attempting to restart...")
            # Attempt to restart TTS
            self._initialize_engine()
            if not self.is_running:
                return False

        if not self.worker_thread or not self.worker_thread.is_alive():
            print("❌ TTS worker thread not active, restarting...")
            self._initialize_engine()
            if not self.worker_thread or not self.worker_thread.is_alive():
                return False

        try:
            # Add to queue (enhanced fault tolerance)
            text = text.strip()
            
            # Sanitize text to remove emoji and special characters
            original_text = text
            text = self._sanitize_text(text)
            
            if not text:
                print(f"⚠️ Text became empty after sanitization: '{original_text[:50]}'")
                return False
            
            if text != original_text:
                print(f"🔄 Sanitized text: '{original_text[:30]}...' -> '{text[:30]}...'")
            
            if len(text) > 500:  # Limit text length
                text = text[:500] + "..."

            # If priority message, clear old tasks from queue
            if priority:
                cleared_count = 0
                while not self.tts_queue.empty() and cleared_count < 10:
                    try:
                        self.tts_queue.get_nowait()
                        cleared_count += 1
                    except queue.Empty:
                        break
                if cleared_count > 0:
                    print(f"🔄 Cleared {cleared_count} old TTS tasks for priority message")

            self.tts_queue.put({"text": text}, timeout=2.0)
            print(f"✅ Added to TTS queue: '{text[:50]}...'")
            return True

        except queue.Full:
            print("⚠️ TTS queue is full, clearing old tasks...")
            # Clear old tasks from queue
            cleared_count = 0
            while not self.tts_queue.empty() and cleared_count < 20:
                try:
                    self.tts_queue.get_nowait()
                    cleared_count += 1
                except queue.Empty:
                    break
            
            print(f"🔄 Cleared {cleared_count} old TTS tasks")

            # Retry adding
            try:
                self.tts_queue.put({"text": text}, timeout=1.0)
                print(f"✅ Added to TTS queue after clearing: '{text[:50]}...'")
                return True
            except Exception as retry_error:
                print(f"❌ Failed to add to queue even after clearing: {retry_error}")
                return False

        except Exception as e:
            print(f"❌ TTS queue error: {e}")
            return False

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text for TTS by removing emoji and special Unicode characters.
        Keeps only ASCII letters, numbers, spaces, and basic punctuation.
        """
        if not text:
            return ""
        
        # Remove emoji and special Unicode characters
        # Keep only ASCII printable characters (letters, numbers, basic punctuation)
        sanitized = ''.join(char for char in text if ord(char) < 128 and (char.isalnum() or char in ' .,!?-:'))
        
        # Clean up multiple spaces
        sanitized = ' '.join(sanitized.split())
        
        return sanitized

    def speak_command(self, command: str) -> bool:
        """Announce recognized command"""
        if not command:
            return False

        speak_text = f"Command recognized: {command}"
        return self.speak_text(speak_text, priority=False)

    def speak_status(self, status: str) -> bool:
        """Announce status information (high priority)"""
        if not status:
            return False

        # Status message mapping
        status_messages = {
            "start": "Voice control system starting",
            "ready": "System ready",
            "listening": "Listening for wake word",
            "please speak": "Wake word detected. Please speak your command",
            "command mode": "Command mode activated",
            "not match": "No matching command found",
            "stand by": "Returning to standby mode",
            "stop": "Voice control system stopped",
            "error": "An error occurred",
            "processing": "Processing your command"
        }
        
        message = status_messages.get(status.lower(), status)
        return self.speak_text(message, priority=True)

    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        with self._lock:
            return self._current_speaking

    def get_queue_size(self) -> int:
        """Get queue size"""
        return self.tts_queue.qsize()

    def clear_queue(self):
        """Clear TTS queue"""
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except queue.Empty:
                break
        print("✅ TTS queue cleared")

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available voices"""
        voices = []

        if TTS_TYPE == "pyttsx3":
            try:
                temp_engine = pyttsx3.init()
                pyttsx3_voices = temp_engine.getProperty('voices')

                for i, voice in enumerate(pyttsx3_voices):
                    voices.append({
                        "index": i,
                        "id": voice.id,
                        "name": voice.name,
                        "languages": getattr(voice, 'languages', [])
                    })

                temp_engine.stop()
            except Exception as e:
                print(f"⚠️ Voice enumeration error: {e}")

        return voices

    def set_rate(self, rate: int) -> bool:
        """Set speech rate"""
        if rate < 50 or rate > 400:
            return False

        self.config["rate"] = rate
        self._save_config()

        # Update engine settings
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass

        return True

    def set_volume(self, volume: float) -> bool:
        """Set volume"""
        if volume < 0.0 or volume > 1.0:
            return False

        self.config["volume"] = volume
        self._save_config()

        # Update engine settings
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
            except:
                pass

        return True

    def _save_config(self):
        """Save configuration"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Config save error: {e}")

    def stop(self):
        """Stop TTS"""
        print("🔄 Stopping TTS...")
        self.is_running = False

        # Clear queue
        self.clear_queue()

        # Send stop signal
        try:
            self.tts_queue.put(None, timeout=1.0)
        except:
            pass

        # Wait for worker thread to end
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
            if self.worker_thread.is_alive():
                print("⚠️ TTS worker thread did not stop gracefully")

        with self._lock:
            self._current_speaking = False

        print("✅ TTS stopped")

    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            "engine_type": TTS_TYPE,
            "enabled": self.config["enabled"],
            "running": self.is_running,
            "speaking": self._current_speaking,
            "queue_size": self.tts_queue.qsize(),
            "error_count": self._engine_error_count,
            "worker_alive": self.worker_thread.is_alive() if self.worker_thread else False,
            "settings": {
                "rate": self.config["rate"],
                "volume": self.config["volume"],
                "voice_index": self.config["voice_index"]
            }
        }