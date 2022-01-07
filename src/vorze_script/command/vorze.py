"""Vorze script module."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from typing import Iterable
from typing import Tuple

from buttplug.core import RotateCmd
from buttplug.core import RotateSubcommand

from .base import BaseCommand

# from buttplug.core import LinearCmd
# from buttplug.core import LinearSubcommand
# from buttplug.core import SpeedSubcommand
# from buttplug.core import VibrateCmd


# def _to_csv_offset(offset_ms: int) -> int:
#     """Convert millisecond time offset to Vorze CSV offsets."""
#     return round(offset_ms / 100)


# def _from_csv_offset(offset_csv: int) -> int:
#     """Convert Vorze CSV time offsets to millisecond offsets."""
#     return offset_csv * 100


class BaseVorzeCommand(BaseCommand):
    """Base Vorze script command."""

    @abstractmethod
    def to_csv(self) -> Iterable[Any]:
        """Return Vorze CSV row data for this command."""

    @classmethod
    @abstractmethod
    def from_csv(cls, row: Iterable[Any]) -> "BaseVorzeCommand":
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.
        """

    @abstractmethod
    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""

    @classmethod
    @abstractmethod
    def from_vcsx(cls, data: bytes) -> "BaseVorzeCommand":
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.
        """


@dataclass
class VorzeRotateCommand(BaseVorzeCommand):
    """Vorze rotation command.

    Attributes:
        speed: Rotation speed with a range of [0-100].
        clockwise: Rotation direction.
    """

    SPEED_DIVISOR: ClassVar[int] = 100

    speed: int
    clockwise: bool

    def to_buttplug(self, device_index: int = 0) -> RotateCmd:
        """Return this command as a Buttplug message.

        Arguments:
            device_index: Buttplug device index.

        Returns:
            Buttplug message.
        """
        cmd = RotateSubcommand(0, self.speed / self.SPEED_DIVISOR, self.clockwise)
        return RotateCmd(device_index, [cmd])

    @classmethod
    def from_buttplug(cls, cmd: RotateCmd) -> "VorzeRotateCommand":
        """Construct command from a Buttplug message."""
        rotation = cmd.rotations[0]
        return VorzeRotateCommand(
            rotation.speed * cls.SPEED_DIVISOR, rotation.clockwise
        )

    def to_csv(self) -> Tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        return 0 if self.clockwise else 1, self.speed

    @classmethod
    def from_csv(cls, row: Iterable[Any]) -> "VorzeRotateCommand":
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Rotation command.
        """
        direction, speed = row
        return cls(speed, direction == 0)

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = (self.speed & 0x7F) | (0 if self.clockwise else 0x80)
        return bytes([cmd])

    @classmethod
    def from_vcsx(cls, data: bytes) -> "BaseVorzeCommand":
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.

        Returns:
            Rotation command.
        """
        cmd = data[0]
        speed = cmd & 0x7F
        clockwise = cmd & 0x80 == 0
        return cls(speed, clockwise)
