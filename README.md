# Voice Control System

## Overview
Voice Control System is a robust, offline-capable speech recognition and command execution platform for Windows. It features:
- Fast, accurate speech-to-text (STT) using the latest Whisper models
- Windows SAPI TTS integration for natural voice feedback
- Customizable wake word and command recognition
- Modern, user-friendly GUI with real-time status and configuration
- Easy packaging as a standalone Windows executable (EXE)

---

## Features
- **Offline Speech Recognition:** Uses local Whisper models for privacy and speed
- **Windows TTS Integration:** Natural-sounding voice feedback via SAPI
- **Custom Commands:** Add, train, and manage commands via GUI or JSON
- **Wake Word Activation:** Default wake word "susie"; easily changeable
- **Hot-Reloadable Configs:** Edit commands and TTS settings without restarting
- **GUI Tabs:** Listen, Commands, Training, System for full control
- **Model Management:** Auto-downloads models or uses local cache
- **Packaged EXE:** Distributable, no Python required for end users

---

## Quick Start

### Prerequisites
- Windows 10/11
- Python 3.8+
- Microphone
- Internet connection (for first-time model download)

### Installation
```bash
# Install dependencies
pip install faster-whisper numpy pyaudio pywin32

# Run pywin32 post-install (as Administrator)
python Scripts/pywin32_postinstall.py -install
```

### Running the Application
```bash
python main_voice_app.py
```

### Using the Application
1. Wait for "System ready" voice prompt
2. Click **Start Listening**
3. Say the wake word (default: "susie")
4. Speak a command (e.g., "open browser")
5. System executes the command and provides voice feedback

---

## Configuration

### TTS Settings (`tts_config.json`)
```json
{
  "voice_index": 0,
  "rate": 0,
  "volume": 100,
  "enabled": true
}
```

### Command Settings (`commands_hotwords.json`)
```json
{
  "commands": {
    "command name": {
      "weight": 1.5,
      "usage_count": 0,
      "last_used": null
    }
  }
}
```

---

## Adding & Training Commands

### Via GUI
- Go to **Commands** tab
- Enter new command
- Click **Add Command**
- Use **Training** tab to boost recognition

### Via File
- Edit `commands_hotwords.json` and add your command
- Click **Reload JSON** in the GUI

---

## Building the Executable

### One-Command Build
```bash
python build_v2.py
```
- Output: `dist/VoiceControlSystem.exe`
- All configs and models are bundled or auto-copied

### Distribution
- Distribute only `VoiceControlSystem.exe`
- Config files and logo are auto-created on first run
- No Python required for end users

---

## Troubleshooting
- **TTS not working:** Ensure pywin32 is installed and post-install script ran
- **No microphone detected:** Check Windows sound settings and permissions
- **Model loading failed:** Ensure internet for first run or place models in `local_models/`
- **STT not recognizing speech:** Check `stt_debug.log` next to EXE for diagnostics

---

## Best Practices
- Use the default wake word "susie" for best results
- Train frequently-used commands for higher accuracy
- Use smaller models for speed, larger for accuracy
- Keep background noise low for best recognition

---

## Support & Updates
- Update dependencies regularly:
  ```bash
  pip install --upgrade faster-whisper pywin32 numpy pyaudio
  ```
- For help, check the console, `stt_debug.log`, or the System tab in the GUI

---

## License
This project is provided for educational and personal use. See LICENSE for details.
