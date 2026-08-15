# Migration Notes

## Legacy to Modern Module Mapping

- `main_voice_app.py` -> `src/robot_voice/ui`, `src/robot_voice/services`, `src/robot_voice/app`
- `audio_engine.py` / `audio_engine_v2.py` -> `src/robot_voice/audio`, `src/robot_voice/speech`, `src/robot_voice/services`
- `command_manager.py` + `commands_hotwords.json` -> `src/robot_voice/commands` + `config/commands.json`
- `model_manager.py` -> `src/robot_voice/speech`
- `tts_engine_v2.py` -> `src/robot_voice/tts/adapters.py` (`LegacyTtsAdapter` compatibility layer)
- `build.py` -> `scripts/build.bat`, `scripts/build.ps1`, `scripts/verify_release.py`

## Deprecation Strategy

Legacy files remain in repository for transitional compatibility, but new development should target `src/robot_voice` only. After production validation of the modular app, legacy modules can be removed.

## Command Data Migration

`commands_hotwords.json` was migrated to `config/commands.json` using `src/robot_voice/commands/migration.py`, preserving phrases while adding typed metadata: intent, risk level, confirmation flag, and validation-ready structure.
