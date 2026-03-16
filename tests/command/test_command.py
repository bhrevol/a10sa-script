"""Test cases for generic commands."""

import pytest
from buttplug import DeviceOutputCommand, OutputType

from a10sa_script.command import PositionCommand
from a10sa_script.command import PositionWithDurationCommand
from a10sa_script.command import RotateCommand
from a10sa_script.command import VibrateCommand


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
def test_vibrate(speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    cmd = VibrateCommand(speed)
    assert cmd.value == speed
    assert cmd.output_command == DeviceOutputCommand(OutputType.VIBRATE, speed, None)
    assert cmd == VibrateCommand.from_output_command(
        DeviceOutputCommand(OutputType.VIBRATE, speed, None)
    )


@pytest.mark.parametrize("position", [0.0, 0.5, 1.0])
def test_position(position: float) -> None:
    """Test position Buttplug roundtrip."""
    cmd = PositionCommand(position)
    assert cmd.value == position
    assert cmd.output_command == DeviceOutputCommand(
        OutputType.POSITION, position, None
    )
    assert cmd == PositionCommand.from_output_command(
        DeviceOutputCommand(OutputType.POSITION, position, None)
    )


@pytest.mark.parametrize("duration", [0, 100, 1000])
@pytest.mark.parametrize("position", [0.0, 0.5, 1.0])
def test_position_with_duration(duration: int, position: float) -> None:
    """Test position with duration Buttplug roundtrip."""
    cmd = PositionWithDurationCommand(position, duration)
    assert cmd.value == position
    assert cmd.duration == duration
    assert cmd.output_command == DeviceOutputCommand(
        OutputType.POSITION_WITH_DURATION, position, duration
    )
    assert cmd == PositionWithDurationCommand.from_output_command(
        DeviceOutputCommand(OutputType.POSITION_WITH_DURATION, position, duration)
    )


@pytest.mark.parametrize("speed", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("clockwise", [True, False])
def test_rotate(speed: float, clockwise: bool) -> None:
    """Test rotate Buttplug roundtrip."""
    cmd = RotateCommand(speed if clockwise else speed * -1)
    assert abs(cmd.value) == speed
    if speed != 0.0:
        assert cmd.clockwise == clockwise
    assert cmd.output_command == DeviceOutputCommand(
        OutputType.ROTATE, speed if clockwise else speed * -1, None
    )
    assert cmd == RotateCommand.from_output_command(
        DeviceOutputCommand(OutputType.ROTATE, speed if clockwise else speed * -1, None)
    )
