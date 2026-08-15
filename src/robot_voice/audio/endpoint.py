from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class EndpointConfig:
    frame_ms: int = 20
    pre_roll_ms: int = 300
    post_roll_ms: int = 450
    min_recording_ms: int = 350
    max_recording_ms: int = 15000
    speech_start_frames: int = 3
    silence_end_frames: int = 8
    energy_threshold: float = 0.015


class EndpointDetector:
    def __init__(self, config: EndpointConfig) -> None:
        self.config = config
        self._speech_frames = 0
        self._silence_frames = 0
        self._recorded_ms = 0
        self._is_recording = False
        pre_roll_frames = max(1, config.pre_roll_ms // config.frame_ms)
        self._pre_roll: deque[np.ndarray] = deque(maxlen=pre_roll_frames)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def reset(self) -> None:
        self._speech_frames = 0
        self._silence_frames = 0
        self._recorded_ms = 0
        self._is_recording = False
        self._pre_roll.clear()

    def process_frame(self, frame: np.ndarray) -> tuple[bool, bool, list[np.ndarray]]:
        energy = float(np.sqrt(np.mean(np.square(frame)))) if frame.size else 0.0
        is_speech = energy >= self.config.energy_threshold
        output: list[np.ndarray] = []

        self._pre_roll.append(frame)

        if is_speech:
            self._speech_frames += 1
            self._silence_frames = 0
        else:
            self._silence_frames += 1
            self._speech_frames = max(0, self._speech_frames - 1)

        started = False
        finished = False

        if not self._is_recording and self._speech_frames >= self.config.speech_start_frames:
            self._is_recording = True
            started = True
            output.extend(self._pre_roll)

        if self._is_recording:
            output.append(frame)
            self._recorded_ms += self.config.frame_ms
            if self._recorded_ms >= self.config.max_recording_ms or (
                self._recorded_ms >= self.config.min_recording_ms
                and self._silence_frames >= self.config.silence_end_frames
            ):
                finished = True

        if finished:
            self._is_recording = False
            self._speech_frames = 0
            self._silence_frames = 0
            self._recorded_ms = 0
            self._pre_roll.clear()

        return started, finished, output
