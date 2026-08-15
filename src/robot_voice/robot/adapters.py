from __future__ import annotations

import asyncio
from dataclasses import dataclass

import requests

from robot_voice.domain.models import ExecutionResult, RobotCommand


@dataclass(slots=True)
class SerialConfig:
    port: str
    baud_rate: int = 115200
    timeout: float = 1.0


@dataclass(slots=True)
class HttpConfig:
    base_url: str
    timeout: float = 3.0


class MockRobotAdapter:
    def __init__(self) -> None:
        self._connected = False
        self.history: list[RobotCommand] = []

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def get_status(self) -> dict[str, str]:
        return {"connected": str(self._connected), "adapter": "mock"}

    async def execute(self, command: RobotCommand) -> ExecutionResult:
        if not self._connected:
            await self.connect()
        self.history.append(command)
        await asyncio.sleep(0)
        return ExecutionResult(ok=True, message=f"Mock executed: {command.intent}")

    async def emergency_stop(self) -> ExecutionResult:
        return ExecutionResult(ok=True, message="Mock emergency stop triggered")

    async def health_check(self) -> ExecutionResult:
        return ExecutionResult(ok=True, message="Mock robot healthy")


class SerialRobotAdapter:
    def __init__(self, config: SerialConfig) -> None:
        self._config = config
        self._serial = None

    async def connect(self) -> None:
        import serial

        self._serial = serial.Serial(self._config.port, self._config.baud_rate, timeout=self._config.timeout)

    async def disconnect(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    async def get_status(self) -> dict[str, str]:
        return {
            "connected": str(self._serial is not None and self._serial.is_open),
            "adapter": "serial",
            "port": self._config.port,
        }

    async def execute(self, command: RobotCommand) -> ExecutionResult:
        if self._serial is None:
            return ExecutionResult(ok=False, message="serial not connected")
        payload = f"{command.intent}:{command.slots}\n".encode("utf-8")
        self._serial.write(payload)
        return ExecutionResult(ok=True, message="serial command sent")

    async def emergency_stop(self) -> ExecutionResult:
        if self._serial is None:
            return ExecutionResult(ok=False, message="serial not connected")
        self._serial.write(b"EMERGENCY_STOP\n")
        return ExecutionResult(ok=True, message="serial emergency stop sent")

    async def health_check(self) -> ExecutionResult:
        return ExecutionResult(ok=True, message="serial adapter ready")


class HttpRobotAdapter:
    def __init__(self, config: HttpConfig) -> None:
        self._config = config
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def get_status(self) -> dict[str, str]:
        return {"connected": str(self._connected), "adapter": "http", "url": self._config.base_url}

    async def execute(self, command: RobotCommand) -> ExecutionResult:
        if not self._connected:
            await self.connect()
        response = requests.post(
            f"{self._config.base_url.rstrip('/')}/execute",
            json=command.model_dump(mode="json"),
            timeout=self._config.timeout,
        )
        if response.ok:
            return ExecutionResult(ok=True, message="http command accepted")
        return ExecutionResult(ok=False, message=f"http error: {response.status_code}")

    async def emergency_stop(self) -> ExecutionResult:
        response = requests.post(f"{self._config.base_url.rstrip('/')}/emergency_stop", timeout=self._config.timeout)
        if response.ok:
            return ExecutionResult(ok=True, message="http emergency stop sent")
        return ExecutionResult(ok=False, message=f"http error: {response.status_code}")

    async def health_check(self) -> ExecutionResult:
        response = requests.get(f"{self._config.base_url.rstrip('/')}/health", timeout=self._config.timeout)
        if response.ok:
            return ExecutionResult(ok=True, message="http robot healthy")
        return ExecutionResult(ok=False, message=f"http health failed: {response.status_code}")
