from __future__ import annotations

import json
from pathlib import Path

import yaml

from robot_voice.domain.models import CommandDefinition, CommandsConfig


class CommandRepository:
    def __init__(self) -> None:
        self._config: CommandsConfig = CommandsConfig(commands=[])

    def load(self, path: Path) -> None:
        payload = self._read(path)
        self._config = CommandsConfig.model_validate(payload)

    def save(self, path: Path) -> None:
        payload = self._config.model_dump(mode="json")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in {".yaml", ".yml"}:
            path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def commands(self) -> list[CommandDefinition]:
        return [cmd for cmd in self._config.commands if cmd.enabled]

    def add_or_update(self, command: CommandDefinition) -> None:
        commands = [c for c in self._config.commands if c.id != command.id]
        commands.append(command)
        self._config = CommandsConfig(version=self._config.version, locale=self._config.locale, commands=commands)

    @staticmethod
    def _read(path: Path) -> dict[str, object]:
        raw = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yml", ".yaml"}:
            loaded = yaml.safe_load(raw)
        else:
            loaded = json.loads(raw)
        if not isinstance(loaded, dict):
            raise TypeError("commands file must be an object")
        return loaded
