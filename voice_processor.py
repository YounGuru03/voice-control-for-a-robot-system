"""
Enhanced Voice Processor Module
===============================

Handles audio recording and speech-to-text conversion using Whisper-small.
Includes audio preprocessing, noise reduction, and filtering capabilities.
Optimized for offline operation without GPU dependencies.
"""

import numpy as np
import tempfile
import os
import threading
import time
from typing import Optional
import scipy.signal
from scipy.signal import butter, lfilter, wiener

# Import whisper and pyaudio only if available
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI Whisper not available. Speech recognition will be disabled.")
    WHISPER_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    print("Warning: PyAudio not available. Audio recording will be disabled.")
    PYAUDIO_AVAILABLE = False

class AudioPreprocessor:
    """Audio preprocessing class with noise reduction and filtering"""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        
    def apply_bandpass_filter(self, audio_data, lowcut=300, highcut=3400):
        """
        Apply bandpass filter to focus on speech frequencies
        
        Args:
            audio_data: Audio signal as numpy array
            lowcut: Low frequency cutoff (Hz)
            highcut: High frequency cutoff (Hz)
            
        Returns:
            Filtered audio data
        """
        try:
            nyquist = 0.5 * self.sample_rate
            low = lowcut / nyquist
            high = highcut / nyquist
            
            # Design butterworth bandpass filter
            b, a = butter(4, [low, high], btype='band')
            
            # Apply filter
            filtered_audio = lfilter(b, a, audio_data)
            return filtered_audio.astype(np.float32)
        except Exception as e:
            print(f"Error applying bandpass filter: {e}")
            return audio_data
    
    def reduce_noise_spectral_subtraction(self, audio_data, noise_factor=2.0):
        """
        Simple spectral subtraction noise reduction
        
        Args:
            audio_data: Audio signal as numpy array
            noise_factor: Factor for noise reduction strength
            
        Returns:
            Noise-reduced audio data
        """
        try:
            # Estimate noise from first 0.5 seconds
            noise_samples = int(0.5 * self.sample_rate)
            noise_segment = audio_data[:min(noise_samples, len(audio_data))]
            
            # Calculate noise power spectrum
            noise_fft = np.fft.fft(noise_segment)
            noise_power = np.abs(noise_fft) ** 2
            
            # Process audio in overlapping windows
            window_size = 1024
            hop_size = 512
            processed_audio = np.zeros_like(audio_data)
            
            for i in range(0, len(audio_data) - window_size, hop_size):
                window = audio_data[i:i + window_size]
                
                # Apply Hanning window
                windowed = window * np.hanning(window_size)
                
                # FFT
                signal_fft = np.fft.fft(windowed)
                signal_power = np.abs(signal_fft) ** 2
                
                # Spectral subtraction
                # Resize noise_power to match signal_power length
                if len(noise_power) != len(signal_power):
                    noise_power_resized = np.resize(noise_power, len(signal_power))
                else:
                    noise_power_resized = noise_power
                    
                enhanced_power = signal_power - noise_factor * noise_power_resized
                enhanced_power = np.maximum(enhanced_power, 0.1 * signal_power)
                
                # Reconstruct signal
                enhanced_magnitude = np.sqrt(enhanced_power)
                enhanced_fft = enhanced_magnitude * np.exp(1j * np.angle(signal_fft))
                enhanced_signal = np.real(np.fft.ifft(enhanced_fft))
                
                # Overlap-add
                processed_audio[i:i + window_size] += enhanced_signal
            
            # Normalize
            max_val = np.max(np.abs(processed_audio))
            if max_val > 0:
                processed_audio = processed_audio / max_val * 0.8
                
            return processed_audio.astype(np.float32)
            
        except Exception as e:
            print(f"Error in noise reduction: {e}")
            return audio_data
    
    def normalize_audio(self, audio_data):
        """
        Normalize audio amplitude
        
        Args:
            audio_data: Audio signal as numpy array
            
        Returns:
            Normalized audio data
        """
        try:
            # Remove DC offset
            audio_data = audio_data - np.mean(audio_data)
            
            # Normalize to [-0.8, 0.8] range
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.8
                
            return audio_data.astype(np.float32)
        except Exception as e:
            print(f"Error normalizing audio: {e}")
            return audio_data
    
    def enhance_speech(self, audio_data, enable_filter=True, enable_noise_reduction=True):
        """
        Apply all preprocessing enhancements
        
        Args:
            audio_data: Raw audio data
            enable_filter: Whether to apply bandpass filter
            enable_noise_reduction: Whether to apply noise reduction
            
        Returns:
            Enhanced audio data
        """
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        enhanced_audio = audio_data.copy()
        
        # Apply bandpass filter
        if enable_filter:
            enhanced_audio = self.apply_bandpass_filter(enhanced_audio)
        
        # Apply noise reduction
        if enable_noise_reduction:
            enhanced_audio = self.reduce_noise_spectral_subtraction(enhanced_audio)
        
        # Normalize
        enhanced_audio = self.normalize_audio(enhanced_audio)
        
        return enhanced_audio
    
    def generate_spectrogram(self, audio_data, window_size=1024, hop_size=512):
        """
        Generate spectrogram data for visualization
        
        Args:
            audio_data: Audio signal
            window_size: FFT window size
            hop_size: Hop size between windows
            
        Returns:
            Spectrogram matrix (time x frequency)
        """
        try:
            if audio_data is None or len(audio_data) < window_size:
                return np.zeros((50, 100))  # Return empty spectrogram
            
            # Calculate number of frames
            n_frames = (len(audio_data) - window_size) // hop_size + 1
            n_freqs = window_size // 2 + 1
            
            spectrogram = np.zeros((n_frames, n_freqs))
            
            for i in range(n_frames):
                start = i * hop_size
                end = start + window_size
                
                if end <= len(audio_data):
                    window = audio_data[start:end] * np.hanning(window_size)
                    fft = np.fft.fft(window)
                    magnitude = np.abs(fft[:n_freqs])
                    spectrogram[i, :] = magnitude
            
            # Convert to dB scale
            spectrogram = 20 * np.log10(spectrogram + 1e-10)
            
            return spectrogram
            
        except Exception as e:
            print(f"Error generating spectrogram: {e}")
            return np.zeros((50, 100))


