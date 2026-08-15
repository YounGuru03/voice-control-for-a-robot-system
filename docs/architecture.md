# Robot Voice Architecture

## Overview

The application now uses a `src/robot_voice` modular architecture:

- `app/`: startup container, settings, app-data paths
- `domain/`: typed models, enums, interfaces
- `audio/`: frame-based endpoint detection and capture abstraction
- `speech/`: offline ASR backends (faster-whisper primary, Vosk fallback stub)
- `nlu/`: deterministic + fuzzy parser and safety policy
- `commands/`: validated command repository and legacy migration
- `robot/`: async adapters (Mock, Serial, HTTP)
- `tts/`: legacy TTS adapter and null backend
- `services/`: non-blocking voice-session state machine orchestration
- `ui/`: PySide6 + QML presentation shell

## Voice Session State Machine

`IDLE -> LISTENING -> SPEECH_DETECTED -> RECORDING -> FINALIZING -> TRANSCRIBING -> UNDERSTANDING -> CONFIRMING -> EXECUTING -> RESPONDING`

Additional states: `PAUSED`, `ERROR`.

## Offline-First Principles

- Core pipeline uses local audio frames and offline ASR.
- Mock adapter is default, so app can run without robot hardware.
- Optional cloud/LLM behaviors are not enabled by default.

## Safety Model

- Risk levels: `INFO`, `LOW`, `MEDIUM`, `HIGH`
- `robot.stop` and `robot.emergency_stop` are always prioritized for interruption.
- Low-confidence and elevated-risk intents trigger confirmation state.
- Execution routes through service/adapters, never direct UI hardware access.

## Data and Runtime Paths

- Runtime user data is stored in platform standard directory via `platformdirs`.
- Commands are validated from `config/commands.json`.
- Default settings are provided in `config/default_settings.yaml`.
