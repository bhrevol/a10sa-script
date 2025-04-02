"""Vorze script module."""
import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from collections.abc import Iterable
from typing import TypeVar

from buttplug.messages.v1 import Rotation, Vector
from buttplug.messages.v3 import Scalar
from loguru import logger

from .base import BaseCommand
from .base import LinearPositionCommand
from .base import RotateCommand
from .base import VibrateCommand


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
    def from_csv(cls: type[_T], row: Iterable[Any]) -> _T:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.
        """

    @abstractmethod
    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""

    @classmethod
    @abstractmethod
    def from_vcsx(cls: type[_T], data: bytes) -> _T:
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.
        """

    @classmethod
    @abstractmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""


@dataclass
class VorzeVibrateCommand(BaseVorzeCommand, VibrateCommand):
    """Vorze vibration command.

    Attributes:
        speed: Vibration speed with a range of [0-100].
    """

    SPEED_DIVISOR: ClassVar[int] = 100

    speed: int

    @property
    def speeds(self) -> list[float]:
        """Return Buttplug VibrateCmd speeds for this command.

        Returns:
            List of speeds suitable for use with buttplug-py
            ``device.send_vibrate_cmd()``.
        """
        return [self.speed / self.SPEED_DIVISOR]

    @classmethod
    def from_speeds(cls, speeds: list[Scalar] | list[float]) -> "VorzeVibrateCommand":
        """Return a command instance from Buttplug VibrateCmd speeds.

        Arguments:
            speeds: Buttplug VibrateCmd speeds list.

        Returns:
            New command instance.

        Raises:
            ValueError: Invalid speeds.
        """
        if not speeds:
            raise ValueError("Vibrate speeds cannot be empty.")
        speed = speeds[0]
        if isinstance(speed, Scalar):
            speed = speed.scalar
        return cls(round(speed * cls.SPEED_DIVISOR))

    def to_csv(self) -> tuple[int]:
        """Return Vorze CSV row data for this command."""
        return (self.speed,)

    @classmethod
    def from_csv(
        cls: type["VorzeVibrateCommand"], row: Iterable[Any]
    ) -> "VorzeVibrateCommand":
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Vibration command.
        """
        (speed,) = row
        return cls(int(speed))

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 1

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = self.speed & 0x7F
        return bytes([cmd])

    @classmethod
    def from_vcsx(
        cls: type["VorzeVibrateCommand"], data: bytes
    ) -> "VorzeVibrateCommand":
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
        return cls(speed)


@dataclass
class VorzeLinearCommand(BaseVorzeCommand, LinearPositionCommand):
    """Vorze linear movement (piston) command.

    Attributes:
        speed: Movement speed with a range of [0-100].
        position: Device position with a range of [0-200], where zero
            corresponds to the entrance end of the device.

    Note:
        Vorze linear movement commands direct the device to move to a
        designated position at a designated speed. Buttplug (and
        Funscript) linear movements direct the device to move to a
        designated position over some period of time. Due to this difference
        loss of resolution will occur when converting between Vorze and
        Buttplug commands.
    """

    POSITION_DIVISOR: ClassVar[int] = 200

    position: int
    speed: int

    def vectors(self, position: float) -> list[tuple[int, float]]:
        """Return Buttplug LinearCmd vectors for this command.

        Arguments:
            position: Current device position in the range [0.0-1.0].

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_linear_cmd()``.
        """
        distance = abs(self.position - round(position * self.POSITION_DIVISOR))
        if distance == 0 or self.speed == 0.0:
            duration = 0.0
        else:
            duration = (
                math.pow(1 / self.speed, 1 / 1.21)
                * 6658
                * distance
                / self.POSITION_DIVISOR
            )
        return [(round(duration), self.position / self.POSITION_DIVISOR)]

    @classmethod
    def from_vectors(
        cls,
        vectors: list[Vector] | list[tuple[int, float]],
        position: float,
    ) -> "VorzeLinearCommand":
        """Return a command instance from Buttplug LinearCmd speeds.

        Arguments:
            vectors: Buttplug LinearCmd vectors list.
            position: Current device position in the range [0.0-1.0].

        Returns:
            New command instance.

        Raises:
            ValueError: Invalid vectors or position.
        """
        if not vectors:
            raise ValueError("Linear vectors cannot be empty.")
        if isinstance(vectors[0], Vector):
            duration = vectors[0].duration
            new_position = vectors[0].position
        else:
            duration, new_position = vectors[0]
        curpos = round(position * cls.POSITION_DIVISOR)
        newpos = round(new_position * cls.POSITION_DIVISOR)
        distance = abs(newpos - curpos)
        if distance == 0:
            speed = 0
        else:
            # speed conversion from Buttplug device/protocol/vorze_sa.rs
            dur = duration * cls.POSITION_DIVISOR / distance
            speed = round(math.pow(dur / 6658, -1.21))
            if speed > 100:
                speed = 100
                logger.warning("Required movement exceeds max speed (using 100).")
            elif speed == 0:
                speed = 1
                logger.warning("Required movement below min speed (using 1).")
        return cls(newpos, speed)

    def to_csv(self) -> tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        return self.position, self.speed

    @classmethod
    def from_csv(
        cls: type["VorzeLinearCommand"], row: Iterable[Any]
    ) -> "VorzeLinearCommand":
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Vibration command.
        """
        (position, speed) = row
        return cls(int(position), int(speed))

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 3

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = [0, self.position & 0xFF, self.speed & 0xFF]
        return bytes(cmd)

    @classmethod
    def from_vcsx(cls: type["VorzeLinearCommand"], data: bytes) -> "VorzeLinearCommand":
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.

        Returns:
            Rotation command.

        Raises:
            ValueError: Invalid VCSX data.
        """
        if len(data) < 3:
            raise ValueError("Invalid VCSX data")
        cmd = data[:3]
        position = cmd[1] & 0xFF
        speed = cmd[2] & 0xFF
        return cls(position, speed)


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
    def rotations(self) -> list[tuple[float, bool]]:
        """Return Buttplug RotateCmd rotations for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_rotate_cmd()``.
        """
        return [(self.speed / self.SPEED_DIVISOR, self.clockwise)]

    @classmethod
    def from_rotations(
        cls, rotations: list[Rotation] | list[tuple[float, bool]]
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
        if isinstance(rotation, Rotation):
            speed = rotation.speed
            clockwise = rotation.clockwise
        else:
            speed, clockwise = rotation
        return cls(round(speed * cls.SPEED_DIVISOR), clockwise)

    def to_csv(self) -> tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        return 0 if self.clockwise else 1, self.speed

    @classmethod
    def from_csv(
        cls: type["VorzeRotateCommand"], row: Iterable[Any]
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
    def from_vcsx(cls: type["VorzeRotateCommand"], data: bytes) -> "VorzeRotateCommand":
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
