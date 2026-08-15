from __future__ import annotations

from pathlib import Path


def assert_exists(path: Path, message: str) -> None:
    if not path.exists():
        raise SystemExit(f"[verify_release] FAIL: {message} ({path})")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    dist_root = project_root / "dist"
    assert_exists(dist_root, "dist directory missing")

    exe = dist_root / "robot-voice" / "robot-voice.exe"
    onefile = dist_root / "robot-voice.exe"
    if not exe.exists() and not onefile.exists():
        raise SystemExit("[verify_release] FAIL: executable not found")

    assert_exists(project_root / "config" / "commands.json", "commands config missing")
    assert_exists(project_root / "src" / "robot_voice" / "ui" / "qml" / "Main.qml", "QML missing")
    print("[verify_release] PASS: package resources look valid")


if __name__ == "__main__":
    main()
