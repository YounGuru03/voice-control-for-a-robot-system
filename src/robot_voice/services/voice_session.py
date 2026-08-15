from __future__ import annotations

import numpy as np

from robot_voice.app.settings import AppSettings
from robot_voice.audio.endpoint import EndpointConfig, EndpointDetector
from robot_voice.domain.interfaces import AsrBackend, IntentParser, RobotAdapter, TtsBackend
from robot_voice.domain.models import (
    RobotCommand,
    VoiceEvent,
    VoiceSessionState,
)
from robot_voice.nlu.safety import SafetyPolicy


class VoiceSessionService:
    def __init__(
        self,
        settings: AppSettings,
        intent_parser: IntentParser,
        asr_backend: AsrBackend,
        robot_adapter: RobotAdapter,
        tts_backend: TtsBackend,
    ) -> None:
        self._settings = settings
        self._intent_parser = intent_parser
        self._asr = asr_backend
        self._robot = robot_adapter
        self._tts = tts_backend
        self._state = VoiceSessionState.IDLE
        self._safety = SafetyPolicy(settings.command_confidence_threshold)
        self._detector = EndpointDetector(
            EndpointConfig(
                frame_ms=settings.vad.frame_ms,
                pre_roll_ms=settings.vad.pre_roll_ms,
                post_roll_ms=settings.vad.post_roll_ms,
                min_recording_ms=settings.vad.min_recording_ms,
                max_recording_ms=settings.vad.max_recording_ms,
                speech_start_frames=settings.vad.speech_start_frames,
                silence_end_frames=settings.vad.silence_end_frames,
                energy_threshold=settings.vad.energy_threshold,
            )
        )
        self._recording_buffer: list[np.ndarray] = []

    @property
    def state(self) -> VoiceSessionState:
        return self._state

    def set_state(self, state: VoiceSessionState, message: str = "") -> VoiceEvent:
        self._state = state
        return VoiceEvent(state=state, message=message)

    def process_frame(self, frame: np.ndarray) -> list[VoiceEvent]:
        events: list[VoiceEvent] = []
        if self._state in {VoiceSessionState.IDLE, VoiceSessionState.PAUSED, VoiceSessionState.ERROR}:
            self.set_state(VoiceSessionState.LISTENING)

        started, finished, frames = self._detector.process_frame(frame)
        if started:
            self._recording_buffer.clear()
            self._recording_buffer.extend(frames)
            events.append(self.set_state(VoiceSessionState.SPEECH_DETECTED, "speech detected"))
            events.append(self.set_state(VoiceSessionState.RECORDING, "recording"))

        if self._state == VoiceSessionState.RECORDING and frames:
            self._recording_buffer.extend(frames)

        if finished:
            events.append(self.set_state(VoiceSessionState.FINALIZING, "finalizing"))

        return events

    async def finalize_recording(self) -> VoiceEvent:
        if not self._recording_buffer:
            return self.set_state(VoiceSessionState.LISTENING)

        self.set_state(VoiceSessionState.TRANSCRIBING)
        audio = np.concatenate(self._recording_buffer) if self._recording_buffer else np.array([], dtype=np.float32)
        transcript = await self._asr.transcribe(audio.tolist())

        self.set_state(VoiceSessionState.UNDERSTANDING)
        parsed = self._intent_parser.parse(transcript)
        if parsed is None:
            self._recording_buffer.clear()
            await self._tts.speak("无法识别命令")
            return self.set_state(VoiceSessionState.RESPONDING, "no command")

        decision = self._safety.evaluate(parsed)
        if not decision.allowed:
            self._recording_buffer.clear()
            return self.set_state(VoiceSessionState.CONFIRMING, decision.reason)

        if parsed.intent in {"robot.stop", "robot.emergency_stop"}:
            self.set_state(VoiceSessionState.EXECUTING)
            result = await self._robot.emergency_stop()
            self._recording_buffer.clear()
            await self._tts.speak(result.message)
            return self.set_state(VoiceSessionState.RESPONDING, result.message)

        if decision.requires_confirmation:
            self._recording_buffer.clear()
            return self.set_state(VoiceSessionState.CONFIRMING, decision.reason)

        self.set_state(VoiceSessionState.EXECUTING)
        result = await self._robot.execute(RobotCommand(intent=parsed.intent, slots=parsed.slots))
        self._recording_buffer.clear()
        await self._tts.speak(result.message)
        return self.set_state(VoiceSessionState.RESPONDING, result.message)

    async def pause(self) -> VoiceEvent:
        return self.set_state(VoiceSessionState.PAUSED, "paused")

    async def resume(self) -> VoiceEvent:
        return self.set_state(VoiceSessionState.LISTENING, "listening")

    async def handle_error(self, message: str) -> VoiceEvent:
        return self.set_state(VoiceSessionState.ERROR, message)
