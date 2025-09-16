# Voice Command Tool v2.0 🎤🤖

A **powerful offline voice command application** powered by [Whisper](https://github.com/openai/whisper) for speech recognition.
Features an enhanced **Material Design GUI**, advanced audio preprocessing, real-time transcription display, and comprehensive command recognition — making it perfect for **robot systems, automation tasks, and personal assistants**.

---

## 🆕 What's New in v2.0

### Major Enhancements
* **🎨 Complete Material Design Overhaul**: Modern, intuitive interface with animations and visual feedback
* **📊 Real-Time Audio Visualization**: Live spectrogram display showing audio input signal 
* **💬 Live Transcription Panel**: Real-time display of speech-to-text conversion with timestamps
* **🔊 Advanced Audio Preprocessing**: Noise reduction and filtering for improved recognition accuracy
* **🎯 Comprehensive Command Set**: 30+ specific commands with 86+ natural language variations
* **⚙️ Enhanced Settings Dialog**: Configurable audio processing and recognition parameters

### Technical Improvements  
* **Spectral Subtraction Noise Reduction**: Removes background noise for clearer audio
* **Bandpass Filtering**: Optimized for speech frequencies (300-3400 Hz)
* **Audio Normalization**: Automatic level adjustment and DC offset removal
* **Three-Column Responsive Layout**: Optimal use of screen real estate
* **Color-Coded Activity Logging**: Visual feedback for different types of events
* **Robust Error Handling**: Graceful fallbacks when dependencies unavailable

### Command Set Updates
Completely updated command recognition to support:
* Application controls (`open main`, `open lamp`, `open robot`, etc.)
* Camera management (`open/close camera 1-4`)
* Template commands (`template A-F`, `template 7-10`) 
* System functions (`alarm`, `open train`, `open report`, etc.)
* User management (`open user admin`, `open user logging`, etc.)

---

## ✨ Features

### 🎨 Enhanced Material Design Interface
* **Modern GUI**: Beautiful Material Design interface with gradient backgrounds and smooth animations
* **Three-Column Layout**: Controls, real-time transcription, and audio visualization in an intuitive layout
* **Real-Time Transcription**: Live display of speech-to-text conversion with timestamps
* **Audio Spectrogram**: Visual representation of audio input to confirm signal acquisition
* **Animated Components**: Interactive buttons with hover effects and command display animations

### 🔊 Advanced Audio Processing
* **Noise Reduction**: Spectral subtraction algorithm to remove background noise
* **Bandpass Filtering**: Optimized for speech frequencies (300-3400 Hz) 
* **Audio Normalization**: Automatic level adjustment and DC offset removal
* **Preprocessing Pipeline**: Configurable enhancement options in settings dialog

### 🎯 Comprehensive Command Recognition
* **Extensive Command Set**: Support for 30+ specific commands including:
  - Application controls (`open main`, `open lamp`, `open robot`, `open robot cell`)
  - Numbered commands (`open 1`, `open 2`)
  - Camera controls (`open/close camera 1-4`)
  - Template commands (`template A-F`, `template 7-10`)
  - System commands (`alarm`, `open train`, `open report`, `open record`)
  - User management (`open user admin`, `open user logging`, `open user log`)
* **Smart NLP Processing**: Advanced text cleaning, filler word removal, and intent mapping
* **Multiple Variants**: Each command supports multiple natural language variations

### 🚀 Core Features
* **Offline Speech Recognition**: Runs Whisper models locally for fast and reliable transcription
* **No GPU/Cloud Dependencies**: Works entirely offline without requiring CUDA or internet access
* **File Monitoring**: Real-time updates to `text.txt` using watchdog with change detection
* **Cross-platform Development**: Runs on Windows, Linux, and can be developed/tested anywhere
* **Executable Packaging**: Built into standalone `.exe` using PyInstaller
* **GitHub Actions CI/CD**: Automated Windows executable builds

---

## 🖥️ Requirements

### Runtime

* **Windows 10/11 x64** (for `.exe`)
* **4 GB RAM minimum** (6 GB recommended for audio processing)
* **Microphone access**
* **No Python installation required** (when using pre-built `.exe`)

### Development

* **Python 3.8+**
* **Additional Dependencies**: `scipy`, `matplotlib`, `numpy`, `watchdog`
* For Linux (e.g., Codespaces / WSL) development, ensure PortAudio is installed:

  ```bash
  sudo apt-get update
  sudo apt-get install portaudio19-dev python3-tk
  ```

---

## ⚙️ Installation

### Option 1: Pre-built Executable (Recommended for End Users)

1. Download `VoiceCommandTool.exe` from the [Releases](../../releases) page.
2. Run the executable directly.
3. No additional setup required.

### Option 2: Run from Source (For Developers)

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/voice-command-tool.git
   cd voice-command-tool
   ```
2. Install dependencies (Linux users: install PortAudio first, see above):

   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:

   ```bash
   python launcher.py
   ```

---

## ▶️ Usage

1. **Launch** the application (`python main.py` or run the `.exe`)
2. **Click "Start Listening"** to begin voice recognition
3. **Speak clearly** into your microphone — watch the live transcription panel
4. **Monitor audio** via the real-time spectrogram visualization  
5. **View commands** as they're processed and saved to `text.txt`
6. **Check activity log** for detailed processing information
7. **Access Settings** to configure audio preprocessing and recognition parameters

### 🎙️ Voice Command Tips
* Speak clearly and at normal volume
* Wait for the "Listening..." status before speaking
* Commands are processed in 3-second chunks
* Audio preprocessing enhances speech recognition accuracy

---

## 🎙️ Supported Commands

### 🏢 Application Controls
* `open main`, `launch main`, `start main`
* `open lamp`, `start lamp`
* `open robot`, `launch robot`
* `open robot cell`, `start robot cell`

### 🔢 Numbered Commands
* `open 1`, `open one`, `launch 1`
* `open 2`, `open two`, `start 2`

### 🚨 System Commands
* `alarm`, `alert`
* `open train`, `launch train`
* `open report`, `start report`  
* `open record`, `launch record`

### 👥 User Management
* `open user admin`, `launch user admin`
* `open user logging`, `start user logging`
* `open user log`, `launch user log`

### 📹 Camera Controls
* **Open:** `open camera 1`, `open camera 2`, `open camera 3`, `open camera 4`
* **Close:** `close camera 1`, `close camera 2`, `close camera 3`, `close camera 4`
* **Variants:** Supports numeric (`1`) and word forms (`one`)

### 📋 Template Commands
* **Letters:** `template A` through `template F` (supports phonetic: `alpha`, `beta`, etc.)
* **Numbers:** `template 7` through `template 10` (supports word forms: `seven`, `eight`, etc.)

### 🆘 Emergency Commands
* `emergency stop`, `e-stop`, `abort`

> **Note:** Each command supports multiple natural language variations. The NLP processor intelligently maps different phrasings to the same command.

---

## 📊 Performance

* **Latency**: < 2 seconds (speech → command)
* **Memory**: Optimized for 4-6GB RAM with audio processing
* **CPU**: Works on standard x64 processors without GPU
* **Model**: Whisper-small (balanced accuracy & speed)
* **Audio Processing**: Real-time noise reduction and filtering
* **Recognition Accuracy**: Enhanced by audio preprocessing pipeline

---

## 🔨 Building from Source

### Local Build

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Run build script:

   ```bash
   python build.py
   ```
3. Find the `.exe` in the `dist/` directory.

### Common Build Issues & Fixes

* **PyAudio Installation Failure (Linux / Codespaces)**
  Install PortAudio before dependencies:

  ```bash
  sudo apt-get install portaudio19-dev
  pip install -r requirements.txt
  ```
* **PyInstaller Error: Python built without shared library**
  Use [pyenv](https://github.com/pyenv/pyenv) to install Python with `--enable-shared`:

  ```bash
  PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.12.1
  pyenv global 3.12.1
  ```

---

## 🤖 GitHub Actions: Automated Windows Build

This repository includes a **GitHub Actions workflow** to automatically build `.exe` files on Windows:

1. Workflow file: `.github/workflows/build-windows-exe.yml`
2. Trigger manually via **Actions > Build Windows Executable > Run workflow**.
3. After successful build, download the artifact `windows-executable` containing `VoiceCommandTool.exe`.

Benefits:

* Automated & repeatable builds.
* Clean Windows build environment.
* No local setup required.

---

## 🗂️ File Structure

```
voice-control-for-a-robot-system/
├── main.py                    # Enhanced Material Design GUI application  
├── voice_processor.py         # Enhanced Whisper speech recognition with audio preprocessing
├── nlp_processor.py           # Updated NLP processing with comprehensive command set
├── file_monitor.py            # Real-time file watcher with change detection
├── launcher.py                # Entry point with error handling
├── build.py                   # PyInstaller build script
├── test_components.py         # Component testing suite
├── demo_enhanced_features.py  # Feature demonstration script
├── requirements.txt           # Python dependencies (updated)
├── text.txt                   # Command output file (generated at runtime)
├── config.json                # Configuration (generated at runtime)
├── main_original.py           # Backup of original GUI (for reference)
└── voice_processor_original.py # Backup of original processor (for reference)
```

---

## ⚙️ Configuration

Example `config.json` with enhanced options:

```json
{
  "confidence_threshold": 0.7,
  "whisper_model": "small",
  "recording_duration": 3.0,
  "noise_reduction": true,
  "audio_filter": true
}
```

### Configuration Options
* `confidence_threshold`: Speech recognition confidence level (0.1-1.0)
* `whisper_model`: Whisper model size (`tiny`, `base`, `small`)  
* `recording_duration`: Audio recording duration in seconds (1.0-10.0)
* `noise_reduction`: Enable/disable noise reduction preprocessing
* `audio_filter`: Enable/disable bandpass filtering for speech frequencies

## 🧪 Testing & Demonstration

Run the comprehensive feature demonstration:

```bash
python demo_enhanced_features.py
```

This script demonstrates:
* ✅ All 86 command variations recognition
* ✅ Audio preprocessing with noise reduction  
* ✅ File monitoring system
* ✅ Material Design GUI components
* ✅ Integrated workflow processing

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Support

* For bug reports, please open an [Issue](../../issues).
* For discussions, use the [GitHub Discussions](../../discussions) tab.
* Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).