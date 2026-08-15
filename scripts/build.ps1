$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python -m PyInstaller --noconfirm --clean --name robot-voice --windowed --paths src src/robot_voice/ui/main.py
& .\.venv\Scripts\python scripts/verify_release.py
