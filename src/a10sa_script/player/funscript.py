import asyncio
from buttplug import Client, ClientError, ProtocolSpec, WebsocketConnector
from loguru import logger

from ..exceptions import DeviceError
from ..command.base import GenericLinearCommand
from ..script import FunscriptScript
from .player import ScriptPlayer


class FunscriptScriptPlayer(ScriptPlayer[GenericLinearCommand]):
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
        self._client = Client(name or "a10sa-script", ProtocolSpec.v3)
        self._connector = WebsocketConnector(
            intiface_addr or "ws://127.0.0.1:12345",
            logger=self._client.logger,
        )
        self._min_position = (
            self._validate_position(min_position) if min_position is not None else None
        )
        self._max_position = (
            self._validate_position(max_position) if max_position is not None else None
        )

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
            await self._client.connect(self._connector)
        except ClientError as e:
            raise DeviceError("Failed to connect to intiface") from e
        logger.debug("funscript connect")

    async def disconnect(self) -> None:
        await self._client.disconnect()
        await super().disconnect()

    async def send(self, command: GenericLinearCommand) -> None:
        try:
            for device in self._client.devices.values():
                if device.linear_actuators:
                    await device.linear_actuators[0].command(
                        command.duration, self._scale_position(command.position)
                    )
        except ClientError as e:
            raise DeviceError("Failed to send command to intiface") from e

    async def reset(self) -> None:
        if self._script is not None and isinstance(self._script, FunscriptScript):
            pos = self._script.initial_position
        else:
            pos = 0.0
        await self.send(GenericLinearCommand(500, pos))
        await asyncio.sleep(0.5)
