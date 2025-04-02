from ..errors import ErrorCode
from .machinery import Field, Incoming, Outgoing, ProtocolSpec
from _typeshed import Incomplete
from dataclasses import dataclass

__all__ = [
    "ServerInfo",
    "Error",
    "StopDeviceCmd",
    "ScanningFinished",
    "RequestServerInfo",
    "RequestDeviceList",
    "messages",
    "KiirooCmd",
    "StopScanning",
    "StartScanning",
    "LovenseCmd",
    "DeviceAdded",
    "Ping",
    "Ok",
    "StopAllDevices",
    "DeviceRemoved",
    "FleshlightLaunchFW12Cmd",
    "SingleMotorVibrateCmd",
    "VorzeA10CycloneCmd",
    "DeviceList",
]

messages: Incomplete

@dataclass
class Ok(Incoming):
    def __init__(self, id) -> None: ...

@dataclass
class Error(Incoming):
    error_message: str
    error_code: ErrorCode
    def __post_init__(self) -> None: ...
    def __init__(self, id, error_message, error_code) -> None: ...

@dataclass
class Ping(Outgoing):
    def __init__(self) -> None: ...

@dataclass
class RequestServerInfo(Outgoing):
    client_name: str
    def __init__(self, client_name) -> None: ...

@dataclass
class ServerInfo(Incoming):
    server_name: str
    major_version: int
    minor_version: int
    build_version: int
    message_version: ProtocolSpec
    max_ping_time: int
    def __post_init__(self) -> None: ...
    def __init__(
        self,
        id,
        server_name,
        major_version,
        minor_version,
        build_version,
        message_version,
        max_ping_time,
    ) -> None: ...

@dataclass
class StartScanning(Outgoing):
    def __init__(self) -> None: ...

@dataclass
class StopScanning(Outgoing):
    def __init__(self) -> None: ...

@dataclass
class ScanningFinished(Incoming):
    def __init__(self, id) -> None: ...

@dataclass
class RequestDeviceList(Outgoing):
    def __init__(self) -> None: ...

@dataclass
class Device(Field):
    device_name: str
    device_index: int
    device_messages: list[str]
    def __init__(self, device_name, device_index, device_messages) -> None: ...

@dataclass
class DeviceList(Incoming):
    devices: list[Device | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, id, devices) -> None: ...

@dataclass
class DeviceAdded(Incoming):
    device_name: str
    device_index: int
    device_messages: list[str]
    def __init__(self, id, device_name, device_index, device_messages) -> None: ...

@dataclass
class DeviceRemoved(Incoming):
    device_index: int
    def __init__(self, id, device_index) -> None: ...

@dataclass
class StopDeviceCmd(Outgoing):
    device_index: int
    def __init__(self, device_index) -> None: ...

@dataclass
class StopAllDevices(Outgoing):
    def __init__(self) -> None: ...

@dataclass
class SingleMotorVibrateCmd(Outgoing):
    device_index: int
    speed: float
    def __init__(self, device_index, speed) -> None: ...

@dataclass
class KiirooCmd(Outgoing):
    device_index: int
    command: str
    def __init__(self, device_index, command) -> None: ...

@dataclass
class FleshlightLaunchFW12Cmd(Outgoing):
    device_index: int
    position: int
    speed: int
    def __init__(self, device_index, position, speed) -> None: ...

@dataclass
class LovenseCmd(Outgoing):
    device_index: int
    command: str
    def __init__(self, device_index, command) -> None: ...

@dataclass
class VorzeA10CycloneCmd(Outgoing):
    device_index: int
    speed: int
    clockwise: bool
    def __init__(self, device_index, speed, clockwise) -> None: ...
