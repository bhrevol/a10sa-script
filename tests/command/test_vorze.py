"""Test cases for vorze commands."""

import pytest
from buttplug import DeviceOutputCommand, OutputType

from a10sa_script.command import VorzePositionCommand
from a10sa_script.command import VorzeRotateCommand
from a10sa_script.command import VorzeVibrateCommand
from a10sa_script.command.vorze import BaseVorzeCommand


@pytest.mark.parametrize(
    "vorze, row",
    [
        (VorzeVibrateCommand.from_speed(0), (0,)),
        (VorzeVibrateCommand.from_speed(50), (50,)),
        (VorzeVibrateCommand.from_speed(100), (100,)),
        (VorzePositionCommand.from_position_and_speed(0, 0), (0, 0)),
        (VorzePositionCommand.from_position_and_speed(100, 50), (100, 50)),
        (VorzePositionCommand.from_position_and_speed(200, 100), (200, 100)),
        (VorzeRotateCommand.from_speed(0, True), (0, 0)),
        (VorzeRotateCommand.from_speed(0, False), (0, 0)),
        (VorzeRotateCommand.from_speed(50, True), (0, 50)),
        (VorzeRotateCommand.from_speed(50, False), (1, 50)),
        (VorzeRotateCommand.from_speed(100, True), (0, 100)),
        (VorzeRotateCommand.from_speed(100, False), (1, 100)),
    ],
)
def test_csv(vorze: BaseVorzeCommand, row: tuple[int]) -> None:
    """Test CSV roundtrip."""
    cmd_cls: type[BaseVorzeCommand] = vorze.__class__
    assert vorze.to_csv() == row
    assert vorze == cmd_cls.from_csv(row)


@pytest.mark.parametrize(
    "vorze, data",
    [
        (VorzeVibrateCommand.from_speed(0), b"\x00"),
        (VorzeVibrateCommand.from_speed(50), b"\x32"),
        (VorzeVibrateCommand.from_speed(100), b"\x64"),
        (VorzePositionCommand.from_position_and_speed(0, 0), b"\x00\x00\x00"),
        (VorzePositionCommand.from_position_and_speed(100, 50), b"\x00\x64\x32"),
        (VorzePositionCommand.from_position_and_speed(200, 100), b"\x00\xc8\x64"),
        (VorzeRotateCommand.from_speed(0, True), b"\x00"),
        (VorzeRotateCommand.from_speed(0, False), b"\x00"),
        (VorzeRotateCommand.from_speed(50, True), b"\x32"),
        (VorzeRotateCommand.from_speed(50, False), b"\xb2"),
        (VorzeRotateCommand.from_speed(100, True), b"\x64"),
        (VorzeRotateCommand.from_speed(100, False), b"\xe4"),
    ],
)
def test_vcsx(vorze: VorzeVibrateCommand, data: bytes) -> None:
    """Test rotate VCSX roundtrip."""
    cmd_cls: type[BaseVorzeCommand] = vorze.__class__
    assert vorze.to_vcsx() == data
    assert vorze == cmd_cls.from_vcsx(data)


@pytest.mark.parametrize(
    "vorze, curpos, buttplug_duration, buttplug_pos",
    [
        (VorzePositionCommand.from_position_and_speed(0, 0), 0.0, 0, 0.0),
        (VorzePositionCommand.from_position_and_speed(100, 50), 0.0, 131, 0.5),
        (
            VorzePositionCommand.from_position_and_speed(200, 50, start_position=100),
            0.5,
            131,
            1.0,
        ),
        (
            VorzePositionCommand.from_position_and_speed(100, 100, start_position=200),
            1.0,
            74,
            0.5,
        ),
        (
            VorzePositionCommand.from_position_and_speed(0, 100, start_position=100),
            0.5,
            74,
            0.0,
        ),
    ],
)
def test_linear_buttplug(
    vorze: VorzePositionCommand,
    curpos: float,
    buttplug_duration: int,
    buttplug_pos: float,
) -> None:
    """Test vibrate Buttplug roundtrip."""
    assert vorze.value == buttplug_pos
    assert vorze.duration == buttplug_duration
    assert vorze == VorzePositionCommand.from_output_command(
        DeviceOutputCommand(
            OutputType.POSITION_WITH_DURATION, buttplug_pos, buttplug_duration
        ),
        start_value=curpos,
    )
