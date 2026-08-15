from __future__ import annotations

import re
from difflib import SequenceMatcher

from robot_voice.app.settings import AppSettings
from robot_voice.commands.repository import CommandRepository
from robot_voice.domain.models import ParsedIntent

SYNONYMS = {
    "前进": "forward",
    "后退": "backward",
    "左转": "left",
    "右转": "right",
    "停止": "stop",
}


class CommandIntentParser:
    def __init__(self, repository: CommandRepository, settings: AppSettings) -> None:
        self._repository = repository
        self._settings = settings

    def parse(self, transcript: str) -> ParsedIntent | None:
        text = self._normalize(transcript)
        if not text:
            return None

        deterministic = self._deterministic_match(text)
        if deterministic is not None:
            return deterministic

        return self._fuzzy_match(text)

    def _normalize(self, text: str) -> str:
        normalized = text.strip().lower()
        for source, target in SYNONYMS.items():
            normalized = normalized.replace(source, target)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def _deterministic_match(self, text: str) -> ParsedIntent | None:
        for command in self._repository.commands():
            aliases = {command.text.lower(), *[a.lower() for a in command.aliases]}
            if text in aliases:
                confidence = 0.95
                return ParsedIntent(
                    intent=command.intent,
                    slots=command.slots,
                    confidence=confidence,
                    needs_confirmation=command.needs_confirmation,
                    risk_level=command.risk_level,
                    source="deterministic",
                )

            if command.regex and re.search(command.regex, text):
                return ParsedIntent(
                    intent=command.intent,
                    slots=command.slots,
                    confidence=0.9,
                    needs_confirmation=command.needs_confirmation,
                    risk_level=command.risk_level,
                    source="regex",
                )
        return None

    def _fuzzy_match(self, text: str) -> ParsedIntent | None:
        best_score = 0.0
        best_command = None
        for command in self._repository.commands():
            candidates = [command.text, *command.aliases]
            for candidate in candidates:
                score = SequenceMatcher(None, text, candidate.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_command = command

        if best_command is None or best_score < self._settings.low_confidence_confirmation_threshold:
            return None

        return ParsedIntent(
            intent=best_command.intent,
            slots=best_command.slots,
            confidence=best_score,
            needs_confirmation=best_command.needs_confirmation
            or best_score < self._settings.command_confidence_threshold,
            risk_level=best_command.risk_level,
            source="fuzzy",
        )
