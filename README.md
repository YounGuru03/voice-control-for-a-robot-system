# Voice Command Tool 🎤🤖

A **lightweight offline Windows voice command application** powered by [Whisper](https://github.com/openai/whisper) for speech recognition.
It provides a simple Tkinter-based GUI, processes natural language commands, and outputs results in real time — making it suitable for **robot systems, automation tasks, and personal assistants**.

---

## ✨ Features

* **Offline Speech Recognition**: Runs the [Whisper-small](https://github.com/openai/whisper) model locally for fast and reliable transcription.
* **No GPU/Cloud Dependencies**: Works entirely offline without requiring CUDA or internet access.
* **Lightweight GUI**: Simple Tkinter interface with a start button, command display, and activity log.
* **Smart NLP Processing**: Cleans transcripts, removes filler words, and maps speech to structured commands.
* **File Monitoring**: Real-time updates to `text.txt` using `watchdog`.
* **Cross-platform Development**: Runs on **Windows**, but can be developed/tested in Linux (Codespaces, WSL).
* **Executable Packaging**: Built into a standalone `.exe` using PyInstaller.
* **GitHub Actions CI/CD**: Automatically builds Windows executables in the cloud.

---

## 🖥️ Requirements

### Runtime

* **Windows 10/11 x64** (for `.exe`)
* **4 GB RAM minimum**
* **Microphone access**
* **No Python installation required** (when using pre-built `.exe`)

### Development

* **Python 3.8+**
* For Linux (e.g., Codespaces / WSL) development, ensure PortAudio is installed:

  ```bash
  sudo apt-get update
  sudo apt-get install portaudio19-dev
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

1. Launch the application.
2. Click **Start Listening**.
3. Speak clearly into your microphone.
4. Recognized commands are processed and written to `text.txt`.
5. Monitor activities in the log window.
6. Adjust recognition parameters in `config.json`.

---

## 🎙️ Supported Commands

### Movement

* `move forward`, `go ahead`
* `move back`, `go backward`
* `turn left`, `turn right`
* `stop`, `halt`

### Navigation

* `go home`, `return to base`
* `go to [location]`

### System

* `start`, `begin`
* `shutdown`, `power off`
* `restart`, `reboot`

### Application

* `open main`, `launch application`
* `close main`, `exit application`
* `minimize`, `maximize`

### Robot-Specific

* `pick up`, `grab`
* `put down`, `drop`
* `lift`, `raise`
* `lower`, `descend`

### Status

* `status`, `how are you`
* `help`, `what can you do`

---

## 📊 Performance

* **Latency**: < 2 seconds (speech → command).
* **Memory**: Optimized for 4GB RAM.
* **CPU**: Works on standard x64 processors without GPU.
* **Model**: Whisper-small (balanced accuracy & speed).

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
├── main.py              # Main GUI application
├── voice_processor.py   # Whisper speech recognition
├── nlp_processor.py     # NLP processing and command mapping
├── file_monitor.py      # Real-time file watcher
├── launcher.py          # Entry point with error handling
├── build.py             # PyInstaller build script
├── test_components.py   # Component testing
├── requirements.txt     # Python dependencies
├── text.txt             # Output file (generated at runtime)
└── config.json          # Configuration (generated at runtime)
```

---

## ⚙️ Configuration

Example `config.json`:

```json
{
  "confidence_threshold": 0.5,
  "whisper_model": "small"
}
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Support

* For bug reports, please open an [Issue](../../issues).
* For discussions, use the [GitHub Discussions](../../discussions) tab.
* Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).