"""Generic command module."""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from buttplug.core import ButtplugMessage
from buttplug.core import LinearCmd
from buttplug.core import LinearSubcommand
from buttplug.core import RotateCmd
from buttplug.core import RotateSubcommand
from buttplug.core import SpeedSubcommand
from buttplug.core import VibrateCmd


class BaseCommand(ABC):
    """Base (native) script command."""

    @abstractmethod
    def to_buttplug(self, device_index: int = 0) -> ButtplugMessage:
        """Return this command as a Buttplug message.

        Arguments:
            device_index: Buttplug device index.
        """

    @classmethod
    @abstractmethod
    def from_buttplug(cls, msg: ButtplugMessage) -> "BaseCommand":
        """Construct command from a Buttplug message."""


@dataclass
class VibrateCommand(BaseCommand):
    """Generic vibration command.

    Attributes
        speed: Vibration speed with a range of [0.0-1.0].
    """

    speed: float

    def to_buttplug(self, device_index: int = 0) -> VibrateCmd:
        """Return this command as a Buttplug message.

        Arguments:
            device_index: Buttplug device index.

        Returns:
            Buttplug message.
        """
        return VibrateCmd(device_index, [SpeedSubcommand(0, self.speed)])

    @classmethod
    def from_buttplug(cls, msg: VibrateCmd) -> "VibrateCommand":
        """Construct command from a Buttplug message."""
        cmd = msg.speeds[0]
        return cls(cmd.speed)


@dataclass
class LinearCommand(BaseCommand):
    """Generic linear movement command.

    Attributes:
        duration: Movement time in milliseconds.
        position: Target position with a range of [0.0-1.0].
    """

    duration: int
    position: float

    def to_buttplug(self, device_index: int = 0) -> LinearCmd:
        """Return this command as a Buttplug message.

        Arguments:
            device_index: Buttplug device index.

        Returns:
            Buttplug message.
        """
        return LinearCmd(
            device_index, [LinearSubcommand(0, self.duration, self.position)]
        )

    @classmethod
    def from_buttplug(cls, msg: LinearCmd) -> "LinearCommand":
        """Construct command from a Buttplug message."""
        cmd = msg.vectors[0]
        return cls(cmd.duration, cmd.position)


@dataclass
class RotateCommand(BaseCommand):
    """Generic rotation command.

    Attributes:
        speed: Rotation speed with a range of [0.0-1.0].
        clockwise: Direction of rotation.
    """

    speed: float
    clockwise: bool

    def to_buttplug(self, device_index: int = 0) -> RotateCmd:
        """Return this command as a Buttplug message.

        Arguments:
            device_index: Buttplug device index.

        Returns:
            Buttplug message.
        """
        return RotateCmd(
            device_index, [RotateSubcommand(0, self.speed, self.clockwise)]
        )

    @classmethod
    def from_buttplug(cls, msg: RotateCmd) -> "RotateCommand":
        """Construct command from a Buttplug message."""
        cmd = msg.rotations[0]
        return cls(cmd.speed, cmd.clockwise)
