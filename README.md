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

Prerequisites

    A GitHub account.

    This repository opened in a GitHub Codespace, or a similar Debian/Ubuntu-based Linux environment for development.

Part 1: Setting Up the Development Environment (Codespaces / Linux)

The application requires specific system and Python environment configurations to work correctly. The following steps ensure that all dependencies can be installed and that the environment is ready for testing and packaging.
Step 1: Install System Dependencies for Audio Processing

Our project uses the pyaudio library, which requires the PortAudio system library. You must install its development headers before installing the Python packages.

In your Codespaces terminal, run the following commands:
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
### Update package lists
sudo apt-get update

### Install PortAudio development headers
sudo apt-get install -y portaudio19-dev

  

Step 2: Install and Configure pyenv for Python Management

To package applications with PyInstaller on Linux, the Python interpreter must be compiled with a shared library (--enable-shared). The default Python in many environments lacks this. We will use pyenv to install a correctly configured version of Python.

    Install pyenv and its build dependencies:
    code Bash

IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

  

Run the official pyenv installer:
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
curl https://pyenv.run | bash

  

Configure your shell environment for pyenv:
Note: This adds the necessary configuration to your .bashrc file. These changes will apply the next time you open a terminal.
code Bash

    IGNORE_WHEN_COPYING_START
    IGNORE_WHEN_COPYING_END

        
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc

      

    Restart your terminal for the changes to take effect. You can do this by typing exec "$SHELL" or by closing and reopening the terminal pane in Codespaces.

Step 3: Install a Shared-Library Python Version

Now, use pyenv to install a specific Python version (e.g., 3.12.1), ensuring the --enable-shared flag is used.

    Install Python:
    code Bash

IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
### This command tells pyenv to use the --enable-shared option during compilation
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.12.1

  

Set the new Python version as the global default:
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
pyenv global 3.12.1

  

Verify your Python installation:
Close and reopen the terminal again. Then check your version and path.
code Bash

    IGNORE_WHEN_COPYING_START
    IGNORE_WHEN_COPYING_END

        
    # Should show '3.12.1'
    python --version

    # Should point to the pyenv shims directory
    # e.g., /home/codespace/.pyenv/shims/python
    which python

      

Step 4: Install Project Dependencies

With the correct system libraries and Python version in place, you can now install the Python packages listed in requirements.txt.
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
pip install -r requirements.txt

  

Your development environment is now fully configured! You can run the application locally for testing purposes.
Part 2: Building the Windows Executable (.exe)

PyInstaller cannot cross-compile; it can only build an executable for the operating system it is running on. Since our development environment is Linux, we will use GitHub Actions to automatically build the .exe on a fresh Windows virtual machine.
Step 1: Create the GitHub Action Workflow File

    In the root of your repository, create a new directory named .github.

    Inside .github, create another directory named workflows.

    Inside .github/workflows, create a new file named build-windows-exe.yml.

The final path should be: .github/workflows/build-windows-exe.yml
Step 2: Add the Workflow Configuration

Copy and paste the following code into your build-windows-exe.yml file.

Important: Change the placeholder your_main_script.py to the actual filename of your main Python script.
code Yaml
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
name: Build Windows Executable

### This allows you to manually trigger the build from the Actions tab
on:
  workflow_dispatch:

jobs:
  build-on-windows:
    # Use the latest Windows environment provided by GitHub
    runs-on: windows-latest

    steps:
      # Step 1: Get the repository code
      - name: Check out repository code
        uses: actions/checkout@v4

      # Step 2: Set up a Python environment
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12' # Match your development Python version

      # Step 3: Install project dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Step 4: Build the executable with PyInstaller
      - name: Build with PyInstaller
        run: |
          # --onefile: Create a single executable file.
          # --windowed: For GUI apps; prevents a console window from appearing. Remove if your app is console-based.
          # --name: The name of the final .exe file.
          pyinstaller --onefile --windowed --name VoiceCommandTool your_main_script.py # <-- CHANGE THIS FILENAME

      # Step 5: Upload the .exe as a build artifact
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          # This is the name of the downloadable file in GitHub
          name: windows-executable
          # This is the path to the file generated by PyInstaller
          path: dist/VoiceCommandTool.exe

  

Step 3: Run the Workflow and Download the .exe

    Commit and push the new .github/workflows/build-windows-exe.yml file to your repository.
    code Bash

IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
git add .github/workflows/build-windows-exe.yml
git commit -m "Add GitHub Action workflow for Windows build"
git push

  

Navigate to the "Actions" tab in your GitHub repository.

In the left sidebar, you will see a workflow named "Build Windows Executable". Click on it.

You will see a message: "This workflow has a workflow_dispatch event trigger." Click the "Run workflow" button on the right.

The build process will start. Wait for it to complete (it will get a green checkmark).

Once finished, a section named "Artifacts" will appear on the summary page for that run. Click on "windows-executable" to download a .zip file containing your VoiceCommandTool.exe.



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
