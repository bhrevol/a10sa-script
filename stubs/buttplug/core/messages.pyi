from typing import Any, Dict, List

class ButtplugMessage:
    SYSTEM_ID: int
    DEFAULT_ID: int
    id: Any
    def __init__(self) -> None: ...
    def as_json(self) -> str: ...
    @staticmethod
    def from_json(json_str: str) -> "ButtplugMessage": ...
    @staticmethod
    def from_dict(msg_dict: Dict[Any, Any]) -> "ButtplugMessage": ...

class ButtplugDeviceMessage(ButtplugMessage):
    device_index: int
    def __init__(self, device_index: int) -> None: ...

class FleshlightLaunchFW12Cmd(ButtplugDeviceMessage):
    position: int
    speed: int
    def __init__(self, device_index: int, position: int, speed: int) -> None: ...

class LovenseCmd(ButtplugDeviceMessage):
    command: str
    def __init__(self, device_index: int, command: str) -> None: ...

class KiirooCmd(ButtplugDeviceMessage):
    command: str
    def __init__(self, device_index: int, command: str) -> None: ...

class VorzeA10CycloneCmd(ButtplugMessage):
    speed: int
    clockwise: bool
    def __init__(self, speed: int, clockwise: bool) -> None: ...

class SpeedSubcommand:
    index: int
    speed: float
    def __init__(self, index: int, speed: float) -> None: ...

class VibrateCmd(ButtplugDeviceMessage):
    speeds: List[SpeedSubcommand]
    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> VibrateCmd: ...
    def __init__(self, device_index: int, speeds: List[SpeedSubcommand]) -> None: ...

class RotateSubcommand:
    index: int
    speed: float
    clockwise: bool
    def __init__(self, index: int, speed: float, clockwise: bool) -> None: ...

class RotateCmd(ButtplugDeviceMessage):
    rotations: List[RotateSubcommand]
    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> RotateCmd: ...
    def __init__(self, device_index: int, rotations: List[RotateSubcommand]) -> None: ...

class LinearSubcommand:
    index: int
    duration: int
    position: float
    def __init__(self, index: int, duration: int, position: float) -> None: ...

class LinearCmd(ButtplugDeviceMessage):
    vectors: List[LinearSubcommand]
    @staticmethod
    def from_dict(d: Dict[Any, Any]) -> LinearCmd: ...
    def __init__(self, device_index: int, vectors: List[LinearSubcommand]) -> None: ...
