"""Generic command module."""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from typing import Protocol
from typing import Tuple
from typing import Union

from buttplug.core import LinearSubcommand
from buttplug.core import RotateSubcommand
from buttplug.core import SpeedSubcommand


class BaseCommand(ABC):  # noqa: B024
    """Base a10sa-script command."""


class VibrateCommand(Protocol):
    """Vibration command protocol.

    Commands which implement VibrateCommand can be serialized to/from Buttplug
    VibrateCmd speeds.
    """

    @property
    @abstractmethod
    def speeds(self) -> List[float]:
        """Return Buttplug VibrateCmd speeds for this command.

        Returns:
            List of speeds suitable for use with buttplug-py
            ``device.send_vibrate_cmd()``.
        """

    @classmethod
    @abstractmethod
    def from_speeds(
        cls, speeds: Union[List[SpeedSubcommand], List[float]]
    ) -> "VibrateCommand":
        """Return a command instance from Buttplug VibrateCmd speeds.

        Arguments:
            speeds: Buttplug VibrateCmd speeds list.

        Returns:
            New command instance.
        """


@dataclass
class GenericVibrateCommand(BaseCommand, VibrateCommand):
    """Generic Buttplug-compliant vibration command.

    Attributes
        speed: Vibration speed with a range of [0.0-1.0].
    """

    speed: float

    @property
    def speeds(self) -> List[float]:
        """Return Buttplug VibrateCmd speeds for this command.

        Returns:
            List of speeds suitable for use with buttplug-py
            ``device.send_vibrate_cmd()``.
        """
        return [self.speed]

    @classmethod
    def from_speeds(
        cls, speeds: Union[List[SpeedSubcommand], List[float]]
    ) -> "GenericVibrateCommand":
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
        if isinstance(speed, SpeedSubcommand):
            speed = speed.speed
        return cls(speed)


class LinearCommand(Protocol):
    """Linear command protocol.

    Commands which implement LinearCommand can be serialized to/from Buttplug
    LinearCmd vectors.
    """

    @property
    @abstractmethod
    def vectors(self) -> List[Tuple[int, float]]:
        """Return Buttplug LinearCmd vectors for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_linear_cmd()``.
        """

    @classmethod
    @abstractmethod
    def from_vectors(
        cls, vectors: Union[List[LinearSubcommand], List[Tuple[int, float]]]
    ) -> "LinearCommand":
        """Return a command instance from Buttplug LinearCmd speeds.

        Arguments:
            vectors: Buttplug LinearCmd vectors list.

        Returns:
            New command instance.
        """


class LinearPositionCommand(Protocol):
    """Alternate linear command protocol for devices which use absolute position.

    Commands which implement LinearPosition Command can be serialized to/from
    Buttplug LinearCmd vectors as long as the current device position is known.
    """

    @abstractmethod
    def vectors(self, position: float) -> List[Tuple[int, float]]:
        """Return Buttplug LinearCmd vectors for this command.

        Arguments:
            position: Current device position in the range [0.0-1.0].

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_linear_cmd()``.
        """

    @classmethod
    @abstractmethod
    def from_vectors(
        cls,
        vectors: Union[List[LinearSubcommand], List[Tuple[int, float]]],
        position: float,
    ) -> "LinearPositionCommand":
        """Return a command instance from Buttplug LinearCmd speeds.

        Arguments:
            vectors: Buttplug LinearCmd vectors list.
            position: Current device position in the range [0.0-1.0].

        Returns:
            New command instance.
        """


@dataclass
class GenericLinearCommand(BaseCommand, LinearCommand):
    """Generic linear movement command.

    Attributes:
        duration: Movement time in milliseconds.
        position: Target position with a range of [0.0-1.0].
    """

    duration: int
    position: float

    @property
    def vectors(self) -> List[Tuple[int, float]]:
        """Return Buttplug LinearCmd vectors for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_linear_cmd()``.
        """
        return [(self.duration, self.position)]

    @classmethod
    def from_vectors(
        cls, vectors: Union[List[LinearSubcommand], List[Tuple[int, float]]]
    ) -> "GenericLinearCommand":
        """Return a command instance from Buttplug LinearCmd speeds.

        Arguments:
            vectors: Buttplug LinearCmd vectors list.

        Returns:
            New command instance.

        Raises:
            ValueError: Invalid vectors.
        """
        if not vectors:
            raise ValueError("Linear vectors cannot be empty.")
        vector = vectors[0]
        if isinstance(vector, LinearSubcommand):
            vector = (vector.duration, vector.position)
        return cls(*vector)


class RotateCommand(Protocol):
    """Rotate command protocol.

    Commands which implement RotateCommand can be serialized to/from Buttplug
    RotateCmd rotations.
    """

    @property
    @abstractmethod
    def rotations(self) -> List[Tuple[float, bool]]:
        """Return Buttplug RotateCmd rotations for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_rotate_cmd()``.
        """

    @classmethod
    @abstractmethod
    def from_rotations(
        cls, rotations: Union[List[RotateSubcommand], List[Tuple[float, bool]]]
    ) -> "RotateCommand":
        """Return a command instance from Buttplug RotateCmd rotations.

        Arguments:
            rotations: Buttplug RotateCmd rotations list.

        Returns:
            New command instance.
        """


@dataclass
class GenericRotateCommand(BaseCommand, RotateCommand):
    """Generic rotation command.

    Attributes:
        speed: Rotation speed with a range of [0.0-1.0].
        clockwise: Direction of rotation.
    """

    speed: float
    clockwise: bool

    @property
    def rotations(self) -> List[Tuple[float, bool]]:
        """Return Buttplug RotateCmd rotations for this command.

        Returns:
            List of vectors suitable for use with buttplug-py
            ``device.send_rotate_cmd()``.
        """
        return [(self.speed, self.clockwise)]

    @classmethod
    def from_rotations(
        cls, rotations: Union[List[RotateSubcommand], List[Tuple[float, bool]]]
    ) -> "GenericRotateCommand":
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
            rotation = (rotation.speed, rotation.clockwise)
        return cls(*rotation)
