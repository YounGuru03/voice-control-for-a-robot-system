from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from robot_voice.app.container import AppContainer
from robot_voice.ui.viewmodel import AppViewModel


def test_viewmodel_state_changes() -> None:
    vm = AppViewModel(AppContainer())
    vm.start()
    assert vm.status == "LISTENING"
    vm.pause()
    assert vm.status == "PAUSED"
