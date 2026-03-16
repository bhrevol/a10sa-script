"""Generic command module."""

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Self

from buttplug import DeviceOutputCommand, OutputType

from ..exceptions import A10SAError


@dataclass(frozen=True)
class BaseCommand(ABC):
    """Base command which can be serialized to/from Buttplug v4 output command."""

    OUTPUT_TYPE: ClassVar[OutputType]
    """Buttplug v4 output command type."""

    value: float
    """Buttplug v4 output command value as percentage.

    Only percentage based values are supported.
    Buttplug v4 DeviceOutputCommand should be used directly if device specific integer
    steps are required.
    """
    duration: int | None = None
    """Optional Buttplug v4 output command duration in ms."""

    @property
    def output_command(self) -> DeviceOutputCommand:
        """Buttplug v4 output command."""
        return DeviceOutputCommand(self.OUTPUT_TYPE, self.value, self.duration)

    @classmethod
    def from_output_command(cls, output_command: DeviceOutputCommand) -> Self:
        """Return a command instance from a Buttplug v4 output command."""
        if output_command.output_type != cls.OUTPUT_TYPE:
            raise A10SAError(
                f"Cannot deserialize v4 {output_command.output_type} to {cls.__name__}"
            )
        return cls(value=output_command.value, duration=output_command.duration)


@dataclass(frozen=True)
class VibrateCommand(BaseCommand):
    """Vibration device feature command."""

    OUTPUT_TYPE: ClassVar[OutputType] = OutputType.VIBRATE

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise ValueError("Speed must be in range [0.0, 1.0]")


@dataclass(frozen=True)
class PositionCommand(BaseCommand):
    """Position device feature command."""

    OUTPUT_TYPE: ClassVar[OutputType] = OutputType.POSITION

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise ValueError("Position must be in range [0.0, 1.0]")


@dataclass(frozen=True)
class PositionWithDurationCommand(BaseCommand):
    """Position with duration device feature command."""

    OUTPUT_TYPE: ClassVar[OutputType] = OutputType.POSITION_WITH_DURATION

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise ValueError("Position must be in range [0.0, 1.0]")
        if self.duration is not None and self.duration < 0:
            raise ValueError("Duration must be >= 0")

    @property
    def output_command(self) -> DeviceOutputCommand:
        """Buttplug v4 output command."""
        return DeviceOutputCommand(self.OUTPUT_TYPE, self.value, self.duration or 0)


@dataclass(frozen=True)
class RotateCommand(BaseCommand):
    """Rotation device feature command."""

    OUTPUT_TYPE: ClassVar[OutputType] = OutputType.ROTATE

    def __post_init__(self) -> None:
        if self.value < -1.0 or self.value > 1.0:
            raise ValueError("Position must be in range [-1.0, 1.0]")

    @property
    def clockwise(self) -> bool:
        return self.value >= 0.0
