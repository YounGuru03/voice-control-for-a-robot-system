from __future__ import annotations

import json
from pathlib import Path

from robot_voice.domain.models import CommandDefinition, CommandsConfig, RiskLevel


RISK_BY_KEYWORD = {
    "emergency stop": RiskLevel.HIGH,
    "stop": RiskLevel.HIGH,
    "shutdown": RiskLevel.HIGH,
    "delete": RiskLevel.HIGH,
    "reset": RiskLevel.MEDIUM,
}


def infer_risk(text: str) -> RiskLevel:
    lowered = text.lower()
    for keyword, risk in RISK_BY_KEYWORD.items():
        if keyword in lowered:
            return risk
    return RiskLevel.LOW


def migrate_legacy_commands(legacy_path: Path, output_path: Path) -> CommandsConfig:
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    migrated: list[CommandDefinition] = []
    for phrase, payload in legacy.get("commands", {}).items():
        lowered = phrase.strip().lower()
        command_id = lowered.replace(" ", "_")
        intent_root = lowered.split(" ", maxsplit=1)[0] if lowered else "robot"
        intent = f"robot.{intent_root}"
        alternatives = payload.get("alternatives") or []
        aliases = [alt for alt in alternatives if isinstance(alt, str) and alt.strip()]
        risk = infer_risk(lowered)
        migrated.append(
            CommandDefinition(
                id=command_id,
                intent=intent,
                text=phrase,
                aliases=aliases,
                keywords=lowered.split(),
                slots={},
                risk_level=risk,
                priority=50,
                enabled=True,
                needs_confirmation=risk in {RiskLevel.MEDIUM, RiskLevel.HIGH},
            )
        )

    config = CommandsConfig(version=1, locale="zh-CN", commands=sorted(migrated, key=lambda c: c.id))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
    return config
