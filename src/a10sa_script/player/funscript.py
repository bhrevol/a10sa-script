import asyncio
from buttplug import ButtplugClient, ButtplugDevice, ButtplugDeviceError, ButtplugError
from loguru import logger

from ..exceptions import DeviceError
from ..command.base import PositionWithDurationCommand
from ..script import FunscriptScript
from .player import ScriptPlayer


class FunscriptScriptPlayer(ScriptPlayer[PositionWithDurationCommand]):
    """Script player for playing funscripts via Buttplug/Intiface.

    Connects to Intiface when used as an async context manager, but does not scan for
    devices. Device scanning should be managed in Intiface.
    """

    DEVICE_LATENCY = 80

    def __init__(
        self,
        name: str | None = None,
        intiface_addr: str | None = None,
        min_position: float | None = None,
        max_position: float | None = None,
    ) -> None:
        super().__init__()
        self._client = ButtplugClient(name or "a10sa-script")
        self._client.on_device_added = self.on_device_added
        self._client.on_device_removed = self.on_device_removed
        self._client.on_server_disconnect = self.on_server_disconnect
        self.intiface_addr = intiface_addr or "ws://127.0.0.1:12345"
        self._min_position = (
            self._validate_position(min_position) if min_position is not None else None
        )
        self._max_position = (
            self._validate_position(max_position) if max_position is not None else None
        )

    @staticmethod
    def on_device_added(device: ButtplugDevice) -> None:
        logger.info("Device connected: {}", device.name)

    @staticmethod
    def on_device_removed(device: ButtplugDevice) -> None:
        logger.info("Device removed: {}", device.name)

    @staticmethod
    def on_server_disconnect() -> None:
        logger.debug("Disconnected from intiface server")

    @property
    def min_position(self) -> float | None:
        return self._min_position

    @min_position.setter
    def min_position(self, value: float | None) -> None:
        if value is not None:
            value = self._validate_position(value)
            if self.max_position is not None and value > self.max_position:
                raise ValueError("min_position must be <= max_position")
        self._min_position = value
        logger.debug("min_position {}", value)

    @property
    def max_position(self) -> float | None:
        return self._max_position

    @max_position.setter
    def max_position(self, value: float | None) -> None:
        if value is not None:
            value = self._validate_position(value)
            if self.min_position is not None and value < self.min_position:
                raise ValueError("max_position must be >= min_position")
        self._max_position = value
        logger.debug("max_position {}", value)

    @staticmethod
    def _validate_position(pos: float) -> float:
        if 0.0 <= pos <= 1.0:
            return pos
        raise ValueError("position must be in range [0.0, 1.0] (inclusive)")

    def _scale_position(self, pos: float) -> float:
        if self.min_position is None and self.max_position is None:
            return pos
        min_position = self.min_position if self.min_position is not None else 0.0
        max_position = self.max_position if self.max_position is not None else 1.0
        return pos * (max_position - min_position) + min_position

    async def connect(self) -> None:
        await super().connect()
        try:
            await self._client.connect(self.intiface_addr)
        except ButtplugError as e:
            raise DeviceError("Failed to connect to intiface") from e

    async def disconnect(self) -> None:
        if self._client.connected:
            await self._client.stop_all_devices()
            await self._client.disconnect()
        await super().disconnect()

    async def send(self, command: PositionWithDurationCommand) -> None:
        if not self._client.connected:
            return
        try:
            scaled_command = PositionWithDurationCommand(
                self._scale_position(command.value),
                duration=command.duration,
            )
            for device in self._client.devices.values():
                if device.has_output(command.OUTPUT_TYPE):
                    await device.run_output(scaled_command.output_command)
        except ButtplugDeviceError as e:
            raise DeviceError("Failed to send command to intiface") from e

    async def reset(self) -> None:
        if self._script is not None and isinstance(self._script, FunscriptScript):
            pos = self._script.initial_position
        else:
            pos = 0.0
        await self.send(PositionWithDurationCommand(pos, 1000))
        await asyncio.sleep(0.5)
