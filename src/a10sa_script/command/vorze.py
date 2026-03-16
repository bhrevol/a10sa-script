"""Vorze script module."""

import math
from abc import abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Self

from buttplug import DeviceOutputCommand
from loguru import logger

from .base import (
    BaseCommand,
    PositionWithDurationCommand,
    RotateCommand,
    VibrateCommand,
)
from ..exceptions import A10SAError


@dataclass(frozen=True)
class BaseVorzeCommand(BaseCommand):
    """Commands which can be serialized to Vorze CSV and LPEG VCSX."""

    @abstractmethod
    def vorze_eq(self, other: Self) -> bool:
        """Return true if Vorze values in self are equal to Vorze values in other."""

    @abstractmethod
    def to_csv(self) -> Iterable[Any]:
        """Return Vorze CSV row data for this command."""

    @classmethod
    @abstractmethod
    def from_csv(cls, row: Sequence[str | int]) -> Self:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.
        """

    @abstractmethod
    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""

    @classmethod
    @abstractmethod
    def from_vcsx(cls, data: bytes) -> Self:
        """Construct command from LPEG VCSX data.

        Arguments:
            data: VCSX data.
        """

    @classmethod
    @abstractmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""


@dataclass(frozen=True)
class VorzeVibrateCommand(VibrateCommand, BaseVorzeCommand):
    """Vorze vibration command."""

    SPEED_DIVISOR: ClassVar[int] = 100

    @property
    def speed(self) -> int:
        """Vorze vibrate speed in range [0, 100]."""
        return round(self.value * self.SPEED_DIVISOR)

    @classmethod
    def from_speed(cls, speed: int) -> Self:
        """Construct command from a Vorze speed value."""
        if speed < 0 or speed > 100:
            raise ValueError("Speed must be in range [0, 100]")
        return cls(speed / cls.SPEED_DIVISOR)

    def vorze_eq(self, other: Self) -> bool:
        """Return true if Vorze values in self are equal to Vorze values in other."""
        return isinstance(other, VorzeVibrateCommand) and self.speed == other.speed

    def to_csv(self) -> tuple[int]:
        """Return Vorze CSV row data for this command."""
        return (self.speed,)

    @classmethod
    def from_csv(cls, row: Sequence[str | int]) -> Self:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Vibration command.
        """
        speed = row[0]
        return cls.from_speed(int(speed))

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 1

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = self.speed & 0x7F
        return bytes([cmd])

    @classmethod
    def from_vcsx(cls, data: bytes) -> Self:
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
        return cls.from_speed(speed)


