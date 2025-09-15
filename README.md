# Voice Command Tool

A lightweight offline Windows voice command application that uses Whisper for speech recognition and provides a simple GUI interface.

## Features

- **Offline Speech Recognition**: Uses Whisper-small model for local speech-to-text conversion
- **No GPU/Cloud Dependencies**: Runs entirely offline without requiring GPU acceleration or internet connectivity
- **Lightweight GUI**: Simple Tkinter interface with start button, command display, and activity log
- **Smart NLP Processing**: Cleans transcripts, removes filler words, and maps speech to commands
- **File Monitoring**: Real-time monitoring of output file (text.txt) with watchdog
- **Standalone Executable**: Packaged with PyInstaller for easy distribution

## Requirements

- Windows 10/11 x64
- 4GB RAM minimum
- Microphone access
- No Python installation required (when using .exe)

## Installation

### Option 1: Use Pre-built Executable
1. Download the `VoiceCommandTool.exe` from the releases
2. Run the executable directly
3. No additional installation required

### Option 2: Run from Source
1. Install Python 3.8+ 
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python launcher.py`

## Usage

1. Launch the application
2. Click "Start Listening" to begin voice recognition
3. Speak commands clearly into your microphone
4. Commands are processed and saved to `text.txt`
5. View activity in the log window
6. Use Settings to adjust recognition parameters

## Supported Commands

The application recognizes various command patterns:

### Movement Commands
- "move forward" / "go ahead"
- "move back" / "go backward"
- "turn left" / "turn right"
- "stop" / "halt"

### Navigation Commands
- "go home" / "return to base"
- "go to [location]"

### System Commands
- "start" / "begin"
- "shutdown" / "power off"
- "restart" / "reboot"

### Application Commands
- "open main" / "launch application"
- "close main" / "exit application"
- "minimize" / "maximize"

### Robot-Specific Commands
- "pick up" / "grab"
- "put down" / "drop"
- "lift" / "raise"
- "lower" / "descend"

### Status Commands
- "status" / "how are you"
- "help" / "what can you do"

## Performance

- **Latency**: < 2 seconds for speech-to-command processing
- **Memory**: Optimized for 4GB RAM systems
- **CPU**: Works on standard x64 processors without GPU
- **Model**: Uses Whisper-small for balance of accuracy and speed

## Building from Source

To create your own executable:

1. Install build dependencies: `pip install -r requirements.txt`
2. Run the build script: `python build.py`
3. Find the executable in the `dist/` directory

## Configuration

The application creates a `config.json` file for settings:

```json
{
  "confidence_threshold": 0.5,
  "whisper_model": "small"
}
```

## File Structure

```
voice-control-for-a-robot-system/
├── main.py              # Main application GUI
├── voice_processor.py   # Whisper speech recognition
├── nlp_processor.py     # Text processing and command mapping
├── file_monitor.py      # File watching functionality
├── launcher.py          # Application launcher with error checking
├── build.py            # PyInstaller build script
├── test_components.py  # Component testing script
├── requirements.txt    # Python dependencies
├── text.txt           # Command output file (created at runtime)
└── config.json        # Configuration file (created at runtime)
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and support, please refer to the project repository.
