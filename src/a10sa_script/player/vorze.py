import asyncio
import importlib.util
from contextlib import AsyncExitStack
from enum import IntEnum
from typing import TYPE_CHECKING, TypeVar

from loguru import logger

from .player import ScriptPlayer
from ..command.vorze import BaseVorzeCommand, VorzeLinearCommand, VorzeRotateCommand

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData
    from bleak import BleakClient


T = TypeVar("T", bound="BaseVorzeCommand")


class DeviceID(IntEnum):
    CYCLONE_SA = 0x01
    UFO_SA = 0x02
    PISTON_SA = 0x03


VORZE_SERVICE_UUID = "40ee1111-63ec-4b7f-8ce7-712efd55b90e"
SA_CONTROL_SERVICE_UUID = "40ee0111-63ec-4b7f-8ce7-712efd55b90e"
SA_INFO_SERVICE_UUID = "40ee0200-63ec-4b7f-8ce7-712efd55b90e"
NLS_COMMAND_CHARACTERISTIC_UUID = "40ee2222-63ec-4b7f-8ce7-712efd55b90e"


class VorzeScriptPlayer(ScriptPlayer[T]):
    DEVICE_ID = DeviceID.CYCLONE_SA
    LOCAL_NAMES = {"CycSA"}

    def __init__(self) -> None:
        if importlib.util.find_spec("bleak") is None:
            logger.error(
                "Vorze script playback requires installation with a10sa_script[ble]."
            )
        super().__init__()
        self._scan_stack: AsyncExitStack | None = None
        self._clients: dict[str, "BleakClient"] = {}
        self._clients_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Connect to any available Vorze Devices."""
        from bleak import BleakScanner

        if self._scan_stack is not None:
            logger.debug("Already scanning for connections.")
            return
        stack = AsyncExitStack()
        scanner = BleakScanner(
            detection_callback=self._detection_callback,
            service_uuids=[VORZE_SERVICE_UUID],
        )
        await stack.enter_async_context(scanner)  # type: ignore[arg-type]
        logger.debug("Started scanning for Vorze BLE devices.")
        self._scan_stack = stack

    async def disconnect(self) -> None:
        if self._scan_stack is None:
            logger.debug("Not scanning for connections.")
            return
        async with self._clients_lock:
            while self._clients:
                _, client = self._clients.popitem()
                if client.is_connected:
                    await client.disconnect()
        await self._scan_stack.aclose()
        logger.debug("Stopped scanning for Vorze BLE devices.")
        self._scan_stack = None

    async def _detection_callback(
        self, device: "BLEDevice", advertisement_data: "AdvertisementData"
    ) -> None:
        from bleak import BleakClient

        if (
            advertisement_data.local_name in self.LOCAL_NAMES
            and device.address not in self._clients
        ):
            client = BleakClient(
                device, disconnected_callback=self._disconnected_callback
            )
            async with self._clients_lock:
                self._clients[client.address] = client
            logger.debug("Registered client {}", client)

    def _disconnected_callback(self, client: "BleakClient") -> None:
        logger.debug("{} disconnected.", client)

    async def _run(self) -> None:
        from bleak.exc import BleakDeviceNotFoundError

        clients = list(self._clients.values())
        disconnected: list[str] = []
        for client in clients:
            try:
                if not client.is_connected:
                    await client.connect()
            except BleakDeviceNotFoundError:
                disconnected.append(client.address)
                continue
        if disconnected:
            async with self._clients_lock:
                for address in disconnected:
                    try:
                        del self._clients[address]
                    except KeyError:
                        pass
        return await super()._run()

    async def _send_command(self, data: list[int]) -> None:
        for client in self._clients.values():
            await client.write_gatt_char(
                NLS_COMMAND_CHARACTERISTIC_UUID,
                bytes([self.DEVICE_ID.value] + data),
                response=True,
            )


class VorzeCyclonePlayer(VorzeScriptPlayer[VorzeRotateCommand]):
    def __init__(self, speed_multiplier: float = 1.0) -> None:
        if speed_multiplier < 0.0:
            raise ValueError("multiplier must be >= 0")
        super().__init__()
        self._speed_multiplier = speed_multiplier

    @property
    def speed_multiplier(self) -> float:
        return self._speed_multiplier

    @speed_multiplier.setter
    def speed_multiplier(self, value: float) -> None:
        if 0.0 <= value:
            self._speed_multiplier = value
        else:
            raise ValueError("multiplier must be >= 0")

    async def send(self, command: VorzeRotateCommand) -> None:
        logger.debug("Rotate {}", command)
        speed = max(0, min(100, round(command.speed * self.speed_multiplier)))
        await self._send_command([0x01, (not command.clockwise) << 7 | speed])

    async def reset(self) -> None:
        await self.send(VorzeRotateCommand(0, True))


class VorzeUFOPlayer(VorzeCyclonePlayer):
    DEVICE_ID = DeviceID.UFO_SA
    LOCAL_NAMES = {"UFOSA"}


class VorzePistonPlayer(VorzeScriptPlayer[VorzeLinearCommand]):
    DEVICE_ID = DeviceID.PISTON_SA
    LOCAL_NAMES = {"VorzePiston"}

    def __init__(self, speed_multiplier: float = 1.0) -> None:
        if speed_multiplier < 0.0:
            raise ValueError("multiplier must be >= 0")
        super().__init__()
        self.speed_multiplier = 1.0

    @property
    def speed_multiplier(self) -> float:
        return self._speed_multiplier

    @speed_multiplier.setter
    def speed_multiplier(self, value: float) -> None:
        if 0.0 <= value:
            self._speed_multiplier = value
        else:
            raise ValueError("multiplier must be >= 0")

    async def send(self, command: VorzeLinearCommand) -> None:
        logger.debug("Move {}", command)
        speed = max(0, min(100, round(command.speed * self.speed_multiplier)))
        await self._send_command([command.position, speed])

    async def reset(self) -> None:
        await self.send(VorzeLinearCommand(0, 10))
