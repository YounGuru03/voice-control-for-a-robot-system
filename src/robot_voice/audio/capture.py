from __future__ import annotations

from collections.abc import AsyncIterator

import numpy as np


class AudioCapture:
    """Sounddevice-backed capture stub; test mode can inject frames manually."""

    def __init__(self, sample_rate: int = 16000, frame_ms: int = 20) -> None:
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)

    async def stream(self) -> AsyncIterator[np.ndarray]:
        raise RuntimeError("Live microphone streaming is provided by UI runtime integration.")
