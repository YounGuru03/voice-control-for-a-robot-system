from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from qasync import QEventLoop

from robot_voice.app.container import AppContainer


def main() -> int:
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    app = QGuiApplication(sys.argv)
    loop = QEventLoop(app)
    container = AppContainer()

    from robot_voice.ui.viewmodel import AppViewModel

    vm = AppViewModel(container)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appVm", vm)
    qml_path = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(str(qml_path))
    if not engine.rootObjects():
        return 1

    asyncio.set_event_loop(loop)
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
