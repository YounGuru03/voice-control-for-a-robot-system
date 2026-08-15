from __future__ import annotations

from pathlib import Path

from robot_voice.app.settings import AppSettings, app_data_root, save_settings
from robot_voice.commands.migration import migrate_legacy_commands


def main() -> None:
    root = app_data_root()
    config_path = root / "config.json"
    if not config_path.exists():
        save_settings(config_path, AppSettings())

    commands_path = Path("config/commands.json")
    if not commands_path.exists():
        migrate_legacy_commands(Path("commands_hotwords.json"), commands_path)


if __name__ == "__main__":
    main()
