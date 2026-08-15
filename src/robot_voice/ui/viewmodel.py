from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from robot_voice.app.container import AppContainer


class AppViewModel(QObject):
    statusChanged = Signal()
    transcriptChanged = Signal()
    historyChanged = Signal()

    def __init__(self, container: AppContainer) -> None:
        super().__init__()
        self._container = container
        self._status = "IDLE"
        self._transcript = ""
        self._history: list[str] = []

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(str, notify=transcriptChanged)
    def transcript(self) -> str:
        return self._transcript

    @Property(str, notify=historyChanged)
    def history(self) -> str:
        return "\n".join(self._history[-20:])

    @Slot()
    def start(self) -> None:
        self._status = "LISTENING"
        self.statusChanged.emit()

    @Slot()
    def pause(self) -> None:
        self._status = "PAUSED"
        self.statusChanged.emit()

    @Slot()
    def stop(self) -> None:
        self._status = "IDLE"
        self.statusChanged.emit()

    @Slot()
    def emergencyStop(self) -> None:
        self._status = "EMERGENCY_STOP"
        self._history.append("EMERGENCY_STOP")
        self.statusChanged.emit()
        self.historyChanged.emit()
