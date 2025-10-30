# Voice Control System - Offline Intelligent Voice Recognition

A fully offline, intelligent voice control system based on Faster-Whisper, employing a two-stage working mode for accurate voice command recognition and execution.

## 🎯 Key Features

### Core Functionality
- **Two-Stage Recognition**: Standby mode (wake word "susie") → Command mode (5 failures returns to standby)
- **Multi-Backend STT Support**: Faster-Whisper (primary), Vosk (alternative)
- **Offline Operation**: All processing happens locally, no internet required after setup
- **Dynamic Weight System**: Automatic command priority adjustment based on usage and training
- **Real-time TTS Feedback**: Voice confirmations for all system states and commands

### Technical Highlights
- **Intelligent Command Matching**: Hot word boosting for improved recognition accuracy
- **Statistical Analysis**: Usage tracking and automatic weight optimization
- **Multi-threaded Architecture**: Responsive UI with separate audio processing thread
- **Comprehensive Training Mode**: Reinforcement learning for specific commands
- **Smart Model Management**: Automatic download, caching, and multi-model support

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Models (Optional)

Models are downloaded automatically on first run. To pre-download:

```bash
python -c "from model_manager import ModelManager; ModelManager().download_model('Systran/faster-whisper-base')"
```

**Available Models:**
- `tiny` - 39MB, fast, basic accuracy
- `base` - 74MB, balanced (recommended)
- `small` - 244MB, high accuracy

### 3. Run the Application

```bash
python main_voice_app.py
```

## 🎮 Usage Guide

### Starting the System
1. Launch `main_voice_app.py`
2. Click "Start Voice Control"
3. Wait for "System Ready" voice confirmation

### Voice Control Workflow
1. **Say "Susie"** - Activates command mode
2. **Speak your command** - e.g., "open browser", "turn on lights"
3. **System responds** - Confirms command execution via TTS
4. **Auto-reset** - Returns to standby after 5 consecutive recognition failures

### Command Management
- **Add Commands**: Use Commands tab to add custom voice commands
- **Train Commands**: Use Training tab to improve recognition accuracy
- **View Statistics**: Check usage frequency and weight adjustments

## 🏗️ Project Structure

```
voice-control-system/
│
├── main_voice_app.py      # Main GUI application with 4-tab interface
├── audio_engine.py         # Audio processing & speech recognition engine
├── tts_engine.py           # Text-to-speech with queue management
├── command_manager.py      # Command storage & weight optimization
├── model_manager.py        # Multi-backend model management
├── build.py                # PyInstaller packaging script
│
├── commands_hotwords.json  # Command database (auto-created)
├── local_models/           # Downloaded STT models (excluded from git)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Module Descriptions

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `main_voice_app.py` | GUI & application logic | 4 tabs (Listen/Commands/Train/System), threading control |
| `audio_engine.py` | Audio I/O & STT | Wake word detection, command transcription, model switching |
| `tts_engine.py` | Text-to-speech | Queue-based processing, fault tolerance, status messages |
| `command_manager.py` | Command database | Weight management, usage statistics, training counts |
| `model_manager.py` | Model management | Multi-backend support, auto-download, offline operation |
| `build.py` | Executable packaging | PyInstaller configuration, model bundling, Windows .exe |

## 🔨 Building Executable

To create a standalone Windows executable:

```bash
python build.py
```

**Output**: `dist/VoiceControl.exe` (includes Python runtime and base model)

**Customization** (in `build.py`):
- Change `MODEL_SIZE = 'base'` to package different model size
- Add multiple models to `MODELS_TO_BUNDLE` list
- Uncomment Vosk section to bundle Vosk models

## ⚙️ Configuration

### System Settings
- **Model Selection**: Choose STT backend in System tab (Whisper/Vosk)
- **TTS Settings**: Adjust speech rate and volume in `tts_config.json`
- **Command Weights**: Auto-adjusted based on usage, or manually trained

### Performance Tuning
- **Faster-Whisper tiny**: Low resource usage, faster response
- **Faster-Whisper base**: Balanced (recommended for most use cases)
- **Faster-Whisper small**: Higher accuracy, needs more RAM
- **Vosk**: Lightweight alternative, good for older hardware

## 🚀 Advanced Features

### Dynamic Weight Adjustment
Commands automatically receive priority boosts based on:
- Usage frequency
- Training iterations
- Recent success rate

### Training Mode
Improve recognition accuracy by:
1. Select command in Training tab
2. Click "Train" button
3. Repeat command 5-10 times
4. Weight automatically increases

### Output Logging
All recognized commands are logged to `output.txt` with timestamps:
```
2025-10-30 14:23:15 - open browser
2025-10-30 14:24:32 - turn on lights
```

## 🐛 Troubleshooting

### Common Issues

**"No microphone detected"**
- Check Windows audio settings
- Ensure microphone is not muted
- Try different USB port for external mic

**"Model download failed"**
- Check internet connection (first run only)
- Manually download from HuggingFace
- Check disk space (base model needs ~100MB)

**"TTS not working"**
- Install Microsoft Visual C++ Redistributable
- Check audio output device
- Try different TTS voice in settings

### System Requirements
- **OS**: Windows 10/11, Linux, macOS
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for application + models
- **Audio**: Microphone and speakers/headphones

## 📝 Notes for Developers

### Model Files
- Excluded from Git via `.gitignore` (exceed 100MB limit)
- Downloaded to `local_models/hf_cache/`
- Managed by `model_manager.py`

### Threading Architecture
- **Main Thread**: GUI (tkinter)
- **Audio Thread**: Recording and recognition
- **TTS Thread**: Speech synthesis queue

### Adding New STT Backends
1. Update `model_manager.py` with new backend support
2. Add backend initialization in `audio_engine.py`
3. Update `SUPPORTED_*_MODELS` dictionaries
4. Add download logic in `ModelManager` class

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit pull request with description

## 🙏 Acknowledgments

- **Faster-Whisper**: OpenAI Whisper optimized for CPU
- **Vosk**: Lightweight offline speech recognition
- **pyttsx3**: Cross-platform TTS engine
