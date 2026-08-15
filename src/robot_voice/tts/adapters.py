from __future__ import annotations

import asyncio
import importlib
from typing import Any


class NullTtsBackend:
    async def speak(self, text: str) -> None:
        await asyncio.sleep(0)


class LegacyTtsAdapter:
    def __init__(self) -> None:
        self._engine: Any = None

    def _ensure(self) -> None:
        if self._engine is not None:
            return
        try:
            module = importlib.import_module("tts_engine_v2")
            self._engine = module.TTSEngine()
        except (ImportError, OSError, RuntimeError):
            self._engine = False

    async def speak(self, text: str) -> None:
        self._ensure()
        if self._engine in (None, False):
            return
        await asyncio.to_thread(self._engine.speak, text)
