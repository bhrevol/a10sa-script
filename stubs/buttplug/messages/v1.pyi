from .v0 import *
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
    "StopScanning",
    "DeviceAdded",
    "VibrateCmd",
    "RotateCmd",
    "Ping",
    "Ok",
    "StopAllDevices",
    "DeviceRemoved",
    "LinearCmd",
    "DeviceList",
    "StartScanning",
]

messages: Incomplete

@dataclass
class RequestServerInfo(Outgoing):
    client_name: str
    message_version: ProtocolSpec = ...
    def __init__(self, client_name, message_version=...) -> None: ...

@dataclass
class DeviceMessageAttributes(Field):
    feature_count: int = ...
    def __init__(self, feature_count=...) -> None: ...

@dataclass
class Device(Field):
    device_name: str
    device_index: int
    device_messages: dict[str, DeviceMessageAttributes | dict]
    def __post_init__(self) -> None: ...
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
    device_messages: dict[str, DeviceMessageAttributes | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, id, device_name, device_index, device_messages) -> None: ...

@dataclass
class Speed(Field):
    index: int
    speed: float
    def __init__(self, index, speed) -> None: ...

@dataclass
class VibrateCmd(Outgoing):
    device_index: int
    speeds: list[Speed | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, device_index, speeds) -> None: ...

@dataclass
class Vector(Field):
    index: int
    duration: int
    position: float
    def __init__(self, index, duration, position) -> None: ...

@dataclass
class LinearCmd(Outgoing):
    device_index: int
    vectors: list[Vector | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, device_index, vectors) -> None: ...

@dataclass
class Rotation(Field):
    index: int
    speed: float
    clockwise: bool
    def __init__(self, index, speed, clockwise) -> None: ...

@dataclass
class RotateCmd(Outgoing):
    device_index: int
    rotations: list[Rotation | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, device_index, rotations) -> None: ...

# Names in __all__ with no definition:
#   DeviceRemoved
#   Error
#   Ok
#   Ping
#   RequestDeviceList
#   ScanningFinished
#   ServerInfo
#   StartScanning
#   StopAllDevices
#   StopDeviceCmd
#   StopScanning
