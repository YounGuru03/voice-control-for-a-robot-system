from __future__ import annotations

import numpy as np

from robot_voice.audio.endpoint import EndpointConfig, EndpointDetector


def test_endpoint_detector_starts_after_consecutive_speech() -> None:
    detector = EndpointDetector(EndpointConfig(speech_start_frames=3, silence_end_frames=4, frame_ms=20))

    silent = np.zeros(320, dtype=np.float32)
    speech = np.ones(320, dtype=np.float32) * 0.5

    for _ in range(2):
        started, finished, _ = detector.process_frame(silent)
        assert not started
        assert not finished

    started_count = 0
    for _ in range(3):
        started, finished, _ = detector.process_frame(speech)
        started_count += int(started)
        assert not finished

    assert started_count == 1


def test_endpoint_detector_finishes_on_sustained_silence() -> None:
    detector = EndpointDetector(EndpointConfig(speech_start_frames=2, silence_end_frames=3, frame_ms=20))

    speech = np.ones(320, dtype=np.float32) * 0.5
    silent = np.zeros(320, dtype=np.float32)

    for _ in range(2):
        detector.process_frame(speech)

    finished = False
    for _ in range(4):
        _, finished, _ = detector.process_frame(silent)

    assert finished
