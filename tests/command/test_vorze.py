"""Test cases for vorze commands."""

import pytest
from buttplug.messages.v1 import Rotation, Vector
from buttplug.messages.v3 import Scalar

from a10sa_script.command import VorzeLinearCommand
from a10sa_script.command import VorzeRotateCommand
from a10sa_script.command import VorzeVibrateCommand
from a10sa_script.command.vorze import BaseVorzeCommand


@pytest.mark.parametrize(
    "vorze, row",
    [
        (VorzeVibrateCommand(0), (0,)),
        (VorzeVibrateCommand(50), (50,)),
        (VorzeVibrateCommand(100), (100,)),
        (VorzeLinearCommand(0, 0), (0, 0)),
        (VorzeLinearCommand(100, 50), (100, 50)),
        (VorzeLinearCommand(200, 100), (200, 100)),
        (VorzeRotateCommand(0, True), (0, 0)),
        (VorzeRotateCommand(0, False), (1, 0)),
        (VorzeRotateCommand(50, True), (0, 50)),
        (VorzeRotateCommand(50, False), (1, 50)),
        (VorzeRotateCommand(100, True), (0, 100)),
        (VorzeRotateCommand(100, False), (1, 100)),
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
        (VorzeVibrateCommand(0), b"\x00"),
        (VorzeVibrateCommand(50), b"\x32"),
        (VorzeVibrateCommand(100), b"\x64"),
        (VorzeLinearCommand(0, 0), b"\x00\x00\x00"),
        (VorzeLinearCommand(100, 50), b"\x00\x64\x32"),
        (VorzeLinearCommand(200, 100), b"\x00\xC8\x64"),
        (VorzeRotateCommand(0, True), b"\x00"),
        (VorzeRotateCommand(0, False), b"\x80"),
        (VorzeRotateCommand(50, True), b"\x32"),
        (VorzeRotateCommand(50, False), b"\xB2"),
        (VorzeRotateCommand(100, True), b"\x64"),
        (VorzeRotateCommand(100, False), b"\xE4"),
    ],
)
def test_vcsx(vorze: VorzeVibrateCommand, data: bytes) -> None:
    """Test rotate VCSX roundtrip."""
    cmd_cls: type[BaseVorzeCommand] = vorze.__class__
    assert vorze.to_vcsx() == data
    assert vorze == cmd_cls.from_vcsx(data)


@pytest.mark.parametrize(
    "vorze, buttplug_speed",
    [
        (VorzeVibrateCommand(0), 0.0),
        (VorzeVibrateCommand(50), 0.5),
        (VorzeVibrateCommand(100), 1.0),
    ],
)
def test_vibrate_buttplug(vorze: VorzeVibrateCommand, buttplug_speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    speed = vorze.speeds[0]
    assert speed == buttplug_speed
    with pytest.raises(ValueError):
        VorzeVibrateCommand.from_speeds([])
    assert vorze == VorzeVibrateCommand.from_speeds(vorze.speeds)
    assert vorze == VorzeVibrateCommand.from_speeds(
        [Scalar(0, speed, "Vibrate") for speed in vorze.speeds]
    )


@pytest.mark.parametrize(
    "vorze, curpos, buttplug_duration, buttplug_pos",
    [
        (VorzeLinearCommand(0, 0), 0.0, 0, 0.0),
        (VorzeLinearCommand(100, 50), 0.0, 131, 0.5),
        (VorzeLinearCommand(200, 50), 0.5, 131, 1.0),
        (VorzeLinearCommand(100, 100), 1.0, 74, 0.5),
        (VorzeLinearCommand(0, 100), 0.5, 74, 0.0),
    ],
)
def test_linear_buttplug(
    vorze: VorzeLinearCommand,
    curpos: float,
    buttplug_duration: int,
    buttplug_pos: float,
) -> None:
    """Test vibrate Buttplug roundtrip."""
    vector = vorze.vectors(curpos)[0]
    assert vector == (buttplug_duration, buttplug_pos)
    with pytest.raises(ValueError):
        VorzeLinearCommand.from_vectors([], curpos)
    assert vorze == VorzeLinearCommand.from_vectors(vorze.vectors(curpos), curpos)
    assert vorze == VorzeLinearCommand.from_vectors(
        [Vector(0, duration, position) for duration, position in vorze.vectors(curpos)],
        curpos,
    )


def test_linear_speed_limits() -> None:
    """Test construction resulting in invalid vorze speeds."""
    cmd = VorzeLinearCommand.from_vectors([(100, 1.0)], 0.0)
    # required speed for 100ms 200 unit command rounds to 161
    assert cmd.speed == 100
    cmd = VorzeLinearCommand.from_vectors([(100000, 1.0)], 0.0)
    # required speed for 100s 200 unit command rounds to 0
    assert cmd.speed == 1


@pytest.mark.parametrize(
    "vorze, buttplug_speed",
    [
        (VorzeRotateCommand(0, True), 0.0),
        (VorzeRotateCommand(0, False), 0.0),
        (VorzeRotateCommand(50, True), 0.5),
        (VorzeRotateCommand(50, False), 0.5),
        (VorzeRotateCommand(100, True), 1.0),
        (VorzeRotateCommand(100, False), 1.0),
    ],
)
def test_rotate_buttplug(vorze: VorzeRotateCommand, buttplug_speed: float) -> None:
    """Test rotate Buttplug roundtrip."""
    rotation = vorze.rotations[0]
    assert rotation == (buttplug_speed, vorze.clockwise)
    with pytest.raises(ValueError):
        VorzeRotateCommand.from_rotations([])
    assert vorze == VorzeRotateCommand.from_rotations(
        [Rotation(0, speed, clockwise) for speed, clockwise in vorze.rotations]
    )
    assert vorze == VorzeRotateCommand.from_rotations(vorze.rotations)
