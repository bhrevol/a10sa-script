from buttplug import Client, WebsocketConnector, ProtocolSpec

from .player import ScriptPlayer
from ..command.base import GenericLinearCommand


class FunscriptScriptPlayer(ScriptPlayer[GenericLinearCommand]):
    """Script player for playing funscripts via Buttplug/Intiface.

    Connects to Intiface when used as an async context manager, but does not scan for
    devices. Device scanning should be managed in Intiface.
    """

    def __init__(
        self, name: str | None = None, intiface_addr: str | None = None
    ) -> None:
        super().__init__()
        self._client = Client(name or "a10sa-script", ProtocolSpec.v3)
        self._connector = WebsocketConnector(
            intiface_addr or "ws://127.0.0.1:12345",
            logger=self._client.logger,
        )

    async def connect(self) -> None:
        await self._client.connect(self._connector)

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def send(self, command: GenericLinearCommand) -> None:
        for device in self._client.devices.values():
            if device.linear_actuators:
                await device.linear_actuators[0].command(
                    command.duration, command.position
                )

    async def reset(self) -> None:
        await self.send(GenericLinearCommand(500, 0.0))
