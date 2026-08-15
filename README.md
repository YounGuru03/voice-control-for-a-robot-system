# Robot Voice Control System (Modernized)

Offline-first desktop voice-control system for robot operations, rebuilt around a modular architecture in `src/robot_voice`.

## Highlights

- Python 3.11+
- PySide6 + QML UI shell
- Async orchestration with `asyncio` + `qasync`
- Frame-based endpoint detection (Auto-VAD ready)
- Offline ASR integration point (faster-whisper primary)
- Safe command pipeline with confidence + risk checks
- Async robot adapters (Mock/Serial/HTTP)
- Beginner Windows setup/run/build scripts

## Project Layout

```text
src/robot_voice/
  app/ domain/ audio/ speech/ nlu/ commands/ robot/ tts/ services/ ui/
config/
docs/
tests/
scripts/
.github/workflows/
```

## Quick Start (Windows)

1. Clone repository.
2. Run:
   - `scripts\setup.bat` or `scripts\setup.ps1`
3. Launch:
   - `scripts\run.bat` or `scripts\run.ps1`

The app defaults to Mock mode so it can start without robot hardware.

## Setup (manual)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run tests

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
.\.venv\Scripts\python -m pytest -p pytest_asyncio.plugin
```

## Build package

```powershell
scripts\build.bat
# or
scripts\build.ps1
```

Build verification uses `scripts/verify_release.py`.

## Migration Notes

See:
- `docs/architecture.md`
- `docs/migration.md`

## Dependencies added/updated

- `pydantic`, `pydantic-settings`, `PyYAML` for typed config/data validation
- `PySide6`, `qasync` for modern desktop UI/event-loop integration
- `sounddevice` for audio capture foundation
- `faster-whisper` (primary) and optional `vosk` fallback integration point
- `pytest`, `pytest-asyncio`, `pytest-qt`, `ruff`, `mypy` for quality gates
- `PyInstaller` for packaging

## Known limitations

- QML pages are currently a foundational shell and need richer interactive editors/diagnostics.
- VAD is implemented with adaptive energy endpoint detection; Silero/WebRTC backend wiring is staged next.
- Serial/HTTP adapters provide async interfaces but protocol-specific command mapping must be finalized per robot firmware/API.
- Legacy files remain for transition and should be removed after full production rollout of the modular app.
