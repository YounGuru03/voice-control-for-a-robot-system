# Voice Control for Robot System

A voice-controlled system using offline speech recognition (Whisper) and text-to-speech.

## Features

- Two-stage voice control: Wake word detection → Command mode
- Offline speech recognition using faster-whisper
- Text-to-speech feedback with pyttsx3
- Dynamic command weight adjustment
- Training mode for command optimization
- Multi-threaded audio processing

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Models

**IMPORTANT**: Model files are not included in the repository due to size limitations (>100MB).

The system will automatically download the required Whisper models on first run:
- Models are cached in `local_models/hf_cache/`
- Default model: `Systran/faster-whisper-base`
- Supported sizes: tiny, base, small

Or manually download models using the application's System tab.

### 3. Run the Application

```bash
python main_voice_app.py
```

## Usage

1. **Start Listening**: Click "Start Voice Control"
2. **Wake Word**: Say "Susie" to activate command mode
3. **Commands**: Speak your command (e.g., "open browser")
4. **Training**: Use the Training tab to optimize command recognition

## Project Structure

- `main_voice_app.py` - Main GUI application
- `optimized_audio_processor.py` - Audio recording and speech recognition
- `optimized_tts_manager.py` - Text-to-speech engine
- `command_hotword_manager.py` - Command storage and weight management
- `local_model_manager.py` - Offline model management
- `speaker_manager.py` - Speaker profile management

## Notes

- Model files (`*.bin`, `*.pth`) are excluded from Git via `.gitignore`
- Models are downloaded automatically from HuggingFace on first use
- System works completely offline after initial model download

## License

[Your License Here]
