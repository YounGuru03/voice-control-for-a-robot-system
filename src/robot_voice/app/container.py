from __future__ import annotations

from pathlib import Path

from robot_voice.app.settings import AppSettings, app_data_root, load_settings
from robot_voice.commands.repository import CommandRepository
from robot_voice.nlu.pipeline import CommandIntentParser
from robot_voice.robot.adapters import MockRobotAdapter
from robot_voice.services.voice_session import VoiceSessionService
from robot_voice.speech.backends import FasterWhisperBackend
from robot_voice.tts.adapters import NullTtsBackend


class AppContainer:
    def __init__(self, settings_path: Path | None = None) -> None:
        root = app_data_root()
        self.settings_path = settings_path or (root / "config.json")
        self.settings: AppSettings = load_settings(self.settings_path)
        self.command_repository = CommandRepository()
        self.command_repository.load(Path("config/commands.json"))
        self.intent_parser = CommandIntentParser(self.command_repository, self.settings)
        self.robot_adapter = MockRobotAdapter()
        self.asr_backend = FasterWhisperBackend(self.settings.asr)
        self.tts_backend = NullTtsBackend()
        self.voice_session = VoiceSessionService(
            settings=self.settings,
            intent_parser=self.intent_parser,
            asr_backend=self.asr_backend,
            robot_adapter=self.robot_adapter,
            tts_backend=self.tts_backend,
        )
