from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .models import ExecutionResult, ParsedIntent, RobotCommand


class AsrBackend(Protocol):
    async def transcribe(self, audio: Iterable[float]) -> str:
        ...


class TtsBackend(Protocol):
    async def speak(self, text: str) -> None:
        ...


class RobotAdapter(Protocol):
    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def get_status(self) -> dict[str, str]:
        ...

    async def execute(self, command: RobotCommand) -> ExecutionResult:
        ...

    async def emergency_stop(self) -> ExecutionResult:
        ...

    async def health_check(self) -> ExecutionResult:
        ...


class IntentParser(Protocol):
    def parse(self, transcript: str) -> ParsedIntent | None:
        ...
