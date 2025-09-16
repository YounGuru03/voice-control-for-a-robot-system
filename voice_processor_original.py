"""
Voice Processor Module
======================

Handles audio recording and speech-to-text conversion using Whisper-small.
Optimized for offline operation without GPU dependencies.
"""

import whisper
import pyaudio
import wave
import numpy as np
import tempfile
import os
import threading
import time
from typing import Optional

class VoiceProcessor:
    """Handles voice recording and speech-to-text processing."""
    
    def __init__(self, model_name="small"):
        """
        Initialize the voice processor.
        
        Args:
            model_name: Whisper model to use ("tiny", "base", "small")
        """
        self.model_name = model_name
        self.model = None
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper works best with 16kHz
        self.chunk = 1024
        
        # Audio recording parameters
        self.pyaudio_instance = None
        
        # Initialize Whisper model in a separate thread to avoid blocking GUI
        self._model_loaded = False
        self._load_model_async()
        
    def _load_model_async(self):
        """Load the Whisper model asynchronously."""
        def load_model():
            try:
                print(f"Loading Whisper model '{self.model_name}'...")
                self.model = whisper.load_model(self.model_name)
                self._model_loaded = True
                print(f"Whisper model '{self.model_name}' loaded successfully")
            except Exception as e:
                print(f"Error loading Whisper model: {str(e)}")
                self._model_loaded = False
                
        loading_thread = threading.Thread(target=load_model, daemon=True)
        loading_thread.start()
        
    def is_model_ready(self) -> bool:
        """Check if the Whisper model is loaded and ready."""
        return self._model_loaded and self.model is not None
        
    def record_audio(self, duration: float = 3.0) -> Optional[np.ndarray]:
        """
        Record audio from the microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array or None if failed
        """
        try:
            # Initialize PyAudio if not already done
            if self.pyaudio_instance is None:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            # Open audio stream
            stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print(f"Recording for {duration} seconds...")
            frames = []
            
            # Record audio data
            for _ in range(int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            # Convert to numpy array
            audio_data = b''.join(frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            print(f"Recorded {len(audio_np)} samples")
            return audio_np
            
        except Exception as e:
            print(f"Error recording audio: {str(e)}")
            return None
            
    def speech_to_text(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Convert audio data to text using Whisper.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_model_ready():
            print("Whisper model not loaded yet")
            return None
            
        if audio_data is None or len(audio_data) == 0:
            print("No audio data provided")
            return None
            
        try:
            # Save audio to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                
                # Convert numpy array to WAV file
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                wf = wave.open(temp_filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.rate)
                wf.writeframes(audio_int16.tobytes())
                wf.close()
                
            # Transcribe with Whisper
            print("Transcribing audio...")
            result = self.model.transcribe(temp_filename, language="en")
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            transcript = result["text"].strip()
            print(f"Transcript: '{transcript}'")
            
            return transcript if transcript else None
            
        except Exception as e:
            print(f"Error in speech-to-text conversion: {str(e)}")
            return None
            
    def cleanup(self):
        """Clean up audio resources."""
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            except:
                pass
                
    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()