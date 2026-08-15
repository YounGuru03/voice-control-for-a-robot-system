from __future__ import annotations

import asyncio


class NullTtsBackend:
    async def speak(self, text: str) -> None:
        await asyncio.sleep(0)


class LegacyTtsAdapter:
    def __init__(self) -> None:
        self._engine = None

    def _ensure(self) -> None:
        if self._engine is not None:
            return
        try:
            from tts_engine_v2 import TTSEngine

            self._engine = TTSEngine()
        except Exception:
            self._engine = False

    async def speak(self, text: str) -> None:
        self._ensure()
        if self._engine in (None, False):
            return
        await asyncio.to_thread(self._engine.speak, text)
