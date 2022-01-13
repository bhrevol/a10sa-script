"""Vorze script module."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from buttplug.core import RotateSubcommand

from .base import BaseCommand
from .base import RotateCommand

# from buttplug.core import LinearSubcommand
# from buttplug.core import SpeedSubcommand


_T = TypeVar("_T", bound="BaseVorzeCommand")


class BaseVorzeCommand(BaseCommand):
    """Base Vorze script command.

    Supports native serialization to Vorze CSV and LPEG VCSX.
    """

    @abstractmethod
    def to_csv(self) -> Iterable[Any]:
        """Return Vorze CSV row data for this command."""

    @classmethod
    @abstractmethod
    def from_csv(cls: Type[_T], row: Iterable[Any]) -> _T:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.
        """

    @abstractmethod
    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""

    @classmethod
    @abstractmethod
    def from_vcsx(cls: Type[_T], data: bytes) -> _T:
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.
        """

    @classmethod
    @abstractmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""


@dataclass
class VorzeRotateCommand(BaseVorzeCommand, RotateCommand):
    """Vorze rotation command.

    Attributes:
        speed: Rotation speed with a range of [0-100].
        clockwise: Rotation direction.
    """

    SPEED_DIVISOR: ClassVar[int] = 100

    speed: int
    clockwise: bool

    @property
    def rotations(self) -> List[Tuple[float, bool]]:
        """Return Buttplug RotateCmd rotations for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_rotate_cmd()``.
        """
        return [(self.speed / self.SPEED_DIVISOR, self.clockwise)]

    @classmethod
    def from_rotations(
        cls, rotations: Union[List[RotateSubcommand], List[Tuple[float, bool]]]
    ) -> "VorzeRotateCommand":
        """Return a command instance from Buttplug RotateCmd rotations.

        Arguments:
            rotations: Buttplug RotateCmd rotations list.

        Returns:
            New command instance.

        Raises:
            ValueError: Invalid rotations.
        """
        if not rotations:
            raise ValueError("Rotations cannot be empty.")
        rotation = rotations[0]
        if isinstance(rotation, RotateSubcommand):
            speed = rotation.speed
            clockwise = rotation.clockwise
        else:
            speed, clockwise = rotation
        return cls(round(speed * cls.SPEED_DIVISOR), clockwise)

    def to_csv(self) -> Tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        return 0 if self.clockwise else 1, self.speed

    @classmethod
    def from_csv(
        cls: Type["VorzeRotateCommand"], row: Iterable[Any]
    ) -> "VorzeRotateCommand":
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Rotation command.
        """
        direction, speed = row
        return cls(int(speed), int(direction) == 0)

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 1

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = (self.speed & 0x7F) | (0 if self.clockwise else 0x80)
        return bytes([cmd])

    @classmethod
    def from_vcsx(cls: Type["VorzeRotateCommand"], data: bytes) -> "VorzeRotateCommand":
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.

        Returns:
            Rotation command.

        Raises:
            ValueError: Invalid VCSX data.
        """
        if not data:
            raise ValueError("Invalid VCSX data")
        cmd = data[0]
        speed = cmd & 0x7F
        clockwise = cmd & 0x80 == 0
        return cls(speed, clockwise)
