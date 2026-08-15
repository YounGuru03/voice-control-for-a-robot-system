from __future__ import annotations

from pathlib import Path

from robot_voice.commands.migration import migrate_legacy_commands


def test_legacy_commands_migrate_to_new_schema(tmp_path: Path) -> None:
    output = tmp_path / "commands.json"
    config = migrate_legacy_commands(Path("commands_hotwords.json"), output)

    assert output.exists()
    assert config.commands
    assert all(cmd.intent.startswith("robot.") for cmd in config.commands)