@dataclass(frozen=True)
class VorzePositionCommand(PositionWithDurationCommand, BaseVorzeCommand):
    """Vorze position (Piston) command.

    Note:
        Vorze linear movement commands direct the device to move to a
        designated position at a designated speed. Buttplug (and
        Funscript) linear movements direct the device to move to a
        designated position over some period of time. Due to this difference
        loss of resolution will occur when converting between Vorze and
        Buttplug commands.
    """

    POSITION_DIVISOR: ClassVar[int] = 200

    position: int | None = None
    """Device position in range [0, 200], where zero corresponds to the entrance end of
    the device.
    """
    speed: int | None = None
    """Device speed in range [0, 100]."""

    def __post_init__(self) -> None:
        if self.position is None or self.position < 0 or self.position > 200:
            raise ValueError("Position is required and must be in range [0, 200]")
        if self.speed is None or self.speed < 0 or self.speed > 100:
            raise ValueError("Speed is required and must be in range [0, 100]")

    @classmethod
    def from_position_and_speed(
        cls, stop_position: int, speed: int, *, start_position: int = 0
    ) -> Self:
        """Construct command from Vorze position and speed values."""
        if (
            start_position < 0
            or start_position > 200
            or stop_position < 0
            or stop_position > 200
        ):
            raise ValueError("Position must be in range [0, 200]")
        if speed < 0 or speed > 100:
            raise ValueError("Speed must be in range [0, 100]")
        distance = abs(stop_position - start_position)
        if distance == 0:
            speed = 0
            duration = 0
        else:
            duration = round(
                math.pow(1 / (speed or 1), 1 / 1.21)
                * 6658
                * distance
                / cls.POSITION_DIVISOR
            )
        return cls(
            value=stop_position / cls.POSITION_DIVISOR,
            duration=duration,
            position=stop_position,
            speed=speed,
        )

    @classmethod
    def from_output_command(
        cls, output_command: DeviceOutputCommand, *, start_value: float = 0.0
    ) -> Self:
        """Return a command instance from a Buttplug v4 output command.

        Arguments:
            start_value: Starting device position in Buttplug percentage range [0.0, 1.0].
        """
        if output_command.output_type != cls.OUTPUT_TYPE:
            raise A10SAError(
                f"Cannot deserialize v4 {output_command.output_type} to {cls.__class__}"
            )
        start_position = start_value * cls.POSITION_DIVISOR
        stop_position = round(output_command.value * cls.POSITION_DIVISOR)
        distance = abs(stop_position - start_position)
        if distance == 0:
            speed = 0
        else:
            duration = (output_command.duration or 0) * cls.POSITION_DIVISOR / distance
            speed = round(math.pow(duration / 6658, -1.21))
            if speed > 100:
                speed = 100
                logger.warning("Required movement exceeds max speed (using 100).")
            elif speed == 0:
                speed = 1
                logger.warning("Required movement below min speed (using 1).")
        return cls(
            value=output_command.value,
            duration=output_command.duration,
            position=stop_position,
            speed=speed,
        )

    def vorze_eq(self, other: Self) -> bool:
        """Return true if Vorze values in self are equal to Vorze values in other."""
        return isinstance(other, VorzePositionCommand) and (
            self.position,
            self.speed,
        ) == (other.position, other.speed)

    def to_csv(self) -> tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        assert self.position is not None
        assert self.speed is not None
        return self.position, self.speed

    @classmethod
    def from_csv(cls, row: Sequence[str | int], *, start_position: int = 0) -> Self:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Vibration command.
        """
        position, speed = row[:2]
        return cls.from_position_and_speed(
            int(position), int(speed), start_position=start_position
        )

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 3

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        assert self.position is not None
        assert self.speed is not None
        cmd = [0, self.position & 0xFF, self.speed & 0xFF]
        return bytes(cmd)

    @classmethod
    def from_vcsx(cls, data: bytes, *, start_position: int = 0) -> Self:
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
        return cls.from_position_and_speed(
            position, speed, start_position=start_position
        )


@dataclass(frozen=True)
class VorzeRotateCommand(RotateCommand, BaseVorzeCommand):
    """Vorze rotation (Cyclone, UFO) command."""

    SPEED_DIVISOR: ClassVar[int] = 100

    @property
    def speed(self) -> int:
        """Vorze rotation speed in range [0, 100]."""
        return abs(round(self.value * self.SPEED_DIVISOR))

    @property
    def clockwise(self) -> bool:
        """True if rotation direction is clockwise."""
        return self.value >= 0.0

    @classmethod
    def from_speed(cls, speed: int, clockwise: bool = True) -> Self:
        """Construct command from Vorze speed and direction values."""
        if speed < 0 or speed > 100:
            raise ValueError("Speed must be in range [0, 100]")
        value = speed / cls.SPEED_DIVISOR
        if not clockwise:
            value *= -1
        return cls(value)

    def vorze_eq(self, other: Self) -> bool:
        """Return true if Vorze values in self are equal to Vorze values in other."""
        return (
            isinstance(other, VorzeRotateCommand)
            and self.speed == other.speed
            and (self.speed == 0 or self.clockwise == other.clockwise)
        )

    def to_csv(self) -> tuple[int, int]:
        """Return Vorze CSV row data for this command."""
        return 0 if self.clockwise else 1, self.speed

    @classmethod
    def from_csv(cls, row: Sequence[str | int]) -> Self:
        """Construct command from a Vorze CSV row.

        Arguments:
            row: CSV row data.

        Returns:
            Rotation command.
        """
        direction, speed = row[:2]
        return cls.from_speed(int(speed), int(direction) == 0)

    @classmethod
    def vcsx_size(cls) -> int:
        """Return size of VCSX command data in bytes."""
        return 1

    def to_vcsx(self) -> bytes:
        """Return LPEG VCSX data for this command."""
        cmd = (self.speed & 0x7F) | (0 if self.clockwise else 0x80)
        return bytes([cmd])

    @classmethod
    def from_vcsx(cls, data: bytes) -> Self:
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
        return cls.from_speed(speed, clockwise)
