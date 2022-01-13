"""Test cases for generic commands."""
import pytest

from a10sa_script.command import GenericLinearCommand
from a10sa_script.command import GenericRotateCommand
from a10sa_script.command import GenericVibrateCommand


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
def test_vibrate(speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    cmd = GenericVibrateCommand(speed)
    assert cmd.speed == cmd.speeds[0]
    assert cmd == GenericVibrateCommand.from_speeds(cmd.speeds)


@pytest.mark.parametrize("duration", [0, 100, 1000])
@pytest.mark.parametrize("position", [0.0, 0.5, 1.0])
def test_linear(duration: int, position: float) -> None:
    """Test rotate Buttplug roundtrip."""
    cmd = GenericLinearCommand(duration, position)
    vector = cmd.vectors[0]
    assert cmd.duration == vector[0]
    assert cmd.position == vector[1]
    assert cmd == GenericLinearCommand.from_vectors(cmd.vectors)


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("clockwise", [True, False])
def test_rotate(speed: float, clockwise: bool) -> None:
    """Test rotate Buttplug roundtrip."""
    cmd = GenericRotateCommand(speed, clockwise)
    rotation = cmd.rotations[0]
    assert cmd.speed == rotation[0]
    assert cmd.clockwise == rotation[1]
    assert cmd == GenericRotateCommand.from_rotations(cmd.rotations)
