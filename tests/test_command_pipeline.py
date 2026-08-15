from __future__ import annotations

from pathlib import Path

from robot_voice.app.settings import AppSettings
from robot_voice.commands.repository import CommandRepository
from robot_voice.nlu.pipeline import CommandIntentParser
from robot_voice.nlu.safety import SafetyPolicy


def test_command_parser_matches_existing_command() -> None:
    repo = CommandRepository()
    repo.load(Path("config/commands.json"))
    parser = CommandIntentParser(repo, AppSettings())

    parsed = parser.parse("open camera")
    assert parsed is not None
    assert parsed.intent.startswith("robot.")


def test_safety_requires_confirmation_for_low_confidence() -> None:
    repo = CommandRepository()
    repo.load(Path("config/commands.json"))
    parser = CommandIntentParser(repo, AppSettings(command_confidence_threshold=0.99))
    parsed = parser.parse("open camra")
    assert parsed is not None

    decision = SafetyPolicy(min_confidence=0.99).evaluate(parsed)
    assert decision.requires_confirmation
