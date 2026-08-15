from __future__ import annotations

import pytest

from robot_voice.domain.models import RobotCommand
from robot_voice.robot.adapters import MockRobotAdapter


@pytest.mark.asyncio
async def test_mock_robot_execute_and_emergency_stop() -> None:
    robot = MockRobotAdapter()
    await robot.connect()

    result = await robot.execute(RobotCommand(intent="robot.forward", slots={"distance_cm": 30}))
    stop = await robot.emergency_stop()

    assert result.ok
    assert stop.ok
    assert robot.history
