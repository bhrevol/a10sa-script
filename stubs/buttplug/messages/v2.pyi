from .v1 import *
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
    "RawUnsubscribeCmd",
    "StopScanning",
    "RawWriteCmd",
    "BatteryLevelCmd",
    "DeviceAdded",
    "VibrateCmd",
    "RotateCmd",
    "RSSILevelCmd",
    "Ping",
    "Ok",
    "StopAllDevices",
    "RawReadCmd",
    "DeviceRemoved",
    "LinearCmd",
    "BatteryLevelReading",
    "RSSILevelReading",
    "RawSubscribeCmd",
    "DeviceList",
    "StartScanning",
    "RawReading",
]

messages: Incomplete

@dataclass
class ServerInfo(Incoming):
    server_name: str
    message_version: ProtocolSpec
    max_ping_time: int
    def __post_init__(self) -> None: ...
    def __init__(self, id, server_name, message_version, max_ping_time) -> None: ...

@dataclass
class DeviceMessageAttributes(Field):
    feature_count: int = ...
    step_count: list[int] = ...
    def __init__(self, feature_count=..., step_count=...) -> None: ...

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
class BatteryLevelCmd(Outgoing):
    device_index: int
    def __init__(self, device_index) -> None: ...

@dataclass
class BatteryLevelReading(Incoming):
    device_index: int
    battery_level: float
    def __init__(self, id, device_index, battery_level) -> None: ...

@dataclass
class RSSILevelCmd(Outgoing):
    device_index: int
    def __init__(self, device_index) -> None: ...

@dataclass
class RSSILevelReading(Incoming):
    device_index: int
    rssi_level: int
    def __init__(self, id, device_index, rssi_level) -> None: ...

@dataclass
class RawWriteCmd(Outgoing):
    device_index: int
    endpoint: str
    data: list[int]
    write_with_response: bool = ...
    def __init__(
        self, device_index, endpoint, data, write_with_response=...
    ) -> None: ...

@dataclass
class RawReadCmd(Outgoing):
    device_index: int
    endpoint: str
    expected_length: int = ...
    wait_for_data: bool = ...
    def __init__(
        self, device_index, endpoint, expected_length=..., wait_for_data=...
    ) -> None: ...

@dataclass
class RawReading(Incoming):
    device_index: int
    endpoint: str
    data: list[int]
    def __init__(self, id, device_index, endpoint, data) -> None: ...

@dataclass
class RawSubscribeCmd(Outgoing):
    device_index: int
    endpoint: str
    def __init__(self, device_index, endpoint) -> None: ...

@dataclass
class RawUnsubscribeCmd(Outgoing):
    device_index: int
    endpoint: str
    def __init__(self, device_index, endpoint) -> None: ...

# Names in __all__ with no definition:
#   DeviceRemoved
#   Error
#   LinearCmd
#   Ok
#   Ping
#   RequestDeviceList
#   RequestServerInfo
#   RotateCmd
#   ScanningFinished
#   StartScanning
#   StopAllDevices
#   StopDeviceCmd
#   StopScanning
#   VibrateCmd
