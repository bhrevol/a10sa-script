"""Test cases for the command module."""
import pytest

from vorze_script.command import LinearCommand
from vorze_script.command import RotateCommand
from vorze_script.command import VibrateCommand


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
def test_vibrate(speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    native = VibrateCommand(speed)
    buttplug = native.to_buttplug()
    cmd = buttplug.speeds[0]
    assert native.speed == cmd.speed
    assert native == VibrateCommand.from_buttplug(buttplug)


@pytest.mark.parametrize(
    "duration, position",
    [(0, 0.0), (100, 0.5), (1000, 1.0)],
)
def test_linear(duration: int, position: float) -> None:
    """Test rotate Buttplug roundtrip."""
    native = LinearCommand(duration, position)
    buttplug = native.to_buttplug()
    cmd = buttplug.vectors[0]
    assert native.duration == cmd.duration
    assert native.position == cmd.position
    assert native == LinearCommand.from_buttplug(buttplug)


@pytest.mark.parametrize(
    "speed, clockwise",
    [
        (0.0, True),
        (0.0, False),
        (0.5, True),
        (0.5, False),
        (1.0, True),
        (1.0, False),
    ],
)
def test_rotate(speed: float, clockwise: bool) -> None:
    """Test rotate Buttplug roundtrip."""
    native = RotateCommand(speed, clockwise)
    buttplug = native.to_buttplug()
    cmd = buttplug.rotations[0]
    assert native.speed == cmd.speed
    assert native.clockwise == cmd.clockwise
    assert native == RotateCommand.from_buttplug(buttplug)
