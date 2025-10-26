# Audio Processor - Complete Final Version
# Handles all audio recording and Whisper model operations

import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pyaudio

# Try faster-whisper first, fallback to openai-whisper
try:
    from faster_whisper import WhisperModel

    BACKEND = "faster-whisper"
except ImportError:
    print("⚠️ faster-whisper not available, falling back to openai-whisper")
    import whisper

    BACKEND = "openai-whisper"


class AudioProcessor:
    """Audio recording and Whisper-based speech recognition"""

    def __init__(self, model_size="base", language="en", device="cpu"):
        """
        Initialize Whisper model

        Args:
            model_size: "tiny", "base", "small", "medium", "large"
            language: Language code, e.g., "en", "zh"
            device: "cpu" or "cuda"
        """
        print(f"🔄 Initializing Whisper model ({model_size})...")

        self.model_size = model_size
        self.language = language
        self.device = device

        if BACKEND == "faster-whisper":
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type="int8"
            )
        else:
            self.model = whisper.load_model(model_size, device=device)

        print(f"✅ Model loaded successfully using {BACKEND}")

    def record_audio(self, duration=5, sample_rate=16000):
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz

        Returns:
            numpy array of audio samples
        """
        print(f"🎤 Recording for {duration} seconds...")

        chunk = 1024
        format_type = pyaudio.paInt16
        channels = 1

        try:
            p = pyaudio.PyAudio()

            stream = p.open(
                format=format_type,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk
            )

            frames = []

            for _ in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            print("✅ Recording complete")

            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0

            return audio_data

        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None

    def detect_wake_word(self, audio_data, wake_word="susie"):
        """
        Detect wake word in audio

        Args:
            audio_data: Audio samples
            wake_word: Wake word to detect

        Returns:
            True if wake word detected, False otherwise
        """
        if audio_data is None:
            return False

        try:
            # Fast transcription with beam_size=1
            if BACKEND == "faster-whisper":
                segments, info = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=1,
                    vad_filter=True
                )
                text = " ".join([segment.text for segment in segments])
            else:
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False
                )
                text = result["text"]

            text = text.strip().lower()
            print(f"🔍 Detected text: {text}")

            if wake_word.lower() in text:
                print(f"✅ Wake-word '{wake_word}' detected!")
                return True

            return False

        except Exception as e:
            print(f"❌ Wake-word detection error: {e}")
            return False

    def transcribe(self, audio_data, boost_phrases=None):
        """
        Transcribe audio to text with optional phrase boosting

        Args:
            audio_data: Audio samples
            boost_phrases: List of phrases to boost (optional)

        Returns:
            Transcribed text string
        """
        if audio_data is None:
            return None

        try:
            # Prepare initial prompt for phrase boosting
            initial_prompt = None
            if boost_phrases and len(boost_phrases) > 0:
                # Take top 10 phrases
                initial_prompt = ", ".join(boost_phrases[:10])

            # Transcribe with higher beam_size for accuracy
            if BACKEND == "faster-whisper":
                segments, info = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=5,
                    vad_filter=True,
                    initial_prompt=initial_prompt
                )
                text = " ".join([segment.text for segment in segments])
            else:
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]

            text = text.strip()
            print(f"📝 Transcribed: {text}")

            return text

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None

    def check_phrase_match(self, transcribed_text, command_list):
        """
        Check if transcribed text matches any command in list

        Args:
            transcribed_text: Text to check
            command_list: List of valid commands

        Returns:
            Matched command or None
        """
        if not transcribed_text or not command_list:
            return None

        transcribed_lower = transcribed_text.lower().strip()

        for command in command_list:
            command_lower = command.lower().strip()

            # Exact match or substring match
            if command_lower == transcribed_lower or command_lower in transcribed_lower:
                return command

        return None