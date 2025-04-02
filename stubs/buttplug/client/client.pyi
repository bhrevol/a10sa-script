import abc
from ..connectors import Connector as Connector
from ..errors import (
    ReconnectError as ReconnectError,
    ScanNotRunningError as ScanNotRunningError,
    UnexpectedMessageError as UnexpectedMessageError,
    UnsupportedCommandError as UnsupportedCommandError,
)
from ..messages import (
    Decoder as Decoder,
    Encoder as Encoder,
    Incoming as Incoming,
    Outgoing as Outgoing,
    ProtocolSpec as ProtocolSpec,
    v0 as v0,
    v1 as v1,
    v2 as v2,
    v3 as v3,
)
from abc import abstractmethod
from asyncio import Future
from logging import Logger
from typing import Callable

class Client:
    def __init__(self, name: str, v: ProtocolSpec = ...) -> None: ...
    def __getitem__(self, device: int) -> Device: ...
    @property
    def name(self) -> str: ...
    @property
    def version(self) -> ProtocolSpec: ...
    @property
    def logger(self) -> Logger: ...
    @property
    def connected(self) -> bool: ...
    @property
    def devices(self) -> dict[int, "Device"]: ...
    async def send(self, message: Outgoing) -> Incoming: ...
    async def connect(self, connector: Connector) -> None: ...
    async def reconnect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def start_scanning(self) -> Future: ...
    async def stop_scanning(self) -> Future: ...
    async def stop_all(self) -> None: ...

class Device:
    def __init__(
        self,
        client: Client,
        name: str,
        index: int,
        messages: list | dict,
        message_timing_gap: int = None,
        display_name: str = None,
    ) -> None: ...
    @property
    def logger(self) -> Logger: ...
    @property
    def name(self) -> str: ...
    @property
    def index(self) -> int: ...
    def remove(self) -> None: ...
    @property
    def removed(self) -> bool: ...
    @property
    def actuators(self) -> tuple["Actuator", ...]: ...
    @property
    def linear_actuators(self) -> tuple["LinearActuator", ...]: ...
    @property
    def rotatory_actuators(self) -> tuple["RotatoryActuator", ...]: ...
    @property
    def sensors(self) -> tuple["Sensor", ...]: ...
    async def stop(self) -> None: ...
    async def send(self, message: Outgoing) -> Incoming: ...

class DevicePart:
    def __init__(self, device: Device, index: int, description: str) -> None: ...
    @property
    def index(self) -> int: ...
    @property
    def description(self) -> str: ...

class Actuator(DevicePart, metaclass=abc.ABCMeta):
    def __init__(
        self, device: Device, index: int, description: str, step_count: int = None
    ) -> None: ...
    @property
    def step_count(self) -> int: ...
    @abstractmethod
    async def command(self, *args) -> None: ...

class SingleMotorVibrateActuator(Actuator):
    def __init__(self, device: Device, index: int) -> None: ...
    async def command(self, speed: float) -> None: ...

class KiirooActuator(Actuator):
    def __init__(self, device: Device, index: int) -> None: ...
    async def command(self, command: str) -> None: ...

class FleshlightLaunchFW12Actuator(Actuator):
    def __init__(self, device: Device, index: int) -> None: ...
    async def command(self, position: int, speed: int) -> None: ...

class LovenseActuator(Actuator):
    def __init__(self, device: Device, index: int) -> None: ...
    async def command(self, command: str) -> None: ...

class VorzeA10CycloneActuator(Actuator):
    def __init__(self, device: Device, index: int) -> None: ...
    async def command(self, speed: int, clockwise: bool) -> None: ...

class VibrateActuator(Actuator):
    def __init__(self, device: Device, index: int, step_count: int = None) -> None: ...
    async def command(self, speed: float) -> None: ...

class LinearActuator(Actuator):
    async def command(self, duration: int, position: float) -> None: ...

class RotatoryActuator(Actuator):
    async def command(self, speed: float, clockwise: bool) -> None: ...

class ScalarActuator(Actuator):
    def __init__(
        self,
        device: Device,
        index: int,
        description: str,
        actuator_type: str,
        step_count: int,
    ) -> None: ...
    @property
    def type(self) -> str: ...
    async def command(self, scalar: float) -> None: ...

Number = int | float
Range = tuple[Number, Number]
SensorDataCallback = Callable[[list[Number]], None]

class Sensor(DevicePart, metaclass=abc.ABCMeta):
    @abstractmethod
    def read(self) -> list[Number]: ...

class BatteryLevel(Sensor):
    def __init__(self, device: Device) -> None: ...
    @property
    async def read(self) -> list[Number]: ...

class RSSILevel(Sensor):
    def __init__(self, device: Device) -> None: ...
    @property
    async def read(self) -> list[Number]: ...

class GenericSensor(Sensor):
    def __init__(
        self,
        device: Device,
        index: int,
        description: str,
        sensor_type: str,
        ranges: list[Range],
    ) -> None: ...
    @property
    def type(self) -> str: ...
    @property
    def ranges(self) -> list[Range]: ...
    async def read(self) -> list[Number]: ...

class SubscribableSensor(GenericSensor):
    def __init__(
        self,
        device: Device,
        index: int,
        description: str,
        sensor_type: str,
        ranges: list[Range],
    ) -> None: ...
    @property
    def callback(self) -> SensorDataCallback: ...
    async def subscribe(self, cb: SensorDataCallback) -> None: ...
    async def unsubscribe(self) -> None: ...
