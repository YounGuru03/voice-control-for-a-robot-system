from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field
from platformdirs import user_data_dir


class VadSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame_ms: int = 20
    pre_roll_ms: int = 300
    post_roll_ms: int = 450
    min_recording_ms: int = 350
    max_recording_ms: int = 15000
    speech_start_frames: int = 3
    silence_end_frames: int = 8
    energy_threshold: float = 0.015


class AsrSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: str = "faster_whisper"
    model_name: str = "base"
    language: str = "zh"
    use_gpu: bool = False


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    locale: str = "zh-CN"
    control_mode: str = "AUTO_VAD"
    vad: VadSettings = Field(default_factory=VadSettings)
    asr: AsrSettings = Field(default_factory=AsrSettings)
    command_confidence_threshold: float = 0.75
    low_confidence_confirmation_threshold: float = 0.65


def app_data_root() -> Path:
    root = Path(user_data_dir("robot_voice", "YounGuru03"))
    root.mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(exist_ok=True)
    (root / "models").mkdir(exist_ok=True)
    return root


def load_settings(path: Path) -> AppSettings:
    if not path.exists():
        settings = AppSettings()
        save_settings(path, settings)
        return settings
    if path.suffix.lower() in {".yml", ".yaml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    return AppSettings.model_validate(data)


def save_settings(path: Path, settings: AppSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".yml", ".yaml"}:
        path.write_text(yaml.safe_dump(settings.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        return
    path.write_text(json.dumps(settings.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
