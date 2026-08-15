from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from robot_voice.app.settings import AsrSettings


class FasterWhisperBackend:
    def __init__(self, settings: AsrSettings) -> None:
        self._settings = settings
        self._model = None

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel

            device = "cuda" if self._settings.use_gpu else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            self._model = WhisperModel(self._settings.model_name, device=device, compute_type=compute_type)
        except Exception:
            self._model = False

    async def transcribe(self, audio: Iterable[float]) -> str:
        self._ensure_model()
        if self._model is False:
            return ""
        if self._model is None:
            return ""
        array = np.asarray(list(audio), dtype=np.float32)
        if not array.size:
            return ""
        segments, _ = self._model.transcribe(array, language=self._settings.language)
        return " ".join(segment.text.strip() for segment in segments).strip()


class VoskBackend:
    def __init__(self) -> None:
        self._enabled = False

    async def transcribe(self, audio: Iterable[float]) -> str:
        if not self._enabled:
            return ""
        return ""