class VoiceProcessor:
    """Enhanced voice processor with audio preprocessing capabilities."""
    
    def __init__(self, model_name="small"):
        """
        Initialize the enhanced voice processor.
        
        Args:
            model_name: Whisper model to use ("tiny", "base", "small")
        """
        self.model_name = model_name
        self.model = None
        self.audio_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        self.channels = 1
        self.rate = 16000  # Whisper works best with 16kHz
        self.chunk = 1024
        
        # Audio recording parameters
        self.pyaudio_instance = None
        
        # Audio preprocessor
        self.preprocessor = AudioPreprocessor(self.rate)
        
        # Settings
        self.enable_noise_reduction = True
        self.enable_audio_filter = True
        
        # Initialize Whisper model in a separate thread to avoid blocking GUI
        self._model_loaded = False
        if WHISPER_AVAILABLE:
            self._load_model_async()
        
    def _load_model_async(self):
        """Load the Whisper model asynchronously."""
        def load_model():
            try:
                print(f"Loading Whisper model '{self.model_name}'...")
                if WHISPER_AVAILABLE:
                    self.model = whisper.load_model(self.model_name)
                    self._model_loaded = True
                    print(f"Whisper model '{self.model_name}' loaded successfully")
                else:
                    print("Whisper not available - using fallback")
                    self._model_loaded = False
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
        Record audio from the microphone with preprocessing.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Enhanced audio data as numpy array or None if failed
        """
        try:
            if not PYAUDIO_AVAILABLE:
                # Return mock audio data for testing
                print(f"Mock recording for {duration} seconds...")
                time.sleep(duration)
                mock_audio = np.random.normal(0, 0.1, int(self.rate * duration))
                return mock_audio.astype(np.float32)
            
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
            
            # Apply preprocessing
            enhanced_audio = self.preprocessor.enhance_speech(
                audio_np, 
                enable_filter=self.enable_audio_filter,
                enable_noise_reduction=self.enable_noise_reduction
            )
            
            return enhanced_audio
            
        except Exception as e:
            print(f"Error recording audio: {str(e)}")
            return None
            
    def speech_to_text(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Convert audio data to text using Whisper.
        
        Args:
            audio_data: Enhanced audio data as numpy array
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_model_ready():
            # Return mock transcription for testing
            if audio_data is not None and len(audio_data) > 0:
                mock_transcripts = [
                    "open main", "open lamp", "open robot", "alarm",
                    "template A", "open camera 1", "close camera 2"
                ]
                import random
                return random.choice(mock_transcripts)
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
                
                import wave
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
    
    def generate_spectrogram(self, audio_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate spectrogram data for visualization.
        
        Args:
            audio_data: Audio data
            
        Returns:
            Spectrogram matrix or None if failed
        """
        try:
            return self.preprocessor.generate_spectrogram(audio_data)
        except Exception as e:
            print(f"Error generating spectrogram: {e}")
            return None
    
    def set_preprocessing_options(self, enable_noise_reduction=True, enable_audio_filter=True):
        """
        Configure audio preprocessing options.
        
        Args:
            enable_noise_reduction: Enable/disable noise reduction
            enable_audio_filter: Enable/disable audio filtering
        """
        self.enable_noise_reduction = enable_noise_reduction
        self.enable_audio_filter = enable_audio_filter
        print(f"Audio preprocessing: noise_reduction={enable_noise_reduction}, filter={enable_audio_filter}")
            
    def cleanup(self):
        """Clean up audio resources."""
        if PYAUDIO_AVAILABLE and self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            except:
                pass
                
    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()