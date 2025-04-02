from .v2 import *
from .machinery import Field, Incoming, Outgoing
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
    "SensorUnsubscribeCmd",
    "RawWriteCmd",
    "SensorReading",
    "ScalarCmd",
    "DeviceAdded",
    "RotateCmd",
    "RawReadCmd",
    "Ping",
    "Ok",
    "StopAllDevices",
    "SensorSubscribeCmd",
    "DeviceRemoved",
    "LinearCmd",
    "RawSubscribeCmd",
    "SensorReadCmd",
    "DeviceList",
    "StartScanning",
    "RawReading",
]

messages: Incomplete

@dataclass
class DeviceMessageAttributes(Field):
    feature_descriptor: str = ...
    step_count: int = ...
    actuator_type: str = ...
    sensor_type: str = ...
    sensor_range: list[tuple[int, int]] = ...
    endpoint: list[str] = ...
    def __post_init__(self) -> None: ...
    def __init__(
        self,
        feature_descriptor=...,
        step_count=...,
        actuator_type=...,
        sensor_type=...,
        sensor_range=...,
        endpoint=...,
    ) -> None: ...

@dataclass
class Device(Field):
    device_name: str
    device_index: int
    device_messages: dict[str, list[DeviceMessageAttributes | dict]]
    device_message_timing_gap: int = ...
    device_display_name: str = ...
    def __post_init__(self) -> None: ...
    def __init__(
        self,
        device_name,
        device_index,
        device_messages,
        device_message_timing_gap=...,
        device_display_name=...,
    ) -> None: ...

@dataclass
class DeviceList(Incoming):
    devices: list[Device | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, id, devices) -> None: ...

@dataclass
class DeviceAdded(Incoming):
    device_name: str
    device_index: int
    device_messages: dict[str, list[DeviceMessageAttributes | dict]]
    device_message_timing_gap: int = ...
    device_display_name: str = ...
    def __post_init__(self) -> None: ...
    def __init__(
        self,
        id,
        device_name,
        device_index,
        device_messages,
        device_message_timing_gap=...,
        device_display_name=...,
    ) -> None: ...

@dataclass
class Scalar(Field):
    index: int
    scalar: float
    actuator_type: str
    def __init__(self, index, scalar, actuator_type) -> None: ...

@dataclass
class ScalarCmd(Outgoing):
    device_index: int
    scalars: list[Scalar | dict]
    def __post_init__(self) -> None: ...
    def __init__(self, device_index, scalars) -> None: ...

@dataclass
class SensorReadCmd(Outgoing):
    device_index: int
    sensor_index: int
    sensor_type: str
    def __init__(self, device_index, sensor_index, sensor_type) -> None: ...

@dataclass
class SensorReading(Incoming):
    device_index: int
    sensor_index: int
    sensor_type: str
    data: list[int]
    def __init__(self, id, device_index, sensor_index, sensor_type, data) -> None: ...

@dataclass
class SensorSubscribeCmd(Outgoing):
    device_index: int
    sensor_index: int
    sensor_type: str
    def __init__(self, device_index, sensor_index, sensor_type) -> None: ...

@dataclass
class SensorUnsubscribeCmd(Outgoing):
    device_index: int
    sensor_index: int
    sensor_type: str
    def __init__(self, device_index, sensor_index, sensor_type) -> None: ...

# Names in __all__ with no definition:
#   DeviceRemoved
#   Error
#   LinearCmd
#   Ok
#   Ping
#   RawReadCmd
#   RawReading
#   RawSubscribeCmd
#   RawUnsubscribeCmd
#   RawWriteCmd
#   RequestDeviceList
#   RequestServerInfo
#   RotateCmd
#   ScanningFinished
#   ServerInfo
#   StartScanning
#   StopAllDevices
#   StopDeviceCmd
#   StopScanning
