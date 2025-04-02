"""Test cases for generic commands."""
import pytest
from buttplug.messages.v1 import Rotation, Vector
from buttplug.messages.v3 import Scalar

from a10sa_script.command import GenericLinearCommand
from a10sa_script.command import GenericRotateCommand
from a10sa_script.command import GenericVibrateCommand


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
def test_vibrate(speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    cmd = GenericVibrateCommand(speed)
    assert cmd.speed == cmd.speeds[0]
    with pytest.raises(ValueError):
        assert GenericVibrateCommand.from_speeds([])
    assert cmd == GenericVibrateCommand.from_speeds(
        [Scalar(0, speed, "Vibrate") for speed in cmd.speeds]
    )
    assert cmd == GenericVibrateCommand.from_speeds(cmd.speeds)


@pytest.mark.parametrize("duration", [0, 100, 1000])
@pytest.mark.parametrize("position", [0.0, 0.5, 1.0])
def test_linear(duration: int, position: float) -> None:
    """Test rotate Buttplug roundtrip."""
    cmd = GenericLinearCommand(duration, position)
    vector = cmd.vectors[0]
    assert cmd.duration == vector[0]
    assert cmd.position == vector[1]
    with pytest.raises(ValueError):
        GenericLinearCommand.from_vectors([])
    assert cmd == GenericLinearCommand.from_vectors(
        [Vector(0, duration, position) for duration, position in cmd.vectors]
    )
    assert cmd == GenericLinearCommand.from_vectors(cmd.vectors)


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("clockwise", [True, False])
def test_rotate(speed: float, clockwise: bool) -> None:
    """Test rotate Buttplug roundtrip."""
    cmd = GenericRotateCommand(speed, clockwise)
    rotation = cmd.rotations[0]
    assert cmd.speed == rotation[0]
    assert cmd.clockwise == rotation[1]
    with pytest.raises(ValueError):
        GenericRotateCommand.from_rotations([])
    assert cmd == GenericRotateCommand.from_rotations(
        [Rotation(0, speed, clockwise) for speed, clockwise in cmd.rotations]
    )
    assert cmd == GenericRotateCommand.from_rotations(cmd.rotations)
