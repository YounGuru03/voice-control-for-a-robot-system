"""
Simple Voice Processor
=====================

Streamlined voice processing module focused on minimal memory usage
and essential functionality for robot voice control.
"""

import tempfile
import os
import threading
import time
from typing import Optional

# Optional imports with fallbacks
try:
    import whisper
    import numpy as np
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice recognition disabled - missing whisper/numpy")

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio recording disabled - missing pyaudio")

class VoiceProcessor:
    """Lightweight voice processor for basic speech recognition"""
    
    def __init__(self, model_name="small"):
        """
        Initialize voice processor
        
        Args:
            model_name: Whisper model ("tiny", "base", "small")
        """
        self.model_name = model_name
        self.model = None
        self.audio = None
        self.is_recording = False
        
        # Audio settings optimized for low memory usage
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = None
        
        if AUDIO_AVAILABLE:
            self.format = pyaudio.paInt16
            self.audio = pyaudio.PyAudio()
        
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if not VOICE_AVAILABLE:
            return
            
        try:
            print(f"Loading Whisper {self.model_name} model...")
            self.model = whisper.load_model(self.model_name)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model = None
    
    def is_model_ready(self):
        """Check if the model is loaded and ready"""
        return self.model is not None
    
    def record_audio(self, duration=3.0):
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            numpy array of audio data or None
        """
        if not AUDIO_AVAILABLE or not self.audio:
            return None
            
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎤 Recording...")
            frames = []
            
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Convert to numpy array
            audio_data = b''.join(frames)
            if VOICE_AVAILABLE:
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                return audio_np
            else:
                return None
                
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def transcribe_audio(self, audio_data):
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: numpy array of audio data
            
        Returns:
            Transcribed text or None
        """
        if not self.is_model_ready() or audio_data is None:
            return None
        
        try:
            # Simple transcription without complex processing
            result = self.model.transcribe(audio_data, language="en")
            return result["text"].strip()
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def record_and_transcribe(self, duration=3.0):
        """
        Record audio and transcribe in one step
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text or None
        """
        audio_data = self.record_audio(duration)
        if audio_data is not None:
            return self.transcribe_audio(audio_data)
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.audio:
            self.audio.terminate()
        print("🔧 Voice processor cleaned up")

# Create a fallback class for when dependencies aren't available
class DemoVoiceProcessor:
    """Fallback processor that simulates voice recognition"""
    
    def __init__(self, model_name="demo"):
        self.model_name = model_name
        self.demo_commands = [
            "open main",
            "start robot", 
            "open lamp",
            "emergency stop",
            "open camera 1"
        ]
        self.command_index = 0
    
    def is_model_ready(self):
        return True
    
    def record_and_transcribe(self, duration=3.0):
        """Return demo commands for testing"""
        time.sleep(duration)  # Simulate recording time
        
        command = self.demo_commands[self.command_index]
        self.command_index = (self.command_index + 1) % len(self.demo_commands)
        
        print(f"🎭 Demo mode: simulating '{command}'")
        return command
    
    def cleanup(self):
        print("🔧 Demo processor cleaned up")

# Factory function to create appropriate processor
def create_voice_processor(model_name="small"):
    """
    Create voice processor based on available dependencies
    
    Args:
        model_name: Whisper model name
        
    Returns:
        VoiceProcessor or DemoVoiceProcessor
    """
    if VOICE_AVAILABLE and AUDIO_AVAILABLE:
        return VoiceProcessor(model_name)
    else:
        print("⚠️  Using demo mode - install dependencies for full functionality")
        return DemoVoiceProcessor(model_name)