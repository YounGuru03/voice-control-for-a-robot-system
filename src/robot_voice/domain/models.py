from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VoiceSessionState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    SPEECH_DETECTED = "SPEECH_DETECTED"
    RECORDING = "RECORDING"
    FINALIZING = "FINALIZING"
    TRANSCRIBING = "TRANSCRIBING"
    UNDERSTANDING = "UNDERSTANDING"
    CONFIRMING = "CONFIRMING"
    EXECUTING = "EXECUTING"
    RESPONDING = "RESPONDING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class ControlMode(str, Enum):
    AUTO_VAD = "AUTO_VAD"
    PUSH_TO_TALK = "PUSH_TO_TALK"
    MANUAL = "MANUAL"


class RiskLevel(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CommandParameterRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str = "number"
    minimum: float | None = None
    maximum: float | None = None


class CommandDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    intent: str
    text: str
    aliases: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    regex: str | None = None
    slots: dict[str, Any] = Field(default_factory=dict)
    parameter_rules: list[CommandParameterRule] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    priority: int = 50
    enabled: bool = True
    needs_confirmation: bool = False


class ParsedIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    slots: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_confirmation: bool = False
    risk_level: RiskLevel = RiskLevel.LOW
    source: str = "deterministic"


class ExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    message: str


class CommandsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    locale: str = "zh-CN"
    commands: list[CommandDefinition]


class SafetyPolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str
    requires_confirmation: bool = False


class VoiceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: VoiceSessionState
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


class RobotCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    slots: dict[str, Any] = Field(default_factory=dict)

    @field_validator("intent")
    @classmethod
    def intent_must_not_be_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("intent is required")
        return stripped
